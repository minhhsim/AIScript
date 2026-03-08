# ⚡ ContentIQ — AI Content Intelligence Platform

A production-ready content analysis and script generation platform that beats traditional script generators through:
- Real emotional intelligence (EQ) frameworks
- RAG-powered brand alignment
- Deep video analysis (transcription + vision)
- Psychological hook optimization
- Platform-native script generation

---

## 🚀 Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Add your API key
Edit `apikeys.py`:
```python
groq_key = "YOUR_GROQ_API_KEY"   # Free at console.groq.com
```

### 3. Run the app
```bash
streamlit run main.py
```

---

## 📁 Project Structure

```
contentiq/
├── main.py                    # Streamlit UI (4 pages)
├── apikeys.py                 # API keys
├── requirements.txt
├── modules/
│   ├── script_analyzer.py     # Deep script analysis (hook, EQ, structure)
│   ├── brand_rag.py           # RAG system for brand documents
│   ├── video_analyzer.py      # Video transcription + vision analysis
│   └── script_generator.py   # EQ-powered script generation
├── utils/
│   └── document_parser.py     # PDF, DOCX, TXT parser + chunker
└── chroma_db/                 # Auto-created: persistent vector store
```

---

## 🎯 Features

### 1. Brand Setup (RAG)
- Upload PDF, DOCX, or TXT brand documents
- Automatically chunked, embedded, and stored in ChromaDB
- Powers brand-aligned script generation across all pages
- Generate an AI brand summary from your documents

### 2. Script Analyzer
- Paste any TikTok/YouTube script for instant deep analysis
- Scores: Hook, Emotional Arc, Structure, Tone, Retention
- Emotional arc visualization chart
- Platform suitability radar
- Actionable improvement plan with priority ranking
- AI-rewritten hook suggestion

### 3. Script Generator
- 7 emotional frameworks (Hero's Journey, PAS, Story Loop, etc.)
- 7 hook types (Controversy, Curiosity Gap, Pattern Interrupt, etc.)
- 15 targetable emotions
- Live trend data integration (DuckDuckGo)
- Brand RAG context injection
- Script variations (More Emotional, Shorter, Higher Energy, etc.)
- Full production notes (music mood, text overlays, thumbnail frame)

### 4. Video Feedback
- Upload MP4/MOV/AVI video
- Audio extraction → Groq Whisper transcription
- OpenCV frame extraction (6 key frames)
- Groq Vision frame-by-frame analysis
- Comprehensive scored report:
  - Overall score + grade
  - Viral potential + retention prediction
  - Script quality breakdown
  - Visual quality breakdown
  - Radar chart across 7 dimensions
  - Priority improvement roadmap (impact vs effort)
  - Thumbnail recommendation

---

## 🔑 API Keys Needed

| Key | Where to get | Cost |
|-----|-------------|------|
| `groq_key` | console.groq.com | Free |
| `rapidapi_key` | rapidapi.com (optional) | Free tier |

---

## 🧠 Technology Stack

| Layer | Technology |
|-------|-----------|
| UI | Streamlit |
| LLM | Groq LLaMA 3.3 70B |
| Vision | Groq LLaMA 4 Scout (vision) |
| Speech-to-text | Groq Whisper Large v3 |
| Vector DB | ChromaDB (local, persistent) |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) |
| Video processing | OpenCV + MoviePy |
| Document parsing | PyPDF2 + python-docx |
| Trend data | DuckDuckGo Search |
| Charts | Plotly |
