# modules/brand_rag.py
"""
RAG system for brand documents.
Uses sentence-transformers + numpy for vector similarity (no ChromaDB).
Compatible with Python 3.14+
"""

import os
import pickle
import hashlib
import numpy as np
from sentence_transformers import SentenceTransformer
from utils.document_parser import chunk_text

STORE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "brand_store.pkl")
EMBED_MODEL = "all-MiniLM-L6-v2"

_embedder = None


def _get_embedder():
    global _embedder
    if _embedder is None:
        _embedder = SentenceTransformer(EMBED_MODEL)
    return _embedder


def _load_store() -> dict:
    if os.path.exists(STORE_PATH):
        try:
            with open(STORE_PATH, "rb") as f:
                return pickle.load(f)
        except Exception:
            pass
    return {"ids": [], "documents": [], "embeddings": [], "sources": []}


def _save_store(store: dict):
    with open(STORE_PATH, "wb") as f:
        pickle.dump(store, f)


def ingest_brand_document(text: str, source_name: str) -> int:
    embedder = _get_embedder()
    store = _load_store()
    chunks = chunk_text(text, chunk_size=400, overlap=40)
    if not chunks:
        return 0
    embeddings = embedder.encode(chunks, show_progress_bar=False).tolist()
    added = 0
    for i, (chunk, emb) in enumerate(zip(chunks, embeddings)):
        uid = hashlib.md5(f"{source_name}_{i}_{chunk[:50]}".encode()).hexdigest()
        if uid in store["ids"]:
            idx = store["ids"].index(uid)
            store["documents"][idx] = chunk
            store["embeddings"][idx] = emb
            store["sources"][idx] = source_name
        else:
            store["ids"].append(uid)
            store["documents"].append(chunk)
            store["embeddings"].append(emb)
            store["sources"].append(source_name)
            added += 1
    _save_store(store)
    return added


def query_brand_context(query: str, top_k: int = 5) -> str:
    store = _load_store()
    if not store["documents"]:
        return ""
    embedder = _get_embedder()
    query_emb = embedder.encode([query], show_progress_bar=False)[0]
    emb_matrix = np.array(store["embeddings"])
    query_norm = query_emb / (np.linalg.norm(query_emb) + 1e-10)
    doc_norms = emb_matrix / (np.linalg.norm(emb_matrix, axis=1, keepdims=True) + 1e-10)
    scores = doc_norms @ query_norm
    top_indices = np.argsort(scores)[::-1][:top_k]
    formatted = []
    for idx in top_indices:
        formatted.append(f"[From: {store['sources'][idx]}]\n{store['documents'][idx]}")
    return "\n\n---\n\n".join(formatted)


def get_brand_summary(groq_client) -> str:
    context = query_brand_context(
        "brand identity target audience tone of voice goals values products", top_k=8
    )
    if not context:
        return "No brand documents uploaded yet."
    resp = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a brand strategist. Summarize brand documents concisely."},
            {"role": "user", "content": f"Summarize:\n1. Brand Identity & Values\n2. Target Audience\n3. Tone of Voice\n4. Key Products/Services\n5. Business Goals\n\nDocuments:\n{context}"}
        ],
        max_tokens=1000
    )
    return resp.choices[0].message.content


def clear_brand_documents():
    empty = {"ids": [], "documents": [], "embeddings": [], "sources": []}
    _save_store(empty)
    if os.path.exists(STORE_PATH):
        try:
            os.remove(STORE_PATH)
        except Exception:
            pass


def get_document_count() -> int:
    try:
        return len(_load_store()["documents"])
    except Exception:
        return 0
