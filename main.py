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
        "🎯 Brand Setup": "brand",
        "📝 Script Analyzer": "analyzer",
        "✍️ Script Generator": "generator",
        "🎬 Video Feedback": "video",
        "🔗 URL Analyzer": "url",
        "👤 Creator Analyzer": "creator",
        "💬 Script Chat": "chat",
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
# PAGE: SCRIPT CHAT
# ════════════════════════════════════════════════════════════════════
elif current_page == "chat":
    st.markdown("# 💬 Script Chat")
    st.markdown('<p style="color:#6b6b8a">Chat with AI to customize, improve, or completely reimagine any script. Context-aware and brand-aligned.</p>', unsafe_allow_html=True)
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    from modules.brand_rag import query_brand_context, get_document_count

    # ── Session state init ─────────────────────────────────────────────────────
    if "chat_messages" not in st.session_state:
        st.session_state["chat_messages"] = []

    if "chat_script_context" not in st.session_state:
        st.session_state["chat_script_context"] = ""

    # ── Sidebar-style context panel ────────────────────────────────────────────
    ctx_col, chat_col = st.columns([1, 3])

    with ctx_col:
        st.markdown("### 📎 Script Context")

        # Import from URL Analyzer
        if st.session_state.get("chat_transcript"):
            meta = st.session_state.get("chat_meta", {})
            st.markdown(f'<div class="info-box">🎬 Loaded from URL Analyzer:<br><strong style="color:#e8e8f0">{meta.get("title","Video")[:40]}</strong></div>', unsafe_allow_html=True)
            if st.button("Load This Script"):
                st.session_state["chat_script_context"] = st.session_state["chat_transcript"]
                st.session_state["chat_messages"] = []
                st.rerun()

        # Import from Script Generator
        if st.session_state.get("last_script"):
            st.markdown(f'<div class="info-box" style="margin-top:8px">✍️ Script from Generator available</div>', unsafe_allow_html=True)
            if st.button("Load Generated Script"):
                st.session_state["chat_script_context"] = st.session_state["last_script"]
                st.session_state["chat_messages"] = []
                st.rerun()

        st.markdown("")
        st.markdown("**Or paste a script:**")
        manual_ctx = st.text_area("Script to work with", value=st.session_state.get("chat_script_context",""), height=180, label_visibility="collapsed")
        if st.button("Set as Context"):
            st.session_state["chat_script_context"] = manual_ctx
            st.session_state["chat_messages"] = []
            st.rerun()

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

        use_brand_chat = st.checkbox("🏷️ Include brand context", value=get_document_count() > 0)
        platform_chat = st.selectbox("Platform", ["TikTok", "YouTube Shorts", "Instagram Reels", "YouTube Long-form"])

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

        st.markdown("**💡 Quick Prompts**")
        quick_prompts = [
            "Make the hook more powerful",
            "Shorten to 30 seconds",
            "Make it more emotional",
            "Add a stronger CTA",
            "Change tone to humorous",
            "Add pattern interrupts",
            "Rewrite for my brand",
            "Make it more conversational",
            "Increase urgency",
            "Add social proof",
        ]
        for qp in quick_prompts:
            if st.button(qp, key=f"qp_{qp}"):
                st.session_state["pending_message"] = qp

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        if st.button("🗑️ Clear Chat"):
            st.session_state["chat_messages"] = []
            st.rerun()

    with chat_col:
        # ── Chat history display ───────────────────────────────────────────────
        chat_container = st.container()

        with chat_container:
            if not st.session_state["chat_messages"]:
                ctx_preview = st.session_state.get("chat_script_context","")
                if ctx_preview:
                    st.markdown(f'<div class="section-card"><p style="color:#6b6b8a;font-size:0.75rem;text-transform:uppercase;letter-spacing:0.1em">Active Script Context ({len(ctx_preview.split())} words)</p><p style="color:#9090b0;font-size:0.85rem">{ctx_preview[:300]}{"..." if len(ctx_preview)>300 else ""}</p></div>', unsafe_allow_html=True)
                st.markdown("""
<div class="section-card" style="text-align:center;padding:40px 20px">
<p style="color:#3a3a5a;font-size:2.5rem">💬</p>
<p style="color:#6b6b8a">Start chatting to customize your script.<br>Use Quick Prompts on the left or type your own request.</p>
</div>""", unsafe_allow_html=True)
            else:
                for msg in st.session_state["chat_messages"]:
                    role = msg["role"]
                    content = msg["content"]
                    if role == "user":
                        st.markdown(f"""
<div style="display:flex;justify-content:flex-end;margin:12px 0">
<div style="background:linear-gradient(135deg,#4c1d95,#1e3a5f);border-radius:16px 16px 4px 16px;padding:12px 18px;max-width:75%;color:#e8e8f0;font-size:0.9rem;line-height:1.5">
{content}
</div>
</div>""", unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
<div style="display:flex;justify-content:flex-start;margin:12px 0">
<div style="background:#12121f;border:1px solid #1e1e30;border-radius:16px 16px 16px 4px;padding:12px 18px;max-width:85%;color:#d0d0e8;font-size:0.9rem;line-height:1.6;white-space:pre-wrap">
{content}
</div>
</div>""", unsafe_allow_html=True)

        st.markdown("")

        # ── Chat input ─────────────────────────────────────────────────────────
        user_input = st.chat_input("Ask anything about your script, request changes, or say 'rewrite as 60 seconds'...")

        # Handle quick prompt
        if "pending_message" in st.session_state:
            user_input = st.session_state.pop("pending_message")

        if user_input:
            # Add user message
            st.session_state["chat_messages"].append({"role": "user", "content": user_input})

            # Build system prompt with context
            script_ctx = st.session_state.get("chat_script_context", "")

            brand_ctx = ""
            if use_brand_chat:
                brand_ctx = query_brand_context(user_input, top_k=4)

            system_content = f"""You are an elite script coach and content strategist specializing in viral {platform_chat} content.
You have deep expertise in:
- Emotional intelligence and psychological hooks
- Platform-native content formats
- Script optimization and rewriting
- Viral content patterns and retention strategies

Your responses are:
- Highly specific and actionable
- Formatted clearly (use sections/emojis when rewriting full scripts)
- Psychologically grounded — explain WHY changes work
- Never generic or vague"""

            if script_ctx:
                system_content += f"\n\nACTIVE SCRIPT CONTEXT:\n\"\"\"{script_ctx}\"\"\"\n\nWhen the user asks to modify, rewrite, or improve — work from this script."

            if brand_ctx:
                system_content += f"\n\nBRAND CONTEXT (align all outputs to this):\n{brand_ctx}"

            # Build messages for API
            api_messages = [{"role": "system", "content": system_content}]

            # Include last 10 messages for context window
            history = st.session_state["chat_messages"][-10:]
            for m in history:
                api_messages.append({"role": m["role"], "content": m["content"]})

            # Stream response
            with st.spinner(""):
                response_placeholder = st.empty()
                full_response = ""
                stream = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=api_messages,
                    max_tokens=2000,
                    temperature=0.75,
                    stream=True
                )
                for chunk in stream:
                    delta = chunk.choices[0].delta.content
                    if delta:
                        full_response += delta
                        response_placeholder.markdown(f"""
<div style="display:flex;justify-content:flex-start;margin:12px 0">
<div style="background:#12121f;border:1px solid #7c3aed44;border-radius:16px 16px 16px 4px;padding:12px 18px;max-width:85%;color:#d0d0e8;font-size:0.9rem;line-height:1.6;white-space:pre-wrap">
{full_response}▌
</div>
</div>""", unsafe_allow_html=True)

                response_placeholder.empty()

            # Save response
            st.session_state["chat_messages"].append({"role": "assistant", "content": full_response})

            # Update script context if it's a full rewrite
            rewrite_signals = ["rewrite", "here's your", "here is your", "━━━", "🎣 hook", "script:"]
            if any(sig.lower() in full_response.lower() for sig in rewrite_signals):
                st.session_state["chat_script_context"] = full_response
                st.session_state["last_script"] = full_response

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
