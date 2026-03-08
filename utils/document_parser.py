# utils/document_parser.py
import io
import PyPDF2
import docx


def parse_document(uploaded_file) -> str:
    """Parse PDF, DOCX, or TXT uploaded via Streamlit and return plain text."""
    name = uploaded_file.name.lower()
    raw = uploaded_file.read()

    if name.endswith(".pdf"):
        return _parse_pdf(raw)
    elif name.endswith(".docx"):
        return _parse_docx(raw)
    elif name.endswith(".txt"):
        return raw.decode("utf-8", errors="ignore")
    else:
        return raw.decode("utf-8", errors="ignore")


def _parse_pdf(raw: bytes) -> str:
    reader = PyPDF2.PdfReader(io.BytesIO(raw))
    pages = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages.append(text.strip())
    return "\n\n".join(pages)


def _parse_docx(raw: bytes) -> str:
    doc = docx.Document(io.BytesIO(raw))
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n\n".join(paragraphs)


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """Split text into overlapping chunks for RAG ingestion."""
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk = " ".join(words[i : i + chunk_size])
        chunks.append(chunk)
        i += chunk_size - overlap
    return chunks
