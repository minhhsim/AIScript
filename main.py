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
    st.markdown('<p style="color:#6b6b8a">Analyze any YouTube or TikTok video by URL. Deep script intelligence + interactive visual connection map.</p>', unsafe_allow_html=True)
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    from modules.url_analyzer import analyze_url, build_analysis_graph
    from modules.script_analyzer import analyze_script
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
        progress.progress(15)

        url_data = analyze_url(client, video_url.strip())

        if url_data.get("error"):
            st.error(f"❌ {url_data['error']}")
            st.markdown('<div class="warn-box">Make sure yt-dlp is installed: <code>pip install yt-dlp</code></div>', unsafe_allow_html=True)
        else:
            meta = url_data.get("metadata", {})
            transcription = url_data.get("transcription", "")

            status.markdown('<div class="info-box">🧠 Running script analysis...</div>', unsafe_allow_html=True)
            progress.progress(55)

            analysis = analyze_script(client, transcription, platform_url)

            status.markdown('<div class="info-box">🕸️ Building connection map...</div>', unsafe_allow_html=True)
            progress.progress(85)

            graph_data = build_analysis_graph(analysis, meta)
            progress.progress(100)
            status.empty()

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
            tab1, tab2, tab3, tab4 = st.tabs(["🎣 Hook & Emotion", "🏗️ Structure & Tone", "📜 Transcript", "💡 Action Plan"])

            with tab1:
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

            with tab2:
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

            with tab3:
                if transcription:
                    st.markdown(f'<div class="script-output">{transcription}</div>', unsafe_allow_html=True)
                    st.download_button("⬇️ Download Transcript", transcription, file_name="transcript.txt", mime="text/plain")
                    # Save for chat
                    st.session_state["chat_transcript"] = transcription
                    st.session_state["chat_meta"] = meta
                    st.markdown('<div class="info-box">💬 Go to Script Chat to customize this script with AI.</div>', unsafe_allow_html=True)
                else:
                    st.info("No transcript available.")

            with tab4:
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
