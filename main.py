# main.py — ContentIQ: AI-Powered Content Intelligence Platform
import streamlit as st
import os
import sys
import time
import tempfile

import json
import plotly.graph_objects as go
import plotly.express as px

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

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
        "🎯 Brand Setup": "brand",
        "📝 Script Analyzer": "analyzer",
        "✍️ Script Generator": "generator",
        "🎬 Video Feedback": "video",
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

    from modules.script_analyzer import analyze_script

    col_input, col_settings = st.columns([3, 1])

    with col_input:
        script_input = st.text_area(
            "Script text",
            placeholder="Paste your TikTok or YouTube script here...\n\nTip: Include timestamps if you have them for more precise analysis.",
            height=250,
            label_visibility="collapsed"
        )

    with col_settings:
        platform = st.selectbox("Platform", ["TikTok", "YouTube Shorts", "Instagram Reels", "YouTube Long-form"])
        st.markdown("")
        analyze_btn = st.button("⚡ Analyze Script")

    if analyze_btn and script_input.strip():
        with st.spinner("Running deep analysis..."):
            analysis = analyze_script(client, script_input, platform)

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

    elif analyze_btn:
        st.warning("Please paste a script to analyze.")


# ════════════════════════════════════════════════════════════════════
# PAGE: SCRIPT GENERATOR
# ════════════════════════════════════════════════════════════════════
elif current_page == "generator":
    st.markdown("# ✍️ EQ-Powered Script Generator")
    st.markdown('<p style="color:#6b6b8a">Generate psychologically-optimized scripts powered by your brand DNA and emotional intelligence.</p>', unsafe_allow_html=True)
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    from modules.script_generator import (
        generate_script, generate_script_variations,
        EMOTIONAL_FRAMEWORKS, HOOK_TYPES, EQ_EMOTIONS
    )
    from modules.brand_rag import query_brand_context, get_document_count
    from duckduckgo_search import DDGS

    col_form, col_preview = st.columns([2, 3])

    with col_form:
        st.markdown("### ⚙️ Script Parameters")

        topic = st.text_input("Topic / Product / Message", placeholder="e.g. Productivity app for busy moms")
        platform = st.selectbox("Platform", ["TikTok", "YouTube Shorts", "Instagram Reels", "YouTube Long-form"])
        duration = st.selectbox("Target Duration", ["15 seconds", "30 seconds", "60 seconds", "90 seconds", "3 minutes", "5+ minutes"])
        tone = st.selectbox("Tone", ["Conversational", "Authoritative", "Inspirational", "Urgent", "Humorous", "Educational", "Empathetic", "Bold"])

        st.markdown("#### 🎣 Hook Strategy")
        hook_type = st.selectbox("Hook Type", list(HOOK_TYPES.keys()))
        st.markdown(f'<div class="info-box" style="margin-top:-8px">{HOOK_TYPES[hook_type]}</div>', unsafe_allow_html=True)

        st.markdown("#### 🌊 Emotional Framework")
        framework = st.selectbox("Framework", list(EMOTIONAL_FRAMEWORKS.keys()))
        st.markdown(f'<div class="info-box" style="margin-top:-8px">{EMOTIONAL_FRAMEWORKS[framework]}</div>', unsafe_allow_html=True)

        st.markdown("#### 💭 Target Emotions")
        emotions = st.multiselect("Select 2-4 emotions to trigger", EQ_EMOTIONS, default=["Curiosity", "Inspiration"])

        st.markdown("#### 📋 Additional Conditions")
        conditions = st.text_area("Any specific requirements", placeholder="e.g. No music, mention the 50% discount, end with testimonial", height=80)

        use_trends = st.checkbox("🔥 Pull live trend data", value=True)
        use_brand = st.checkbox("🏷️ Use brand context (RAG)", value=get_document_count() > 0)

        generate_btn = st.button("⚡ Generate Script")

    with col_preview:
        st.markdown("### 📄 Generated Script")

        if generate_btn and topic.strip():
            brand_ctx = ""
            if use_brand:
                with st.spinner("Retrieving brand context..."):
                    brand_ctx = query_brand_context(
                        f"{topic} {tone} {platform} script",
                        top_k=6
                    )
                if brand_ctx:
                    with st.expander("📎 Brand Context Used"):
                        st.text(brand_ctx[:800] + "..." if len(brand_ctx) > 800 else brand_ctx)

            trend_data = ""
            if use_trends:
                with st.spinner("Fetching live trends..."):
                    try:
                        with DDGS() as ddgs:
                            res = list(ddgs.text(f"{topic} {platform} trends 2025", max_results=6))
                            trend_data = "\n".join([r['body'] for r in res if 'body' in r])
                    except Exception:
                        trend_data = ""

            output_box = st.empty()
            full_script = ""

            with st.spinner("Generating your script..."):
                stream = generate_script(
                    client, topic, platform, duration, tone,
                    hook_type, framework, emotions, conditions,
                    brand_ctx, trend_data
                )
                for chunk in stream:
                    delta = chunk.choices[0].delta.content
                    if delta:
                        full_script += delta
                        output_box.markdown(f'<div class="script-output">{full_script}▌</div>', unsafe_allow_html=True)

            output_box.markdown(f'<div class="script-output">{full_script}</div>', unsafe_allow_html=True)
            st.session_state["last_script"] = full_script

            # Download
            st.download_button(
                "⬇️ Download Script",
                full_script,
                file_name=f"script_{topic[:20].replace(' ','_')}.txt",
                mime="text/plain"
            )

        elif "last_script" in st.session_state:
            st.markdown(f'<div class="script-output">{st.session_state["last_script"]}</div>', unsafe_allow_html=True)

            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
            st.markdown("### 🔄 Generate Variation")
            var_type = st.selectbox("Variation type", [
                "More Emotional", "Shorter (30s)", "Different Hook",
                "More Conversational", "Higher Energy"
            ])
            if st.button("Generate Variation"):
                var_box = st.empty()
                var_text = ""
                stream = generate_script_variations(client, st.session_state["last_script"], var_type)
                for chunk in stream:
                    delta = chunk.choices[0].delta.content
                    if delta:
                        var_text += delta
                        var_box.markdown(f'<div class="script-output">{var_text}▌</div>', unsafe_allow_html=True)
                var_box.markdown(f'<div class="script-output">{var_text}</div>', unsafe_allow_html=True)
                st.session_state["last_script"] = var_text

        elif generate_btn:
            st.warning("Please enter a topic.")
        else:
            st.markdown('<div class="section-card" style="text-align:center;padding:60px 20px"><p style="color:#3a3a5a;font-size:2rem">✍️</p><p style="color:#6b6b8a">Configure your script parameters on the left<br>and click Generate Script.</p></div>', unsafe_allow_html=True)


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
        st.markdown('<div class="info-box">Analysis includes:<br>• Audio transcription<br>• Frame-by-frame visual analysis<br>• Script quality scoring<br>• Retention prediction<br>• Improvement roadmap</div>', unsafe_allow_html=True)

    if analyze_video_btn and video_file:
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

        # Save video to temp file
        with tempfile.NamedTemporaryFile(suffix=f".{video_file.name.split('.')[-1]}", delete=False) as tmp:
            tmp.write(video_file.read())
            tmp_path = tmp.name

        steps = st.empty()
        progress_bar = st.progress(0)

        steps.markdown('<div class="info-box">🎵 Step 1/4: Extracting audio and transcribing...</div>', unsafe_allow_html=True)
        progress_bar.progress(10)

        with st.spinner("Running full video analysis pipeline..."):
            steps.markdown('<div class="info-box">🖼️ Step 2/4: Extracting key frames...</div>', unsafe_allow_html=True)
            progress_bar.progress(30)

            results = analyze_video_file(client, tmp_path, platform_v)

            steps.markdown('<div class="info-box">🧠 Step 3/4: Running AI visual analysis...</div>', unsafe_allow_html=True)
            progress_bar.progress(70)

            steps.markdown('<div class="info-box">📊 Step 4/4: Generating report...</div>', unsafe_allow_html=True)
            progress_bar.progress(95)

        progress_bar.progress(100)
        steps.empty()

        # Clean up temp file
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
