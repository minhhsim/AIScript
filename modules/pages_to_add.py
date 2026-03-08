# ═══════════════════════════════════════════════════════════════════════════════
# STEP 1: In main.py, find the pages dict (around line 273) and REPLACE it with:
# ═══════════════════════════════════════════════════════════════════════════════

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


# ═══════════════════════════════════════════════════════════════════════════════
# STEP 2: Paste everything below at the END of main.py
# ═══════════════════════════════════════════════════════════════════════════════


# ════════════════════════════════════════════════════════════════════
# PAGE: URL ANALYZER
# ════════════════════════════════════════════════════════════════════
elif current_page == "url":
    st.markdown("# 🔗 URL Video Analyzer")
    st.markdown('<p style="color:#6b6b8a">Analyze any YouTube or TikTok video by URL — transcript, script intelligence map, visual storyboard, and social trend data.</p>', unsafe_allow_html=True)
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    from modules.url_analyzer import analyze_url, build_analysis_graph, generate_visual_direction
    from modules.script_analyzer import analyze_script
    from modules.social_scraper import scrape_social_trends, format_trends_for_display
    try:
        from apikeys import rapidapi_key
    except Exception:
        rapidapi_key = ""

    # ── Input row ─────────────────────────────────────────────────────────────
    col_url, col_plat = st.columns([3, 1])
    with col_url:
        video_url = st.text_input("Video URL",
            placeholder="https://www.youtube.com/watch?v=... or https://www.tiktok.com/@user/video/...",
            label_visibility="collapsed")
    with col_plat:
        platform_url = st.selectbox("Platform", ["TikTok", "YouTube Shorts", "YouTube Long-form", "Instagram Reels"])

    col_b1, col_b2, col_b3 = st.columns([2, 2, 3])
    with col_b1:
        fetch_btn = st.button("⚡ Analyze Video")
    with col_b2:
        trend_topic = st.text_input("Trend topic", placeholder="e.g. fitness", label_visibility="collapsed")
    with col_b3:
        scrape_platforms = st.multiselect("Scrape platforms", ["TikTok", "Instagram"], default=["TikTok"])

    scrape_btn = st.button("🔥 Scrape Social Trends")

    # ── SOCIAL TREND SCRAPER ──────────────────────────────────────────────────
    if scrape_btn and trend_topic.strip():
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        st.markdown("### 🔥 Live Social Trends")

        with st.spinner(f"Scraping {', '.join(scrape_platforms)} for '{trend_topic}'..."):
            trends = scrape_social_trends(
                trend_topic, scrape_platforms, rapidapi_key, count=12
            )

        cards = format_trends_for_display(trends)

        if cards:
            # Stats row
            tiktok_count = sum(1 for c in cards if c["platform"] == "TikTok")
            ig_count = sum(1 for c in cards if c["platform"] == "Instagram")
            total_likes = sum(c.get("likes", 0) for c in cards)
            total_views = sum(c.get("views", 0) for c in cards)

            s1, s2, s3, s4 = st.columns(4)
            s1.markdown(f'<div class="score-card"><div class="score-number" style="font-size:1.6rem">{tiktok_count}</div><div class="score-label">TikTok Results</div></div>', unsafe_allow_html=True)
            s2.markdown(f'<div class="score-card"><div class="score-number" style="font-size:1.6rem">{ig_count}</div><div class="score-label">Instagram Results</div></div>', unsafe_allow_html=True)
            s3.markdown(f'<div class="score-card"><div class="score-number" style="font-size:1.3rem">{total_likes/1000:.0f}K</div><div class="score-label">Total Likes</div></div>', unsafe_allow_html=True)
            s4.markdown(f'<div class="score-card"><div class="score-number" style="font-size:1.3rem">{total_views/1000:.0f}K</div><div class="score-label">Total Views</div></div>', unsafe_allow_html=True)

            st.markdown("")

            # Trend cards grid
            cols = st.columns(2)
            for i, card in enumerate(cards[:12]):
                platform_color = "#1d9bf0" if card["platform"] == "TikTok" else "#e1306c"
                platform_icon  = "🎵" if card["platform"] == "TikTok" else "📸"
                type_badge     = card.get("type", "post")
                desc           = card.get("description", "")[:140]
                likes          = card.get("likes", 0)
                views          = card.get("views", 0)
                comments       = card.get("comments", 0)

                stats_html = ""
                if likes:    stats_html += f'<span style="margin-right:12px">❤️ {likes:,}</span>'
                if views:    stats_html += f'<span style="margin-right:12px">👁️ {views:,}</span>'
                if comments: stats_html += f'<span>💬 {comments:,}</span>'

                url_link = f'<a href="{card["url"]}" target="_blank" style="color:#7c3aed;font-size:0.75rem">View post ↗</a>' if card.get("url") else ""

                cols[i % 2].markdown(f"""
<div class="section-card" style="margin-bottom:12px;border-left:3px solid {platform_color}">
  <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px">
    <span style="font-size:1rem">{platform_icon}</span>
    <span style="color:{platform_color};font-size:0.7rem;text-transform:uppercase;font-weight:700;letter-spacing:0.08em">{card["platform"]}</span>
    <span class="tag" style="font-size:0.65rem">{type_badge}</span>
    {url_link}
  </div>
  <p style="color:#d0d0e8;font-size:0.85rem;line-height:1.5;margin:0 0 8px 0">{desc}</p>
  <div style="color:#6b6b8a;font-size:0.8rem">{stats_html}</div>
</div>""", unsafe_allow_html=True)

            # Save summary for script generation
            st.session_state["trend_summary"] = trends.get("summary", "")
            st.markdown('<div class="info-box" style="margin-top:12px">✅ Trend data saved — go to Script Generator to use it in your script.</div>', unsafe_allow_html=True)

        else:
            st.warning("No trend data found. Try a different topic or check your RapidAPI key.")

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # ── VIDEO URL ANALYSIS ────────────────────────────────────────────────────
    if fetch_btn and video_url.strip():

        progress = st.progress(0)
        status   = st.empty()
        status.markdown('<div class="info-box">📡 Fetching video metadata...</div>', unsafe_allow_html=True)
        progress.progress(15)

        url_data = analyze_url(client, video_url.strip())

        if url_data.get("error"):
            st.error(f"❌ {url_data['error']}")
            st.markdown('<div class="warn-box">Make sure yt-dlp is installed: <code>pip install yt-dlp</code></div>', unsafe_allow_html=True)
        else:
            meta          = url_data.get("metadata", {})
            transcription = url_data.get("transcription", "")

            status.markdown('<div class="info-box">🧠 Running script intelligence analysis...</div>', unsafe_allow_html=True)
            progress.progress(50)

            analysis   = analyze_script(client, transcription, platform_url)
            graph_data = build_analysis_graph(analysis, meta)

            status.markdown('<div class="info-box">🎬 Generating visual storyboard...</div>', unsafe_allow_html=True)
            progress.progress(75)

            shots = generate_visual_direction(client, transcription, platform_url)
            progress.progress(100)
            status.empty()

            # ── Metadata banner ───────────────────────────────────────────────
            m1, m2, m3, m4, m5 = st.columns(5)
            m1.markdown(f'<div class="score-card"><div class="score-number">{analysis.get("overview",{}).get("overall_score","—")}</div><div class="score-label">Score</div></div>', unsafe_allow_html=True)
            m2.markdown(f'<div class="score-card"><div class="score-number" style="font-size:1rem">{meta.get("uploader","—")[:15]}</div><div class="score-label">Creator</div></div>', unsafe_allow_html=True)
            dur = meta.get("duration", 0)
            m3.markdown(f'<div class="score-card"><div class="score-number" style="font-size:1.3rem">{dur//60}m {dur%60}s</div><div class="score-label">Duration</div></div>', unsafe_allow_html=True)
            views = meta.get("view_count", 0)
            views_str = f"{views/1000000:.1f}M" if views >= 1000000 else f"{views/1000:.0f}K" if views >= 1000 else str(views)
            m4.markdown(f'<div class="score-card"><div class="score-number" style="font-size:1.3rem">{views_str}</div><div class="score-label">Views</div></div>', unsafe_allow_html=True)
            m5.markdown(f'<div class="score-card"><div class="score-number" style="font-size:1rem">{analysis.get("retention_prediction",{}).get("virality_potential","—")}</div><div class="score-label">Viral Potential</div></div>', unsafe_allow_html=True)

            st.markdown(f'<div class="section-card"><span style="color:#6b6b8a;font-size:0.75rem;text-transform:uppercase">Title</span><br><strong style="color:#e8e8f0">{meta.get("title","—")}</strong></div>', unsafe_allow_html=True)
            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

            # ── Main tabs ─────────────────────────────────────────────────────
            tab_map, tab_story, tab_hook, tab_transcript, tab_actions = st.tabs([
                "🕸️ Intelligence Map",
                "🎬 Visual Storyboard",
                "🎣 Hook & Emotion",
                "📜 Transcript",
                "💡 Action Plan"
            ])

            # ── TAB: INTELLIGENCE MAP ─────────────────────────────────────────
            with tab_map:
                st.markdown('<p style="color:#6b6b8a;font-size:0.85rem">Hover nodes for details. Scroll to zoom. Drag to pan.</p>', unsafe_allow_html=True)

                nodes    = graph_data["nodes"]
                edges    = graph_data["edges"]
                node_map = {n["id"]: n for n in nodes}

                fig = go.Figure()

                for edge in edges:
                    src = node_map.get(edge["from"])
                    dst = node_map.get(edge["to"])
                    if not src or not dst:
                        continue
                    fig.add_trace(go.Scatter(
                        x=[src["x"], dst["x"], None], y=[src["y"], dst["y"], None],
                        mode="lines",
                        line=dict(width=max(0.5, edge.get("weight", 0.5) * 3.5), color=edge.get("color", "#2a2a40")),
                        hoverinfo="skip", showlegend=False
                    ))

                group_order = ["journey", "platform", "strength", "weakness", "hook", "emotion", "structure", "tone", "retention", "center"]
                rendered = set()
                for group in group_order:
                    gnodes = [n for n in nodes if n.get("group") == group and n["id"] not in rendered]
                    if not gnodes:
                        continue
                    hover_texts = [f"<b>{n['label'].replace(chr(10),' · ')}</b><br>{n.get('detail','')}" for n in gnodes]
                    fig.add_trace(go.Scatter(
                        x=[n["x"] for n in gnodes], y=[n["y"] for n in gnodes],
                        mode="markers+text",
                        marker=dict(size=[n["size"] for n in gnodes], color=[n["color"] for n in gnodes],
                                    line=dict(color="#ffffff22", width=1), opacity=0.92),
                        text=[n["label"].split("\n")[0] for n in gnodes],
                        textposition="middle center",
                        textfont=dict(color=[n.get("text_color","#fff") for n in gnodes],
                                      size=[max(7, min(10, n["size"]*0.28)) for n in gnodes], family="DM Sans"),
                        hovertext=hover_texts,
                        hovertemplate="%{hovertext}<extra></extra>",
                        hoverlabel=dict(bgcolor="#1a1a2e", bordercolor="#7c3aed",
                                        font=dict(color="#e8e8f0", size=12, family="DM Sans")),
                        showlegend=False
                    ))
                    for n in gnodes:
                        rendered.add(n["id"])

                fig.update_layout(
                    paper_bgcolor="#0a0a0f", plot_bgcolor="#0a0a0f",
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-7, 7]),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-7, 7]),
                    margin=dict(l=0, r=0, t=0, b=0), height=560,
                    dragmode="pan", hoverdistance=20
                )
                st.plotly_chart(fig, use_container_width=True, config={"scrollZoom": True, "displayModeBar": False})

                # Legend
                legend_items = [("#7c3aed","Core"),("#06b6d4","Hook"),("#10b981","Emotion"),("#f59e0b","Structure"),
                                ("#ec4899","Tone"),("#8b5cf6","Retention"),("#1e3a5f","Journey"),("#374151","Platform")]
                leg = '<div style="display:flex;flex-wrap:wrap;gap:10px">'
                for color, label in legend_items:
                    leg += f'<span style="display:flex;align-items:center;gap:5px"><span style="width:9px;height:9px;border-radius:50%;background:{color};display:inline-block"></span><span style="color:#6b6b8a;font-size:0.75rem">{label}</span></span>'
                st.markdown(leg + '</div>', unsafe_allow_html=True)

            # ── TAB: VISUAL STORYBOARD ────────────────────────────────────────
            with tab_story:
                if shots:
                    st.markdown("### 🎬 Shot-by-Shot Visual Direction")
                    st.markdown('<p style="color:#6b6b8a;font-size:0.85rem">AI-generated cinematography guide for recreating or improving this video.</p>', unsafe_allow_html=True)

                    for i, shot in enumerate(shots):
                        mood_color = shot.get("color_mood", "#7c3aed")
                        icon       = shot.get("icon", "🎥")
                        shot_num   = shot.get("shot_number", i+1)

                        # Shot card
                        st.markdown(f"""
<div style="background:#0f0f1a;border:1px solid #1e1e30;border-left:4px solid {mood_color};border-radius:12px;padding:20px;margin-bottom:16px;position:relative;overflow:hidden">
  <div style="position:absolute;top:0;right:0;width:120px;height:120px;background:radial-gradient(circle at 100% 0%, {mood_color}22, transparent 70%);pointer-events:none"></div>
  <div style="display:flex;align-items:center;gap:12px;margin-bottom:14px">
    <div style="background:{mood_color}22;border:1px solid {mood_color}44;border-radius:50%;width:40px;height:40px;display:flex;align-items:center;justify-content:center;font-size:1.2rem;flex-shrink:0">{icon}</div>
    <div>
      <span style="color:{mood_color};font-family:Syne;font-weight:700;font-size:0.9rem">SHOT {shot_num}</span>
      <span style="color:#6b6b8a;font-size:0.8rem;margin-left:10px">{shot.get("timestamp","")}</span>
    </div>
    <div style="margin-left:auto;display:flex;gap:6px;flex-wrap:wrap">
      <span class="tag" style="border-color:{mood_color}44;color:{mood_color}">{shot.get("shot_type","")}</span>
      <span class="tag">{shot.get("camera_angle","")}</span>
      <span class="tag">{shot.get("camera_movement","")}</span>
    </div>
  </div>

  <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:12px">
    <div>
      <p style="color:#6b6b8a;font-size:0.7rem;text-transform:uppercase;letter-spacing:0.08em;margin:0 0 4px 0">Subject</p>
      <p style="color:#d0d0e8;font-size:0.9rem;margin:0">{shot.get("subject","—")}</p>
    </div>
    <div>
      <p style="color:#6b6b8a;font-size:0.7rem;text-transform:uppercase;letter-spacing:0.08em;margin:0 0 4px 0">Action</p>
      <p style="color:#d0d0e8;font-size:0.9rem;margin:0">{shot.get("action","—")}</p>
    </div>
    <div>
      <p style="color:#6b6b8a;font-size:0.7rem;text-transform:uppercase;letter-spacing:0.08em;margin:0 0 4px 0">Lighting</p>
      <p style="color:#d0d0e8;font-size:0.9rem;margin:0">{shot.get("lighting","—")}</p>
    </div>
    <div>
      <p style="color:#6b6b8a;font-size:0.7rem;text-transform:uppercase;letter-spacing:0.08em;margin:0 0 4px 0">Emotion Target</p>
      <p style="color:{mood_color};font-size:0.9rem;margin:0;font-weight:600">{shot.get("emotion_target","—")}</p>
    </div>
  </div>

  <div style="background:#0a0a14;border-radius:8px;padding:10px 14px;margin-bottom:10px;border-left:2px solid {mood_color}66">
    <p style="color:#6b6b8a;font-size:0.7rem;text-transform:uppercase;letter-spacing:0.08em;margin:0 0 4px 0">Script Line</p>
    <p style="color:#e8e8f0;font-style:italic;font-size:0.9rem;margin:0">"{shot.get("script_line","—")}"</p>
  </div>

  <div style="background:{mood_color}11;border-radius:8px;padding:10px 14px;border:1px solid {mood_color}22">
    <p style="color:#6b6b8a;font-size:0.7rem;text-transform:uppercase;letter-spacing:0.08em;margin:0 0 4px 0">🎯 Director Note</p>
    <p style="color:{mood_color};font-size:0.85rem;margin:0">{shot.get("director_note","—")}</p>
  </div>
</div>""", unsafe_allow_html=True)

                    # Download storyboard as text
                    storyboard_text = "\n\n".join([
                        f"SHOT {s.get('shot_number',i+1)} [{s.get('timestamp','')}]\n"
                        f"Type: {s.get('shot_type','')} | Angle: {s.get('camera_angle','')} | Movement: {s.get('camera_movement','')}\n"
                        f"Subject: {s.get('subject','')}\nAction: {s.get('action','')}\n"
                        f"Lighting: {s.get('lighting','')} | Emotion: {s.get('emotion_target','')}\n"
                        f'Script: "{s.get("script_line","")}"\n'
                        f"Director Note: {s.get('director_note','')}"
                        for i, s in enumerate(shots)
                    ])
                    st.download_button("⬇️ Download Storyboard", storyboard_text,
                                       file_name="storyboard.txt", mime="text/plain")
                else:
                    st.info("Generate an analysis first to see the visual storyboard.")

            # ── TAB: HOOK & EMOTION ────────────────────────────────────────────
            with tab_hook:
                hook    = analysis.get("hook", {})
                emotion = analysis.get("emotional_arc", {})
                h1c, h2c = st.columns(2)
                with h1c:
                    st.markdown(f"""
<div class="section-card">
<p style="color:#06b6d4;font-size:0.75rem;text-transform:uppercase">Hook Analysis</p>
<p style="color:#e8e8f0;font-style:italic">"{hook.get('text','—')}"</p>
<div style="margin-top:8px"><span class="tag">{hook.get('type','—')}</span> <span class="tag">{hook.get('psychological_trigger','—')}</span></div>
<p style="color:#9090b0;font-size:0.85rem;margin-top:8px">{hook.get('feedback','—')}</p>
</div>""", unsafe_allow_html=True)
                with h2c:
                    st.markdown(f"""
<div class="section-card">
<p style="color:#10b981;font-size:0.75rem;text-transform:uppercase">Emotional Intelligence</p>
<p><span class="tag">Dominant: {emotion.get('dominant_emotion','—')}</span></p>
<p><span class="tag">EQ: {emotion.get('emotional_intelligence_rating','—')}</span></p>
<p style="color:#9090b0;font-size:0.85rem;margin-top:8px">{emotion.get('feedback','—')}</p>
</div>""", unsafe_allow_html=True)

                journey = emotion.get("journey", [])
                if journey:
                    arc_fig = go.Figure()
                    arc_fig.add_trace(go.Scatter(
                        x=[j.get("timestamp","") for j in journey],
                        y=[j.get("intensity",50) for j in journey],
                        mode="lines+markers",
                        line=dict(color="#10b981", width=3, shape="spline"),
                        marker=dict(size=10, color="#06b6d4"),
                        text=[j.get("emotion","") for j in journey],
                        hovertemplate="<b>%{x}</b><br>%{text}<br>%{y}%<extra></extra>",
                        fill="tozeroy", fillcolor="rgba(16,185,129,0.08)"
                    ))
                    arc_fig.update_layout(paper_bgcolor="#0a0a0f", plot_bgcolor="#12121f",
                        font=dict(color="#9090b0", family="DM Sans"),
                        xaxis=dict(gridcolor="#1e1e30"), yaxis=dict(range=[0,100], gridcolor="#1e1e30"),
                        margin=dict(l=10,r=10,t=10,b=10), height=200)
                    st.plotly_chart(arc_fig, use_container_width=True)

                if hook.get("improved_version"):
                    st.markdown(f'<div class="info-box">✨ <strong>Improved Hook:</strong> {hook["improved_version"]}</div>', unsafe_allow_html=True)

            # ── TAB: TRANSCRIPT ────────────────────────────────────────────────
            with tab_transcript:
                if transcription:
                    st.markdown(f'<div class="script-output">{transcription}</div>', unsafe_allow_html=True)
                    st.download_button("⬇️ Download Transcript", transcription,
                                       file_name="transcript.txt", mime="text/plain")
                    st.session_state["chat_transcript"] = transcription
                    st.session_state["chat_meta"]       = meta
                    st.markdown('<div class="info-box">💬 Go to Script Chat to customize this script with AI.</div>', unsafe_allow_html=True)

            # ── TAB: ACTION PLAN ───────────────────────────────────────────────
            with tab_actions:
                for item in analysis.get("actionable_improvements", []):
                    pri   = item.get("priority","Low")
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

    if "chat_messages"       not in st.session_state: st.session_state["chat_messages"]       = []
    if "chat_script_context" not in st.session_state: st.session_state["chat_script_context"] = ""

    ctx_col, chat_col = st.columns([1, 3])

    with ctx_col:
        st.markdown("### 📎 Script Context")

        if st.session_state.get("chat_transcript"):
            meta = st.session_state.get("chat_meta", {})
            st.markdown(f'<div class="info-box">🎬 From URL Analyzer:<br><strong style="color:#e8e8f0">{meta.get("title","Video")[:35]}</strong></div>', unsafe_allow_html=True)
            if st.button("Load This Script", key="load_url"):
                st.session_state["chat_script_context"] = st.session_state["chat_transcript"]
                st.session_state["chat_messages"] = []
                st.rerun()

        if st.session_state.get("last_script"):
            st.markdown('<div class="info-box" style="margin-top:8px">✍️ Generated script available</div>', unsafe_allow_html=True)
            if st.button("Load Generated Script", key="load_gen"):
                st.session_state["chat_script_context"] = st.session_state["last_script"]
                st.session_state["chat_messages"] = []
                st.rerun()

        st.markdown("")
        st.markdown("**Or paste a script:**")
        manual_ctx = st.text_area("Script", value=st.session_state.get("chat_script_context",""),
                                   height=160, label_visibility="collapsed")
        if st.button("Set as Context"):
            st.session_state["chat_script_context"] = manual_ctx
            st.session_state["chat_messages"] = []
            st.rerun()

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        use_brand_chat = st.checkbox("🏷️ Brand context", value=get_document_count() > 0)
        platform_chat  = st.selectbox("Platform", ["TikTok","YouTube Shorts","Instagram Reels","YouTube Long-form"])

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
            "More conversational",
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
        chat_container = st.container()

        with chat_container:
            if not st.session_state["chat_messages"]:
                ctx_preview = st.session_state.get("chat_script_context","")
                if ctx_preview:
                    st.markdown(f'<div class="section-card"><p style="color:#6b6b8a;font-size:0.75rem;text-transform:uppercase">Active Script ({len(ctx_preview.split())} words)</p><p style="color:#9090b0;font-size:0.85rem">{ctx_preview[:300]}{"..." if len(ctx_preview)>300 else ""}</p></div>', unsafe_allow_html=True)
                st.markdown("""
<div class="section-card" style="text-align:center;padding:40px 20px">
<p style="color:#3a3a5a;font-size:2.5rem">💬</p>
<p style="color:#6b6b8a">Use Quick Prompts on the left or type your own request.</p>
</div>""", unsafe_allow_html=True)
            else:
                for msg in st.session_state["chat_messages"]:
                    if msg["role"] == "user":
                        st.markdown(f'<div style="display:flex;justify-content:flex-end;margin:10px 0"><div style="background:linear-gradient(135deg,#4c1d95,#1e3a5f);border-radius:16px 16px 4px 16px;padding:12px 18px;max-width:75%;color:#e8e8f0;font-size:0.9rem;line-height:1.5">{msg["content"]}</div></div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div style="display:flex;justify-content:flex-start;margin:10px 0"><div style="background:#12121f;border:1px solid #1e1e30;border-radius:16px 16px 16px 4px;padding:12px 18px;max-width:85%;color:#d0d0e8;font-size:0.9rem;line-height:1.6;white-space:pre-wrap">{msg["content"]}</div></div>', unsafe_allow_html=True)

        st.markdown("")

        user_input = st.chat_input("Ask anything — request changes, rewrites, or say 'make a 60-second version'...")
        if "pending_message" in st.session_state:
            user_input = st.session_state.pop("pending_message")

        if user_input:
            st.session_state["chat_messages"].append({"role": "user", "content": user_input})

            script_ctx = st.session_state.get("chat_script_context","")
            brand_ctx  = query_brand_context(user_input, top_k=4) if use_brand_chat else ""

            system_content = f"""You are an elite script coach and viral content strategist for {platform_chat}.
You have deep expertise in emotional intelligence, psychological hooks, platform-native formats, and script optimization.
Your responses are specific, actionable, and psychologically grounded — always explain WHY changes work."""

            if script_ctx:
                system_content += f'\n\nACTIVE SCRIPT:\n"""{script_ctx}"""\n\nWork from this script when the user asks to modify or improve.'
            if brand_ctx:
                system_content += f"\n\nBRAND CONTEXT:\n{brand_ctx}"

            api_messages = [{"role":"system","content":system_content}]
            for m in st.session_state["chat_messages"][-10:]:
                api_messages.append({"role": m["role"], "content": m["content"]})

            resp_box      = st.empty()
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
                    resp_box.markdown(f'<div style="display:flex;justify-content:flex-start;margin:10px 0"><div style="background:#12121f;border:1px solid #7c3aed44;border-radius:16px 16px 16px 4px;padding:12px 18px;max-width:85%;color:#d0d0e8;font-size:0.9rem;line-height:1.6;white-space:pre-wrap">{full_response}▌</div></div>', unsafe_allow_html=True)
            resp_box.empty()

            st.session_state["chat_messages"].append({"role":"assistant","content":full_response})

            rewrite_signals = ["rewrite","here's your","here is your","━━━","🎣 hook","script:"]
            if any(sig.lower() in full_response.lower() for sig in rewrite_signals):
                st.session_state["chat_script_context"] = full_response
                st.session_state["last_script"]         = full_response

            st.rerun()
