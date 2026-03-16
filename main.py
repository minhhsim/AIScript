# main.py — ContentIQ: AI-Powered Content Intelligence Platform
import streamlit as st
import os
import sys
import time
import tempfile
import json
import plotly.graph_objects as go
import plotly.express as px

sys.path.insert(0, os.path.dirname(__file__))

from apikeys import groq_key
from groq import Groq

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ContentIQ",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

/* Base */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* Dark background */
.stApp {
    background: #0a0a0f;
    color: #e8e8f0;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #0f0f1a;
    border-right: 1px solid #1e1e30;
}

/* Headers */
h1, h2, h3 {
    font-family: 'Syne', sans-serif !important;
    letter-spacing: -0.02em;
}

/* Logo */
.logo-text {
    font-family: 'Syne', sans-serif;
    font-size: 1.8rem;
    font-weight: 800;
    background: linear-gradient(135deg, #7c3aed, #06b6d4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -0.03em;
}

/* Score card */
.score-card {
    background: linear-gradient(135deg, #12121f, #1a1a2e);
    border: 1px solid #2a2a40;
    border-radius: 16px;
    padding: 24px;
    text-align: center;
    position: relative;
    overflow: hidden;
}
.score-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #7c3aed, #06b6d4);
}
.score-number {
    font-family: 'Syne', sans-serif;
    font-size: 3rem;
    font-weight: 800;
    background: linear-gradient(135deg, #7c3aed, #06b6d4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 1;
}
.score-label {
    color: #6b6b8a;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-top: 4px;
}

/* Metric pill */
.metric-pill {
    display: inline-block;
    background: #1a1a2e;
    border: 1px solid #2a2a40;
    border-radius: 999px;
    padding: 6px 16px;
    font-size: 0.8rem;
    color: #9090b0;
    margin: 4px;
}

/* Section card */
.section-card {
    background: #12121f;
    border: 1px solid #1e1e30;
    border-radius: 12px;
    padding: 20px;
    margin: 12px 0;
}

/* Tag */
.tag {
    display: inline-block;
    background: rgba(124, 58, 237, 0.15);
    border: 1px solid rgba(124, 58, 237, 0.3);
    color: #a78bfa;
    border-radius: 6px;
    padding: 3px 10px;
    font-size: 0.8rem;
    margin: 2px;
}

/* Priority badges */
.badge-high { background: rgba(239,68,68,0.15); border: 1px solid rgba(239,68,68,0.3); color: #f87171; border-radius: 6px; padding: 2px 8px; font-size: 0.75rem; }
.badge-medium { background: rgba(245,158,11,0.15); border: 1px solid rgba(245,158,11,0.3); color: #fbbf24; border-radius: 6px; padding: 2px 8px; font-size: 0.75rem; }
.badge-low { background: rgba(16,185,129,0.15); border: 1px solid rgba(16,185,129,0.3); color: #34d399; border-radius: 6px; padding: 2px 8px; font-size: 0.75rem; }

/* Script output */
.script-output {
    background: #0d0d1a;
    border: 1px solid #2a2a40;
    border-radius: 12px;
    padding: 24px;
    font-family: 'DM Sans', sans-serif;
    font-size: 0.95rem;
    line-height: 1.7;
    white-space: pre-wrap;
    color: #d0d0e8;
}

/* Streamlit overrides */
.stButton > button {
    background: linear-gradient(135deg, #7c3aed, #06b6d4);
    color: white;
    border: none;
    border-radius: 10px;
    padding: 10px 24px;
    font-family: 'Syne', sans-serif;
    font-weight: 600;
    font-size: 0.9rem;
    letter-spacing: 0.02em;
    transition: all 0.2s;
    width: 100%;
}
.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 8px 24px rgba(124,58,237,0.3);
}

.stTextArea textarea, .stTextInput input {
    background: #12121f !important;
    border: 1px solid #2a2a40 !important;
    border-radius: 10px !important;
    color: #e8e8f0 !important;
    font-family: 'DM Sans', sans-serif !important;
}

.stSelectbox > div > div {
    background: #12121f !important;
    border: 1px solid #2a2a40 !important;
    border-radius: 10px !important;
    color: #e8e8f0 !important;
}

.stTabs [data-baseweb="tab-list"] {
    background: #0f0f1a;
    border-radius: 12px;
    padding: 4px;
    gap: 4px;
    border: 1px solid #1e1e30;
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    border-radius: 8px;
    color: #6b6b8a;
    font-family: 'Syne', sans-serif;
    font-weight: 600;
    font-size: 0.85rem;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #7c3aed22, #06b6d422) !important;
    color: #c4b5fd !important;
    border: 1px solid #7c3aed44 !important;
}

.stFileUploader {
    background: #12121f !important;
    border: 1px dashed #2a2a40 !important;
    border-radius: 12px !important;
}

[data-testid="stExpander"] {
    background: #12121f;
    border: 1px solid #1e1e30;
    border-radius: 10px;
}

.stSlider > div > div > div {
    background: linear-gradient(90deg, #7c3aed, #06b6d4) !important;
}

/* Divider */
.divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, #2a2a40, transparent);
    margin: 24px 0;
}

/* Alert/info box */
.info-box {
    background: rgba(6,182,212,0.08);
    border: 1px solid rgba(6,182,212,0.2);
    border-radius: 10px;
    padding: 12px 16px;
    color: #67e8f9;
    font-size: 0.85rem;
}

.warn-box {
    background: rgba(245,158,11,0.08);
    border: 1px solid rgba(245,158,11,0.2);
    border-radius: 10px;
    padding: 12px 16px;
    color: #fbbf24;
    font-size: 0.85rem;
}

/* Strength/weakness items */
.strength-item {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    padding: 8px 0;
    border-bottom: 1px solid #1a1a2e;
    color: #d0d0e8;
    font-size: 0.9rem;
}
</style>
""", unsafe_allow_html=True)

# ── Groq client ───────────────────────────────────────────────────────────────
@st.cache_resource
def get_groq_client():
    return Groq(api_key=groq_key)

client = get_groq_client()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="logo-text">⚡ ContentIQ</div>', unsafe_allow_html=True)
    st.markdown('<p style="color:#6b6b8a;font-size:0.8rem;margin-top:-4px;">AI Content Intelligence Platform</p>', unsafe_allow_html=True)
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    st.markdown('<p style="color:#6b6b8a;font-size:0.75rem;text-transform:uppercase;letter-spacing:0.1em;">Navigation</p>', unsafe_allow_html=True)

    pages = {
        "🎯 Brand Setup":       "brand",
        "📝 Script Analyzer":   "analyzer",
        "✍️ Script Generator":  "generator",
        "📊 Market Research":   "market",
        "🤖 Research Agent":    "research",
        "🎬 Video Feedback":    "video",
        "🔗 URL Analyzer":      "url",
        "👤 Creator Analyzer":  "creator",
        "💬 Script Chat":       "chat",
    }
    page = st.radio("", list(pages.keys()), label_visibility="collapsed")
    current_page = pages[page]

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # Brand status
    try:
        from modules.brand_rag import get_document_count
        doc_count = get_document_count()
        if doc_count > 0:
            st.markdown(f'<div class="info-box">🏷️ Brand context active<br><span style="color:#9090b0">{doc_count} chunks indexed</span></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="warn-box">⚠️ No brand docs uploaded<br><span style="color:#9090b0">Go to Brand Setup first</span></div>', unsafe_allow_html=True)
    except Exception:
        pass

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown('<p style="color:#3a3a5a;font-size:0.72rem;text-align:center;">ContentIQ v1.0 · Powered by Groq</p>', unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════
# PAGE: BRAND SETUP
# ════════════════════════════════════════════════════════════════════
if current_page == "brand":
    st.markdown("# 🎯 Brand Intelligence Setup")
    st.markdown('<p style="color:#6b6b8a">Upload brand documents to power context-aware script generation with RAG.</p>', unsafe_allow_html=True)
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    from modules.brand_rag import ingest_brand_document, get_brand_summary, clear_brand_documents, get_document_count
    from utils.document_parser import parse_document

    col1, col2 = st.columns([3, 2])

    with col1:
        st.markdown("### 📁 Upload Brand Documents")
        st.markdown('<p style="color:#6b6b8a;font-size:0.85rem">Supports PDF, DOCX, TXT — brand guides, tone of voice docs, target market research, product sheets.</p>', unsafe_allow_html=True)

        uploaded = st.file_uploader(
            "Drop files here",
            type=["pdf", "docx", "txt"],
            accept_multiple_files=True,
            label_visibility="collapsed"
        )

        if uploaded:
            if st.button("⚡ Ingest Documents into Brand Memory"):
                progress = st.progress(0)
                total_chunks = 0
                for i, f in enumerate(uploaded):
                    with st.spinner(f"Processing {f.name}..."):
                        text = parse_document(f)
                        chunks = ingest_brand_document(text, f.name)
                        total_chunks += chunks
                    progress.progress((i + 1) / len(uploaded))

                st.success(f"✅ Ingested {len(uploaded)} documents ({total_chunks} knowledge chunks)")
                st.rerun()

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

        # Manual text input
        st.markdown("### ✏️ Or Paste Brand Information")
        manual_text = st.text_area(
            "Brand description, values, target audience...",
            placeholder="We are [Brand Name], a [category] brand targeting [audience]. Our tone is [adjectives]. Our key values are...",
            height=160,
            label_visibility="collapsed"
        )
        manual_name = st.text_input("Document name", value="Manual Brand Input")

        if st.button("💾 Save Brand Information"):
            if manual_text.strip():
                chunks = ingest_brand_document(manual_text, manual_name)
                st.success(f"✅ Saved ({chunks} chunks indexed)")
                st.rerun()

    with col2:
        st.markdown("### 🧠 Brand Intelligence Summary")
        doc_count = get_document_count()

        if doc_count > 0:
            st.markdown(f'<div class="score-card"><div class="score-number">{doc_count}</div><div class="score-label">Knowledge Chunks Indexed</div></div>', unsafe_allow_html=True)
            st.markdown("")

            if st.button("🔍 Generate Brand Summary"):
                with st.spinner("Analyzing brand documents..."):
                    summary = get_brand_summary(client)
                st.markdown('<div class="section-card">' + summary.replace('\n', '<br>') + '</div>', unsafe_allow_html=True)

            st.markdown("")
            if st.button("🗑️ Clear All Brand Documents"):
                clear_brand_documents()
                st.warning("Brand memory cleared.")
                st.rerun()
        else:
            st.markdown('<div class="section-card"><p style="color:#6b6b8a;text-align:center;padding:40px 0">No documents indexed yet.<br>Upload brand files to activate RAG.</p></div>', unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════
# PAGE: SCRIPT ANALYZER
# ════════════════════════════════════════════════════════════════════
elif current_page == "analyzer":
    st.markdown("# 📝 Script Analyzer")
    st.markdown('<p style="color:#6b6b8a">Paste any TikTok or YouTube script for deep psychological and structural analysis.</p>', unsafe_allow_html=True)
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    from modules.script_analyzer import analyze_script, NARRATIVE_FRAMEWORKS, HOOK_ARCHETYPES
    from modules.brand_intelligence import research_brand

    col_input, col_settings = st.columns([3, 1])

    with col_input:
        script_input = st.text_area(
            "Script text",
            placeholder="Paste your TikTok or YouTube script here...",
            height=240,
            label_visibility="collapsed"
        )
        # Brand research for alignment scoring
        brand_for_analysis = st.text_input(
            "Brand name (optional — for brand alignment scoring)",
            placeholder="e.g. Nike, Apple, your startup name...",
            key="analyzer_brand_input"
        )

    with col_settings:
        platform = st.selectbox("Platform", ["TikTok", "YouTube Shorts", "Instagram Reels", "YouTube Long-form"])
        st.markdown("")
        analyze_btn = st.button("⚡ Analyze Script")
        if brand_for_analysis.strip():
            st.markdown(f'<div class="info-box" style="border-color:#7c3aed;padding:8px">🏷️ Will score brand alignment for <strong>{brand_for_analysis}</strong></div>', unsafe_allow_html=True)

    if analyze_btn and script_input.strip():
        # Research brand if provided
        brand_intel_block = ""
        if brand_for_analysis.strip():
            with st.spinner(f"🔍 Researching {brand_for_analysis}..."):
                bi = research_brand(client, brand_for_analysis.strip())
                brand_intel_block = bi.get("injection_block","")

        with st.spinner("Running deep analysis..."):
            analysis = analyze_script(client, script_input, platform, brand_context=brand_intel_block)

        if "error" in analysis and len(analysis) <= 2:
            st.error(f"Analysis failed: {analysis.get('error')}")
        else:
            # ── Overview scores ──────────────────────────────────────────────
            st.markdown("### 📊 Overall Analysis")

            overview = analysis.get("overview", {})
            hook = analysis.get("hook", {})
            emotion = analysis.get("emotional_arc", {})
            structure = analysis.get("structure", {})
            tone = analysis.get("tone_voice", {})
            retention = analysis.get("retention_prediction", {})

            c1, c2, c3, c4, c5 = st.columns(5)
            def score_card(col, score, label):
                col.markdown(f'<div class="score-card"><div class="score-number">{score}</div><div class="score-label">{label}</div></div>', unsafe_allow_html=True)

            score_card(c1, overview.get("overall_score", "—"), "Overall")
            score_card(c2, hook.get("score", "—"), "Hook")
            score_card(c3, emotion.get("score", "—"), "Emotion")
            score_card(c4, structure.get("score", "—"), "Structure")
            score_card(c5, tone.get("score", "—"), "Tone")

            st.markdown("")

            # ── Category & Metadata ─────────────────────────────────────────
            meta_cols = st.columns([2,1,1,1,1])
            meta_cols[0].markdown(f'<span class="tag">📂 {overview.get("category","—")}</span> <span class="tag">🎯 {overview.get("sub_category","—")}</span>', unsafe_allow_html=True)
            meta_cols[1].metric("Duration", f'{overview.get("estimated_duration_seconds","—")}s')
            meta_cols[2].metric("Words", overview.get("word_count","—"))
            meta_cols[3].metric("Virality", retention.get("virality_potential","—"))
            meta_cols[4].metric("Retention", retention.get("predicted_watch_through_rate","—"))

            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

            # ── Emotional Arc Chart ─────────────────────────────────────────
            st.markdown("### 🌊 Emotional Arc")
            journey = emotion.get("journey", [])
            if journey:
                times = [j.get("timestamp", "") for j in journey]
                emotions_list = [j.get("emotion", "") for j in journey]
                intensities = [j.get("intensity", 50) for j in journey]
                purposes = [j.get("purpose", "") for j in journey]

                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=times, y=intensities,
                    mode='lines+markers',
                    line=dict(color='#7c3aed', width=3, shape='spline'),
                    marker=dict(size=10, color='#06b6d4',
                                line=dict(color='#7c3aed', width=2)),
                    text=[f"{e}<br>{p}" for e, p in zip(emotions_list, purposes)],
                    hovertemplate='<b>%{x}</b><br>%{text}<br>Intensity: %{y}/100<extra></extra>',
                    fill='tozeroy',
                    fillcolor='rgba(124,58,237,0.08)'
                ))
                fig.update_layout(
                    paper_bgcolor='#0a0a0f',
                    plot_bgcolor='#12121f',
                    font=dict(color='#9090b0', family='DM Sans'),
                    xaxis=dict(title='Timestamp', gridcolor='#1e1e30', color='#6b6b8a'),
                    yaxis=dict(title='Intensity', range=[0, 100], gridcolor='#1e1e30', color='#6b6b8a'),
                    margin=dict(l=10, r=10, t=10, b=10),
                    height=250,
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)

                eq_col1, eq_col2, eq_col3 = st.columns(3)
                eq_col1.markdown(f'<div class="score-card"><div class="score-number" style="font-size:1.2rem">{emotion.get("dominant_emotion","—")}</div><div class="score-label">Dominant Emotion</div></div>', unsafe_allow_html=True)
                eq_col2.markdown(f'<div class="score-card"><div class="score-number" style="font-size:1.2rem">{emotion.get("emotional_intelligence_rating","—")}</div><div class="score-label">EQ Rating</div></div>', unsafe_allow_html=True)
                eq_col3.markdown(f'<div class="score-card"><div class="score-number" style="font-size:1.2rem">{hook.get("psychological_trigger","—")}</div><div class="score-label">Primary Trigger</div></div>', unsafe_allow_html=True)

            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

            # ── Hook Analysis ────────────────────────────────────────────────
            st.markdown("### 🎣 Hook Analysis")
            h_col1, h_col2 = st.columns([3,2])
            with h_col1:
                st.markdown(f'<div class="section-card"><p style="color:#6b6b8a;font-size:0.75rem;text-transform:uppercase;letter-spacing:0.1em">Hook Text</p><p style="color:#e8e8f0;font-size:1rem;font-style:italic">"{hook.get("text","—")}"</p><p style="color:#6b6b8a;font-size:0.75rem;text-transform:uppercase;letter-spacing:0.1em;margin-top:12px">Feedback</p><p style="color:#d0d0e8;font-size:0.9rem">{hook.get("feedback","—")}</p></div>', unsafe_allow_html=True)
            with h_col2:
                st.markdown(f'<div class="section-card"><p style="color:#6b6b8a;font-size:0.75rem;text-transform:uppercase;letter-spacing:0.1em">Hook Type</p><p><span class="tag">{hook.get("type","—")}</span></p><p style="color:#6b6b8a;font-size:0.75rem;text-transform:uppercase;letter-spacing:0.1em;margin-top:10px">Psychological Trigger</p><p><span class="tag">{hook.get("psychological_trigger","—")}</span></p><p style="color:#6b6b8a;font-size:0.75rem;text-transform:uppercase;letter-spacing:0.1em;margin-top:10px">First 3 Seconds</p><p style="color:#d0d0e8;font-size:0.85rem">{hook.get("first_3_seconds","—")}</p></div>', unsafe_allow_html=True)

            # Improved hook
            if hook.get("improved_version"):
                st.markdown(f'<div class="info-box">💡 <strong>Improved Hook:</strong> {hook.get("improved_version")}</div>', unsafe_allow_html=True)

            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

            # ── Platform Fit ─────────────────────────────────────────────────
            st.markdown("### 📱 Platform Suitability")
            pf = overview.get("platform_fit", {})
            if pf:
                pf_fig = go.Figure(go.Bar(
                    x=list(pf.keys()),
                    y=list(pf.values()),
                    marker_color=['#7c3aed','#06b6d4','#10b981','#f59e0b'],
                    text=[f'{v}/100' for v in pf.values()],
                    textposition='outside',
                    textfont=dict(color='#9090b0', size=11)
                ))
                pf_fig.update_layout(
                    paper_bgcolor='#0a0a0f',
                    plot_bgcolor='#12121f',
                    font=dict(color='#9090b0', family='DM Sans'),
                    xaxis=dict(gridcolor='#1e1e30', color='#6b6b8a'),
                    yaxis=dict(range=[0,110], gridcolor='#1e1e30', color='#6b6b8a'),
                    margin=dict(l=10, r=10, t=10, b=10),
                    height=220,
                    showlegend=False
                )
                st.plotly_chart(pf_fig, use_container_width=True)

            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

            # ── Strengths & Weaknesses ───────────────────────────────────────
            sw_col1, sw_col2 = st.columns(2)
            with sw_col1:
                st.markdown("### ✅ Strengths")
                for s in analysis.get("strengths", []):
                    st.markdown(f'<div class="strength-item"><span style="color:#10b981">▲</span>{s}</div>', unsafe_allow_html=True)
            with sw_col2:
                st.markdown("### ❌ Weaknesses")
                for w in analysis.get("weaknesses", []):
                    st.markdown(f'<div class="strength-item"><span style="color:#ef4444">▼</span>{w}</div>', unsafe_allow_html=True)

            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

            # ── Action Plan ──────────────────────────────────────────────────
            st.markdown("### 🛠️ Improvement Action Plan")
            for item in analysis.get("actionable_improvements", []):
                pri = item.get("priority","Low")
                badge = f'<span class="badge-{"high" if pri=="High" else "medium" if pri=="Medium" else "low"}">{pri}</span>'
                st.markdown(f'<div class="section-card">{badge} <strong style="color:#e8e8f0">{item.get("area","")}</strong><br><span style="color:#9090b0;font-size:0.9rem">{item.get("suggestion","")}</span></div>', unsafe_allow_html=True)

            # ── Rewritten Hook ───────────────────────────────────────────────
            if analysis.get("rewritten_hook"):
                st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
                st.markdown("### ✨ AI-Rewritten Hook")
                st.markdown(f'<div class="script-output">🎣 {analysis.get("rewritten_hook")}</div>', unsafe_allow_html=True)

            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

            # ── Framework & Pattern Intelligence ─────────────────────────────
            st.markdown("### 🧩 Framework & Pattern Intelligence")

            nf   = analysis.get("narrative_framework", {})
            hook = analysis.get("hook", {})
            recs = analysis.get("pattern_recommendations", [])
            balign = analysis.get("brand_alignment", {})

            # Detected framework card
            detected_fw  = nf.get("detected", "None")
            fw_info      = NARRATIVE_FRAMEWORKS.get(detected_fw, {})
            conf         = nf.get("confidence", 0)
            exec_quality = nf.get("execution_quality", "—")
            exec_color   = {"Excellent":"#10b981","Good":"#06b6d4","Fair":"#f59e0b","Poor":"#ef4444"}.get(exec_quality, "#6b6b8a")
            fw_color     = "#7c3aed"

            fw_col1, fw_col2 = st.columns([3, 2])
            with fw_col1:
                st.markdown(f"""
<div style="background:#0f0f1a;border:1px solid #1e1e30;border-left:4px solid {fw_color};border-radius:12px;padding:18px;margin-bottom:12px">
  <div style="display:flex;align-items:center;gap:10px;margin-bottom:10px">
    <span style="font-size:1.5rem">{fw_info.get("icon","🎬")}</span>
    <div>
      <span style="color:{fw_color};font-family:Syne;font-weight:700;font-size:0.95rem">Detected Framework</span>
      <span class="tag" style="margin-left:8px;border-color:{fw_color}44;color:{fw_color}">{conf}% confident</span>
    </div>
  </div>
  <p style="color:#e8e8f0;font-size:1.05rem;font-weight:600;margin:0 0 4px 0">{detected_fw}</p>
  <p style="color:#9090b0;font-size:0.83rem;margin:0 0 10px 0">{fw_info.get("full","—")}</p>
  <div style="background:#0a0a14;border-radius:8px;padding:8px 12px;margin-bottom:8px">
    <span style="color:#6b6b8a;font-size:0.67rem;text-transform:uppercase">Evidence in script</span>
    <p style="color:#d0d0e8;font-style:italic;font-size:0.84rem;margin:3px 0 0 0">"{nf.get("evidence","—")}"</p>
  </div>
  <div style="display:flex;gap:8px;flex-wrap:wrap">
    <span class="tag" style="color:{exec_color};border-color:{exec_color}44">Execution: {exec_quality}</span>
    {"".join([f'<span class="tag" style="color:#ef4444;font-size:0.72rem">Missing: {m}</span>' for m in nf.get("missing_elements",[]) if m])}
  </div>
  {f'<p style="color:#9090b0;font-size:0.82rem;margin-top:8px">{nf.get("execution_notes","")}</p>' if nf.get("execution_notes") else ""}
</div>""", unsafe_allow_html=True)

            with fw_col2:
                hook_arch  = hook.get("archetype", hook.get("type","—"))
                ha_info    = HOOK_ARCHETYPES.get(hook_arch, "")
                st.markdown(f"""
<div style="background:#0f0f1a;border:1px solid #1e1e30;border-left:4px solid #06b6d4;border-radius:12px;padding:18px;margin-bottom:12px">
  <p style="color:#06b6d4;font-size:0.72rem;text-transform:uppercase;font-weight:700;margin-bottom:8px">Hook Archetype</p>
  <p style="color:#e8e8f0;font-weight:600;font-size:0.95rem;margin:0 0 4px 0">{hook_arch}</p>
  <p style="color:#9090b0;font-size:0.82rem;margin:0 0 10px 0">{ha_info}</p>
  {"<div style=\'background:#0a0a14;border-radius:6px;padding:6px 10px;margin-bottom:6px\'><span style=\'color:#10b981;font-size:0.72rem\'>✓ Why it works</span><p style=\'color:#d0d0e8;font-size:0.82rem;margin:2px 0 0 0\'>" + hook.get("why_it_works","") + "</p></div>" if hook.get("why_it_works") else ""}
  {"<div style=\'background:#0a0a14;border-radius:6px;padding:6px 10px\'><span style=\'color:#ef4444;font-size:0.72rem\'>⚠ Weakness</span><p style=\'color:#d0d0e8;font-size:0.82rem;margin:2px 0 0 0\'>" + str(hook.get("why_it_fails","")) + "</p></div>" if hook.get("why_it_fails") and hook.get("why_it_fails") not in [None,"null","None"] else ""}
</div>""", unsafe_allow_html=True)

                # Brand alignment if available
                if balign and balign.get("score") and balign.get("notes") != "No brand context provided":
                    ba_score = balign.get("score", 0)
                    ba_color = "#10b981" if ba_score >= 70 else "#f59e0b" if ba_score >= 40 else "#ef4444"
                    st.markdown(f"""
<div style="background:#0f0f1a;border:1px solid #1e1e30;border-left:4px solid {ba_color};border-radius:12px;padding:14px">
  <p style="color:{ba_color};font-size:0.72rem;text-transform:uppercase;font-weight:700;margin-bottom:6px">Brand Alignment</p>
  <p style="color:{ba_color};font-family:Syne;font-weight:700;font-size:1.4rem;margin:0 0 4px 0">{ba_score}/100</p>
  <p style="color:#9090b0;font-size:0.8rem;margin:0">{balign.get("notes","")}</p>
  {"<p style=\'color:#6b6b8a;font-size:0.75rem;margin-top:6px\'>⚠ " + " · ".join(balign.get("misaligned_elements",[])) + "</p>" if balign.get("misaligned_elements") else ""}
</div>""", unsafe_allow_html=True)

            # ── Pattern Recommendations ───────────────────────────────────────
            if recs:
                st.markdown("#### 💡 Better Pattern Recommendations")
                st.markdown('<p style="color:#6b6b8a;font-size:0.83rem;margin-top:-8px">AI-ranked alternatives that would outperform the current framework for this content.</p>', unsafe_allow_html=True)

                rec_colors = ["#10b981", "#06b6d4", "#f59e0b"]
                for i, rec in enumerate(recs[:3]):
                    rc         = rec_colors[i]
                    rec_fw     = rec.get("framework","")
                    rec_hook   = rec.get("hook_archetype","")
                    rec_fw_info = NARRATIVE_FRAMEWORKS.get(rec_fw, {})
                    st.markdown(f"""
<div style="background:#0a0a14;border:1px solid {rc}33;border-left:3px solid {rc};border-radius:10px;padding:16px;margin-bottom:10px">
  <div style="display:flex;align-items:center;gap:8px;margin-bottom:10px;flex-wrap:wrap">
    <span style="background:{rc}22;border:1px solid {rc}44;border-radius:50%;width:24px;height:24px;display:flex;align-items:center;justify-content:center;color:{rc};font-weight:700;font-size:0.78rem;flex-shrink:0">#{i+1}</span>
    <span style="color:{rc};font-family:Syne;font-weight:700">{rec_fw}</span>
    <span style="color:#6b6b8a">+</span>
    <span class="tag" style="color:{rc};border-color:{rc}44">{rec_hook} Hook</span>
    <span style="color:#6b6b8a;font-size:0.75rem">{rec_fw_info.get("full","")}</span>
  </div>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:10px">
    <div>
      <p style="color:#6b6b8a;font-size:0.67rem;text-transform:uppercase;margin:0 0 3px 0">Why this works better</p>
      <p style="color:#d0d0e8;font-size:0.84rem;margin:0">{rec.get("why_better","")}</p>
    </div>
    <div>
      <p style="color:#6b6b8a;font-size:0.67rem;text-transform:uppercase;margin:0 0 3px 0">Expected improvement</p>
      <p style="color:{rc};font-size:0.84rem;margin:0;font-weight:600">{rec.get("expected_improvement","")}</p>
    </div>
  </div>
  <div style="background:#0f0f1a;border-radius:8px;padding:8px 12px;border-left:2px solid {rc}55">
    <p style="color:#6b6b8a;font-size:0.67rem;text-transform:uppercase;margin:0 0 3px 0">Example opening with this pattern</p>
    <p style="color:{rc};font-style:italic;font-size:0.86rem;margin:0">"{rec.get("example_opening","")}"</p>
  </div>
</div>""", unsafe_allow_html=True)

                # Rewrite with top recommendation button
                top_rec = recs[0] if recs else {}
                if top_rec and st.button(f"✍️ Rewrite with #{1}: {top_rec.get('framework','')} + {top_rec.get('hook_archetype','')} Hook", key="rewrite_top_pattern"):
                    st.session_state["pending_rewrite_framework"] = top_rec.get("framework","")
                    st.session_state["pending_rewrite_hook"]      = top_rec.get("hook_archetype","")
                    st.session_state["pending_rewrite_script"]    = script_input
                    st.markdown('<div class="info-box" style="border-color:#10b981">✅ Go to ✍️ Script Generator — framework and hook are pre-selected.</div>', unsafe_allow_html=True)

    elif analyze_btn:
        st.warning("Please paste a script to analyze.")


# ════════════════════════════════════════════════════════════════════
# PAGE: SCRIPT GENERATOR
# ════════════════════════════════════════════════════════════════════
elif current_page == "generator":
    st.markdown("# ✍️ EQ-Powered Script Generator")
    st.markdown('<p style="color:#6b6b8a">Generate psychologically-optimized scripts — brand-researched, framework-driven, emotionally precise.</p>', unsafe_allow_html=True)
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    from modules.script_generator import generate_script, EMOTIONAL_FRAMEWORKS, HOOK_TYPES, EQ_EMOTIONS
    from modules.brand_rag import query_brand_context, get_document_count
    from modules.brand_intelligence import research_brand, get_topic_research
    from duckduckgo_search import DDGS

    # Inject framework from analyzer recommendation if set
    default_fw   = st.session_state.get("pending_rewrite_framework", list(EMOTIONAL_FRAMEWORKS.keys())[0])
    default_hook = st.session_state.get("pending_rewrite_hook", list(HOOK_TYPES.keys())[0])
    default_topic_prefill = ""
    if st.session_state.get("pending_script_topic"):
        default_topic_prefill = st.session_state.pop("pending_script_topic")

    col_form, col_preview = st.columns([2, 3])

    with col_form:
        st.markdown("### ⚙️ Script Parameters")

        topic = st.text_input("Topic / Product / Message",
                              value=default_topic_prefill,
                              placeholder="e.g. Productivity app for busy moms")
        platform = st.selectbox("Platform", ["TikTok", "YouTube Shorts", "Instagram Reels", "YouTube Long-form"])
        duration = st.selectbox("Duration", ["15 seconds", "30 seconds", "60 seconds", "90 seconds", "3 minutes", "5+ minutes"])
        tone     = st.selectbox("Tone", ["Conversational", "Authoritative", "Inspirational", "Urgent", "Humorous", "Educational", "Empathetic", "Bold"])

        st.markdown("#### 🎣 Hook Strategy")
        hook_idx = list(HOOK_TYPES.keys()).index(default_hook) if default_hook in HOOK_TYPES else 0
        hook_type = st.selectbox("Hook Type", list(HOOK_TYPES.keys()), index=hook_idx)
        st.markdown(f'<div class="info-box" style="margin-top:-8px;padding:8px 12px;font-size:0.82rem">{HOOK_TYPES[hook_type]}</div>', unsafe_allow_html=True)

        st.markdown("#### 🌊 Narrative Framework")
        fw_idx = list(EMOTIONAL_FRAMEWORKS.keys()).index(default_fw) if default_fw in EMOTIONAL_FRAMEWORKS else 0
        framework = st.selectbox("Framework", list(EMOTIONAL_FRAMEWORKS.keys()), index=fw_idx)
        st.markdown(f'<div class="info-box" style="margin-top:-8px;padding:8px 12px;font-size:0.82rem">{EMOTIONAL_FRAMEWORKS[framework]}</div>', unsafe_allow_html=True)

        st.markdown("#### 💭 Target Emotions")
        emotions = st.multiselect("Emotions to trigger", EQ_EMOTIONS, default=["Curiosity", "Inspiration"])

        st.markdown("#### 📋 Additional Conditions")
        conditions = st.text_area("Special requirements", placeholder="e.g. Mention 50% discount, no music, end with testimonial", height=70)

        st.markdown("#### 🏷️ Brand / Topic Intelligence")

        # Brand name for live research
        brand_name_input = st.text_input(
            "Brand name (for live web research)",
            placeholder="e.g. Nike, Tesla, your product name...",
            help="AI will search the web to learn about this brand and inject real facts into the script",
            key="gen_brand_input"
        )

        use_rag    = st.checkbox("📎 Use uploaded brand docs (RAG)", value=get_document_count() > 0)
        use_trends = st.checkbox("🔥 Pull live trend data", value=True)
        use_topic_research = st.checkbox("🔍 Research topic facts from web", value=True)

        # Show injected creator style if set
        creator_style_name = st.session_state.get("creator_style_name","")
        creator_style      = st.session_state.get("creator_style_prompt","")
        if creator_style:
            st.markdown(f'<div class="info-box" style="border-color:#8b5cf6">💉 <strong>Creator style injected:</strong> {creator_style_name}</div>', unsafe_allow_html=True)
            if st.button("✕ Remove style", key="remove_style"):
                st.session_state.pop("creator_style_prompt","")
                st.session_state.pop("creator_style_name","")
                st.rerun()

        generate_btn = st.button("⚡ Generate Script", use_container_width=True)

    with col_preview:
        st.markdown("### 📄 Generated Script")

        if generate_btn and topic.strip():
            prog = st.progress(0); status = st.empty()

            # ── Step 1: Live brand research ──────────────────────────────────
            brand_intel_block = ""
            if brand_name_input.strip():
                status.markdown(f'<div class="info-box">🔍 Researching <strong>{brand_name_input}</strong> from the web...</div>', unsafe_allow_html=True)
                prog.progress(10)
                bi = research_brand(client, brand_name_input.strip())
                brand_intel_block = bi.get("injection_block","")
                if brand_intel_block:
                    bi_profile = bi.get("profile",{})
                    st.markdown(f"""
<div style="background:#0a0a14;border:1px solid #7c3aed33;border-left:3px solid #7c3aed;border-radius:10px;padding:14px;margin-bottom:12px">
  <p style="color:#7c3aed;font-size:0.7rem;text-transform:uppercase;font-weight:700;margin:0 0 8px 0">🔍 Brand Research: {brand_name_input}</p>
  <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:6px">
    <span class="tag" style="color:#7c3aed">🎯 {bi_profile.get("tagline","")}</span>
    <span class="tag">{bi_profile.get("brand_voice","")}</span>
    <span class="tag">👥 {bi_profile.get("target_audience","")[:40]}</span>
  </div>
  <p style="color:#6b6b8a;font-size:0.78rem;margin:0">{bi_profile.get("mission","")[:120]}</p>
</div>""", unsafe_allow_html=True)

            # ── Step 2: RAG context ──────────────────────────────────────────
            brand_ctx = ""
            if use_rag:
                status.markdown('<div class="info-box">📎 Loading brand documents...</div>', unsafe_allow_html=True)
                prog.progress(25)
                brand_ctx = query_brand_context(f"{topic} {tone} {platform} script", top_k=6)

            # ── Step 3: Topic research ────────────────────────────────────────
            topic_facts = ""
            if use_topic_research and not brand_intel_block:
                status.markdown('<div class="info-box">🔍 Researching topic facts...</div>', unsafe_allow_html=True)
                prog.progress(35)
                topic_facts = get_topic_research(client, topic)

            # ── Step 4: Trend data ────────────────────────────────────────────
            trend_data = ""
            if use_trends:
                status.markdown('<div class="info-box">📈 Fetching live trend data...</div>', unsafe_allow_html=True)
                prog.progress(45)
                try:
                    with DDGS() as ddgs:
                        res = list(ddgs.text(f"{topic} {platform} trends 2025", max_results=5))
                        trend_data = "\n".join([r["body"] for r in res if "body" in r])
                except Exception:
                    trend_data = ""

            # ── Step 5: Generate ──────────────────────────────────────────────
            status.markdown('<div class="info-box">✍️ Generating script...</div>', unsafe_allow_html=True)
            prog.progress(60)

            output_box  = st.empty()
            full_script = ""

            stream = generate_script(
                client, topic, platform, duration, tone,
                hook_type, framework, emotions, conditions,
                brand_context     = brand_ctx,
                brand_intelligence = brand_intel_block,
                topic_research    = topic_facts,
                creator_style     = creator_style,
                trend_data        = trend_data,
            )
            for chunk in stream:
                full_script += chunk
                output_box.markdown(f'<div class="script-output">{full_script}▌</div>', unsafe_allow_html=True)

            prog.progress(100); status.empty()
            output_box.markdown(f'<div class="script-output">{full_script}</div>', unsafe_allow_html=True)
            st.session_state["last_script"] = full_script
            # Clear pending rewrite flags
            st.session_state.pop("pending_rewrite_framework","")
            st.session_state.pop("pending_rewrite_hook","")

            # Actions row
            ac1, ac2 = st.columns(2)
            with ac1:
                st.download_button("⬇️ Download Script", full_script,
                    file_name=f"script_{topic[:20].replace(' ','_')}.txt", mime="text/plain")
            with ac2:
                if st.button("💬 Send to Script Chat"):
                    st.session_state["chat_script_context"] = full_script
                    st.markdown('<div class="info-box" style="border-color:#10b981">✅ Script sent to Script Chat!</div>', unsafe_allow_html=True)

        elif "last_script" in st.session_state:
            st.markdown(f'<div class="script-output">{st.session_state["last_script"]}</div>', unsafe_allow_html=True)

        elif generate_btn:
            st.warning("Please enter a topic.")
        else:
            st.markdown('<div class="section-card" style="text-align:center;padding:60px 20px"><p style="color:#3a3a5a;font-size:2rem">✍️</p><p style="color:#6b6b8a">Configure parameters on the left and hit Generate.</p></div>', unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════
# PAGE: VIDEO FEEDBACK
# ════════════════════════════════════════════════════════════════════
elif current_page == "video":
    st.markdown("# 🎬 Video Feedback Engine")
    st.markdown('<p style="color:#6b6b8a">Upload your video for comprehensive AI analysis of script, visuals, energy, retention, and improvement roadmap.</p>', unsafe_allow_html=True)
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    from modules.video_analyzer import analyze_video_file

    col_upload, col_settings = st.columns([2, 1])

    with col_upload:
        st.markdown("### 📤 Upload Video")
        video_file = st.file_uploader(
            "Upload video",
            type=["mp4", "mov", "avi", "mkv"],
            label_visibility="collapsed"
        )
        if video_file:
            st.video(video_file)

    with col_settings:
        st.markdown("### ⚙️ Analysis Settings")
        platform_v = st.selectbox("Platform", ["TikTok", "YouTube Shorts", "Instagram Reels", "YouTube Long-form"])
        st.markdown("")
        analyze_video_btn = st.button("⚡ Analyze Video")
        st.markdown("")
        st.markdown('<div class="info-box">Analysis includes:<br>• Audio transcription (Whisper)<br>• 4 key frame visual analysis<br>• Script quality scoring<br>• Retention prediction<br>• Priority improvement roadmap</div>', unsafe_allow_html=True)

    if analyze_video_btn and video_file:
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

        with tempfile.NamedTemporaryFile(suffix=f".{video_file.name.split('.')[-1]}", delete=False) as tmp:
            tmp.write(video_file.read())
            tmp_path = tmp.name

        progress_bar = st.progress(0)
        status_box = st.empty()

        status_box.markdown('<div class="info-box">🖼️ Extracting frames...</div>', unsafe_allow_html=True)
        progress_bar.progress(10)

        results = {}
        try:
            status_box.markdown('<div class="info-box">🎵 Transcribing audio...</div>', unsafe_allow_html=True)
            progress_bar.progress(30)
            results = analyze_video_file(client, tmp_path, platform_v)
            progress_bar.progress(90)
        except Exception as e:
            st.error(f"Analysis pipeline error: {e}")
            results = {"report": {"error": str(e)}, "transcription": "", "visual_analysis": "", "steps": []}

        progress_bar.progress(100)
        status_box.empty()

        # Show pipeline step log
        if results.get("steps"):
            with st.expander("🔍 Pipeline Log"):
                for step in results["steps"]:
                    st.markdown(f'<span style="color:#9090b0;font-size:0.85rem">{step}</span>', unsafe_allow_html=True)

        try:
            os.remove(tmp_path)
        except Exception:
            pass

        report = results.get("report", {})

        if "error" in report:
            st.error(f"Report generation failed: {report.get('error')}")
            if results.get("transcription"):
                st.markdown("**Transcription:**")
                st.text(results["transcription"])
        else:
            # ── Summary banner ───────────────────────────────────────────────
            grade = report.get("grade", "—")
            overall = report.get("overall_score", 0)
            viral = report.get("viral_potential", "—")

            col_g1, col_g2, col_g3, col_g4 = st.columns(4)
            col_g1.markdown(f'<div class="score-card"><div class="score-number">{overall}</div><div class="score-label">Overall Score</div></div>', unsafe_allow_html=True)
            col_g2.markdown(f'<div class="score-card"><div class="score-number">{grade}</div><div class="score-label">Grade</div></div>', unsafe_allow_html=True)
            col_g3.markdown(f'<div class="score-card"><div class="score-number" style="font-size:1.3rem">{viral}</div><div class="score-label">Viral Potential</div></div>', unsafe_allow_html=True)

            retention_pct = report.get("retention_analysis", {}).get("predicted_retention", "—")
            col_g4.markdown(f'<div class="score-card"><div class="score-number" style="font-size:1.5rem">{retention_pct}</div><div class="score-label">Predicted Retention</div></div>', unsafe_allow_html=True)

            # Executive summary
            if report.get("executive_summary"):
                st.markdown(f'<div class="section-card" style="margin-top:16px"><p style="color:#6b6b8a;font-size:0.75rem;text-transform:uppercase;letter-spacing:0.1em">Executive Summary</p><p style="color:#e8e8f0">{report["executive_summary"]}</p></div>', unsafe_allow_html=True)

            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

            # ── Script vs Visual breakdown ────────────────────────────────────
            st.markdown("### 📊 Score Breakdown")
            script_a = report.get("script_analysis", {})
            visual_a = report.get("visual_analysis", {})

            radar_fig = go.Figure()
            categories = ['Hook Strength', 'Clarity', 'Emotion', 'CTA', 'Production', 'Energy', 'Framing']
            values = [
                script_a.get("hook_strength", 0),
                script_a.get("clarity", 0),
                script_a.get("emotional_resonance", 0),
                script_a.get("cta_effectiveness", 0),
                visual_a.get("production_quality", 0),
                visual_a.get("presenter_energy", 0),
                visual_a.get("framing_score", 0),
            ]
            values_closed = values + [values[0]]
            categories_closed = categories + [categories[0]]

            radar_fig.add_trace(go.Scatterpolar(
                r=values_closed, theta=categories_closed,
                fill='toself', fillcolor='rgba(124,58,237,0.15)',
                line=dict(color='#7c3aed', width=2),
                marker=dict(color='#06b6d4', size=6)
            ))
            radar_fig.update_layout(
                polar=dict(
                    bgcolor='#12121f',
                    radialaxis=dict(visible=True, range=[0,100], gridcolor='#2a2a40', tickfont=dict(color='#6b6b8a', size=9)),
                    angularaxis=dict(gridcolor='#2a2a40', tickfont=dict(color='#9090b0', size=10))
                ),
                paper_bgcolor='#0a0a0f',
                font=dict(color='#9090b0'),
                margin=dict(l=40, r=40, t=20, b=20),
                height=320,
                showlegend=False
            )
            st.plotly_chart(radar_fig, use_container_width=True)

            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

            # ── Script & Visual details ───────────────────────────────────────
            detail_tab1, detail_tab2, detail_tab3 = st.tabs(["📝 Script Analysis", "🎥 Visual Analysis", "🛣️ Improvement Roadmap"])

            with detail_tab1:
                st.markdown(f'<div class="info-box">🎣 <strong>Hook Feedback:</strong> {script_a.get("hook_feedback","—")}</div>', unsafe_allow_html=True)
                st.markdown("")
                s_col1, s_col2 = st.columns(2)
                with s_col1:
                    st.markdown("**✅ Strengths**")
                    for s in script_a.get("top_strengths", []):
                        st.markdown(f'<div class="strength-item"><span style="color:#10b981">▲</span>{s}</div>', unsafe_allow_html=True)
                with s_col2:
                    st.markdown("**❌ Issues**")
                    for s in script_a.get("top_issues", []):
                        st.markdown(f'<div class="strength-item"><span style="color:#ef4444">▼</span>{s}</div>', unsafe_allow_html=True)

                if results.get("transcription"):
                    with st.expander("📜 View Transcription"):
                        st.markdown(f'<div class="script-output">{results["transcription"]}</div>', unsafe_allow_html=True)

                if report.get("rewritten_hook"):
                    st.markdown("**✨ AI-Improved Hook:**")
                    st.markdown(f'<div class="script-output">🎣 {report["rewritten_hook"]}</div>', unsafe_allow_html=True)

            with detail_tab2:
                if results.get("visual_analysis"):
                    st.markdown(f'<div class="section-card">{results["visual_analysis"].replace(chr(10),"<br>")}</div>', unsafe_allow_html=True)

                v_col1, v_col2 = st.columns(2)
                with v_col1:
                    st.markdown("**✅ Visual Strengths**")
                    for s in visual_a.get("top_strengths", []):
                        st.markdown(f'<div class="strength-item"><span style="color:#10b981">▲</span>{s}</div>', unsafe_allow_html=True)
                with v_col2:
                    st.markdown("**❌ Visual Issues**")
                    for s in visual_a.get("top_issues", []):
                        st.markdown(f'<div class="strength-item"><span style="color:#ef4444">▼</span>{s}</div>', unsafe_allow_html=True)

                if report.get("thumbnail_recommendation"):
                    st.markdown(f'<div class="info-box">🖼️ <strong>Thumbnail Recommendation:</strong> {report["thumbnail_recommendation"]}</div>', unsafe_allow_html=True)

            with detail_tab3:
                st.markdown("### 🎯 Priority Action Roadmap")
                roadmap = report.get("improvement_roadmap", [])
                for item in roadmap:
                    impact = item.get("impact","Low")
                    effort = item.get("effort","Low")
                    badge_i = f'<span class="badge-{"high" if impact=="High" else "medium" if impact=="Medium" else "low"}">Impact: {impact}</span>'
                    badge_e = f'<span class="badge-{"low" if effort=="Low" else "medium" if effort=="Medium" else "high"}">Effort: {effort}</span>'
                    st.markdown(f'<div class="section-card"><div style="display:flex;gap:8px;align-items:center;margin-bottom:8px"><span style="color:#7c3aed;font-family:Syne;font-weight:700">#{item.get("priority","")}</span> {badge_i} {badge_e}</div><strong style="color:#e8e8f0">{item.get("action","")}</strong><br><span style="color:#9090b0;font-size:0.85rem">Expected: {item.get("expected_result","")}</span></div>', unsafe_allow_html=True)

                # Retention drop-off
                st.markdown("### 📉 Retention Analysis")
                ret = report.get("retention_analysis", {})
                r_col1, r_col2 = st.columns(2)
                with r_col1:
                    st.markdown("**Drop-off Risk Points**")
                    for d in ret.get("drop_off_moments", []):
                        st.markdown(f'<div class="strength-item"><span style="color:#ef4444">⚠</span>{d}</div>', unsafe_allow_html=True)
                with r_col2:
                    st.markdown("**High Engagement Moments**")
                    for h in ret.get("high_engagement_moments", []):
                        st.markdown(f'<div class="strength-item"><span style="color:#10b981">★</span>{h}</div>', unsafe_allow_html=True)

                st.markdown(f'<div class="section-card"><strong style="color:#e8e8f0">Pacing Verdict:</strong> <span style="color:#9090b0">{ret.get("pacing_verdict","—")}</span></div>', unsafe_allow_html=True)

    elif analyze_video_btn:
        st.warning("Please upload a video first.")

# ════════════════════════════════════════════════════════════════════
# PAGE: URL ANALYZER
# ════════════════════════════════════════════════════════════════════
elif current_page == "url":
    st.markdown("# 🔗 URL Video Analyzer")
    st.markdown('<p style="color:#6b6b8a">Analyze any YouTube or TikTok video by URL — auto-detects video type and tailors analysis for dance, voiceover, tutorial, comedy, and more.</p>', unsafe_allow_html=True)
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    from modules.url_analyzer import analyze_url, build_analysis_graph, detect_video_type, analyze_script_typed, generate_visual_direction
    import math

    col_input, col_meta = st.columns([3, 2])

    with col_input:
        st.markdown("### 🌐 Video URL")
        video_url = st.text_input(
            "Paste URL",
            placeholder="https://www.youtube.com/watch?v=... or https://www.tiktok.com/@user/video/...",
            label_visibility="collapsed"
        )
        platform_url = st.selectbox("Platform context", ["TikTok", "YouTube Shorts", "YouTube Long-form", "Instagram Reels"])

        import shutil as _shutil, sys as _sys, subprocess as _sp2
        if _shutil.which("yt-dlp"):
            _ytdlp_ok = True
        else:
            try:
                _ytdlp_ok = _sp2.run([_sys.executable, "-m", "yt_dlp", "--version"],
                                      capture_output=True, timeout=10).returncode == 0
            except Exception:
                _ytdlp_ok = False

        col_b1, col_b2 = st.columns(2)
        with col_b1:
            fetch_btn = st.button("⚡ Analyze Video")
        with col_b2:
            if _ytdlp_ok:
                st.markdown('<div class="info-box" style="margin-top:0;border-color:#10b981">✅ yt-dlp ready</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="info-box" style="margin-top:0;border-color:#ef4444">⚠️ Run: <code>pip install yt-dlp</code></div>', unsafe_allow_html=True)

    with col_meta:
        st.markdown("### 💡 What You Get")
        st.markdown("""
<div class="section-card">
<div class="strength-item"><span style="color:#7c3aed">◆</span> Full transcript from any video</div>
<div class="strength-item"><span style="color:#06b6d4">◆</span> Interactive node connection map</div>
<div class="strength-item"><span style="color:#10b981">◆</span> Hook · Emotion · Structure scores</div>
<div class="strength-item"><span style="color:#f59e0b">◆</span> Platform fit analysis</div>
<div class="strength-item"><span style="color:#ec4899">◆</span> Emotional journey visualization</div>
<div class="strength-item"><span style="color:#8b5cf6">◆</span> Strengths & weakness nodes</div>
</div>
""", unsafe_allow_html=True)

    if fetch_btn and video_url.strip():
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

        progress = st.progress(0)
        status = st.empty()

        status.markdown('<div class="info-box">📡 Fetching video metadata...</div>', unsafe_allow_html=True)
        progress.progress(10)

        url_data = analyze_url(client, video_url.strip())

        if url_data.get("error"):
            st.error(f"❌ {url_data['error']}")
            st.markdown('<div class="warn-box">Make sure yt-dlp is installed: <code>pip install yt-dlp</code></div>', unsafe_allow_html=True)
        else:
            meta          = url_data.get("metadata", {})
            transcription = url_data.get("transcription", "")

            # ── Step 1: Detect video type ─────────────────────────────────────
            status.markdown('<div class="info-box">🔍 Detecting video type...</div>', unsafe_allow_html=True)
            progress.progress(25)
            video_type = detect_video_type(client, transcription, meta)

            # ── Step 2: Type-specific analysis ────────────────────────────────
            status.markdown(f'<div class="info-box">🧠 Analyzing as {video_type["label"]}...</div>', unsafe_allow_html=True)
            progress.progress(50)
            analysis = analyze_script_typed(client, transcription, platform_url, video_type)

            # ── Step 3: Visual storyboard ─────────────────────────────────────
            status.markdown('<div class="info-box">🎬 Generating visual storyboard...</div>', unsafe_allow_html=True)
            progress.progress(70)
            shots = generate_visual_direction(client, transcription, platform_url, video_type)

            # ── Step 4: Network graph ─────────────────────────────────────────
            status.markdown('<div class="info-box">🕸️ Building intelligence map...</div>', unsafe_allow_html=True)
            progress.progress(90)
            graph_data = build_analysis_graph(analysis, meta, video_type)
            progress.progress(100)
            status.empty()

            # ── Video type banner ─────────────────────────────────────────────
            vt_color = video_type.get("color", "#7c3aed")
            st.markdown(f"""
<div style="background:linear-gradient(135deg,{vt_color}22,transparent);border:1px solid {vt_color}44;border-left:4px solid {vt_color};border-radius:12px;padding:16px 20px;margin-bottom:16px;display:flex;align-items:center;gap:16px">
  <span style="font-size:2rem">{video_type.get("icon","🎬")}</span>
  <div style="flex:1">
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:4px">
      <span style="color:{vt_color};font-family:Syne;font-weight:700;font-size:1rem">{video_type.get("label","")}</span>
      <span class="tag" style="border-color:{vt_color}44;color:{vt_color}">Confidence: {video_type.get("confidence",0)}%</span>
      <span class="tag">{video_type.get("subtype","")}</span>
    </div>
    <p style="color:#9090b0;font-size:0.85rem;margin:0">{video_type.get("reasoning","")}</p>
  </div>
  <div style="display:flex;flex-direction:column;gap:4px;align-items:flex-end">
    {"<span class='tag'>🗣️ Speech</span>" if video_type.get("has_speech") else ""}
    {"<span class='tag'>🎵 Music</span>" if video_type.get("has_music") else ""}
    <span class="tag">⚡ {video_type.get("pacing","").title()} Pacing</span>
  </div>
</div>""", unsafe_allow_html=True)

            # ── Video metadata banner ─────────────────────────────────────────
            m1, m2, m3, m4, m5 = st.columns(5)
            m1.markdown(f'<div class="score-card"><div class="score-number">{analysis.get("overview",{}).get("overall_score","—")}</div><div class="score-label">Score</div></div>', unsafe_allow_html=True)
            m2.markdown(f'<div class="score-card"><div class="score-number" style="font-size:1.1rem">{meta.get("uploader","—")[:15]}</div><div class="score-label">Creator</div></div>', unsafe_allow_html=True)

            dur = meta.get("duration", 0)
            dur_str = f"{dur//60}m {dur%60}s" if dur else "—"
            m3.markdown(f'<div class="score-card"><div class="score-number" style="font-size:1.3rem">{dur_str}</div><div class="score-label">Duration</div></div>', unsafe_allow_html=True)

            views = meta.get("view_count", 0)
            views_str = f"{views/1000:.0f}K" if views and views < 1000000 else (f"{views/1000000:.1f}M" if views else "—")
            m4.markdown(f'<div class="score-card"><div class="score-number" style="font-size:1.3rem">{views_str}</div><div class="score-label">Views</div></div>', unsafe_allow_html=True)
            m5.markdown(f'<div class="score-card"><div class="score-number" style="font-size:1.1rem">{analysis.get("retention_prediction",{}).get("virality_potential","—")}</div><div class="score-label">Viral Potential</div></div>', unsafe_allow_html=True)

            st.markdown(f'<div class="section-card"><span style="color:#6b6b8a;font-size:0.75rem;text-transform:uppercase;letter-spacing:0.1em">Video Title</span><br><strong style="color:#e8e8f0;font-size:1rem">{meta.get("title","—")}</strong></div>', unsafe_allow_html=True)

            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

            # ── VISUAL CONNECTION MAP ─────────────────────────────────────────
            st.markdown("### 🕸️ Script Intelligence Map")
            st.markdown('<p style="color:#6b6b8a;font-size:0.85rem">Every node represents a script dimension. Edge thickness = connection strength. Hover nodes for details.</p>', unsafe_allow_html=True)

            nodes = graph_data["nodes"]
            edges = graph_data["edges"]

            # Build node lookup
            node_map = {n["id"]: n for n in nodes}

            fig = go.Figure()

            # Draw edges first (behind nodes)
            for edge in edges:
                src = node_map.get(edge["from"])
                dst = node_map.get(edge["to"])
                if not src or not dst:
                    continue
                weight = edge.get("weight", 0.5)
                color = edge.get("color", "#2a2a40")
                # Make color semi-transparent based on weight
                fig.add_trace(go.Scatter(
                    x=[src["x"], dst["x"], None],
                    y=[src["y"], dst["y"], None],
                    mode="lines",
                    line=dict(
                        width=max(0.5, weight * 3.5),
                        color=color
                    ),
                    hoverinfo="skip",
                    showlegend=False
                ))

            # Group nodes by type for layered rendering
            group_order = ["journey", "platform", "strength", "weakness", "hook", "emotion", "structure", "tone", "retention", "center"]
            rendered = set()

            for group in group_order:
                group_nodes = [n for n in nodes if n.get("group") == group and n["id"] not in rendered]
                if not group_nodes:
                    continue

                xs = [n["x"] for n in group_nodes]
                ys = [n["y"] for n in group_nodes]
                sizes = [n["size"] for n in group_nodes]
                colors = [n["color"] for n in group_nodes]
                labels = [n["label"] for n in group_nodes]
                details = [n.get("detail", "") for n in group_nodes]

                hover_texts = [f"<b>{l.replace(chr(10),' · ')}</b><br>{d}" for l, d in zip(labels, details)]

                fig.add_trace(go.Scatter(
                    x=xs, y=ys,
                    mode="markers+text",
                    marker=dict(
                        size=sizes,
                        color=colors,
                        line=dict(color="rgba(255,255,255,0.13)", width=1),
                        opacity=0.92,
                    ),
                    text=[l.split("\n")[0] for l in labels],
                    textposition="middle center",
                    textfont=dict(
                        color=[n.get("text_color", "#ffffff") for n in group_nodes],
                        size=[max(7, min(10, n["size"] * 0.28)) for n in group_nodes],
                        family="DM Sans"
                    ),
                    hovertext=hover_texts,
                    hovertemplate="%{hovertext}<extra></extra>",
                    hoverlabel=dict(
                        bgcolor="#1a1a2e",
                        bordercolor="#7c3aed",
                        font=dict(color="#e8e8f0", size=12, family="DM Sans")
                    ),
                    showlegend=False,
                    name=group
                ))
                for n in group_nodes:
                    rendered.add(n["id"])

            # Subtitles for ring nodes (score below label)
            ring_ids = ["hook_node", "emotion_node", "structure_node", "tone_node", "retention_node"]
            ring_nodes = [node_map[rid] for rid in ring_ids if rid in node_map]
            if ring_nodes:
                fig.add_trace(go.Scatter(
                    x=[n["x"] for n in ring_nodes],
                    y=[n["y"] - 0.35 for n in ring_nodes],
                    mode="text",
                    text=[n["label"].split("\n")[1] if "\n" in n["label"] else "" for n in ring_nodes],
                    textfont=dict(size=9, color="#9090b0", family="DM Sans"),
                    hoverinfo="skip",
                    showlegend=False
                ))

            fig.update_layout(
                paper_bgcolor="#0a0a0f",
                plot_bgcolor="#0a0a0f",
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-7, 7]),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-7, 7]),
                margin=dict(l=0, r=0, t=0, b=0),
                height=580,
                dragmode="pan",
                hoverdistance=20,
            )

            st.plotly_chart(fig, use_container_width=True, config={"scrollZoom": True, "displayModeBar": False})

            # Legend
            legend_items = [
                ("#7c3aed", "Video Core"),
                ("#06b6d4", "Hook"),
                ("#10b981", "Emotion Arc"),
                ("#f59e0b", "Structure"),
                ("#ec4899", "Tone"),
                ("#8b5cf6", "Retention"),
                ("#1e3a5f", "Emotion Journey"),
                ("#374151", "Platform Fit"),
            ]
            leg_html = '<div style="display:flex;flex-wrap:wrap;gap:12px;margin-top:-8px;margin-bottom:16px">'
            for color, label in legend_items:
                leg_html += f'<span style="display:flex;align-items:center;gap:5px"><span style="width:10px;height:10px;border-radius:50%;background:{color};display:inline-block"></span><span style="color:#6b6b8a;font-size:0.78rem">{label}</span></span>'
            leg_html += '</div>'
            st.markdown(leg_html, unsafe_allow_html=True)

            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

            # ── Detail tabs ────────────────────────────────────────────────────
            tab1, tab2, tab3, tab4, tab5 = st.tabs(["🎬 Storyboard", "🎣 Hook & Emotion", "🏗️ Structure & Tone", "📜 Transcript", "💡 Action Plan"])

            with tab1:
                if shots:
                    st.markdown(f'<p style="color:#9090b0;font-size:0.85rem">Shot-by-shot visual direction tailored for <strong style="color:{vt_color}">{video_type.get("label","")}</strong> content.</p>', unsafe_allow_html=True)
                    for i, shot in enumerate(shots):
                        mood_color = shot.get("color_mood", vt_color)
                        if not mood_color.startswith("#") or len(mood_color) not in [4,7]:
                            mood_color = vt_color
                        icon = shot.get("icon","🎥")
                        st.markdown(f"""
<div style="background:#0f0f1a;border:1px solid #1e1e30;border-left:4px solid {mood_color};border-radius:12px;padding:18px;margin-bottom:14px">
  <div style="display:flex;align-items:center;gap:10px;margin-bottom:12px">
    <div style="background:{mood_color}22;border:1px solid {mood_color}44;border-radius:50%;width:36px;height:36px;display:flex;align-items:center;justify-content:center;font-size:1.1rem;flex-shrink:0">{icon}</div>
    <div>
      <span style="color:{mood_color};font-family:Syne;font-weight:700;font-size:0.85rem">SHOT {shot.get("shot_number",i+1)}</span>
      <span style="color:#6b6b8a;font-size:0.78rem;margin-left:8px">{shot.get("timestamp","")}</span>
    </div>
    <div style="margin-left:auto;display:flex;gap:5px;flex-wrap:wrap">
      <span class="tag" style="color:{mood_color};border-color:{mood_color}44">{shot.get("shot_type","")}</span>
      <span class="tag">{shot.get("camera_angle","")}</span>
      <span class="tag">{shot.get("camera_movement","")}</span>
    </div>
  </div>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:10px">
    <div><p style="color:#6b6b8a;font-size:0.68rem;text-transform:uppercase;margin:0 0 3px 0">Subject</p><p style="color:#d0d0e8;font-size:0.88rem;margin:0">{shot.get("subject","—")}</p></div>
    <div><p style="color:#6b6b8a;font-size:0.68rem;text-transform:uppercase;margin:0 0 3px 0">Action</p><p style="color:#d0d0e8;font-size:0.88rem;margin:0">{shot.get("action","—")}</p></div>
    <div><p style="color:#6b6b8a;font-size:0.68rem;text-transform:uppercase;margin:0 0 3px 0">Lighting</p><p style="color:#d0d0e8;font-size:0.88rem;margin:0">{shot.get("lighting","—")}</p></div>
    <div><p style="color:#6b6b8a;font-size:0.68rem;text-transform:uppercase;margin:0 0 3px 0">Emotion Target</p><p style="color:{mood_color};font-size:0.88rem;margin:0;font-weight:600">{shot.get("emotion_target","—")}</p></div>
  </div>
  <div style="background:#0a0a14;border-radius:8px;padding:8px 12px;margin-bottom:8px;border-left:2px solid {mood_color}55">
    <p style="color:#6b6b8a;font-size:0.68rem;text-transform:uppercase;margin:0 0 3px 0">Script / Audio</p>
    <p style="color:#e8e8f0;font-style:italic;font-size:0.88rem;margin:0">"{shot.get("script_line","—")}"</p>
  </div>
  <div style="background:{mood_color}11;border-radius:8px;padding:8px 12px;border:1px solid {mood_color}22">
    <p style="color:#6b6b8a;font-size:0.68rem;text-transform:uppercase;margin:0 0 3px 0">🎯 Director Note</p>
    <p style="color:{mood_color};font-size:0.85rem;margin:0">{shot.get("director_note","—")}</p>
  </div>
</div>""", unsafe_allow_html=True)

                    sb_text = "\n\n".join([
                        f"SHOT {s.get('shot_number',i+1)} [{s.get('timestamp','')}]\n"
                        f"Type: {s.get('shot_type','')} | Angle: {s.get('camera_angle','')} | Move: {s.get('camera_movement','')}\n"
                        f"Subject: {s.get('subject','')}\nAction: {s.get('action','')}\n"
                        f"Lighting: {s.get('lighting','')} | Emotion: {s.get('emotion_target','')}\n"
                        f'Audio: "{s.get("script_line","")}"\nDirector Note: {s.get("director_note","")}'
                        for i, s in enumerate(shots)
                    ])
                    st.download_button("⬇️ Download Storyboard", sb_text, file_name="storyboard.txt", mime="text/plain")
                else:
                    st.info("Storyboard could not be generated. Try again.")

            with tab2:
                hook = analysis.get("hook", {})
                emotion = analysis.get("emotional_arc", {})

                h1, h2 = st.columns(2)
                with h1:
                    st.markdown(f"""
<div class="section-card">
<p style="color:#06b6d4;font-size:0.75rem;text-transform:uppercase;letter-spacing:0.1em">Hook Analysis</p>
<p style="color:#e8e8f0;font-style:italic">"{hook.get('text','—')}"</p>
<div style="margin-top:10px">
<span class="tag">{hook.get('type','—')}</span>
<span class="tag">{hook.get('psychological_trigger','—')}</span>
</div>
<p style="color:#9090b0;font-size:0.85rem;margin-top:10px">{hook.get('feedback','—')}</p>
</div>""", unsafe_allow_html=True)

                with h2:
                    st.markdown(f"""
<div class="section-card">
<p style="color:#10b981;font-size:0.75rem;text-transform:uppercase;letter-spacing:0.1em">Emotional Intelligence</p>
<p><span class="tag">Dominant: {emotion.get('dominant_emotion','—')}</span></p>
<p><span class="tag">EQ Rating: {emotion.get('emotional_intelligence_rating','—')}</span></p>
<p style="color:#9090b0;font-size:0.85rem;margin-top:8px">{emotion.get('feedback','—')}</p>
</div>""", unsafe_allow_html=True)

                # Emotion arc chart
                journey = emotion.get("journey", [])
                if journey:
                    times = [j.get("timestamp", "") for j in journey]
                    intensities = [j.get("intensity", 50) for j in journey]
                    emotions_list = [j.get("emotion", "") for j in journey]
                    arc_fig = go.Figure()
                    arc_fig.add_trace(go.Scatter(
                        x=times, y=intensities,
                        mode="lines+markers",
                        line=dict(color="#10b981", width=3, shape="spline"),
                        marker=dict(size=10, color="#06b6d4"),
                        text=emotions_list,
                        hovertemplate="<b>%{x}</b><br>Emotion: %{text}<br>Intensity: %{y}%<extra></extra>",
                        fill="tozeroy", fillcolor="rgba(16,185,129,0.08)"
                    ))
                    arc_fig.update_layout(
                        paper_bgcolor="#0a0a0f", plot_bgcolor="#12121f",
                        font=dict(color="#9090b0", family="DM Sans"),
                        xaxis=dict(gridcolor="#1e1e30", color="#6b6b8a"),
                        yaxis=dict(range=[0, 100], gridcolor="#1e1e30", color="#6b6b8a"),
                        margin=dict(l=10, r=10, t=10, b=10), height=200
                    )
                    st.plotly_chart(arc_fig, use_container_width=True)

                if hook.get("improved_version"):
                    st.markdown(f'<div class="info-box">✨ <strong>Improved Hook:</strong> {hook["improved_version"]}</div>', unsafe_allow_html=True)

            with tab3:
                structure = analysis.get("structure", {})
                tone = analysis.get("tone_voice", {})
                s1, s2 = st.columns(2)
                with s1:
                    segs = structure.get("segments", [])
                    if segs:
                        seg_fig = go.Figure(go.Bar(
                            x=[s.get("name","") for s in segs],
                            y=[s.get("effectiveness",0) for s in segs],
                            marker_color=["#7c3aed","#06b6d4","#10b981"],
                            text=[f'{s.get("effectiveness",0)}/100' for s in segs],
                            textposition="outside"
                        ))
                        seg_fig.update_layout(
                            paper_bgcolor="#0a0a0f", plot_bgcolor="#12121f",
                            font=dict(color="#9090b0"), margin=dict(l=0,r=0,t=0,b=0),
                            height=200, yaxis=dict(range=[0,110], gridcolor="#1e1e30")
                        )
                        st.plotly_chart(seg_fig, use_container_width=True)
                with s2:
                    traits = tone.get("personality_traits", [])
                    st.markdown(f"""
<div class="section-card">
<p style="color:#ec4899;font-size:0.75rem;text-transform:uppercase">Tone Profile</p>
<p><span class="tag">{tone.get('primary_tone','—')}</span> <span class="tag">{tone.get('secondary_tone','—')}</span></p>
<p style="color:#6b6b8a;margin-top:8px;font-size:0.8rem">Energy: <span style="color:#e8e8f0">{tone.get('energy_level','—')}</span></p>
<p style="color:#6b6b8a;font-size:0.8rem">Authenticity: <span style="color:#e8e8f0">{tone.get('authenticity_score','—')}/100</span></p>
<div style="margin-top:8px">{"".join([f'<span class="tag">{t}</span>' for t in traits])}</div>
</div>""", unsafe_allow_html=True)

            with tab4:
                if transcription:
                    st.markdown(f'<div class="script-output">{transcription}</div>', unsafe_allow_html=True)
                    st.download_button("⬇️ Download Transcript", transcription, file_name="transcript.txt", mime="text/plain")
                    # Save for chat
                    st.session_state["chat_transcript"] = transcription
                    st.session_state["chat_meta"] = meta
                    st.markdown('<div class="info-box">💬 Go to Script Chat to customize this script with AI.</div>', unsafe_allow_html=True)
                else:
                    st.info("No transcript available.")

            with tab5:
                for item in analysis.get("actionable_improvements", []):
                    pri = item.get("priority", "Low")
                    badge = f'<span class="badge-{"high" if pri=="High" else "medium" if pri=="Medium" else "low"}">{pri}</span>'
                    st.markdown(f'<div class="section-card">{badge} <strong style="color:#e8e8f0">{item.get("area","")}</strong><br><span style="color:#9090b0;font-size:0.9rem">{item.get("suggestion","")}</span></div>', unsafe_allow_html=True)

                if analysis.get("rewritten_hook"):
                    st.markdown(f'<div class="info-box">🎣 <strong>Rewritten Hook:</strong> {analysis["rewritten_hook"]}</div>', unsafe_allow_html=True)

    elif fetch_btn:
        st.warning("Please enter a video URL.")


# ════════════════════════════════════════════════════════════════════
# PAGE: SCRIPT CHAT  (injected below)
# ════════════════════════════════════════════════════════════════════
elif current_page == "chat":
    from modules.brand_rag import query_brand_context, get_document_count

    # ─────────────────────────────────────────────────────────────────────────
    # Session state
    # ─────────────────────────────────────────────────────────────────────────
    for _k, _v in {
        "chat_messages":       [],
        "chat_script_context": "",
        "chat_wizard_active":  False,
        "chat_wizard_step":    0,
        "chat_wizard_data":    {},
        "chat_pending_msg":    None,
        "chat_suggestions":    [],
    }.items():
        if _k not in st.session_state:
            st.session_state[_k] = _v

    # ─────────────────────────────────────────────────────────────────────────
    # Helper: generate contextual next-step suggestions after each AI reply
    # ─────────────────────────────────────────────────────────────────────────
    def generate_suggestions(groq_client, last_ai_msg: str, script_ctx: str, platform: str) -> list:
        """Ask AI to propose 4-5 smart follow-up action chips."""
        prompt = f"""You are a script coach. The user is refining a {platform} script.

LAST AI RESPONSE (summarised):
{last_ai_msg[:600]}

SCRIPT CONTEXT:
{script_ctx[:400] if script_ctx else "No script loaded yet"}

Generate 5 SHORT, specific, actionable follow-up options the user would actually want to click next.
Rules:
- Each option is ≤7 words
- Mix categories: tone · hook · structure · emotion · platform · brand
- Make them feel like natural next steps, not generic
- No duplicates

Return ONLY a JSON array of 5 strings:
["option 1", "option 2", "option 3", "option 4", "option 5"]"""

        try:
            resp = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200, temperature=0.7,
            )
            import re, json
            raw = resp.choices[0].message.content.strip()
            raw = re.sub(r"^```json\s*","",raw); raw = re.sub(r"^```\s*","",raw); raw = re.sub(r"\s*```$","",raw)
            opts = json.loads(raw)
            return [str(o) for o in opts if o][:5]
        except Exception:
            return []

    # ─────────────────────────────────────────────────────────────────────────
    # Helper: Script Builder Wizard — generates a complete brief then script
    # ─────────────────────────────────────────────────────────────────────────
    WIZARD_STEPS = [
        {
            "id":      "topic",
            "q":       "What's your script about? 🎯",
            "sub":     "Describe the topic, product, or story you want to tell.",
            "type":    "text",
            "ph":      "e.g. My skincare routine that cleared my acne in 2 weeks…",
        },
        {
            "id":      "platform",
            "q":       "Which platform is this for? 📱",
            "sub":     "Pick where this will be posted.",
            "type":    "chips",
            "options": ["TikTok","Instagram Reels","YouTube Shorts","YouTube Long","LinkedIn"],
        },
        {
            "id":      "goal",
            "q":       "What's the #1 goal of this script? 🎯",
            "sub":     "What should the viewer do or feel after watching?",
            "type":    "chips",
            "options": [
                "Build brand awareness",
                "Drive product sales",
                "Get followers",
                "Go viral / entertain",
                "Educate my audience",
                "Build personal brand",
            ],
        },
        {
            "id":      "tone",
            "q":       "What's the vibe? 🎤",
            "sub":     "How should you sound?",
            "type":    "chips",
            "options": ["Conversational","Authoritative","Inspirational","Humorous","Urgent","Empathetic","Bold"],
        },
        {
            "id":      "hook",
            "q":       "How do you want to open? 🎣",
            "sub":     "Choose the hook style that feels right.",
            "type":    "chips",
            "options": [
                "Shocking / hot take",
                "Relatable question",
                "Surprising stat or fact",
                "Mid-story drop",
                "Direct value promise",
                "Pattern interrupt / POV",
            ],
        },
        {
            "id":      "extras",
            "q":       "Any special sauce? ✨",
            "sub":     "Select everything you want included. (Multi-select OK)",
            "type":    "chips_multi",
            "options": [
                "😂 Make it funny",
                "⭐ Add social proof",
                "📊 Include stats",
                "🧍 Personal story",
                "🔥 Mild controversy",
                "💰 Mention a deal/offer",
                "📣 Strong CTA",
                "👥 Collab-friendly",
            ],
        },
        {
            "id":      "length",
            "q":       "How long? ⏱️",
            "sub":     "Target video duration.",
            "type":    "chips",
            "options": ["15 seconds","30 seconds","60 seconds","90 seconds","3 minutes"],
        },
    ]

    # ─────────────────────────────────────────────────────────────────────────
    # Page layout: sidebar | chat
    # ─────────────────────────────────────────────────────────────────────────
    st.markdown("# 💬 Script Chat")
    st.markdown('<p style="color:#6b6b8a;font-size:0.92rem">Refine, rewrite, or build any script through conversation. The AI suggests next steps after every reply.</p>', unsafe_allow_html=True)
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    sidebar_col, chat_col = st.columns([1, 3])

    # ── LEFT SIDEBAR ──────────────────────────────────────────────────────────
    with sidebar_col:
        st.markdown("### 📎 Script Context")

        has_ctx = bool(st.session_state.get("chat_script_context","").strip())

        # Auto-load from other pages
        if st.session_state.get("last_script") and not has_ctx:
            st.markdown('<div class="info-box" style="border-color:#10b981;padding:8px">✍️ Script from Generator ready</div>', unsafe_allow_html=True)
            if st.button("⬇️ Load It", use_container_width=True, key="load_gen"):
                st.session_state["chat_script_context"] = st.session_state["last_script"]
                st.session_state["chat_messages"] = []
                st.session_state["chat_suggestions"] = []
                st.rerun()

        if st.session_state.get("chat_transcript") and not has_ctx:
            meta = st.session_state.get("chat_meta", {})
            st.markdown(f'<div class="info-box" style="padding:8px">🎬 URL: <strong>{meta.get("title","Video")[:30]}</strong></div>', unsafe_allow_html=True)
            if st.button("⬇️ Load Transcript", use_container_width=True, key="load_transcript"):
                st.session_state["chat_script_context"] = st.session_state["chat_transcript"]
                st.session_state["chat_messages"] = []
                st.session_state["chat_suggestions"] = []
                st.rerun()

        # Paste area
        new_ctx = st.text_area(
            "Or paste a script",
            value=st.session_state.get("chat_script_context",""),
            height=140,
            label_visibility="collapsed",
            placeholder="Paste your script here...",
            key="chat_ctx_area",
        )
        ctx_btn_col, wiz_btn_col = st.columns(2)
        if ctx_btn_col.button("Set Context", use_container_width=True, key="set_ctx"):
            st.session_state["chat_script_context"] = new_ctx
            st.session_state["chat_messages"] = []
            st.session_state["chat_suggestions"] = []
            st.rerun()
        if wiz_btn_col.button("🪄 Wizard", use_container_width=True, key="start_wiz",
                              help="Answer 7 quick questions → get a perfect script"):
            st.session_state["chat_wizard_active"] = True
            st.session_state["chat_wizard_step"]   = 0
            st.session_state["chat_wizard_data"]   = {}
            st.session_state["chat_messages"]      = []
            st.session_state["chat_suggestions"]   = []
            st.rerun()

        if has_ctx:
            ctx_words = len(st.session_state["chat_script_context"].split())
            st.markdown(f'<div class="info-box" style="border-color:#10b981;padding:7px;text-align:center"><span style="color:#10b981;font-weight:700">✓ Context set</span><br><span style="color:#6b6b8a;font-size:0.75rem">{ctx_words} words</span></div>', unsafe_allow_html=True)

        st.markdown('<div class="divider" style="margin:12px 0"></div>', unsafe_allow_html=True)

        # Settings
        platform_chat = st.selectbox("Platform", ["TikTok","YouTube Shorts","Instagram Reels","YouTube Long-form","LinkedIn"], key="chat_platform")
        use_brand_chat = st.checkbox("🏷️ Brand context (RAG)", value=get_document_count() > 0, key="chat_brand")

        st.markdown('<div class="divider" style="margin:12px 0"></div>', unsafe_allow_html=True)

        # Categorised quick prompts
        st.markdown("**⚡ Quick Actions**")

        QUICK_CATS = {
            "🎣 Hook": [
                "Make the hook scroll-stopping",
                "Try a shocking opening instead",
                "Start with a relatable question",
                "Open mid-story, skip the setup",
            ],
            "📐 Structure": [
                "Shorten to 30 seconds",
                "Add a pattern interrupt",
                "Restructure using PAS framework",
                "Add a stronger CTA at the end",
            ],
            "🎤 Voice": [
                "Make it more conversational",
                "Increase energy and urgency",
                "Make it funnier",
                "Make it more empathetic",
            ],
            "💡 Content": [
                "Add social proof / testimonial",
                "Include a surprising stat",
                "Add a personal story angle",
                "Make it more controversial",
            ],
            "🏷️ Brand": [
                "Rewrite aligned to brand voice",
                "Weave in product naturally",
                "Make it less salesy",
                "Add brand storytelling",
            ],
        }

        for cat_label, prompts in QUICK_CATS.items():
            with st.expander(cat_label, expanded=False):
                for qp in prompts:
                    if st.button(qp, key=f"qp_{qp}", use_container_width=True):
                        st.session_state["chat_pending_msg"] = qp
                        st.rerun()

        st.markdown('<div class="divider" style="margin:12px 0"></div>', unsafe_allow_html=True)

        # Script actions
        if st.session_state.get("chat_messages"):
            last_ai = next((m["content"] for m in reversed(st.session_state["chat_messages"]) if m["role"]=="assistant"), "")
            if last_ai:
                col_dl, col_save = st.columns(2)
                col_dl.download_button("⬇️", last_ai, file_name="script.txt", mime="text/plain",
                                       use_container_width=True, key="chat_dl")
                if col_save.button("💬→Gen", use_container_width=True, key="chat_save",
                                   help="Send to Script Generator"):
                    st.session_state["last_script"] = last_ai
                    st.success("Saved!")
        if st.button("🗑️ Clear Chat", use_container_width=True, key="clear_chat"):
            st.session_state["chat_messages"]      = []
            st.session_state["chat_suggestions"]   = []
            st.session_state["chat_wizard_active"] = False
            st.rerun()

    # ── RIGHT: MAIN CHAT AREA ─────────────────────────────────────────────────
    with chat_col:

        # ════════════════════════════════════════════════════════════════════
        # WIZARD MODE
        # ════════════════════════════════════════════════════════════════════
        if st.session_state.get("chat_wizard_active"):
            step_idx  = st.session_state["chat_wizard_step"]
            wiz_data  = st.session_state["chat_wizard_data"]
            total_steps = len(WIZARD_STEPS)

            if step_idx < total_steps:
                step = WIZARD_STEPS[step_idx]

                # Progress bar
                pct = int((step_idx / total_steps) * 100)
                st.markdown(f"""
<div style="background:#1a1a2e;border-radius:999px;height:6px;margin-bottom:4px;overflow:hidden">
  <div style="background:linear-gradient(90deg,#7c3aed,#06b6d4);height:100%;width:{pct}%;border-radius:999px;transition:width 0.3s"></div>
</div>
<p style="color:#6b6b8a;font-size:0.75rem;margin:0 0 20px 0">Step {step_idx + 1} of {total_steps}</p>""",
                    unsafe_allow_html=True)

                # Question card
                st.markdown(f"""
<div style="background:#0f0f1a;border:1px solid #2a2a3e;border-top:3px solid #7c3aed;border-radius:14px;padding:24px 28px;margin-bottom:20px">
  <p style="color:#7c3aed;font-size:0.72rem;font-weight:700;text-transform:uppercase;letter-spacing:0.12em;margin:0 0 6px 0">Question {step_idx + 1}</p>
  <p style="color:#e8e8f0;font-size:1.1rem;font-weight:600;margin:0 0 6px 0">{step["q"]}</p>
  <p style="color:#6b6b8a;font-size:0.85rem;margin:0">{step["sub"]}</p>
</div>""", unsafe_allow_html=True)

                wiz_answer = None

                if step["type"] == "text":
                    wiz_input = st.text_area("Your answer", placeholder=step.get("ph",""),
                                             height=90, label_visibility="collapsed",
                                             key=f"wiz_txt_{step_idx}")
                    if st.button("Next →", key=f"wiz_next_{step_idx}", type="primary"):
                        if wiz_input.strip():
                            wiz_answer = wiz_input.strip()

                elif step["type"] == "chips":
                    st.markdown('<div style="display:flex;flex-wrap:wrap;gap:8px;margin-bottom:16px">', unsafe_allow_html=True)
                    for opt in step["options"]:
                        if st.button(opt, key=f"wiz_chip_{step_idx}_{opt}"):
                            wiz_answer = opt
                    st.markdown('</div>', unsafe_allow_html=True)

                elif step["type"] == "chips_multi":
                    chosen = st.multiselect(
                        "Select all that apply",
                        step["options"],
                        label_visibility="collapsed",
                        key=f"wiz_multi_{step_idx}",
                    )
                    if st.button("Next →", key=f"wiz_mnext_{step_idx}", type="primary"):
                        wiz_answer = chosen if chosen else ["None"]

                if wiz_answer is not None:
                    wiz_data[step["id"]] = wiz_answer
                    st.session_state["chat_wizard_data"] = wiz_data
                    st.session_state["chat_wizard_step"] = step_idx + 1
                    st.rerun()

                # Show answers collected so far
                if wiz_data:
                    st.markdown('<div class="divider" style="margin:16px 0 12px 0"></div>', unsafe_allow_html=True)
                    st.markdown('<p style="color:#6b6b8a;font-size:0.75rem;text-transform:uppercase">Your answers so far</p>', unsafe_allow_html=True)
                    for k, v in wiz_data.items():
                        val_str = ", ".join(v) if isinstance(v, list) else str(v)
                        st.markdown(f'<span class="tag" style="margin-right:4px;margin-bottom:4px"><strong>{k}:</strong> {val_str[:40]}</span>', unsafe_allow_html=True)

            else:
                # All questions answered — generate script
                wd = st.session_state["chat_wizard_data"]
                st.markdown("""
<div style="background:#0f0f1a;border:1px solid #10b98144;border-top:3px solid #10b981;border-radius:14px;padding:24px;margin-bottom:20px;text-align:center">
  <p style="font-size:2rem;margin:0 0 8px 0">🎉</p>
  <p style="color:#10b981;font-size:1rem;font-weight:700;margin:0 0 4px 0">Perfect! Generating your script…</p>
  <p style="color:#6b6b8a;font-size:0.85rem;margin:0">Based on your 7 answers</p>
</div>""", unsafe_allow_html=True)

                extras_list = wd.get("extras", [])
                extras_str  = ", ".join(extras_list) if isinstance(extras_list, list) else str(extras_list)
                platform_wiz = wd.get("platform","TikTok")
                tone_wiz     = wd.get("tone","Conversational")
                length_wiz   = wd.get("length","60 seconds")
                hook_wiz     = wd.get("hook","Relatable question")
                goal_wiz     = wd.get("goal","Go viral / entertain")
                topic_wiz    = wd.get("topic","")

                # Brand context
                brand_ctx_wiz = ""
                if use_brand_chat:
                    brand_ctx_wiz = query_brand_context(topic_wiz, top_k=4)

                wiz_system = f"""You are an elite viral script writer.

Write a complete, publish-ready {platform_wiz} script based on:
TOPIC: {topic_wiz}
GOAL: {goal_wiz}
TONE: {tone_wiz}
HOOK STYLE: {hook_wiz}
LENGTH: {length_wiz}
EXTRAS: {extras_str}
{"BRAND CONTEXT: " + brand_ctx_wiz if brand_ctx_wiz else ""}

Format:
🎣 HOOK (0-3s):
[hook]

📖 BODY:
[main content]

🎯 CTA:
[call to action]

---
📊 Pattern: [framework] + [{hook_wiz}] hook
🧠 Why: [1 sentence on the psychology]

Make it feel real, human, platform-native. Every word earns its place."""

                out_placeholder = st.empty()
                full_wiz_script = ""
                stream_wiz = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role":"system","content":wiz_system},
                               {"role":"user","content":"Generate the script now."}],
                    max_tokens=1200, temperature=0.75, stream=True,
                )
                for chunk in stream_wiz:
                    delta = chunk.choices[0].delta.content
                    if delta:
                        full_wiz_script += delta
                        out_placeholder.markdown(
                            f'<div class="script-output">{full_wiz_script}▌</div>',
                            unsafe_allow_html=True)

                out_placeholder.markdown(f'<div class="script-output">{full_wiz_script}</div>', unsafe_allow_html=True)

                # Save and transition to chat mode
                st.session_state["chat_script_context"] = full_wiz_script
                st.session_state["last_script"]         = full_wiz_script
                st.session_state["chat_messages"].append({
                    "role": "assistant",
                    "content": full_wiz_script,
                    "_is_script": True,
                })

                # Generate initial suggestions
                suggs = generate_suggestions(client, full_wiz_script, full_wiz_script, platform_wiz)
                st.session_state["chat_suggestions"] = suggs

                st.markdown("")
                wc1, wc2 = st.columns(2)
                if wc1.button("✅ Use This — Start Refining", type="primary", use_container_width=True, key="wiz_done"):
                    st.session_state["chat_wizard_active"] = False
                    st.rerun()
                if wc2.button("🔄 Redo Wizard", use_container_width=True, key="wiz_redo"):
                    st.session_state["chat_wizard_step"] = 0
                    st.session_state["chat_wizard_data"] = {}
                    st.rerun()

        # ════════════════════════════════════════════════════════════════════
        # NORMAL CHAT MODE
        # ════════════════════════════════════════════════════════════════════
        else:
            messages   = st.session_state["chat_messages"]
            script_ctx = st.session_state.get("chat_script_context","")

            # Empty state
            if not messages and not script_ctx:
                st.markdown("""
<div style="background:#0a0a14;border:1px solid #1e1e30;border-radius:16px;padding:36px;text-align:center;margin-bottom:24px">
  <p style="font-size:2.8rem;margin:0 0 10px 0">💬</p>
  <p style="color:#e8e8f0;font-size:1.05rem;font-weight:600;margin:0 0 6px 0">How do you want to work today?</p>
  <p style="color:#6b6b8a;font-size:0.88rem;margin:0 0 24px 0">Paste a script on the left, load one from another page, or let the Wizard build one from scratch.</p>
</div>""", unsafe_allow_html=True)
                # Getting-started action chips
                st.markdown("**Or start with a quick action:**")
                ga1, ga2, ga3 = st.columns(3)
                if ga1.button("🪄 Build from scratch (Wizard)", use_container_width=True, key="gs_wiz"):
                    st.session_state["chat_wizard_active"] = True
                    st.session_state["chat_wizard_step"]   = 0
                    st.session_state["chat_wizard_data"]   = {}
                    st.rerun()
                if ga2.button("📋 Analyze my script's hook", use_container_width=True, key="gs_hook"):
                    st.session_state["chat_pending_msg"] = "Analyze the hook in my script and tell me how to improve it"
                if ga3.button("✍️ Give me 3 better versions", use_container_width=True, key="gs_vers"):
                    st.session_state["chat_pending_msg"] = "Rewrite this script in 3 different styles: emotional, humorous, and direct value"

            elif not messages and script_ctx:
                # Script loaded, no messages yet
                word_count = len(script_ctx.split())
                st.markdown(f"""
<div style="background:#0f0f1a;border:1px solid #7c3aed33;border-left:3px solid #7c3aed;border-radius:12px;padding:16px 20px;margin-bottom:16px">
  <p style="color:#7c3aed;font-size:0.7rem;font-weight:700;text-transform:uppercase;margin:0 0 6px 0">✓ Script context active — {word_count} words</p>
  <p style="color:#d0d0e8;font-size:0.85rem;font-style:italic;margin:0">"{script_ctx[:200]}{"…" if len(script_ctx)>200 else ""}"</p>
</div>""", unsafe_allow_html=True)
                st.markdown("**What do you want to do with it?**")
                # Contextual opening chips
                init_chips = [
                    ("🔍 Diagnose what's weak", "Diagnose the weaknesses in this script — be specific about what to fix and why"),
                    ("🎣 Upgrade the hook",      "Rewrite just the opening hook to make it more scroll-stopping"),
                    ("📐 Restructure it",         "Suggest a better narrative framework for this script and show a rewrite"),
                    ("✂️ Make it shorter",        "Tighten this script to 30 seconds without losing impact"),
                    ("🔥 Add controversy",        "Add a mild controversial take to increase shareability"),
                    ("😂 Make it funnier",        "Rewrite with humor — keep the core message but add wit and personality"),
                ]
                for row_s in range(0, len(init_chips), 3):
                    chip_row = init_chips[row_s:row_s+3]
                    chip_cols = st.columns(3)
                    for col, (label, msg) in zip(chip_cols, chip_row):
                        if col.button(label, key=f"init_{label}", use_container_width=True):
                            st.session_state["chat_pending_msg"] = msg
                            st.rerun()

            # ── Chat message history ───────────────────────────────────────────
            for i, msg in enumerate(messages):
                role    = msg["role"]
                content = msg["content"]
                is_script_msg = msg.get("_is_script", False)

                if role == "user":
                    st.markdown(f"""
<div style="display:flex;justify-content:flex-end;margin:10px 0 4px 60px">
  <div style="background:linear-gradient(135deg,#4c1d95,#1e3a8a);border-radius:18px 18px 4px 18px;padding:12px 18px;color:#e8e8f0;font-size:0.9rem;line-height:1.55;max-width:85%">
    {content}
  </div>
</div>""", unsafe_allow_html=True)
                else:
                    st.markdown(f"""
<div style="display:flex;justify-content:flex-start;margin:10px 60px 4px 0">
  <div style="background:#0d0d1a;border:1px solid {"#7c3aed44" if is_script_msg else "#1e1e30"};border-radius:18px 18px 18px 4px;padding:14px 20px;color:#d0d0e8;font-size:0.9rem;line-height:1.65;white-space:pre-wrap;max-width:100%">
    {content}
  </div>
</div>""", unsafe_allow_html=True)

                    # ── Contextual suggestion chips (only after last AI msg) ───
                    if i == len(messages) - 1 and role == "assistant":
                        # Action row below the message
                        act_col1, act_col2, act_col3 = st.columns([1,1,4])
                        act_col1.download_button("⬇️ Save", content,
                            file_name="script.txt", mime="text/plain",
                            use_container_width=True, key=f"dl_msg_{i}")
                        if act_col2.button("📋 Copy brief", use_container_width=True, key=f"copy_{i}"):
                            st.session_state["last_script"] = content
                            st.success("Saved as last script!")

                        # Smart suggestions
                        suggestions = st.session_state.get("chat_suggestions", [])
                        if suggestions:
                            st.markdown('<p style="color:#4a4a6a;font-size:0.72rem;margin:8px 0 4px 0;text-transform:uppercase;letter-spacing:0.08em">💡 What to do next</p>', unsafe_allow_html=True)
                            # Display in rows of 3
                            for srow in range(0, len(suggestions), 3):
                                scols = st.columns(min(3, len(suggestions[srow:srow+3])))
                                for sc, suggestion in zip(scols, suggestions[srow:srow+3]):
                                    if sc.button(suggestion, key=f"sugg_{i}_{suggestion[:20]}", use_container_width=True):
                                        st.session_state["chat_pending_msg"] = suggestion
                                        st.session_state["chat_suggestions"] = []
                                        st.rerun()

            # ── Chat input ────────────────────────────────────────────────────
            st.markdown("")
            user_input = st.chat_input(
                "Ask anything — 'make the hook stronger', 'add a twist', 'rewrite in 30 seconds'…",
                key="chat_input_box",
            )

            # Consume pending message from quick actions / suggestions
            if st.session_state.get("chat_pending_msg") and not user_input:
                user_input = st.session_state.pop("chat_pending_msg")
            elif st.session_state.get("chat_pending_msg"):
                st.session_state.pop("chat_pending_msg")

            # ── Process user input ────────────────────────────────────────────
            if user_input:
                st.session_state["chat_messages"].append({"role":"user","content":user_input})
                st.session_state["chat_suggestions"] = []

                # Build brand context
                brand_ctx_chat = ""
                if use_brand_chat:
                    brand_ctx_chat = query_brand_context(user_input, top_k=4)

                # System prompt — highly specific to context
                system = f"""You are an elite script coach and viral content strategist for {platform_chat}.

You specialise in:
- Psychological hooks and scroll-stopping openers
- Emotional arcs and narrative frameworks (AIDA, PAS, BAB, Hero's Journey, Story Loop)
- Platform-native phrasing and rhythm
- Retention engineering and pacing
- Brand voice alignment

YOUR RESPONSE RULES:
1. Be surgical and specific — never vague
2. When rewriting, show the FULL rewrite (not just suggestions)
3. Explain the WHY behind every change in 1 line
4. Use clear formatting: emojis for sections, bold for key phrases
5. If the request is about the hook, ONLY change the hook (unless asked otherwise)
6. Match the platform energy: {platform_chat}"""

                if script_ctx.strip():
                    system += f"\n\nACTIVE SCRIPT (work from this unless asked to start fresh):\n\"\"\"\n{script_ctx}\n\"\"\""
                if brand_ctx_chat:
                    system += f"\n\nBRAND CONTEXT (align all output to this):\n{brand_ctx_chat}"

                # Build conversation history
                api_msgs = [{"role":"system","content":system}]
                for m in st.session_state["chat_messages"][-12:]:
                    api_msgs.append({"role": m["role"], "content": m["content"]})

                # Stream response
                resp_placeholder = st.empty()
                full_resp = ""
                stream = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=api_msgs,
                    max_tokens=2000, temperature=0.72, stream=True,
                )
                for chunk in stream:
                    delta = chunk.choices[0].delta.content
                    if delta:
                        full_resp += delta
                        resp_placeholder.markdown(f"""
<div style="display:flex;justify-content:flex-start;margin:10px 60px 4px 0">
  <div style="background:#0d0d1a;border:1px solid #7c3aed44;border-radius:18px 18px 18px 4px;padding:14px 20px;color:#d0d0e8;font-size:0.9rem;line-height:1.65;white-space:pre-wrap;max-width:100%">
    {full_resp}▌
  </div>
</div>""", unsafe_allow_html=True)

                resp_placeholder.empty()
                st.session_state["chat_messages"].append({
                    "role": "assistant",
                    "content": full_resp,
                    "_is_script": any(sig in full_resp.lower() for sig in
                                      ["🎣","📖","🎯","hook","body","cta","━━━","---"]),
                })

                # Auto-update script context if it looks like a full rewrite
                if any(sig in full_resp.lower() for sig in ["🎣","hook (0-3","📖 body","🎯 cta"]):
                    st.session_state["chat_script_context"] = full_resp
                    st.session_state["last_script"]         = full_resp

                # Generate fresh contextual suggestions asynchronously
                suggs = generate_suggestions(client, full_resp, script_ctx, platform_chat)
                st.session_state["chat_suggestions"] = suggs

                st.rerun()


# ════════════════════════════════════════════════════════════════════
# PAGE: CREATOR ANALYZER
# ════════════════════════════════════════════════════════════════════
elif current_page == "creator":
    from modules.creator_analyzer import (
        fetch_youtube_creator, fetch_tiktok_creator, fetch_instagram_creator,
        analyze_creator, compute_video_stats, transcribe_top_videos,
        extract_creator_patterns, fmt_num,
    )
    try:
        from apikeys import rapidapi_key, youtube_api_key
    except Exception:
        rapidapi_key = ""; youtube_api_key = ""

    st.markdown("# 👤 Creator Analyzer")
    st.markdown('<p style="color:#6b6b8a">Paste a username → fetch their videos → transcribe top content → extract their exact talking patterns → inject their style into Script Generator.</p>', unsafe_allow_html=True)
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # API key status bar
    k1, k2, k3 = st.columns(3)
    k1.markdown(f'<div class="info-box" style="border-color:{"#10b981" if youtube_api_key else "#374151"};text-align:center;padding:8px">{"✅" if youtube_api_key else "⚪"} YouTube API Key</div>', unsafe_allow_html=True)
    k2.markdown(f'<div class="info-box" style="border-color:{"#10b981" if rapidapi_key else "#374151"};text-align:center;padding:8px">{"✅" if rapidapi_key else "⚪"} RapidAPI Key</div>', unsafe_allow_html=True)
    k3.markdown(f'<div class="info-box" style="border-color:#10b981;text-align:center;padding:8px">✅ yt-dlp fallback ready</div>', unsafe_allow_html=True)
    st.markdown("")

    tab_tt, tab_ig, tab_yt = st.tabs(["🎵 TikTok", "📸 Instagram", "▶️ YouTube"])

    # ─────────────────────────────────────────────────────────────────────────
    # Shared render function
    # ─────────────────────────────────────────────────────────────────────────
    def render_creator(profile, analysis, stats, transcribed, patterns, color, pkey):
        videos   = profile.get("videos", [])
        username = profile.get("username", "")
        platform = profile.get("platform", "")

        # Always show debug info so user knows what happened
        debug = profile.get("debug", [])
        method = profile.get("method", "")
        if method:
            status_color = "#10b981" if videos else "#ef4444"
            st.markdown(f'<div class="info-box" style="border-color:{status_color}">📡 <strong>{method}</strong> · {len(videos)} videos fetched</div>', unsafe_allow_html=True)
        if debug:
            with st.expander("🔍 Debug info", expanded=(not videos)):
                for d in debug:
                    st.markdown(f'<span style="color:#6b6b8a;font-size:0.8rem">• {d}</span>', unsafe_allow_html=True)

        if profile.get("error") and not videos:
            st.error(f"❌ {profile['error']}")
            if pkey == "tiktok":
                st.markdown('<div class="info-box">For TikTok: add RapidAPI key to apikeys.py (rapidapi_key). Get one at rapidapi.com → search "tokapi"</div>', unsafe_allow_html=True)
            elif pkey == "instagram":
                st.markdown('<div class="info-box">For Instagram: add RapidAPI key OR run <code>pip install instaloader</code></div>', unsafe_allow_html=True)
            elif pkey == "youtube":
                st.markdown('<div class="info-box">For YouTube: add YouTube Data API key (youtube_api_key) from console.cloud.google.com — free, 10k calls/day</div>', unsafe_allow_html=True)
            return

        followers = profile.get("followers", 0) or profile.get("subscribers", 0)
        following = profile.get("following", 0)
        bio       = profile.get("bio", "")
        score     = analysis.get("overall_score", 0) if analysis else 0
        tier      = analysis.get("tier", "—") if analysis else "—"
        archetype = analysis.get("creator_archetype", "—") if analysis else "—"
        mono      = analysis.get("monetization_potential", "—") if analysis else "—"

        # ── Profile card ──────────────────────────────────────────────────────
        icon = "🎵" if platform == "TikTok" else "📸" if platform == "Instagram" else "▶️"
        st.markdown(f"""
<div style="background:linear-gradient(135deg,{color}15,#0a0a0f);border:1px solid {color}33;border-radius:16px;padding:22px;margin-bottom:18px">
  <div style="display:flex;align-items:flex-start;gap:18px;flex-wrap:wrap">
    <div style="background:{color}22;border:2px solid {color}55;border-radius:50%;width:60px;height:60px;display:flex;align-items:center;justify-content:center;font-size:1.7rem;flex-shrink:0">{icon}</div>
    <div style="flex:1;min-width:200px">
      <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-bottom:6px">
        <span style="color:#e8e8f0;font-family:Syne;font-weight:700;font-size:1.15rem">@{username}</span>
        <span style="color:{color};font-size:0.9rem">{profile.get("display_name","")}</span>
        <span class="tag" style="border-color:{color}44;color:{color}">{tier}</span>
        <span class="tag">{archetype}</span>
      </div>
      <p style="color:#9090b0;font-size:0.84rem;margin:0 0 10px 0;line-height:1.5">{bio[:200] if bio else "No bio available"}</p>
      <div style="display:flex;gap:18px;flex-wrap:wrap">
        <span><strong style="color:{color};font-size:1.05rem">{fmt_num(followers) if followers else "—"}</strong><span style="color:#6b6b8a;font-size:0.78rem;margin-left:4px">followers</span></span>
        {"<span><strong style='color:#d0d0e8;font-size:1.05rem'>" + fmt_num(following) + "</strong><span style='color:#6b6b8a;font-size:0.78rem;margin-left:4px'>following</span></span>" if following else ""}
        <span><strong style="color:#d0d0e8;font-size:1.05rem">{len(videos)}</strong><span style="color:#6b6b8a;font-size:0.78rem;margin-left:4px">videos fetched</span></span>
      </div>
    </div>
    <div style="text-align:right;flex-shrink:0">
      <div style="font-size:2rem;font-family:Syne;font-weight:700;color:{color}">{score}</div>
      <div style="color:#6b6b8a;font-size:0.7rem;margin-bottom:6px">Creator Score</div>
      <span class="tag" style="color:{'#10b981' if mono in ['High','Very High'] else '#f59e0b'}">💰 {mono}</span>
    </div>
  </div>
</div>""", unsafe_allow_html=True)

        if analysis and analysis.get("summary"):
            st.markdown(f'<div class="section-card"><p style="color:#6b6b8a;font-size:0.7rem;text-transform:uppercase;letter-spacing:0.1em">Executive Summary</p><p style="color:#d0d0e8;font-size:0.9rem;line-height:1.6;margin:0">{analysis["summary"]}</p></div>', unsafe_allow_html=True)

        # Stats bar
        if stats:
            c1,c2,c3,c4,c5 = st.columns(5)
            c1.markdown(f'<div class="score-card"><div class="score-number" style="font-size:1.2rem">{fmt_num(stats.get("avg_views",0))}</div><div class="score-label">Avg Views</div></div>', unsafe_allow_html=True)
            c2.markdown(f'<div class="score-card"><div class="score-number" style="font-size:1.2rem">{fmt_num(stats.get("avg_likes",0))}</div><div class="score-label">Avg Likes</div></div>', unsafe_allow_html=True)
            c3.markdown(f'<div class="score-card"><div class="score-number" style="font-size:1.2rem">{stats.get("engagement_rate",0):.1f}%</div><div class="score-label">Eng Rate</div></div>', unsafe_allow_html=True)
            c4.markdown(f'<div class="score-card"><div class="score-number" style="font-size:1.2rem">{fmt_num(stats.get("total_views",0))}</div><div class="score-label">Total Views</div></div>', unsafe_allow_html=True)
            c5.markdown(f'<div class="score-card"><div class="score-number" style="font-size:1.2rem">{stats.get("avg_duration",0)}s</div><div class="score-label">Avg Duration</div></div>', unsafe_allow_html=True)
            st.markdown("")

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

        # ── Tabs ──────────────────────────────────────────────────────────────
        tv, tp, ts, ti = st.tabs(["📋 Videos", "🎤 Talking Patterns", "🧠 Strategy", "💡 Video Ideas"])

        # ── VIDEOS TAB ────────────────────────────────────────────────────────
        with tv:
            if not videos:
                st.info("No videos to display.")
            else:
                # Bar chart of views
                chart_data = [(v.get("title","")[:28] or f"#{i+1}", v.get("views",0))
                              for i,v in enumerate(videos[:15]) if v.get("views",0) > 0]
                if len(chart_data) >= 3:
                    fig_bar = go.Figure(go.Bar(
                        x=[d[0] for d in chart_data],
                        y=[d[1] for d in chart_data],
                        marker=dict(
                            color=[d[1] for d in chart_data],
                            colorscale=[[0,"#1a1a2e"],[1,color]],
                            showscale=False
                        ),
                        hovertemplate="<b>%{x}</b><br>%{y:,} views<extra></extra>"
                    ))
                    fig_bar.update_layout(
                        paper_bgcolor="#0a0a0f", plot_bgcolor="#12121f",
                        font=dict(color="#6b6b8a", size=9), height=180,
                        xaxis=dict(tickangle=-40, gridcolor="#1a1a2e"),
                        yaxis=dict(gridcolor="#1a1a2e"),
                        margin=dict(l=0,r=0,t=6,b=60)
                    )
                    st.plotly_chart(fig_bar, use_container_width=True)
                elif not chart_data:
                    st.markdown('<div class="info-box" style="border-color:#374151">Views data not available for this platform/method — video titles still shown below.</div>', unsafe_allow_html=True)

                # Full list
                st.markdown(f"**{len(videos)} videos**")
                for i, v in enumerate(videos):
                    title    = (v.get("title") or "[No caption]")[:100]
                    url      = v.get("url","")
                    views    = v.get("views",0)
                    likes    = v.get("likes",0)
                    comments = v.get("comments",0)
                    dur      = v.get("duration",0)
                    date     = str(v.get("upload_date",""))[:10]
                    vtype    = v.get("type","")

                    meta_parts = []
                    if views:    meta_parts.append(f"👁️ {views:,}")
                    if likes:    meta_parts.append(f"❤️ {likes:,}")
                    if comments: meta_parts.append(f"💬 {comments:,}")
                    if dur:      meta_parts.append(f"⏱️ {dur}s")
                    if date:     meta_parts.append(f"📅 {date}")
                    meta_str = " · ".join(meta_parts) if meta_parts else "No stats (limited API access)"

                    link = f'<a href="{url}" target="_blank" style="color:{color};font-size:0.75rem;text-decoration:none;flex-shrink:0">↗</a>' if url else ""
                    type_badge = f'<span class="tag" style="font-size:0.68rem;flex-shrink:0">{vtype}</span>' if vtype else ""

                    st.markdown(f"""
<div style="display:flex;align-items:flex-start;gap:10px;padding:9px 0;border-bottom:1px solid #14141f">
  <span style="color:{color};font-family:Syne;font-size:0.75rem;min-width:22px;padding-top:3px;flex-shrink:0">#{i+1}</span>
  <div style="flex:1;min-width:0">
    <div style="display:flex;align-items:center;gap:6px;flex-wrap:wrap">
      <p style="color:#d0d0e8;font-size:0.87rem;margin:0;flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{title}</p>
      {type_badge}{link}
    </div>
    <p style="color:#6b6b8a;font-size:0.74rem;margin:2px 0 0 0">{meta_str}</p>
  </div>
</div>""", unsafe_allow_html=True)

        # ── PATTERNS TAB ─────────────────────────────────────────────────────
        with tp:
            if not patterns:
                st.markdown(f"""
<div class="section-card" style="text-align:center;padding:36px">
  <p style="font-size:2rem;margin:0 0 10px 0">🎤</p>
  <p style="color:#6b6b8a;margin:0">Use the <strong style="color:{color}">+ Extract Patterns</strong> button to transcribe this creator's top 3 videos and extract their exact talking style.</p>
  <p style="color:#4a4a6a;font-size:0.8rem;margin-top:8px">Takes ~2 min · Requires yt-dlp and the video to be downloadable</p>
</div>""", unsafe_allow_html=True)
            elif patterns.get("error"):
                st.warning(f"Pattern extraction failed: {patterns['error']}")
            else:
                # Style fingerprint
                if patterns.get("style_summary"):
                    st.markdown(f'<div class="section-card"><p style="color:{color};font-size:0.7rem;text-transform:uppercase;font-weight:700;letter-spacing:0.1em">🎤 Style Fingerprint of @{username}</p><p style="color:#d0d0e8;font-size:0.95rem;line-height:1.6;margin:0">{patterns["style_summary"]}</p></div>', unsafe_allow_html=True)

                # Voice characteristics row
                chars = [
                    ("Addresses as",     patterns.get("audience_address","—")),
                    ("Energy",           patterns.get("energy_level","—")),
                    ("Speaking pace",    patterns.get("speaking_pace","—")),
                    ("Sentence length",  patterns.get("sentence_length","—")),
                    ("Vocabulary",       patterns.get("vocabulary_style","—")),
                    ("Format",           patterns.get("content_format","—")),
                    ("Humor",            patterns.get("humor_style","—")),
                ]
                cc1,cc2,cc3 = st.columns(3)
                cols = [cc1,cc2,cc3]
                for i,(lbl,val) in enumerate(chars):
                    cols[i%3].markdown(f'<div class="section-card" style="padding:9px 12px;margin-bottom:8px"><span style="color:#6b6b8a;font-size:0.67rem;text-transform:uppercase">{lbl}</span><br><span style="color:{color};font-weight:600;font-size:0.88rem">{val}</span></div>', unsafe_allow_html=True)

                st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

                # Pattern columns
                pc1, pc2 = st.columns(2)
                left_patterns = [
                    ("🎣 Hook Formulas",     patterns.get("hook_formulas",[])),
                    ("🎬 Opening Patterns",  patterns.get("opening_patterns",[])),
                    ("🔀 Transitions",       patterns.get("transition_phrases",[])),
                    ("✍️ Signature Phrases", patterns.get("signature_phrases",[])),
                ]
                right_patterns = [
                    ("🔚 Closing / CTA",     patterns.get("closing_patterns",[])),
                    ("😂 Humor",             [patterns.get("humor_style","")]),
                    ("💥 Emotional Triggers",patterns.get("emotional_triggers",[])),
                    ("📖 Story Structure",   [patterns.get("storytelling_structure","")]),
                    ("⏱️ Pacing Technique",  [patterns.get("pacing_technique","")]),
                ]
                for lbl, items in left_patterns:
                    if items and any(str(x).strip() for x in items):
                        pc1.markdown(f"**{lbl}**")
                        for item in items:
                            if str(item).strip():
                                pc1.markdown(f'<div class="strength-item"><span style="color:{color}">◆</span> {item}</div>', unsafe_allow_html=True)
                        pc1.markdown("")
                for lbl, items in right_patterns:
                    if items and any(str(x).strip() for x in items):
                        pc2.markdown(f"**{lbl}**")
                        for item in items:
                            if str(item).strip():
                                pc2.markdown(f'<div class="strength-item"><span style="color:{color}">◆</span> {item}</div>', unsafe_allow_html=True)
                        pc2.markdown("")

                # Inject to script generator
                inject = patterns.get("script_injection_prompt","")
                if inject:
                    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
                    st.markdown("**🤖 Script Style Injection**")
                    st.markdown(f'<div class="section-card"><p style="color:#6b6b8a;font-size:0.7rem;text-transform:uppercase;margin-bottom:6px">Use this in Script Generator to write like @{username}</p><p style="color:#d0d0e8;font-size:0.88rem;line-height:1.7;font-style:italic;margin:0">{inject}</p></div>', unsafe_allow_html=True)

                    if st.button(f"💉 Inject @{username} Style → Script Generator", key=f"inject_btn_{pkey}"):
                        st.session_state["creator_style_prompt"] = inject
                        st.session_state["creator_style_name"]   = f"@{username} ({platform})"
                        st.markdown(f'<div class="info-box" style="border-color:#10b981">✅ Style injected! Go to ✍️ Script Generator — their style will be applied automatically.</div>', unsafe_allow_html=True)

                # Show transcripts
                if transcribed:
                    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
                    st.markdown(f"**📜 Transcribed Videos ({len(transcribed)})**")
                    for i, tv_item in enumerate(transcribed):
                        t = tv_item.get("transcript","").strip()
                        label = f"Video {i+1}: {tv_item.get('title','')[:55]} · {fmt_num(tv_item.get('views',0))} views"
                        with st.expander(label, expanded=False):
                            if t and not t.startswith("[Transcription failed"):
                                st.markdown(f'<div class="script-output" style="font-size:0.84rem;max-height:300px;overflow-y:auto">{t}</div>', unsafe_allow_html=True)
                            else:
                                st.markdown(f'<span style="color:#ef4444">{t or "No transcript"}</span>', unsafe_allow_html=True)

        # ── STRATEGY TAB ─────────────────────────────────────────────────────
        with ts:
            if not analysis or analysis.get("error"):
                st.info("No analysis available.")
            else:
                if analysis.get("viral_formula"):
                    st.markdown(f'<div class="info-box">🔥 <strong>Viral Formula:</strong> {analysis["viral_formula"]}</div>', unsafe_allow_html=True)

                sl, sr = st.columns(2)
                with sl:
                    if analysis.get("content_pillars"):
                        st.markdown("**🏛️ Content Pillars**")
                        for p in analysis["content_pillars"]:
                            st.markdown(f'<div class="strength-item"><span style="color:{color}">◆</span> {p}</div>', unsafe_allow_html=True)
                        st.markdown("")
                    st.markdown("**✅ Strengths**")
                    for s in analysis.get("strengths",[]):
                        st.markdown(f'<div class="strength-item"><span style="color:#10b981">▲</span> {s}</div>', unsafe_allow_html=True)
                    st.markdown("")
                    st.markdown("**🚀 Growth Opportunities**")
                    for o in analysis.get("growth_opportunities",[]):
                        st.markdown(f'<div class="strength-item"><span style="color:#06b6d4">→</span> {o}</div>', unsafe_allow_html=True)
                with sr:
                    st.markdown("**❌ Weaknesses**")
                    for w in analysis.get("weaknesses",[]):
                        st.markdown(f'<div class="strength-item"><span style="color:#ef4444">▼</span> {w}</div>', unsafe_allow_html=True)
                    st.markdown("")
                    st.markdown("**🕳️ Content Gaps**")
                    for g in analysis.get("content_gaps",[]):
                        st.markdown(f'<div class="strength-item"><span style="color:#f59e0b">!</span> {g}</div>', unsafe_allow_html=True)
                    st.markdown("")
                    for lbl,val in [("👥 Audience",     analysis.get("audience_profile","—")),
                                    ("🎤 Tone",         analysis.get("tone","—")),
                                    ("🤝 Collab Fit",   analysis.get("collaboration_fit","—")),
                                    ("🎣 Hook Patterns",analysis.get("hook_patterns","—"))]:
                        st.markdown(f'<div class="section-card" style="padding:9px 12px;margin-bottom:7px"><span style="color:#6b6b8a;font-size:0.68rem;text-transform:uppercase">{lbl}</span><br><span style="color:#d0d0e8;font-size:0.84rem">{val}</span></div>', unsafe_allow_html=True)

                # Top videos by engagement
                top = stats.get("top_videos",[]) if stats else []
                if top:
                    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
                    st.markdown("**🏆 Top 5 Videos by Views**")
                    for i,v in enumerate(top):
                        url_link = f'<a href="{v["url"]}" target="_blank" style="color:{color};font-size:0.75rem">↗</a>' if v.get("url") else ""
                        st.markdown(f"""
<div class="section-card" style="padding:10px 14px;margin-bottom:7px">
  <div style="display:flex;align-items:center;gap:8px">
    <span style="color:{color};font-family:Syne;font-weight:700;font-size:0.9rem;min-width:20px">#{i+1}</span>
    <div style="flex:1">
      <p style="color:#d0d0e8;font-size:0.86rem;margin:0 0 3px 0">{(v.get("title") or "[No title]")[:85]} {url_link}</p>
      <p style="color:#6b6b8a;font-size:0.75rem;margin:0">👁️{fmt_num(v.get("views",0))} · ❤️{fmt_num(v.get("likes",0))} · 💬{v.get("comments",0)}</p>
    </div>
  </div>
</div>""", unsafe_allow_html=True)

        # ── IDEAS TAB ─────────────────────────────────────────────────────────
        with ti:
            if not analysis or not analysis.get("next_3_video_ideas"):
                st.info("No ideas generated.")
            else:
                st.markdown(f"### 💡 3 Video Ideas for @{username}")
                idea_colors = [color, "#06b6d4", "#10b981"]
                for i, idea in enumerate(analysis["next_3_video_ideas"]):
                    c = idea_colors[i % 3]
                    st.markdown(f"""
<div style="background:#0d0d1a;border:1px solid #1e1e30;border-left:4px solid {c};border-radius:12px;padding:18px;margin-bottom:12px">
  <div style="display:flex;align-items:center;gap:8px;margin-bottom:10px">
    <span style="background:{c}22;border:1px solid {c}44;border-radius:50%;width:26px;height:26px;display:flex;align-items:center;justify-content:center;color:{c};font-weight:700;font-size:0.82rem;flex-shrink:0">{i+1}</span>
    <strong style="color:#e8e8f0;font-size:0.92rem">{idea.get("title","")}</strong>
  </div>
  <div style="background:{c}0f;border-left:2px solid {c}55;border-radius:0 6px 6px 0;padding:8px 12px;margin-bottom:8px">
    <span style="color:#6b6b8a;font-size:0.67rem;text-transform:uppercase">Hook</span>
    <p style="color:{c};font-size:0.86rem;margin:2px 0 0 0;font-style:italic">"{idea.get("hook","")}"</p>
  </div>
  <p style="color:#9090b0;font-size:0.84rem;margin:0;line-height:1.5">{idea.get("why","")}</p>
</div>""", unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────────────────────────
    # TikTok tab
    # ─────────────────────────────────────────────────────────────────────────
    with tab_tt:
        st.markdown("### 🎵 TikTok Creator")
        if not rapidapi_key:
            st.markdown('<div class="info-box" style="border-color:#f59e0b">⚠️ No RapidAPI key — will use yt-dlp fallback (limited stats). For full data add <code>rapidapi_key</code> to apikeys.py</div>', unsafe_allow_html=True)

        ci1, ci2, ci3 = st.columns([3,1,1])
        with ci1:
            tt_user = st.text_input("TikTok username", placeholder="e.g. charlidamelio",
                                    label_visibility="collapsed", key="tt_username_input")
        with ci2:
            tt_fetch = st.button("⚡ Fetch", key="tt_fetch_btn", use_container_width=True)
        with ci3:
            tt_pat   = st.button("🎤 + Patterns", key="tt_pat_btn", use_container_width=True,
                                 help="Also transcribes top 3 videos (~2 min)")

        if (tt_fetch or tt_pat) and tt_user.strip():
            prog = st.progress(0); stat_box = st.empty()
            stat_box.markdown('<div class="info-box">📡 Fetching TikTok profile & videos...</div>', unsafe_allow_html=True)
            prog.progress(15)
            profile = fetch_tiktok_creator(tt_user.strip(), rapidapi_key, max_videos=20)
            prog.progress(40)
            stats = compute_video_stats(profile.get("videos",[]))
            stat_box.markdown('<div class="info-box">🧠 Running AI strategy analysis...</div>', unsafe_allow_html=True)
            prog.progress(60)
            analysis = analyze_creator(client, profile)
            transcribed, patterns = [], {}
            if tt_pat and profile.get("videos"):
                stat_box.markdown('<div class="info-box">🎤 Transcribing top 3 videos (~2 min)...</div>', unsafe_allow_html=True)
                prog.progress(75)
                transcribed = transcribe_top_videos(client, profile["videos"], n=3)
                stat_box.markdown('<div class="info-box">🔍 Extracting talking patterns...</div>', unsafe_allow_html=True)
                prog.progress(90)
                patterns = extract_creator_patterns(client, transcribed, profile)
            prog.progress(100); stat_box.empty()
            render_creator(profile, analysis, stats, transcribed, patterns, "#1d9bf0", "tiktok")
        elif tt_fetch or tt_pat:
            st.warning("Enter a username first.")

    # ─────────────────────────────────────────────────────────────────────────
    # Instagram tab
    # ─────────────────────────────────────────────────────────────────────────
    with tab_ig:
        st.markdown("### 📸 Instagram Creator")
        if not rapidapi_key:
            st.markdown('<div class="info-box" style="border-color:#f59e0b">⚠️ No RapidAPI key — trying instaloader. Public accounts only. Add key for full access.</div>', unsafe_allow_html=True)

        ii1, ii2, ii3 = st.columns([3,1,1])
        with ii1:
            ig_user = st.text_input("Instagram username", placeholder="e.g. natgeo",
                                    label_visibility="collapsed", key="ig_username_input")
        with ii2:
            ig_fetch = st.button("⚡ Fetch", key="ig_fetch_btn", use_container_width=True)
        with ii3:
            ig_pat   = st.button("🎤 + Patterns", key="ig_pat_btn", use_container_width=True)

        if (ig_fetch or ig_pat) and ig_user.strip():
            prog = st.progress(0); stat_box = st.empty()
            stat_box.markdown('<div class="info-box">📡 Fetching Instagram profile & posts...</div>', unsafe_allow_html=True)
            prog.progress(15)
            profile = fetch_instagram_creator(ig_user.strip(), rapidapi_key, max_videos=20)
            prog.progress(40)
            stats = compute_video_stats(profile.get("videos",[]))
            stat_box.markdown('<div class="info-box">🧠 Running AI strategy analysis...</div>', unsafe_allow_html=True)
            prog.progress(60)
            analysis = analyze_creator(client, profile)
            transcribed, patterns = [], {}
            if ig_pat and profile.get("videos"):
                stat_box.markdown('<div class="info-box">🎤 Transcribing top 3 reels...</div>', unsafe_allow_html=True)
                prog.progress(75)
                transcribed = transcribe_top_videos(client, profile["videos"], n=3)
                stat_box.markdown('<div class="info-box">🔍 Extracting talking patterns...</div>', unsafe_allow_html=True)
                prog.progress(90)
                patterns = extract_creator_patterns(client, transcribed, profile)
            prog.progress(100); stat_box.empty()
            render_creator(profile, analysis, stats, transcribed, patterns, "#e1306c", "instagram")
        elif ig_fetch or ig_pat:
            st.warning("Enter a username first.")

    # ─────────────────────────────────────────────────────────────────────────
    # YouTube tab
    # ─────────────────────────────────────────────────────────────────────────
    with tab_yt:
        st.markdown("### ▶️ YouTube Creator")
        if youtube_api_key:
            st.markdown('<div class="info-box" style="border-color:#10b981">✅ YouTube Data API v3 active — full stats, subscriber count, all video metadata.</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="info-box" style="border-color:#f59e0b">⚠️ No YouTube API key — using yt-dlp (limited: no subs count). Free key at <strong>console.cloud.google.com</strong> → APIs → YouTube Data API v3 → Create credentials → API key</div>', unsafe_allow_html=True)

        yi1, yi2, yi3 = st.columns([3,1,1])
        with yi1:
            yt_user = st.text_input("YouTube handle", placeholder="e.g. @MrBeast",
                                    label_visibility="collapsed", key="yt_username_input")
        with yi2:
            yt_fetch = st.button("⚡ Fetch", key="yt_fetch_btn", use_container_width=True)
        with yi3:
            yt_pat   = st.button("🎤 + Patterns", key="yt_pat_btn", use_container_width=True)

        if (yt_fetch or yt_pat) and yt_user.strip():
            prog = st.progress(0); stat_box = st.empty()
            stat_box.markdown('<div class="info-box">📡 Fetching YouTube channel & videos...</div>', unsafe_allow_html=True)
            prog.progress(15)
            profile = fetch_youtube_creator(yt_user.strip(), youtube_api_key, max_videos=20)
            prog.progress(40)
            stats = compute_video_stats(profile.get("videos",[]))
            stat_box.markdown('<div class="info-box">🧠 Running AI strategy analysis...</div>', unsafe_allow_html=True)
            prog.progress(60)
            analysis = analyze_creator(client, profile)
            transcribed, patterns = [], {}
            if yt_pat and profile.get("videos"):
                stat_box.markdown('<div class="info-box">🎤 Transcribing top 3 videos (~2 min)...</div>', unsafe_allow_html=True)
                prog.progress(75)
                transcribed = transcribe_top_videos(client, profile["videos"], n=3)
                stat_box.markdown('<div class="info-box">🔍 Extracting talking patterns...</div>', unsafe_allow_html=True)
                prog.progress(90)
                patterns = extract_creator_patterns(client, transcribed, profile)
            prog.progress(100); stat_box.empty()
            render_creator(profile, analysis, stats, transcribed, patterns, "#ff0000", "youtube")
        elif yt_fetch or yt_pat:
            st.warning("Enter a channel handle first.")

# ════════════════════════════════════════════════════════════════════
# PAGE: RESEARCH AGENT
# ════════════════════════════════════════════════════════════════════
elif current_page == "research":
    import requests as _req_mod
    from modules.research_agent import run_full_pipeline
    from modules.brand_rag import query_brand_context, get_document_count

    try:
        from apikeys import rapidapi_key as _ra_key, youtube_api_key as _yt_api_key
    except Exception:
        _ra_key = ""; _yt_api_key = ""

    _has_yt  = bool(_yt_api_key and _yt_api_key not in ("","YOUR_YOUTUBE_KEY"))
    _has_rap = bool(_ra_key and _ra_key not in ("","YOUR_RAPIDAPI_KEY"))

    # Session state
    for _k, _v in {
        "ra_results":None, "ra_running":False, "ra_niche":"",
        "ra_active_agent":0, "ra_log":[],
    }.items():
        if _k not in st.session_state: st.session_state[_k] = _v

    # ── Header ────────────────────────────────────────────────────────────────
    st.markdown("# 🤖 Research Agent Pipeline")
    st.markdown(
        '<p style="color:#6b6b8a;font-size:0.95rem">'
        '6 AI agents: Niche Research → Keyword Expansion → Trend Detection → '
        'Viral Hooks → Script Generation → Content Calendar.</p>',
        unsafe_allow_html=True,
    )

    # ── Engine status ─────────────────────────────────────────────────────────
    _eng = []
    _eng.append('<span style="color:#10b981;font-weight:700">⚡ Groq AI (primary engine — always active)</span>')
    _eng.append(f'<span style="color:{"#ff0000" if _has_yt else "#4a4a6a"}">{"✓" if _has_yt else "○"} YouTube API {"(live video data)" if _has_yt else "(add key for live data)"}</span>')
    _eng.append(f'<span style="color:{"#7c3aed" if _has_rap else "#4a4a6a"}">{"✓" if _has_rap else "○"} RapidAPI {"(live web/Reddit)" if _has_rap else "(add key for live web data)"}</span>')
    _eng.append('<span style="color:#ff4500">✓ Reddit public API (always active)</span>')
    st.markdown(
        '<div style="background:#0a0a14;border:1px solid #1e1e30;border-radius:8px;'
        'padding:10px 16px;margin-bottom:16px;display:flex;flex-wrap:wrap;gap:16px;font-size:0.8rem">'
        + " &nbsp;·&nbsp; ".join(_eng) + '</div>',
        unsafe_allow_html=True,
    )
    if not _has_yt and not _has_rap:
        st.info("💡 Running on **Groq AI + Reddit** — add YouTube/RapidAPI keys in `apikeys.py` to enrich with live web data. Results are still fully functional.")

    # ── Agent strip ───────────────────────────────────────────────────────────
    _AMETA = [("1","Niche Research","#7c3aed"),("2","Keywords","#06b6d4"),
              ("3","Trends","#f59e0b"),("4","Hooks","#ec4899"),
              ("5","Scripts","#10b981"),("6","Calendar","#ef4444")]
    _active_a = st.session_state.get("ra_active_agent",0)
    _acols    = st.columns(6)
    for _ac, (_n, _name, _clr) in zip(_acols, _AMETA):
        _ni = int(_n)
        _isa = (_ni == _active_a); _isd = (_ni < _active_a)
        _bg  = f"{_clr}22" if (_isa or _isd) else "#0a0a14"
        _brd = f"2px solid {_clr}" if _isa else f"1px solid {'#2a2a3a' if not _isd else _clr+'44'}"
        _ico = "⚡" if _isa else ("✓" if _isd else _n)
        _ac.markdown(
            f'<div style="background:{_bg};border:{_brd};border-radius:10px;padding:9px 6px;text-align:center">'
            f'<div style="color:{_clr};font-size:1.1rem;font-weight:800">{_ico}</div>'
            f'<div style="color:{"#e8e8f0" if _isa else "#6b6b8a"};font-size:0.65rem;font-weight:600">{_name}</div>'
            f'</div>', unsafe_allow_html=True)
    st.markdown("")

    # ══════════════════════════════════════════════════════════════════════════
    # CONFIG PANEL
    # ══════════════════════════════════════════════════════════════════════════
    if not st.session_state["ra_running"] and not st.session_state["ra_results"]:
        st.markdown("### ⚙️ Configure Pipeline")
        _cl, _cr = st.columns([3,2])
        with _cl:
            _niche_inp = st.text_input(
                "Client Niche / Industry",
                placeholder="e.g. car dealership, vegan skincare, fitness coaching, real estate...",
                key="ra_niche_inp",
            )
            _platforms_inp = st.multiselect(
                "Target Platforms",
                ["TikTok","YouTube Shorts","Instagram Reels","YouTube Long","LinkedIn"],
                default=["TikTok","YouTube Shorts","Instagram Reels"],
                key="ra_plat_inp",
            )
            _cw1, _cw2 = st.columns(2)
            _weeks_inp = _cw1.slider("Calendar weeks", 1, 8, 4, key="ra_wk")
            _ppw_inp   = _cw2.slider("Posts / week",   3, 14, 5, key="ra_ppw")
        with _cr:
            _doc_cnt = get_document_count()
            st.markdown("**🏷️ Brand Context**")
            if _doc_cnt > 0:
                st.markdown(f'<div class="info-box" style="border-color:#10b981">✓ Brand RAG active ({_doc_cnt} docs)<br><span style="color:#6b6b8a;font-size:0.78rem">Scripts will be brand-aligned</span></div>', unsafe_allow_html=True)
                _brand_cb = st.checkbox("Inject into scripts", value=True, key="ra_brand_cb")
            else:
                st.markdown('<div class="warn-box">No brand docs<br><span style="color:#9090b0;font-size:0.78rem">Upload in 🎯 Brand Setup</span></div>', unsafe_allow_html=True)
                _brand_cb = False

            st.markdown("""<div style="background:#0a0a14;border:1px solid #1e1e30;border-radius:8px;padding:12px;font-size:0.78rem;color:#6b6b8a;line-height:1.8;margin-top:8px">
<strong style="color:#e8e8f0">What runs:</strong><br>
1️⃣ Groq generates niche intelligence<br>
2️⃣ Expands 300–500 long-tail keywords<br>
3️⃣ Scores keyword trend velocity<br>
4️⃣ Extracts viral hook patterns<br>
5️⃣ Writes platform-specific scripts<br>
6️⃣ Builds weekly content calendar<br><br>
⏱️ <strong style="color:#e8e8f0">~3–6 minutes</strong>
</div>""", unsafe_allow_html=True)

        st.markdown("")
        _run_btn = st.button(
            "🚀 Run Full Pipeline", type="primary",
            use_container_width=True, key="ra_run",
            disabled=not bool(_niche_inp.strip() if "_niche_inp" in dir() else False),
        )
        if _run_btn and _niche_inp.strip():
            st.session_state.update({
                "ra_niche":        _niche_inp.strip(),
                "ra_running":      True,
                "ra_results":      None,
                "ra_active_agent": 1,
                "ra_log":          [],
                "_ra_plats":       _platforms_inp,
                "_ra_weeks":       _weeks_inp,
                "_ra_ppw":         _ppw_inp,
                "_ra_brand":       _brand_cb,
            })
            st.rerun()

    # ══════════════════════════════════════════════════════════════════════════
    # RUNNING STATE
    # ══════════════════════════════════════════════════════════════════════════
    elif st.session_state["ra_running"]:
        _niche     = st.session_state["ra_niche"]
        _plats     = st.session_state.get("_ra_plats",["TikTok","YouTube Shorts"])
        _wks       = st.session_state.get("_ra_weeks",4)
        _ppw       = st.session_state.get("_ra_ppw",5)
        _use_brand = st.session_state.get("_ra_brand",False)

        _brand_ctx = ""
        if _use_brand and get_document_count() > 0:
            _brand_ctx = query_brand_context(f"{_niche} content strategy audience", top_k=6)

        st.markdown(f"### 🤖 Running pipeline for: **{_niche}**")
        st.markdown(
            '<div class="info-box">⏳ <strong>Running — do not navigate away.</strong> '
            'Groq is generating your full research package. Takes 3–6 minutes.</div>',
            unsafe_allow_html=True,
        )

        _ACOLORS = {1:"#7c3aed",2:"#06b6d4",3:"#f59e0b",4:"#ec4899",5:"#10b981",6:"#ef4444"}
        _ALABELS = {1:"🔍 Niche Research",2:"🔑 Keyword Expansion",3:"📈 Trend Detection",
                    4:"🎣 Viral Hooks",5:"✍️ Scripts",6:"📅 Calendar"}

        _pbar    = st.progress(0)
        _statbox = st.empty()
        _logbox  = st.empty()
        _log     = []

        def _apcb(agent_num, pct, msg):
            st.session_state["ra_active_agent"] = agent_num
            _log.append(f"[A{agent_num}] {msg}")
            if len(_log) > 10: _log.pop(0)

            overall = min(99, int(((agent_num-1)*100 + pct) / 600 * 100))
            _pbar.progress(overall, text=f"Agent {agent_num}/6 · {pct}% · {msg[:55]}...")

            _clr = _ACOLORS.get(agent_num,"#7c3aed")
            _lbl = _ALABELS.get(agent_num,"")
            _statbox.markdown(
                f'<div style="background:#0a0a14;border:1px solid {_clr}44;border-left:4px solid {_clr};'
                f'border-radius:8px;padding:10px 14px">'
                f'<span style="color:{_clr};font-weight:700">Agent {agent_num}: {_lbl}</span><br>'
                f'<span style="color:#9090b0;font-size:0.85rem">{msg}</span></div>',
                unsafe_allow_html=True,
            )
            _rows = "".join(
                f'<div style="color:{"#7c3aed" if j==len(_log)-1 else "#3a3a5a"};font-size:0.75rem;padding:1px 0">'
                f'{"▶ " if j==len(_log)-1 else "  "}{l}</div>'
                for j,l in enumerate(_log)
            )
            _logbox.markdown(
                f'<div style="background:#060610;border:1px solid #181828;border-radius:6px;padding:8px 12px">{_rows}</div>',
                unsafe_allow_html=True,
            )

        try:
            _results = run_full_pipeline(
                client, _niche, _plats, _wks, _ppw,
                _yt_api_key, _ra_key, _brand_ctx, _apcb,
            )
            _pbar.progress(100, text="✅ Pipeline complete!")
            st.session_state["ra_results"]      = _results
            st.session_state["ra_running"]      = False
            st.session_state["ra_active_agent"] = 0
            time.sleep(0.5)
            st.rerun()
        except Exception as _err:
            import traceback
            st.error(f"Pipeline error: {_err}")
            st.code(traceback.format_exc())
            st.session_state["ra_running"]      = False
            st.session_state["ra_active_agent"] = 0

    # ══════════════════════════════════════════════════════════════════════════
    # RESULTS STATE
    # ══════════════════════════════════════════════════════════════════════════
    elif st.session_state["ra_results"]:
        _R          = st.session_state["ra_results"]
        _niche      = _R.get("niche", st.session_state.get("ra_niche",""))
        _clusters   = _R.get("clusters",[])
        _kwg        = _R.get("keyword_groups",{})
        _trends     = _R.get("trends",[])
        _hooks      = _R.get("hook_data",{})
        _scripts    = _R.get("scripts_data",[])
        _cal        = _R.get("calendar",[])
        _enrich     = _R.get("enrichment",{})
        _total_kws  = sum(g.get("total",0) for g in _kwg.values())
        _emerging   = sum(1 for t in _trends if t.get("status") in ("EMERGING","GROWING"))
        _cal_posts  = sum(len(w.get("posts",[])) for w in _cal)

        # Summary strip
        st.markdown(f"### ✅ Research results for: **{_niche}**")
        _sc = st.columns(4)
        for _col, (_lbl,_val,_c) in zip(_sc, [
            ("📡 Signals collected", str(_R.get("signal_count",0)), "#7c3aed"),
            ("🟠 Reddit posts",      str(len(_enrich.get("reddit_hot",[]))), "#ff4500"),
            ("📺 YouTube videos",    str(len(_enrich.get("youtube_viral",[]))), "#ff0000"),
            ("🔑 Search queries",    str(len(_enrich.get("search_queries",[]))), "#06b6d4"),
        ]):
            _col.markdown(
                f'<div class="score-card"><div class="score-number" style="font-size:1.4rem;color:{_c}">{_val}</div>'
                f'<div class="score-label">{_lbl}</div></div>',
                unsafe_allow_html=True)

        st.markdown("")
        if st.button("🔄 New Research", key="ra_reset"):
            st.session_state["ra_results"] = None
            st.session_state["ra_niche"]   = ""
            st.session_state["ra_running"] = False
            st.rerun()
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

        # ── Reddit Hot Posts ──────────────────────────────────────────────────
        _reddit_posts = _enrich.get("reddit_hot",[])
        if _reddit_posts:
            st.markdown("### 🟠 Reddit — Hot Posts")
            for _p in _reddit_posts:
                _sc3   = int(_p.get("score", _p.get("upvotes", 0)) or 0)
                _title = _p.get("title","")
                _sub   = _p.get("subreddit","")
                _url   = _p.get("url","")
                _body  = _p.get("body","")[:120]
                # Build Reddit search link if no direct URL
                if not _url and _title:
                    _url = f"https://www.reddit.com/search/?q={_req_mod.utils.quote(_title)}&sort=relevance"
                _link_html = (
                    f'<a href="{_url}" target="_blank" style="color:#ff4500;font-size:0.7rem;text-decoration:none;font-weight:600">↗ open</a>'
                    if _url else ""
                )
                _sub_html = (
                    f'<a href="https://www.reddit.com/{_sub}" target="_blank" style="color:#4a4a6a;font-size:0.7rem;text-decoration:none">{_sub}</a>'
                    if _sub else ""
                )
                _body_html = f'<div style="color:#9090b0;font-size:0.76rem;margin-top:3px">{_body}...</div>' if _body else ""
                st.markdown(
                    f'<div style="background:#0d0d1a;border:1px solid #1e1e30;border-left:3px solid #ff4500;'
                    f'border-radius:8px;padding:10px 14px;margin-bottom:6px">'
                    f'<div style="display:flex;justify-content:space-between;align-items:flex-start;gap:8px">'
                    f'<div style="flex:1">'
                    f'<span style="color:#ff4500;font-size:0.72rem;font-weight:700">▲ {_sc3:,}</span>'
                    f'<span style="color:#e8e8f0;font-size:0.87rem;font-weight:600;margin-left:8px">{_title}</span>'
                    f'{_body_html}'
                    f'</div>'
                    f'<div style="display:flex;gap:8px;align-items:center;white-space:nowrap">'
                    f'{_sub_html}'
                    f'{_link_html}'
                    f'</div></div></div>',
                    unsafe_allow_html=True,
                )

        st.markdown("")

        # ── YouTube Viral Videos ──────────────────────────────────────────────
        _yt_videos = _enrich.get("youtube_viral",[])
        if _yt_videos:
            st.markdown("### 📺 YouTube — Viral Videos")
            for _v in _yt_videos:
                _vtitle   = _v.get("title","")
                _vchannel = _v.get("channel","")
                _views    = _v.get("views", _v.get("view_estimate",""))
                _vurl     = _v.get("url","")
                _vwhy     = _v.get("why_works","") or _v.get("body","")
                # Build YouTube search URL if no direct link
                if not _vurl and _vtitle:
                    _vurl = f"https://www.youtube.com/results?search_query={_req_mod.utils.quote(_vtitle)}"
                _vlink = (
                    f'<a href="{_vurl}" target="_blank" style="color:#ff0000;font-size:0.7rem;text-decoration:none;font-weight:600">▶ watch</a>'
                    if _vurl else ""
                )
                _views_fmt = f"{int(_views):,}" if str(_views).isdigit() else str(_views)
                _vwhy_html  = f'<div style="color:#9090b0;font-size:0.76rem;margin-top:3px">{_vwhy[:100]}</div>' if _vwhy else ""
                _views_html = f'<span style="color:#4a4a6a;font-size:0.7rem">👁 {_views_fmt}</span>' if _views_fmt else ""
                _chan_html   = f'<span style="color:#4a4a6a;font-size:0.7rem">{_vchannel}</span>' if _vchannel else ""
                st.markdown(
                    f'<div style="background:#0d0d1a;border:1px solid #1e1e30;border-left:3px solid #ff0000;'
                    f'border-radius:8px;padding:10px 14px;margin-bottom:6px">'
                    f'<div style="display:flex;justify-content:space-between;align-items:flex-start;gap:8px">'
                    f'<div style="flex:1">'
                    f'<span style="color:#e8e8f0;font-size:0.87rem;font-weight:600">{_vtitle}</span>'
                    f'{_vwhy_html}'
                    f'</div>'
                    f'<div style="display:flex;gap:10px;align-items:center;white-space:nowrap">'
                    f'{_views_html}'
                    f'{_chan_html}'
                    f'{_vlink}'
                    f'</div></div></div>',
                    unsafe_allow_html=True,
                )

        st.markdown("")

        # ── Search Queries ────────────────────────────────────────────────────
        _queries = _enrich.get("search_queries",[])
        if _queries:
            st.markdown("### 🔍 Search Queries People Use")
            _qrows = []
            for _q in _queries:
                _qurl = f"https://www.google.com/search?q={_req_mod.utils.quote(str(_q))}"
                _yturl = f"https://www.youtube.com/results?search_query={_req_mod.utils.quote(str(_q))}"
                _qrows.append(
                    f'<div style="display:flex;justify-content:space-between;align-items:center;'
                    f'border-bottom:1px solid #12121f;padding:7px 0">'
                    f'<span style="color:#e8e8f0;font-size:0.85rem">{_q}</span>'
                    f'<div style="display:flex;gap:10px">'
                    f'<a href="{_qurl}" target="_blank" style="color:#4285f4;font-size:0.72rem;text-decoration:none">Google ↗</a>'
                    f'<a href="{_yturl}" target="_blank" style="color:#ff0000;font-size:0.72rem;text-decoration:none">YouTube ↗</a>'
                    f'</div></div>'
                )
            st.markdown(
                f'<div style="background:#0d0d1a;border:1px solid #1e1e30;border-radius:8px;padding:4px 14px">'
                + "".join(_qrows) + "</div>",
                unsafe_allow_html=True,
            )

        st.markdown("")

        # ── Pain Points ───────────────────────────────────────────────────────
        _pains = _enrich.get("pain_points",[])
        if _pains:
            st.markdown("### 😤 Pain Points Identified")
            _pain_html = "".join(
                f'<div style="display:flex;align-items:flex-start;gap:8px;border-bottom:1px solid #12121f;padding:7px 0">'
                f'<span style="color:#ef4444;font-size:0.8rem;margin-top:1px">●</span>'
                f'<span style="color:#e8e8f0;font-size:0.85rem;flex:1">{_pp}</span>'
                f'<a href="https://www.reddit.com/search/?q={_req_mod.utils.quote(str(_pp))}" target="_blank" '
                f'style="color:#4a4a6a;font-size:0.7rem;text-decoration:none;white-space:nowrap">Reddit ↗</a>'
                f'</div>'
                for _pp in _pains
            )
            st.markdown(
                f'<div style="background:#0d0d1a;border:1px solid #1e1e30;border-radius:8px;padding:4px 14px">'
                + _pain_html + "</div>",
                unsafe_allow_html=True,
            )

        st.markdown("")

        # ── Common Questions ──────────────────────────────────────────────────
        _questions = _enrich.get("questions",[])
        if _questions:
            st.markdown("### ❓ Questions People Are Asking")
            _q_html = "".join(
                f'<div style="display:flex;justify-content:space-between;align-items:center;'
                f'border-bottom:1px solid #12121f;padding:7px 0">'
                f'<span style="color:#e8e8f0;font-size:0.85rem">{_qq}</span>'
                f'<div style="display:flex;gap:10px">'
                f'<a href="https://www.google.com/search?q={_req_mod.utils.quote(str(_qq))}" target="_blank" style="color:#4285f4;font-size:0.72rem;text-decoration:none">Google ↗</a>'
                f'<a href="https://www.youtube.com/results?search_query={_req_mod.utils.quote(str(_qq))}" target="_blank" style="color:#ff0000;font-size:0.72rem;text-decoration:none">YouTube ↗</a>'
                f'<a href="https://www.reddit.com/search/?q={_req_mod.utils.quote(str(_qq))}" target="_blank" style="color:#ff4500;font-size:0.72rem;text-decoration:none">Reddit ↗</a>'
                f'</div></div>'
                for _qq in _questions
            )
            st.markdown(
                f'<div style="background:#0d0d1a;border:1px solid #1e1e30;border-radius:8px;padding:4px 14px">'
                + _q_html + "</div>",
                unsafe_allow_html=True,
            )

        st.markdown("")

        # ── Trending Topics ───────────────────────────────────────────────────
        _trending = _enrich.get("trending",[])
        if _trending:
            st.markdown("### 📈 Trending Topics Right Now")
            _tr_html = "".join(
                f'<div style="display:flex;justify-content:space-between;align-items:center;'
                f'border-bottom:1px solid #12121f;padding:7px 0">'
                f'<span style="color:#e8e8f0;font-size:0.85rem">🔥 {_tr}</span>'
                f'<div style="display:flex;gap:10px">'
                f'<a href="https://trends.google.com/trends/explore?q={_req_mod.utils.quote(str(_tr))}" target="_blank" style="color:#4285f4;font-size:0.72rem;text-decoration:none">Trends ↗</a>'
                f'<a href="https://www.tiktok.com/search?q={_req_mod.utils.quote(str(_tr))}" target="_blank" style="color:#1d9bf0;font-size:0.72rem;text-decoration:none">TikTok ↗</a>'
                f'<a href="https://www.youtube.com/results?search_query={_req_mod.utils.quote(str(_tr))}" target="_blank" style="color:#ff0000;font-size:0.72rem;text-decoration:none">YouTube ↗</a>'
                f'</div></div>'
                for _tr in _trending
            )
            st.markdown(
                f'<div style="background:#0d0d1a;border:1px solid #1e1e30;border-radius:8px;padding:4px 14px">'
                + _tr_html + "</div>",
                unsafe_allow_html=True,
            )

        st.markdown("")

        # ── Controversial Angles ──────────────────────────────────────────────
        _controversial = _enrich.get("controversial",[])
        if _controversial:
            st.markdown("### 🔥 High-Engagement Controversial Angles")
            _ca_html = "".join(
                f'<div style="display:flex;align-items:flex-start;gap:8px;border-bottom:1px solid #12121f;padding:7px 0">'
                f'<span style="color:#ec4899;font-size:0.8rem;margin-top:1px">◆</span>'
                f'<span style="color:#e8e8f0;font-size:0.85rem;flex:1">{_ca}</span>'
                f'<a href="https://www.reddit.com/search/?q={_req_mod.utils.quote(str(_ca))}&sort=controversial" '
                f'target="_blank" style="color:#4a4a6a;font-size:0.7rem;text-decoration:none;white-space:nowrap">Reddit ↗</a>'
                f'</div>'
                for _ca in _controversial
            )
            st.markdown(
                f'<div style="background:#0d0d1a;border:1px solid #1e1e30;border-radius:8px;padding:4px 14px">'
                + _ca_html + "</div>",
                unsafe_allow_html=True,
            )

        st.markdown("")

        # ── Buyer Objections ──────────────────────────────────────────────────
        _objections = _enrich.get("objections",[])
        if _objections:
            st.markdown("### 🚧 Buyer Objections to Address")
            _ob_html = "".join(
                f'<div style="display:flex;align-items:flex-start;gap:8px;border-bottom:1px solid #12121f;padding:7px 0">'
                f'<span style="color:#f59e0b;font-size:0.8rem;margin-top:1px">⚠</span>'
                f'<span style="color:#e8e8f0;font-size:0.85rem">{_ob}</span>'
                f'</div>'
                for _ob in _objections
            )
            st.markdown(
                f'<div style="background:#0d0d1a;border:1px solid #1e1e30;border-radius:8px;padding:4px 14px">'
                + _ob_html + "</div>",
                unsafe_allow_html=True,
            )

# ════════════════════════════════════════════════════════════════════
# PAGE: MARKET RESEARCH
# ════════════════════════════════════════════════════════════════════
elif current_page == "market":
    from modules.market_research import (
        fetch_market_trends, enrich_cards, build_script_brief,
        RESEARCH_CATEGORIES, PLATFORM_ANGLES,
    )
    from modules.social_trends import (
        fetch_social_trends, enrich_social_posts,
        PLATFORM_CONFIG,
    )
    from modules.script_generator import generate_script, EMOTIONAL_FRAMEWORKS, HOOK_TYPES, EQ_EMOTIONS
    from modules.brand_rag import query_brand_context, get_document_count
    from modules.brand_intelligence import research_brand
    from apikeys import rapidapi_key as _rapidapi_key, youtube_api_key as _yt_key

    # ── Category colour map (defined once, referenced everywhere) ─────────────
    CAT_COLORS = {
        "🔥 Trending Now":       "#ef4444",
        "📈 Market Shifts":      "#f59e0b",
        "💡 Tips & How-To":      "#06b6d4",
        "😱 Hot Takes":          "#ec4899",
        "✅ Success Stories":    "#10b981",
        "❓ Pain Points & FAQs": "#8b5cf6",
        "🌍 Industry News":      "#3b82f6",
        "💰 Money & Business":   "#f59e0b",
    }
    EMOTION_COLORS = {
        "Curiosity":"#06b6d4","Surprise":"#f59e0b","FOMO":"#ef4444",
        "Fear":"#ef4444","Inspiration":"#10b981","Hope":"#10b981",
        "Validation":"#8b5cf6","Outrage":"#ec4899",
    }

    # ── Session state ─────────────────────────────────────────────────────────
    for _k, _v in {
        "mkt_cards": [], "mkt_topic": "", "mkt_platform": "",
        "mkt_selected_id": None, "mkt_selected_card": None,
        "mkt_show_panel": False, "mkt_script": "", "mkt_generating": False,
        "mkt_brand_ctx": "", "mkt_brand_loaded": False,
    }.items():
        if _k not in st.session_state:
            st.session_state[_k] = _v

    # ── Load brand RAG context once (cached in session state) ─────────────────
    doc_count = get_document_count()
    if doc_count > 0 and not st.session_state["mkt_brand_loaded"]:
        # Pull a broad brand query to get the core identity
        _brand_ctx = query_brand_context(
            "brand identity products services target audience values messaging tone", top_k=8
        )
        st.session_state["mkt_brand_ctx"]    = _brand_ctx
        st.session_state["mkt_brand_loaded"] = True
    elif doc_count == 0:
        st.session_state["mkt_brand_ctx"]    = ""
        st.session_state["mkt_brand_loaded"] = False

    brand_ctx_mkt = st.session_state["mkt_brand_ctx"]
    has_brand     = bool(brand_ctx_mkt.strip())

    # ── Page header ───────────────────────────────────────────────────────────
    st.markdown("# 📊 Market Research")
    st.markdown(
        '<p style="color:#6b6b8a;font-size:0.95rem">Search any topic → AI scores each trend for viral potential <em>and brand fit</em> → pick one → answer questions → get a script.</p>',
        unsafe_allow_html=True,
    )

    mkt_tab1, mkt_tab2 = st.tabs(["📰 News & Web Trends", "📱 Social Media Trends"])
    with mkt_tab1:

        # ── Brand context banner ──────────────────────────────────────────────────
        if has_brand:
            # Extract a short brand summary for display
            brand_preview = brand_ctx_mkt[:180].replace("\n"," ").strip()
            st.markdown(f"""
    <div style="background:#0c0c18;border:1px solid #7c3aed44;border-left:4px solid #7c3aed;border-radius:10px;padding:12px 16px;margin-bottom:4px;display:flex;align-items:center;gap:12px;flex-wrap:wrap">
      <div style="flex:1;min-width:200px">
        <span style="color:#7c3aed;font-size:0.7rem;font-weight:700;text-transform:uppercase;letter-spacing:0.1em">🏷️ Brand RAG Active — {doc_count} doc{"s" if doc_count!=1 else ""} loaded</span>
        <p style="color:#9090b0;font-size:0.78rem;margin:3px 0 0 0;line-height:1.4">{brand_preview}{"…" if len(brand_ctx_mkt)>180 else ""}</p>
      </div>
      <span style="background:#7c3aed22;color:#7c3aed;font-size:0.72rem;padding:4px 10px;border-radius:20px;white-space:nowrap">Cards scored for brand fit ✓</span>
    </div>""", unsafe_allow_html=True)
        else:
            st.markdown("""
    <div style="background:#0a0a14;border:1px solid #2a2a3e;border-radius:10px;padding:10px 14px;margin-bottom:4px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px">
      <p style="color:#4a4a6a;font-size:0.8rem;margin:0">🏷️ No brand docs uploaded — cards will be scored on viral potential only</p>
      <span style="color:#6b6b8a;font-size:0.75rem">Upload docs in <strong>🎯 Brand Setup</strong> to enable brand-fit scoring</span>
    </div>""", unsafe_allow_html=True)

        # ── Search bar ────────────────────────────────────────────────────────────
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        sb1, sb2, sb3, sb4 = st.columns([3.5, 1.4, 1.6, 0.9])
        with sb1:
            mkt_topic_input = st.text_input(
                "topic", label_visibility="collapsed",
                placeholder="🔍  Search topic — e.g. AI productivity, vegan skincare, electric cars...",
                key="mkt_topic_input",
            )
        with sb2:
            mkt_platform = st.selectbox(
                "platform", list(PLATFORM_ANGLES.keys()),
                label_visibility="collapsed", key="mkt_platform_sel",
            )
        with sb3:
            mkt_cats = st.multiselect(
                "categories", list(RESEARCH_CATEGORIES.keys()),
                default=list(RESEARCH_CATEGORIES.keys()),
                label_visibility="collapsed", key="mkt_cats_sel",
                placeholder="All categories",
            )
        with sb4:
            do_search = st.button("🔍 Search", use_container_width=True, key="mkt_search_btn")

        if do_search and mkt_topic_input.strip():
            # Reset selection state
            st.session_state["mkt_selected_id"]   = None
            st.session_state["mkt_selected_card"] = None
            st.session_state["mkt_show_panel"]    = False
            st.session_state["mkt_script"]        = ""

            cats  = mkt_cats or list(RESEARCH_CATEGORIES.keys())
            _prog = st.progress(0)
            _stat = st.empty()

            # If brand context exists, enrich the search query with brand keywords
            search_topic = mkt_topic_input.strip()
            if has_brand:
                _stat.markdown(f'<div class="info-box">🏷️ Aligning search with brand context...</div>', unsafe_allow_html=True)
                _prog.progress(8)
                try:
                    _brand_q_resp = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[
                            {"role":"system","content":"Extract 3-5 keywords from brand context that best complement a search topic. Return only comma-separated keywords, nothing else."},
                            {"role":"user","content":f"Brand context:\n{brand_ctx_mkt[:600]}\n\nSearch topic: {search_topic}\n\nReturn 3-5 brand-relevant keywords to add to this search:"}
                        ],
                        max_tokens=60, temperature=0.2
                    )
                    brand_keywords = _brand_q_resp.choices[0].message.content.strip()
                    st.session_state["mkt_brand_keywords"] = brand_keywords
                except Exception:
                    brand_keywords = ""
                    st.session_state["mkt_brand_keywords"] = ""
            else:
                brand_keywords = ""
                st.session_state["mkt_brand_keywords"] = ""

            _stat.markdown(f'<div class="info-box">🌐 Searching {len(cats)} angles for <strong>{search_topic}</strong>...</div>', unsafe_allow_html=True)
            _prog.progress(20)
            raw = fetch_market_trends(search_topic, mkt_platform, cats, max_per=6)

            enrich_msg = "🧠 AI-scoring results for viral potential"
            if has_brand:
                enrich_msg += " + brand fit"
            _stat.markdown(f'<div class="info-box">{enrich_msg}...</div>', unsafe_allow_html=True)
            _prog.progress(60)
            enriched = enrich_cards(client, raw, search_topic, mkt_platform, brand_context=brand_ctx_mkt)

            _prog.progress(100); _stat.empty(); _prog.empty()
            st.session_state["mkt_cards"]    = enriched
            st.session_state["mkt_topic"]    = search_topic
            st.session_state["mkt_platform"] = mkt_platform

        elif do_search:
            st.warning("Please enter a topic to research.")

        # ── Cards grid ────────────────────────────────────────────────────────────
        cards = st.session_state["mkt_cards"]

        if not cards:
            st.markdown("""
    <div style="text-align:center;padding:80px 20px">
      <div style="font-size:3.5rem;margin-bottom:12px">📡</div>
      <p style="color:#3a3a5a;font-size:1.05rem;margin:0">Enter a topic and hit <strong style="color:#7c3aed">Search</strong> to discover trends</p>
      <p style="color:#252535;font-size:0.85rem;margin-top:8px">Searches news, tips, controversies, social proof, FAQs & more — all in one go</p>
    </div>""", unsafe_allow_html=True)
        else:
            topic_shown    = st.session_state["mkt_topic"]
            platform_shown = st.session_state["mkt_platform"]

            # ── Stats bar ─────────────────────────────────────────────────────────
            st.markdown("")
            scores  = [c.get("content_score",0)   for c in cards]
            bscores = [c.get("brand_relevance",0) for c in cards]
            hot          = sum(1 for s in scores  if s >= 75)
            brand_fit    = sum(1 for b in bscores if b >= 60)
            cats_u       = list(dict.fromkeys(c["category"] for c in cards))
            avg_brand    = int(sum(bscores)/len(bscores)) if bscores else 0

            stat_cols = st.columns(6 if has_brand else 4)
            stat_cols[0].markdown(f'<div class="score-card"><div class="score-number" style="font-size:1.3rem">{len(cards)}</div><div class="score-label">Topics Found</div></div>', unsafe_allow_html=True)
            stat_cols[1].markdown(f'<div class="score-card"><div class="score-number" style="font-size:1.3rem;color:#ef4444">{hot}</div><div class="score-label">🔥 Hot</div></div>', unsafe_allow_html=True)
            stat_cols[2].markdown(f'<div class="score-card"><div class="score-number" style="font-size:1.3rem">{max(scores) if scores else 0}</div><div class="score-label">Top Score</div></div>', unsafe_allow_html=True)
            stat_cols[3].markdown(f'<div class="score-card"><div class="score-number" style="font-size:1.3rem">{len(cats_u)}</div><div class="score-label">Categories</div></div>', unsafe_allow_html=True)
            if has_brand:
                stat_cols[4].markdown(f'<div class="score-card"><div class="score-number" style="font-size:1.3rem;color:#7c3aed">{brand_fit}</div><div class="score-label">🏷️ Brand Fit</div></div>', unsafe_allow_html=True)
                stat_cols[5].markdown(f'<div class="score-card"><div class="score-number" style="font-size:1.3rem;color:#7c3aed">{avg_brand}</div><div class="score-label">Avg Brand Score</div></div>', unsafe_allow_html=True)
            st.markdown("")

            # ── Filter / sort bar ─────────────────────────────────────────────────
            f1, f2, f3, f4, f5 = st.columns([2, 1.5, 1.5, 1.5, 1.5])
            with f1:
                filt_cat = st.selectbox("Category", ["All"] + cats_u, key="mkt_fcat", label_visibility="collapsed")
            with f2:
                emotions_u = list(dict.fromkeys(c["emotion"] for c in cards if c.get("emotion")))
                filt_emo   = st.selectbox("Emotion", ["All emotions"] + emotions_u, key="mkt_femo", label_visibility="collapsed")
            with f3:
                filt_fmt = st.selectbox(
                    "Format", ["All formats"] + list(dict.fromkeys(c["format_fit"] for c in cards if c.get("format_fit"))),
                    key="mkt_ffmt", label_visibility="collapsed",
                )
            with f4:
                sort_options = ["Score ↓", "Brand Fit ↓", "Newest", "A-Z"] if has_brand else ["Score ↓", "Newest", "A-Z"]
                sort_opt = st.selectbox("Sort", sort_options, key="mkt_sort", label_visibility="collapsed")
            with f5:
                brand_only = st.checkbox("🏷️ Brand fit only", value=False, key="mkt_brand_only",
                                         disabled=not has_brand,
                                         help="Show only cards with brand relevance ≥ 50")

            # Apply filters
            shown = [c for c in cards
                     if (filt_cat == "All"         or c["category"]   == filt_cat)
                     and (filt_emo == "All emotions" or c.get("emotion","") == filt_emo)
                     and (filt_fmt == "All formats"  or c.get("format_fit","") == filt_fmt)
                     and (not brand_only or c.get("brand_relevance",0) >= 50)]
            if sort_opt == "Brand Fit ↓":
                shown = sorted(shown, key=lambda x: x.get("brand_relevance",0), reverse=True)
            elif sort_opt == "Newest":
                shown = sorted(shown, key=lambda x: x.get("date",""), reverse=True)
            elif sort_opt == "A-Z":
                shown = sorted(shown, key=lambda x: x.get("title",""))

            st.markdown(
                f'<p style="color:#6b6b8a;font-size:0.8rem;margin-bottom:4px">Showing <strong style="color:#e8e8f0">{len(shown)}</strong> of {len(cards)} results for <strong style="color:#7c3aed">{topic_shown}</strong></p>',
                unsafe_allow_html=True,
            )

            # ── 3-column card grid ────────────────────────────────────────────────
            sel_id = st.session_state["mkt_selected_id"]

            for row_i in range(0, len(shown), 3):
                row_cards = shown[row_i: row_i + 3]
                cols      = st.columns(3)

                for col, card in zip(cols, row_cards):
                    cid    = card["id"]
                    score  = card.get("content_score", 50)
                    brel   = card.get("brand_relevance", 0)
                    bangle = card.get("brand_angle", "")
                    cat    = card.get("category","")
                    cc     = CAT_COLORS.get(cat, "#6b6b8a")
                    emo    = card.get("emotion","")
                    ec     = EMOTION_COLORS.get(emo, "#6b6b8a")
                    angle  = card.get("content_angle","")
                    hook   = card.get("hook_idea","")
                    tags   = card.get("tags",[])[:3]
                    fmt    = card.get("format_fit","")
                    src    = (card.get("source","") or "")[:28]
                    url    = card.get("url","")
                    tago   = card.get("time_ago","")
                    title  = card.get("title","")
                    body   = card.get("body","")
                    is_sel = (cid == sel_id)

                    # Viral score badge
                    if score >= 80:   sbadge, sbcolor = "🔥 Hot",    "#ef4444"
                    elif score >= 65: sbadge, sbcolor = "⚡ Strong", "#f59e0b"
                    elif score >= 50: sbadge, sbcolor = "💡 Good",   "#06b6d4"
                    else:             sbadge, sbcolor = "📌 Low",    "#6b6b8a"

                    # Brand relevance badge
                    if has_brand:
                        if brel >= 75:   bbadge, bbcolor = f"🏷️ {brel}",  "#7c3aed"
                        elif brel >= 50: bbadge, bbcolor = f"🏷️ {brel}",  "#8b5cf6"
                        elif brel >= 25: bbadge, bbcolor = f"🏷️ {brel}",  "#4a4a6a"
                        else:            bbadge, bbcolor = f"🏷️ {brel}",  "#2a2a3a"
                        brand_badge_html = f'<span style="background:{bbcolor}22;color:{bbcolor};font-size:0.62rem;font-weight:700;padding:3px 9px;border-radius:20px">Brand {bbadge}</span>'
                    else:
                        brand_badge_html = ""

                    tags_html = " ".join(
                        f'<span style="background:#1a1a2e;color:#9090b0;font-size:0.62rem;padding:2px 7px;border-radius:20px">{t}</span>'
                        for t in tags
                    )
                    border   = "2px solid #7c3aed" if is_sel else "1px solid #1e1e30"
                    bg       = "#130f20" if is_sel else "#0d0d1a"
                    top_bdr  = f'border-top:3px solid {"#7c3aed" if is_sel else cc}'

                    # Brand angle block (shown only if brand docs exist and angle is meaningful)
                    brand_angle_html = ""
                    if has_brand and bangle and brel >= 40:
                        brand_angle_html = f'<div style="background:#100a1f;border-left:2px solid #7c3aed66;padding:7px 10px;border-radius:0 8px 8px 0"><p style="color:#7c3aed;font-size:0.63rem;font-weight:700;text-transform:uppercase;margin:0 0 2px 0">🏷️ Brand Angle</p><p style="color:#c8c0e8;font-size:0.76rem;margin:0;line-height:1.4">{bangle}</p></div>'

                    with col:
                        st.markdown(f"""
    <div style="background:{bg};border:{border};{top_bdr};border-radius:14px;padding:18px 16px;margin-bottom:2px;display:flex;flex-direction:column;gap:10px;min-height:300px">

      <!-- top row: category + scores -->
      <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:4px">
        <span style="background:{cc}22;color:{cc};font-size:0.62rem;font-weight:700;padding:3px 9px;border-radius:20px;white-space:nowrap">{cat}</span>
        <div style="display:flex;gap:4px;flex-wrap:wrap">
          <span style="background:{sbcolor}22;color:{sbcolor};font-size:0.62rem;font-weight:700;padding:3px 9px;border-radius:20px">{sbadge} {score}</span>
          {brand_badge_html}
        </div>
      </div>

      <!-- title -->
      <p style="color:#e8e8f0;font-size:0.9rem;font-weight:600;line-height:1.45;margin:0">{title[:100]}{"…" if len(title)>100 else ""}</p>

      <!-- body preview -->
      <p style="color:#8080a0;font-size:0.78rem;line-height:1.55;margin:0;flex:1">{body[:180]}{"…" if len(body)>180 else ""}</p>

      <!-- brand angle (if relevant) -->
      {brand_angle_html}

      <!-- content angle -->
      {f'<div style="background:#0a0a14;border-left:2px solid {cc}66;padding:7px 10px;border-radius:0 8px 8px 0"><p style="color:{cc};font-size:0.63rem;font-weight:700;text-transform:uppercase;margin:0 0 2px 0">📐 Content Angle</p><p style="color:#d0d0e8;font-size:0.76rem;margin:0;line-height:1.4">{angle}</p></div>' if angle else ''}

      <!-- hook idea -->
      {f'<div style="background:#0a0a14;border-radius:8px;padding:7px 10px"><p style="color:#7c3aed;font-size:0.63rem;font-weight:700;text-transform:uppercase;margin:0 0 2px 0">🎣 Hook Idea</p><p style="color:#c8c8e0;font-size:0.76rem;font-style:italic;margin:0">"{hook}"</p></div>' if hook else ''}

      <!-- tags + emotion + format -->
      <div style="display:flex;flex-wrap:wrap;gap:4px;align-items:center">
        {tags_html}
        {f'<span style="background:{ec}22;color:{ec};font-size:0.62rem;padding:2px 7px;border-radius:20px">{emo}</span>' if emo else ''}
        {f'<span style="color:#4a4a6a;font-size:0.62rem">{fmt}</span>' if fmt else ''}
      </div>

      <!-- source + time -->
      <div style="display:flex;justify-content:space-between;align-items:center;border-top:1px solid #181828;padding-top:8px;margin-top:auto">
        {'<a href="' + url + '" target="_blank" style="color:#5a5a7a;font-size:0.7rem;text-decoration:none;max-width:65%;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">' + src + ' ↗</a>' if url else f'<span style="color:#4a4a6a;font-size:0.7rem">{src}</span>'}
        <span style="color:#3a3a5a;font-size:0.68rem">{tago}</span>
      </div>

    </div>""", unsafe_allow_html=True)

                        # Action buttons
                        bc1, bc2 = col.columns([3, 1])
                        if bc1.button(
                            "✓ Selected — Make Script" if is_sel else "✍️ Use This Topic",
                            key=f"sel_{cid}",
                            use_container_width=True,
                            type="primary" if is_sel else "secondary",
                        ):
                            st.session_state["mkt_selected_id"]   = cid
                            st.session_state["mkt_selected_card"] = card
                            st.session_state["mkt_show_panel"]    = True
                            st.session_state["mkt_script"]        = ""
                            st.rerun()

                        if url:
                            bc2.markdown(
                                f'<a href="{url}" target="_blank" style="display:block;text-align:center;'
                                f'padding:7px 0;border:1px solid #2a2a3e;border-radius:6px;'
                                f'color:#5a5a7a;font-size:0.75rem;text-decoration:none">↗</a>',
                                unsafe_allow_html=True,
                            )

            st.markdown("")

        # ── Script creation panel (shown when a card is selected) ─────────────────
        if st.session_state.get("mkt_show_panel") and st.session_state.get("mkt_selected_card"):
            card = st.session_state["mkt_selected_card"]
            cat  = card.get("category","")
            cc   = CAT_COLORS.get(cat, "#7c3aed")

            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

            # Selected card summary strip
            st.markdown(f"""
    <div style="background:#0f0f1e;border:1px solid #7c3aed44;border-left:4px solid #7c3aed;border-radius:12px;padding:16px 20px;margin-bottom:22px;display:flex;gap:16px;align-items:flex-start;flex-wrap:wrap">
      <div style="flex:1;min-width:200px">
        <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-bottom:6px">
          <span style="background:{cc}22;color:{cc};font-size:0.62rem;font-weight:700;padding:3px 9px;border-radius:20px">{cat}</span>
          <span style="color:#7c3aed;font-size:0.7rem;font-weight:700">SELECTED TOPIC</span>
        </div>
        <p style="color:#e8e8f0;font-size:0.95rem;font-weight:600;margin:0 0 4px 0">{card.get("title","")}</p>
        <p style="color:#7c3aed;font-size:0.82rem;margin:0;font-style:italic">{card.get("content_angle","")}</p>
      </div>
      <div style="text-align:right;flex-shrink:0">
        <div style="color:#7c3aed;font-family:Syne;font-weight:700;font-size:1.6rem">{card.get("content_score",0)}</div>
        <div style="color:#6b6b8a;font-size:0.68rem">Viral Score</div>
      </div>
    </div>""", unsafe_allow_html=True)

            st.markdown("## 🎯 Customise Your Script")
            st.markdown('<p style="color:#6b6b8a;font-size:0.85rem;margin:-6px 0 18px 0">Answer these questions and we\'ll generate a script built exactly around this topic and your brand.</p>', unsafe_allow_html=True)

            # ── Two-column question form ──────────────────────────────────────────
            ql, qr = st.columns(2)

            with ql:
                st.markdown("#### 📱 Platform & Format")
                q_plat = st.selectbox("Platform", list(PLATFORM_ANGLES.keys()), key="q_plat")
                q_dur  = st.selectbox("Duration", ["15 sec","30 sec","60 sec","90 sec","3 min","5+ min"], index=2, key="q_dur")
                q_fw   = st.selectbox("Narrative Framework", list(EMOTIONAL_FRAMEWORKS.keys()), key="q_fw")
                q_hook = st.selectbox("Hook Style", list(HOOK_TYPES.keys()), index=1, key="q_hook")
                st.caption(f"💡 {HOOK_TYPES.get(st.session_state.q_hook,'')}")

                st.markdown("#### 🎤 Voice & Tone")
                q_tone = st.selectbox("Tone",
                    ["Conversational","Authoritative","Inspirational","Urgent","Humorous","Educational","Empathetic","Bold"],
                    key="q_tone")
                q_emo  = st.multiselect("Emotions to trigger", EQ_EMOTIONS,
                    default=[card.get("emotion","Curiosity"), "Inspiration"] if card.get("emotion") else ["Curiosity","Inspiration"],
                    key="q_emo")

            with qr:
                st.markdown("#### ✨ Content Style")
                q_humor = st.radio("😂 Humor?", [
                    "No — keep it straight",
                    "Light — relatable & witty",
                    "Yes — make it comedic",
                ], key="q_humor")
                st.markdown("")

                q_sp = st.radio("⭐ Social proof?", [
                    "No",
                    "Yes — include stats & numbers",
                    "Yes — add testimonial angle",
                ], key="q_sp")
                st.markdown("")

                q_story = st.radio("🧍 Personal story?", [
                    "No",
                    "Yes — first-person journey",
                    "Yes — as a third-party case study",
                ], key="q_story")
                st.markdown("")

                q_hot = st.radio("🔥 Controversy level?", [
                    "Low — safe & balanced",
                    "Medium — mild hot take",
                    "High — challenge the norm",
                ], key="q_hot")
                st.markdown("")

                q_cta = st.selectbox("📣 CTA", [
                    "Follow for more",
                    "Comment your opinion",
                    "Share with a friend",
                    "Visit link in bio",
                    "Try it now",
                    "Save this video",
                    "DM me for details",
                    "Custom...",
                ], key="q_cta")
                if st.session_state.q_cta == "Custom...":
                    q_cta = st.text_input("Custom CTA text", placeholder="e.g. DM me 'FREE' for the template", key="q_cta_custom")
                else:
                    q_cta = st.session_state.q_cta

            # Extra instructions full-width
            q_extra = st.text_area(
                "💬 Anything else? (keywords, things to avoid, specific angle, product to mention…)",
                placeholder="e.g. Mention our 30-day free trial, avoid naming competitors, use the phrase 'most people don't know this'…",
                height=75,
                key="q_extra",
            )

            # Brand alignment
            st.markdown("#### 🏷️ Brand Context")
            if has_brand:
                brel_card = card.get("brand_relevance", 0)
                brel_color = "#7c3aed" if brel_card >= 60 else "#f59e0b" if brel_card >= 35 else "#6b6b8a"
                st.markdown(f"""
    <div style="background:#0c0c18;border:1px solid #7c3aed33;border-radius:10px;padding:12px 16px;margin-bottom:10px;display:flex;align-items:center;gap:12px;flex-wrap:wrap">
      <div style="flex:1">
        <span style="color:#7c3aed;font-size:0.7rem;font-weight:700;text-transform:uppercase">✓ Brand RAG auto-included ({doc_count} doc{"s" if doc_count!=1 else ""})</span>
        <p style="color:#9090b0;font-size:0.78rem;margin:3px 0 0 0">Brand context will be injected into the script. Brand fit score for this topic: <strong style="color:{brel_color}">{brel_card}/100</strong></p>
      </div>
    </div>""", unsafe_allow_html=True)

            bcol1, bcol2 = st.columns(2)
            with bcol1:
                q_brand = st.text_input(
                    "Brand name for extra live web research (optional)",
                    placeholder="e.g. your brand name for real-time lookup…",
                    key="q_brand",
                )
            with bcol2:
                q_use_rag = st.checkbox(
                    f"📎 Brand docs (RAG){' — ' + str(doc_count) + ' docs' if doc_count else ' — none uploaded'}",
                    value=has_brand,
                    key="q_rag",
                    disabled=not has_brand,
                )

            # Creator style notice
            if st.session_state.get("creator_style_prompt"):
                st.markdown(f'<div class="info-box" style="border-color:#8b5cf6">💉 <strong>Creator style active:</strong> {st.session_state.get("creator_style_name","")}</div>', unsafe_allow_html=True)

            st.markdown("")
            gb1, gb2 = st.columns([4, 1])
            gen_btn = gb1.button("⚡ Generate Script", use_container_width=True, type="primary", key="mkt_gen_btn")
            if gb2.button("✕ Deselect", use_container_width=True, key="mkt_desel"):
                st.session_state["mkt_show_panel"]    = False
                st.session_state["mkt_selected_id"]   = None
                st.session_state["mkt_selected_card"] = None
                st.rerun()

            # ── Generate ──────────────────────────────────────────────────────────
            if gen_btn:
                answers = {
                    "tone":           q_tone,
                    "humor":          q_humor,
                    "social_proof":   q_sp,
                    "personal_story": q_story,
                    "controversy":    q_hot,
                    "cta_type":       q_cta,
                    "target_emotion": ", ".join(q_emo) if q_emo else card.get("emotion","Curiosity"),
                    "extra_notes":    q_extra,
                    "use_stats":      "Yes — use real numbers" if "stats" in q_sp.lower() else "Include if available",
                }

                _p2 = st.progress(0); _s2 = st.empty()

                # Step 1 — brand intel
                brand_intel = ""
                if q_brand.strip():
                    _s2.markdown(f'<div class="info-box">🔍 Researching <strong>{q_brand}</strong>...</div>', unsafe_allow_html=True)
                    _p2.progress(15)
                    bi = research_brand(client, q_brand.strip())
                    brand_intel = bi.get("injection_block","")

                # Step 2 — RAG (already loaded in brand_ctx_mkt)
                rag_ctx = brand_ctx_mkt if q_use_rag else ""
                if rag_ctx:
                    # Also query specifically for this card's topic for tighter relevance
                    _topic_rag = query_brand_context(
                        f"{card.get('title','')} {q_tone} {q_plat}", top_k=4
                    )
                    if _topic_rag:
                        rag_ctx = _topic_rag  # use the topic-specific pull

                # Step 3 — build brief
                brief = build_script_brief(card, answers)

                _s2.markdown('<div class="info-box">✍️ Generating script...</div>', unsafe_allow_html=True)
                _p2.progress(50)

                out = st.empty()
                full_s = ""

                gen = generate_script(
                    client,
                    topic              = brief,
                    platform           = q_plat,
                    duration           = q_dur,
                    tone               = q_tone,
                    hook_type          = q_hook,
                    emotional_framework= q_fw,
                    target_emotions    = q_emo,
                    conditions         = q_extra,
                    brand_context      = rag_ctx,
                    brand_intelligence = brand_intel,
                    topic_research     = "",
                    creator_style      = st.session_state.get("creator_style_prompt",""),
                    trend_data         = "",
                )
                for chunk in gen:
                    full_s += chunk
                    out.markdown(f'<div class="script-output">{full_s}▌</div>', unsafe_allow_html=True)

                _p2.progress(100); _s2.empty(); _p2.empty()
                out.markdown(f'<div class="script-output">{full_s}</div>', unsafe_allow_html=True)
                st.session_state["mkt_script"]  = full_s
                st.session_state["last_script"] = full_s

        # ── Generated script actions ──────────────────────────────────────────────
        if st.session_state.get("mkt_script"):
            sc = st.session_state["mkt_script"]
            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
            st.markdown("### 📄 Generated Script")
            st.markdown(f'<div class="script-output">{sc}</div>', unsafe_allow_html=True)
            st.markdown("")

            a1, a2, a3, a4 = st.columns(4)
            slug = (st.session_state.get("mkt_topic","topic") or "topic")[:20].replace(" ","_")
            a1.download_button("⬇️ Download", sc, file_name=f"script_{slug}.txt", mime="text/plain", key="mkt_dl")
            if a2.button("💬 Send to Chat", key="mkt_to_chat"):
                st.session_state["chat_script_context"] = sc
                st.success("Sent to Script Chat!")
            if a3.button("📝 Analyze Script", key="mkt_analyze"):
                st.session_state["pending_analyze_script"] = sc
                st.success("Go to Script Analyzer!")
            if a4.button("🔄 Regenerate", key="mkt_regen"):
                st.session_state["mkt_script"] = ""
                st.rerun()

    # ════════════════════════════════════════════════════════════════════
    # TAB 2: SOCIAL MEDIA TRENDS
    # ════════════════════════════════════════════════════════════════════
    with mkt_tab2:
        # ── Platform colours ──────────────────────────────────────────────────
        SOC_COLORS = {
            "Reddit":        "#ff4500",
            "YouTube":       "#ff0000",
            "TikTok":        "#1d9bf0",
            "Instagram":     "#e1306c",
            "Facebook":      "#1877f2",
            "Twitter/X":     "#1da1f2",
            "Google Trends": "#4285f4",
        }
        EMOTION_COLORS_SOC = {
            "Curiosity":"#06b6d4","Surprise":"#f59e0b","FOMO":"#ef4444",
            "Fear":"#ef4444","Inspiration":"#10b981","Hope":"#10b981",
            "Validation":"#8b5cf6","Outrage":"#ec4899",
        }

        # ── Session state ─────────────────────────────────────────────────────
        for _sk, _sv in {
            "soc_posts": [], "soc_topic": "", "soc_platform": "",
            "soc_selected_id": None, "soc_selected_post": None,
            "soc_show_panel": False, "soc_script": "",
            "soc_ig_user": "", "soc_ig_pass": "", "soc_ig_session": "",
            "soc_fb_cookies": {}, "soc_accounts_open": False,
        }.items():
            if _sk not in st.session_state:
                st.session_state[_sk] = _sv

        # ── API + Account status banner ───────────────────────────────────────
        api_status = []
        api_status.append('<span style="color:#10b981">✓ Reddit (free)</span>')
        api_status.append('<span style="color:#10b981">✓ Twitter/X (Nitter)</span>')
        api_status.append('<span style="color:#10b981">✓ Google Trends</span>')
        if _yt_key and _yt_key not in ("","YOUR_YOUTUBE_KEY"):
            api_status.append('<span style="color:#ff0000">✓ YouTube API</span>')
        else:
            api_status.append('<span style="color:#4a4a6a">⚠ YouTube (yt-dlp fallback)</span>')
        if _rapidapi_key and _rapidapi_key not in ("","YOUR_RAPIDAPI_KEY"):
            api_status.append('<span style="color:#1d9bf0">✓ TikTok (RapidAPI)</span>')
        else:
            api_status.append('<span style="color:#4a4a6a">⚠ TikTok (add RapidAPI key)</span>')

        ig_authed = bool(st.session_state.get("soc_ig_session") or
                         (st.session_state.get("soc_ig_user") and st.session_state.get("soc_ig_pass")))
        fb_authed = bool(st.session_state.get("soc_fb_cookies",{}).get("c_user") or _rapidapi_key)
        api_status.append(
            f'<span style="color:#e1306c">{"✓ Instagram (logged in)" if ig_authed else "⚠ Instagram (add account)"}</span>'
        )
        api_status.append(
            f'<span style="color:#1877f2">{"✓ Facebook (connected)" if fb_authed else "⚠ Facebook (add account)"}</span>'
        )

        st.markdown(
            '<div style="background:#0a0a14;border:1px solid #1e1e30;border-radius:10px;padding:10px 16px;margin-bottom:8px;display:flex;flex-wrap:wrap;gap:12px">'
            + " &nbsp;·&nbsp; ".join(api_status) + '</div>',
            unsafe_allow_html=True,
        )

        # ── Account credentials panel ─────────────────────────────────────────
        with st.expander("🔐 Connect Accounts (Instagram & Facebook)", expanded=not ig_authed and not fb_authed):
            st.markdown('<p style="color:#6b6b8a;font-size:0.82rem;margin:0 0 12px 0">Connect your accounts to scrape real posts from Instagram and Facebook. Credentials are stored only in your session — never saved to disk.</p>', unsafe_allow_html=True)

            acc_c1, acc_c2 = st.columns(2)

            with acc_c1:
                st.markdown("**📸 Instagram**")
                _ig_method = st.radio("Login method", ["Session ID (safer)", "Username + Password"],
                                      key="ig_method_radio", horizontal=True, label_visibility="collapsed")
                if _ig_method == "Session ID (safer)":
                    st.caption("Find your sessionid cookie in browser DevTools → Application → Cookies → instagram.com")
                    _ig_sid = st.text_input("Instagram Session ID", type="password",
                                            value=st.session_state.get("soc_ig_session",""),
                                            placeholder="paste sessionid cookie value…", key="ig_sid_input")
                    _ig_user_sid = st.text_input("Instagram Username (for display)", key="ig_user_sid",
                                                  value=st.session_state.get("soc_ig_user",""),
                                                  placeholder="your_username")
                    if st.button("Connect Instagram", key="ig_connect_sid"):
                        st.session_state["soc_ig_session"] = _ig_sid.strip()
                        st.session_state["soc_ig_user"]    = _ig_user_sid.strip()
                        st.success("✓ Instagram session saved")
                        st.rerun()
                else:
                    _ig_u = st.text_input("Instagram Username", key="ig_u",
                                           value=st.session_state.get("soc_ig_user",""))
                    _ig_p = st.text_input("Instagram Password", type="password", key="ig_p")
                    if st.button("Connect Instagram", key="ig_connect_up"):
                        st.session_state["soc_ig_user"] = _ig_u.strip()
                        st.session_state["soc_ig_pass"] = _ig_p
                        st.success("✓ Instagram credentials saved")
                        st.rerun()

                if ig_authed:
                    st.markdown(f'<div style="color:#10b981;font-size:0.8rem">✓ Connected as @{st.session_state.get("soc_ig_user","")}</div>', unsafe_allow_html=True)
                    if st.button("Disconnect Instagram", key="ig_disconnect"):
                        st.session_state["soc_ig_user"] = ""
                        st.session_state["soc_ig_pass"] = ""
                        st.session_state["soc_ig_session"] = ""
                        st.rerun()

            with acc_c2:
                st.markdown("**📘 Facebook**")
                st.caption("Paste your Facebook cookie values from browser DevTools → Application → Cookies → facebook.com")
                _fb_cuser  = st.text_input("c_user cookie", key="fb_cuser",
                                             value=st.session_state.get("soc_fb_cookies",{}).get("c_user",""),
                                             placeholder="numeric user ID…")
                _fb_xs     = st.text_input("xs cookie", type="password", key="fb_xs",
                                            value=st.session_state.get("soc_fb_cookies",{}).get("xs",""),
                                            placeholder="xs value…")
                _fb_datr   = st.text_input("datr cookie (optional)", key="fb_datr",
                                            value=st.session_state.get("soc_fb_cookies",{}).get("datr",""),
                                            placeholder="datr value…")
                if st.button("Connect Facebook", key="fb_connect"):
                    _fb_c = {"c_user": _fb_cuser.strip(), "xs": _fb_xs.strip()}
                    if _fb_datr.strip():
                        _fb_c["datr"] = _fb_datr.strip()
                    st.session_state["soc_fb_cookies"] = _fb_c
                    st.success("✓ Facebook cookies saved")
                    st.rerun()

                if fb_authed and st.session_state.get("soc_fb_cookies",{}).get("c_user"):
                    st.markdown(f'<div style="color:#10b981;font-size:0.8rem">✓ Connected (user {st.session_state["soc_fb_cookies"]["c_user"][:6]}…)</div>', unsafe_allow_html=True)
                    if st.button("Disconnect Facebook", key="fb_disconnect"):
                        st.session_state["soc_fb_cookies"] = {}
                        st.rerun()

                st.markdown('<p style="color:#4a4a6a;font-size:0.72rem;margin-top:8px">Tip: RapidAPI key also enables Facebook scraping without cookies.</p>', unsafe_allow_html=True)

        # ── Search bar ────────────────────────────────────────────────────────
        sc1, sc2, sc3, sc4 = st.columns([3, 1.4, 1.4, 0.8])
        with sc1:
            soc_topic = st.text_input(
                "Social topic", label_visibility="collapsed",
                placeholder="🔍  Topic — e.g. AI tools, sustainable fashion, crypto...",
                key="soc_topic_input",
            )
        with sc2:
            soc_target_platform = st.selectbox(
                "Script platform", list(PLATFORM_ANGLES.keys()),
                label_visibility="collapsed", key="soc_tgt_platform",
                help="Which platform will your scripts be for?",
            )
        with sc3:
            all_soc_platforms = list(SOC_COLORS.keys())
            soc_platforms = st.multiselect(
                "Scrape from", all_soc_platforms,
                default=["Reddit","YouTube","Twitter/X","Google Trends"],
                label_visibility="collapsed", key="soc_platforms_sel",
                placeholder="Choose platforms...",
            )
        with sc4:
            soc_search_btn = st.button("📡 Scrape", use_container_width=True, key="soc_search_btn")

        if soc_search_btn and soc_topic.strip():
            st.session_state["soc_selected_id"]   = None
            st.session_state["soc_selected_post"] = None
            st.session_state["soc_show_panel"]    = False
            st.session_state["soc_script"]        = ""

            plats = soc_platforms or ["Reddit","YouTube","Twitter/X","Google Trends"]
            _p3   = st.progress(0)
            _s3   = st.empty()

            _s3.markdown(f'<div class="info-box">📡 Scraping <strong>{", ".join(plats)}</strong> for "<strong>{soc_topic}</strong>"...</div>', unsafe_allow_html=True)
            _p3.progress(10)

            raw_posts = fetch_social_trends(
                soc_topic.strip(),
                platforms        = plats,
                rapidapi_key     = _rapidapi_key,
                youtube_api_key  = _yt_key,
                max_per_platform = 10,
                ig_username      = st.session_state.get("soc_ig_user",""),
                ig_password      = st.session_state.get("soc_ig_pass",""),
                ig_sessionid     = st.session_state.get("soc_ig_session",""),
                fb_cookies       = st.session_state.get("soc_fb_cookies",{}),
            )
            _p3.progress(65)

            enrich_msg = "🧠 AI-enriching posts"
            if brand_ctx_mkt:
                enrich_msg += " + scoring brand fit"
            _s3.markdown(f'<div class="info-box">{enrich_msg}...</div>', unsafe_allow_html=True)

            enriched_posts = enrich_social_posts(
                client, raw_posts, soc_topic.strip(),
                soc_target_platform, brand_context=brand_ctx_mkt,
            )
            _p3.progress(100); _s3.empty(); _p3.empty()

            st.session_state["soc_posts"]    = enriched_posts
            st.session_state["soc_topic"]    = soc_topic.strip()
            st.session_state["soc_platform"] = soc_target_platform

        elif soc_search_btn:
            st.warning("Enter a topic first.")

        # ── Posts grid ────────────────────────────────────────────────────────
        soc_posts = st.session_state["soc_posts"]

        if not soc_posts:
            st.markdown("""
<div style="text-align:center;padding:80px 20px">
  <div style="font-size:3.5rem;margin-bottom:12px">📱</div>
  <p style="color:#3a3a5a;font-size:1.05rem;margin:0">Enter a topic and hit <strong style="color:#7c3aed">Scrape</strong></p>
  <p style="color:#252535;font-size:0.85rem;margin-top:8px">Scrapes Reddit, YouTube, TikTok, Instagram, Twitter/X, and Google Trends simultaneously</p>
</div>""", unsafe_allow_html=True)
        else:
            soc_topic_shown = st.session_state["soc_topic"]
            sc_scores  = [p.get("content_score",0) for p in soc_posts]
            sc_bscores = [p.get("brand_relevance",0) for p in soc_posts]
            sc_hot     = sum(1 for s in sc_scores if s >= 75)
            sc_brand   = sum(1 for b in sc_bscores if b >= 60)
            plat_counts = {}
            for p in soc_posts:
                plat_counts[p["platform"]] = plat_counts.get(p["platform"],0) + 1

            # Stats
            st.markdown("")
            _cols = st.columns(5 + (1 if has_brand else 0))
            _cols[0].markdown(f'<div class="score-card"><div class="score-number" style="font-size:1.3rem">{len(soc_posts)}</div><div class="score-label">Posts Found</div></div>', unsafe_allow_html=True)
            _cols[1].markdown(f'<div class="score-card"><div class="score-number" style="font-size:1.3rem;color:#ef4444">{sc_hot}</div><div class="score-label">🔥 Hot</div></div>', unsafe_allow_html=True)
            _cols[2].markdown(f'<div class="score-card"><div class="score-number" style="font-size:1.3rem">{max(sc_scores) if sc_scores else 0}</div><div class="score-label">Top Score</div></div>', unsafe_allow_html=True)
            _cols[3].markdown(f'<div class="score-card"><div class="score-number" style="font-size:1.3rem">{len(plat_counts)}</div><div class="score-label">Platforms</div></div>', unsafe_allow_html=True)
            _cols[4].markdown(
                '<div class="score-card">' +
                "".join(f'<span style="color:{SOC_COLORS.get(pl,"#6b6b8a")};font-size:0.65rem;display:block">{pl[:4]}: {n}</span>'
                        for pl, n in plat_counts.items()) +
                '</div>', unsafe_allow_html=True)
            if has_brand:
                _cols[5].markdown(f'<div class="score-card"><div class="score-number" style="font-size:1.3rem;color:#7c3aed">{sc_brand}</div><div class="score-label">🏷️ Brand Fit</div></div>', unsafe_allow_html=True)
            st.markdown("")

            # Filters
            sf1, sf2, sf3, sf4, sf5 = st.columns([1.8, 1.8, 1.8, 1.8, 1.5])
            with sf1:
                soc_plat_filter = st.selectbox("Platform", ["All"] + list(plat_counts.keys()), key="soc_pf", label_visibility="collapsed")
            with sf2:
                soc_emos = list(dict.fromkeys(p["emotion"] for p in soc_posts if p.get("emotion")))
                soc_emo_filter = st.selectbox("Emotion", ["All"]+soc_emos, key="soc_ef", label_visibility="collapsed")
            with sf3:
                soc_fmts = list(dict.fromkeys(p["format_fit"] for p in soc_posts if p.get("format_fit")))
                soc_fmt_filter = st.selectbox("Format", ["All"]+soc_fmts, key="soc_ff", label_visibility="collapsed")
            with sf4:
                soc_sort = st.selectbox("Sort", ["Score ↓","Brand Fit ↓","Engagement ↓","Newest"] if has_brand else ["Score ↓","Engagement ↓","Newest"],
                                        key="soc_sf", label_visibility="collapsed")
            with sf5:
                soc_viral_only = st.checkbox("🔥 Viral only", key="soc_vo")

            soc_shown = [p for p in soc_posts
                         if (soc_plat_filter == "All"  or p["platform"]       == soc_plat_filter)
                         and (soc_emo_filter == "All"  or p.get("emotion","") == soc_emo_filter)
                         and (soc_fmt_filter == "All"  or p.get("format_fit","") == soc_fmt_filter)
                         and (not soc_viral_only or p.get("is_viral") or p.get("content_score",0) >= 70)]

            if soc_sort == "Brand Fit ↓":
                soc_shown = sorted(soc_shown, key=lambda x: x.get("brand_relevance",0), reverse=True)
            elif soc_sort == "Engagement ↓":
                soc_shown = sorted(soc_shown, key=lambda x: x.get("likes",0)+x.get("comments",0), reverse=True)
            elif soc_sort == "Newest":
                soc_shown = sorted(soc_shown, key=lambda x: x.get("date",""), reverse=True)

            st.markdown(f'<p style="color:#6b6b8a;font-size:0.8rem;margin-bottom:4px">Showing <strong style="color:#e8e8f0">{len(soc_shown)}</strong> posts for <strong style="color:#7c3aed">{soc_topic_shown}</strong></p>', unsafe_allow_html=True)

            # ── 3-col card grid ───────────────────────────────────────────────
            soc_sel_id = st.session_state["soc_selected_id"]

            for _row in range(0, len(soc_shown), 3):
                _row_posts = soc_shown[_row:_row+3]
                _row_cols  = st.columns(3)

                for _col, post in zip(_row_cols, _row_posts):
                    _pid      = post["id"]
                    _plat     = post["platform"]
                    _pc       = SOC_COLORS.get(_plat, "#6b6b8a")
                    _score    = post.get("content_score", 50)
                    _brel     = post.get("brand_relevance", 0)
                    _bangle   = post.get("brand_angle", "")
                    _angle    = post.get("content_angle", "")
                    _hook     = post.get("hook_idea", "")
                    _emo      = post.get("emotion", "")
                    _ec       = EMOTION_COLORS_SOC.get(_emo, "#6b6b8a")
                    _tags     = post.get("tags", [])[:3]
                    _likes    = post.get("likes_fmt", "")
                    _views    = post.get("views_fmt", "")
                    _author   = post.get("author", "")[:25]
                    _url      = post.get("url", "")
                    _tago     = post.get("time_ago", "")
                    _title    = post.get("title", "")[:105]
                    _body     = post.get("body", "")[:170]
                    _is_sel   = (_pid == soc_sel_id)
                    _is_viral = post.get("is_viral", False)

                    # pre-compute badge text/colours — no conditionals inside HTML string
                    if _score >= 80:   _sb, _sbc = "🔥 Hot",    "#ef4444"
                    elif _score >= 65: _sb, _sbc = "⚡ Strong", "#f59e0b"
                    elif _score >= 50: _sb, _sbc = "💡 Good",   "#06b6d4"
                    else:              _sb, _sbc = "📌 Low",    "#6b6b8a"

                    _card_bg     = "#130f20" if _is_sel else "#0d0d1a"
                    _card_border = "2px solid #7c3aed" if _is_sel else "1px solid #1e1e30"

                    # pre-build every HTML fragment individually
                    _viral_html = (
                        '<span style="background:#ef444422;color:#ef4444;'
                        'font-size:0.62rem;padding:2px 7px;border-radius:20px;'
                        'font-weight:700">🔥 VIRAL</span>'
                        if _is_viral else ""
                    )
                    _br_badge_html = ""
                    if has_brand:
                        _brc = "#7c3aed" if _brel >= 65 else "#8b5cf6" if _brel >= 40 else "#3a3a4a"
                        _br_badge_html = (
                            f'<span style="background:{_brc}22;color:{_brc};'
                            f'font-size:0.62rem;font-weight:700;padding:3px 8px;'
                            f'border-radius:20px">🏷️ {_brel}</span>'
                        )
                    _tags_html = " ".join(
                        f'<span style="background:#1a1a2e;color:#9090b0;'
                        f'font-size:0.62rem;padding:2px 7px;border-radius:20px">{t}</span>'
                        for t in _tags
                    )
                    _stats_html = ""
                    if _likes: _stats_html += f'<span style="color:#6b6b8a;font-size:0.68rem">♥ {_likes} &nbsp;</span>'
                    if _views: _stats_html += f'<span style="color:#6b6b8a;font-size:0.68rem">👁 {_views}</span>'

                    _emo_html = (
                        f'<span style="background:{_ec}22;color:{_ec};'
                        f'font-size:0.62rem;padding:2px 7px;border-radius:20px">{_emo}</span>'
                        if _emo else ""
                    )
                    _brand_angle_html = ""
                    if has_brand and _bangle and _brel >= 40:
                        _brand_angle_html = (
                            '<div style="background:#100a1f;border-left:2px solid #7c3aed66;'
                            'padding:7px 10px;border-radius:0 8px 8px 0">'
                            '<p style="color:#7c3aed;font-size:0.63rem;font-weight:700;'
                            'text-transform:uppercase;margin:0 0 2px 0">🏷️ Brand Angle</p>'
                            f'<p style="color:#c8c0e8;font-size:0.76rem;margin:0;line-height:1.4">{_bangle}</p>'
                            '</div>'
                        )
                    _angle_html = ""
                    if _angle:
                        _angle_html = (
                            f'<div style="background:#0a0a14;border-left:2px solid {_pc}55;'
                            f'padding:6px 10px;border-radius:0 8px 8px 0">'
                            f'<p style="color:{_pc};font-size:0.63rem;font-weight:700;'
                            f'text-transform:uppercase;margin:0 0 2px 0">📐 Content Angle</p>'
                            f'<p style="color:#d0d0e8;font-size:0.76rem;margin:0">{_angle}</p>'
                            f'</div>'
                        )
                    _hook_html = ""
                    if _hook:
                        _hook_html = (
                            '<div style="background:#0a0a14;border-radius:8px;padding:6px 10px">'
                            '<p style="color:#7c3aed;font-size:0.63rem;font-weight:700;'
                            'text-transform:uppercase;margin:0 0 2px 0">🎣 Hook</p>'
                            f'<p style="color:#c8c8e0;font-size:0.76rem;font-style:italic;margin:0">&quot;{_hook}&quot;</p>'
                            '</div>'
                        )
                    _footer_html = (
                        f'<a href="{_url}" target="_blank" style="color:#5a5a7a;font-size:0.7rem;text-decoration:none">@{_author} ↗</a>'
                        if (_url and _author)
                        else f'<span style="color:#4a4a6a;font-size:0.7rem">{_author}</span>'
                    )

                    # single clean markdown call — no nested f-strings
                    _card_html = (
                        f'<div style="background:{_card_bg};border:{_card_border};'
                        f'border-top:3px solid {_pc};border-radius:14px;padding:16px;'
                        f'margin-bottom:2px;display:flex;flex-direction:column;gap:9px;min-height:300px">'

                        f'<div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:4px">'
                        f'<div style="display:flex;align-items:center;gap:6px">'
                        f'<span style="background:{_pc}22;color:{_pc};font-size:0.62rem;font-weight:700;padding:3px 9px;border-radius:20px">{_plat}</span>'
                        f'{_viral_html}'
                        f'</div>'
                        f'<div style="display:flex;gap:4px;flex-wrap:wrap">'
                        f'<span style="background:{_sbc}22;color:{_sbc};font-size:0.62rem;font-weight:700;padding:3px 9px;border-radius:20px">{_sb} {_score}</span>'
                        f'{_br_badge_html}'
                        f'</div></div>'

                        f'<p style="color:#e8e8f0;font-size:0.88rem;font-weight:600;line-height:1.45;margin:0">{_title}</p>'
                        f'<p style="color:#8080a0;font-size:0.77rem;line-height:1.55;margin:0;flex:1">{_body}</p>'

                        f'{_brand_angle_html}'
                        f'{_angle_html}'
                        f'{_hook_html}'

                        f'<div style="display:flex;flex-wrap:wrap;gap:4px;align-items:center">'
                        f'{_tags_html}{_emo_html}{_stats_html}'
                        f'</div>'

                        f'<div style="display:flex;justify-content:space-between;align-items:center;'
                        f'border-top:1px solid #181828;padding-top:7px;margin-top:auto">'
                        f'{_footer_html}'
                        f'<span style="color:#3a3a5a;font-size:0.67rem">{_tago}</span>'
                        f'</div></div>'
                    )

                    with _col:
                        st.markdown(_card_html, unsafe_allow_html=True)

                        _bc1, _bc2 = _col.columns([3,1])
                        if _bc1.button(
                            "✓ Selected — Make Script" if _is_sel else "✍️ Use This Post",
                            key=f"socsел_{_pid}",
                            use_container_width=True,
                            type="primary" if _is_sel else "secondary",
                        ):
                            st.session_state["soc_selected_id"]   = _pid
                            st.session_state["soc_selected_post"] = post
                            st.session_state["soc_show_panel"]    = True
                            st.session_state["soc_script"]        = ""
                            st.rerun()

                        if _url:
                            _bc2.markdown(
                                f'<a href="{_url}" target="_blank" style="display:block;text-align:center;padding:7px 0;border:1px solid #2a2a3e;border-radius:6px;color:#5a5a7a;font-size:0.75rem;text-decoration:none">↗</a>',
                                unsafe_allow_html=True)

            st.markdown("")

        # ── Script creation panel ─────────────────────────────────────────────
        if st.session_state.get("soc_show_panel") and st.session_state.get("soc_selected_post"):
            _sp   = st.session_state["soc_selected_post"]
            _plat = _sp["platform"]
            _pclr = SOC_COLORS.get(_plat, "#7c3aed")

            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

            st.markdown(f"""
<div style="background:#0f0f1e;border:1px solid {_pclr}44;border-left:4px solid {_pclr};border-radius:12px;padding:16px 20px;margin-bottom:20px;display:flex;gap:16px;flex-wrap:wrap">
  <div style="flex:1;min-width:200px">
    <div style="display:flex;gap:8px;align-items:center;margin-bottom:6px;flex-wrap:wrap">
      <span style="background:{_pclr}22;color:{_pclr};font-size:0.62rem;font-weight:700;padding:3px 9px;border-radius:20px">{_plat}</span>
      <span style="color:#7c3aed;font-size:0.7rem;font-weight:700">SELECTED POST</span>
      {'<span style="color:#ef4444;font-size:0.7rem;font-weight:700">🔥 VIRAL</span>' if _sp.get("is_viral") else ""}
    </div>
    <p style="color:#e8e8f0;font-size:0.95rem;font-weight:600;margin:0 0 4px 0">{_sp.get("title","")[:120]}</p>
    <p style="color:#7c3aed;font-size:0.82rem;margin:0;font-style:italic">{_sp.get("content_angle","")}</p>
  </div>
  <div style="text-align:right">
    <div style="color:#7c3aed;font-family:Syne;font-weight:700;font-size:1.6rem">{_sp.get("content_score",0)}</div>
    <div style="color:#6b6b8a;font-size:0.68rem">Score</div>
    {f'<div style="color:#7c3aed;font-size:0.85rem">🏷️ {_sp.get("brand_relevance",0)}</div>' if has_brand else ""}
  </div>
</div>""", unsafe_allow_html=True)

            st.markdown("## 🎯 Customise Your Script")

            _ql, _qr = st.columns(2)
            with _ql:
                st.markdown("#### 📱 Platform & Format")
                _q_plat = st.selectbox("Platform", list(PLATFORM_ANGLES.keys()), key="sq_plat")
                _q_dur  = st.selectbox("Duration", ["15 sec","30 sec","60 sec","90 sec","3 min","5+ min"], index=2, key="sq_dur")
                _q_fw   = st.selectbox("Framework", list(EMOTIONAL_FRAMEWORKS.keys()), key="sq_fw")
                _q_hook = st.selectbox("Hook Style", list(HOOK_TYPES.keys()), index=1, key="sq_hook")
                st.caption(f"💡 {HOOK_TYPES.get(st.session_state.sq_hook,'')}")
                st.markdown("#### 🎤 Voice")
                _q_tone = st.selectbox("Tone",
                    ["Conversational","Authoritative","Inspirational","Urgent","Humorous","Educational","Empathetic","Bold"],
                    key="sq_tone")
                _q_emo_sel = st.multiselect("Emotions", EQ_EMOTIONS,
                    default=[_sp.get("emotion","Curiosity"),"Inspiration"], key="sq_emo")
            with _qr:
                st.markdown("#### ✨ Style Options")
                _q_humor   = st.radio("😂 Humor?",["No","Light — relatable","Yes — comedic"], key="sq_humor")
                st.markdown("")
                _q_sp2     = st.radio("⭐ Social proof?",["No","Yes — stats/numbers","Yes — testimonial angle"], key="sq_sp2")
                st.markdown("")
                _q_story   = st.radio("🧍 Personal story?",["No","Yes — first-person","Yes — case study"], key="sq_story")
                st.markdown("")
                _q_hot2    = st.radio("🔥 Controversy?",["Low — safe","Medium — hot take","High — challenge norm"], key="sq_hot")
                st.markdown("")
                _q_cta2    = st.selectbox("📣 CTA",["Follow for more","Comment below","Share with a friend","Link in bio","Try it now","Save this","Custom..."], key="sq_cta")
                if st.session_state.sq_cta == "Custom...":
                    _q_cta2 = st.text_input("CTA text", key="sq_cta_custom")

            _q_extra = st.text_area("💬 Extra instructions",
                placeholder="Specific keywords, things to avoid, product to mention...", height=65, key="sq_extra")

            # Brand
            st.markdown("#### 🏷️ Brand")
            _bq1, _bq2 = st.columns(2)
            with _bq1:
                _q_brand2 = st.text_input("Brand name (extra web research)", placeholder="optional...", key="sq_brand")
            with _bq2:
                _q_rag2 = st.checkbox(f"📎 Brand docs (RAG){' — '+str(doc_count)+' docs' if doc_count else ''}", value=has_brand, key="sq_rag", disabled=not has_brand)

            if st.session_state.get("creator_style_prompt"):
                st.markdown(f'<div class="info-box" style="border-color:#8b5cf6">💉 Creator style: {st.session_state.get("creator_style_name","")}</div>', unsafe_allow_html=True)

            st.markdown("")
            _gb1, _gb2 = st.columns([4,1])
            _soc_gen_btn = _gb1.button("⚡ Generate Script", use_container_width=True, type="primary", key="soc_gen_btn")
            if _gb2.button("✕ Deselect", use_container_width=True, key="soc_desel"):
                st.session_state["soc_show_panel"]    = False
                st.session_state["soc_selected_id"]   = None
                st.session_state["soc_selected_post"] = None
                st.rerun()

            if _soc_gen_btn:
                _answers = {
                    "tone": _q_tone, "humor": _q_humor, "social_proof": _q_sp2,
                    "personal_story": _q_story, "controversy": _q_hot2,
                    "cta_type": _q_cta2, "target_emotion": ", ".join(_q_emo_sel),
                    "extra_notes": _q_extra,
                }
                _p4 = st.progress(0); _s4 = st.empty()

                _brand_intel2 = ""
                if _q_brand2.strip():
                    _s4.markdown(f'<div class="info-box">🔍 Researching {_q_brand2}...</div>', unsafe_allow_html=True)
                    _p4.progress(15)
                    _bi2 = research_brand(client, _q_brand2.strip())
                    _brand_intel2 = _bi2.get("injection_block","")

                _rag_ctx2 = brand_ctx_mkt if _q_rag2 else ""
                if _rag_ctx2 and doc_count > 0:
                    _topic_rag2 = query_brand_context(f"{_sp.get('title','')} {_q_tone} {_q_plat}", top_k=4)
                    if _topic_rag2:
                        _rag_ctx2 = _topic_rag2

                # Build brief from post
                _brief2 = build_script_brief(
                    {**_sp, "content_angle": _sp.get("content_angle",""),
                     "hook_idea": _sp.get("hook_idea",""),
                     "brand_angle": _sp.get("brand_angle","")},
                    _answers
                )

                _s4.markdown('<div class="info-box">✍️ Generating...</div>', unsafe_allow_html=True)
                _p4.progress(50)
                _out2 = st.empty(); _fs2 = ""

                _gen2 = generate_script(
                    client, topic=_brief2, platform=_q_plat, duration=_q_dur,
                    tone=_q_tone, hook_type=_q_hook, emotional_framework=_q_fw,
                    target_emotions=_q_emo_sel, conditions=_q_extra,
                    brand_context=_rag_ctx2, brand_intelligence=_brand_intel2,
                    topic_research="", creator_style=st.session_state.get("creator_style_prompt",""),
                    trend_data="",
                )
                for _chunk in _gen2:
                    _fs2 += _chunk
                    _out2.markdown(f'<div class="script-output">{_fs2}▌</div>', unsafe_allow_html=True)

                _p4.progress(100); _s4.empty(); _p4.empty()
                _out2.markdown(f'<div class="script-output">{_fs2}</div>', unsafe_allow_html=True)
                st.session_state["soc_script"]  = _fs2
                st.session_state["last_script"] = _fs2

        # Script actions
        if st.session_state.get("soc_script"):
            _sc2 = st.session_state["soc_script"]
            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
            st.markdown("### 📄 Your Script")
            st.markdown(f'<div class="script-output">{_sc2}</div>', unsafe_allow_html=True)
            _a1, _a2, _a3 = st.columns(3)
            _slug2 = (st.session_state.get("soc_topic","topic")[:20] or "topic").replace(" ","_")
            _a1.download_button("⬇️ Download", _sc2, file_name=f"script_{_slug2}.txt", mime="text/plain", key="soc_dl")
            if _a2.button("💬 Send to Chat", key="soc_to_chat"):
                st.session_state["chat_script_context"] = _sc2
                st.success("Sent to Script Chat!")
            if _a3.button("🔄 Regenerate", key="soc_regen"):
                st.session_state["soc_script"] = ""
                st.rerun()
