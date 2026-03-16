# modules/research_agent.py  — v3  (Groq-primary, APIs optional)
"""
6-Agent Research Pipeline

PRIMARY ENGINE: Groq LLaMA 3.3 70B
  - Generates realistic niche intelligence from training data
  - Knows Reddit communities, YouTube trends, search behavior, viral patterns
  - ALWAYS works — only needs GROQ_KEY

LIVE ENRICHMENT (optional, enhances results):
  - YouTube Data API v3         (real video stats)
  - RapidAPI Google Search      (real-time web results)
  - RapidAPI Reddit scraper     (live Reddit posts)
  - pytrends                    (Google Trends velocity)

Architecture: synchronous functions, progress via callback(pct, message)
"""

import re, json, time, requests
from datetime import datetime, timezone
from typing import Callable

TIMEOUT = 12
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}


# ─────────────────────────────────────────────────────────────────────────────
# Core Groq helpers
# ─────────────────────────────────────────────────────────────────────────────

def _gj(client, system, user, tokens=2500, temp=0.4):
    """Groq → parse JSON."""
    r = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role":"system","content":system},{"role":"user","content":user}],
        max_tokens=tokens, temperature=temp,
    )
    raw = r.choices[0].message.content.strip()
    raw = re.sub(r"^```json\s*","",raw)
    raw = re.sub(r"^```\s*","",raw)
    raw = re.sub(r"\s*```$","",raw)
    raw = raw.strip()
    return json.loads(raw)

def _gt(client, system, user, tokens=1000, temp=0.7):
    """Groq → plain text."""
    r = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role":"system","content":system},{"role":"user","content":user}],
        max_tokens=tokens, temperature=temp,
    )
    return r.choices[0].message.content.strip()

def noop(pct, msg): pass


# ─────────────────────────────────────────────────────────────────────────────
# Optional live data fetchers (silently skip if key missing or request fails)
# ─────────────────────────────────────────────────────────────────────────────

def _live_youtube(query, yt_key, n=8):
    if not yt_key or yt_key in ("","YOUR_YOUTUBE_KEY"):
        return []
    try:
        r = requests.get(
            "https://www.googleapis.com/youtube/v3/search",
            params={"key":yt_key,"q":query,"part":"snippet","type":"video","order":"viewCount","maxResults":n},
            timeout=TIMEOUT,
        )
        if r.status_code != 200: return []
        items = r.json().get("items",[])
        vids  = [i["id"]["videoId"] for i in items if i.get("id",{}).get("videoId")]
        stats = {}
        if vids:
            sr = requests.get(
                "https://www.googleapis.com/youtube/v3/videos",
                params={"key":yt_key,"id":",".join(vids),"part":"statistics"},
                timeout=TIMEOUT,
            )
            for sv in sr.json().get("items",[]):
                stats[sv["id"]] = sv.get("statistics",{})
        out = []
        for item in items:
            vid  = item.get("id",{}).get("videoId","")
            snip = item.get("snippet",{})
            out.append({
                "title":   snip.get("title","")[:120],
                "views":   int(stats.get(vid,{}).get("viewCount",0) or 0),
                "channel": snip.get("channelTitle",""),
                "source":  "youtube_live",
            })
        return out
    except Exception as e:
        print(f"[YT live] {e}")
        return []

def _live_reddit(query, rapidapi_key, n=10):
    """Try public Reddit JSON first, then RapidAPI."""
    out = []
    # Public Reddit
    try:
        url = f"https://www.reddit.com/search.json?q={requests.utils.quote(query)}&sort=hot&limit={n}&t=month"
        r   = requests.get(url, headers={**HEADERS,"Accept":"application/json"}, timeout=TIMEOUT)
        if r.status_code == 200:
            for c in r.json().get("data",{}).get("children",[]):
                d = c.get("data",{})
                if d.get("title"):
                    out.append({"title":d["title"][:120],"score":d.get("score",0),"source":"reddit_live"})
        if out: return out
    except Exception as e:
        print(f"[Reddit public] {e}")

    # RapidAPI fallback
    if rapidapi_key and rapidapi_key not in ("","YOUR_RAPIDAPI_KEY"):
        for host in ["reddit-scraper2.p.rapidapi.com","reddit34.p.rapidapi.com"]:
            try:
                r = requests.get(
                    f"https://{host}/search_posts",
                    headers={"X-RapidAPI-Key":rapidapi_key,"X-RapidAPI-Host":host},
                    params={"query":query,"sort":"hot","limit":str(n)},
                    timeout=TIMEOUT,
                )
                if r.status_code == 200:
                    data  = r.json()
                    posts = data if isinstance(data,list) else data.get("posts",data.get("data",[]))
                    for p in (posts or [])[:n]:
                        t = p.get("title","") or p.get("name","")
                        if t:
                            out.append({"title":t[:120],"score":int(p.get("score",0) or 0),"source":"reddit_api"})
                    if out: return out
            except Exception as e:
                print(f"[Reddit RapidAPI {host}] {e}")
    return out

def _live_trends(query):
    """pytrends rising queries."""
    try:
        from pytrends.request import TrendReq
        pt = TrendReq(hl="en-US", tz=360, timeout=(8,20), retries=1, backoff_factor=0.3)
        pt.build_payload([query], timeframe="now 7-d")
        rq   = pt.related_queries()
        rising = rq.get(query,{}).get("rising")
        if rising is not None and not rising.empty:
            return [str(row["query"]) for _,row in rising.head(10).iterrows()]
    except Exception as e:
        print(f"[pytrends] {e}")
    return []


# ═════════════════════════════════════════════════════════════════════════════
# AGENT 1 — Niche Research
# ═════════════════════════════════════════════════════════════════════════════

def agent_niche_research(client, niche, yt_key="", rapidapi_key="", cb=noop):
    """
    Returns (clusters: list, enrichment: dict)
    Groq generates full niche intelligence; live APIs add real signal data.
    """
    cb(5, "🧠 Groq generating niche intelligence...")

    # ── Step 1: Groq generates comprehensive niche research ──────────────────
    try:
        raw_intel = _gj(
            client,
            system=(
                "You are a senior content strategist with deep knowledge of social media, "
                "Reddit communities, YouTube trends, consumer psychology, and viral content. "
                "Generate highly specific, realistic research. Return ONLY valid JSON."
            ),
            user=(
                f"Generate comprehensive content research for niche: '{niche}'\n\n"
                f"Based on your knowledge of Reddit discussions, YouTube viral content, "
                f"Google search behavior, and social media trends, provide:\n\n"
                f"{{"
                f'"reddit_hot_posts": [{{"title":"...","subreddit":"r/...","upvotes":1200,"why_viral":"..."}}], '
                f'"youtube_viral_videos": [{{"title":"...","channel":"...","view_estimate":"2.3M","why_works":"..."}}], '
                f'"search_queries": ["query1","query2",...], '
                f'"pain_points": ["specific pain1","specific pain2",...], '
                f'"common_questions": ["question1","question2",...], '
                f'"trending_now": ["trend1","trend2",...], '
                f'"controversial_angles": ["angle1","angle2",...], '
                f'"buyer_objections": ["objection1","objection2",...]'
                f"}}\n\n"
                f"Generate: 12 reddit posts, 10 youtube videos, 12 search queries, "
                f"8 pain points, 8 common questions, 6 trending topics, "
                f"5 controversial angles, 5 buyer objections. "
                f"Make them VERY specific and realistic for '{niche}'."
            ),
            tokens=3000, temp=0.6,
        )
    except Exception as e:
        print(f"[Agent1 intel] {e}")
        raw_intel = {}

    cb(30, "📡 Fetching live Reddit data...")
    live_reddit = _live_reddit(niche, rapidapi_key, n=15)
    live_reddit += _live_reddit(f"best {niche} tips", rapidapi_key, n=8)

    cb(45, "📺 Fetching live YouTube data...")
    live_yt = _live_youtube(niche, yt_key, n=10)
    live_yt += _live_youtube(f"{niche} tips advice", yt_key, n=8)

    cb(55, "📈 Fetching Google Trends data...")
    live_trends_kws = _live_trends(niche)

    # ── Step 2: Groq synthesises everything into clusters ────────────────────
    cb(65, "🧠 Synthesising all signals into topic clusters...")

    # Build combined signal summary
    signal_lines = []
    for p in raw_intel.get("reddit_hot_posts",[])[:12]:
        signal_lines.append(f"[REDDIT] {p.get('title','')} (r/{p.get('subreddit','')}, {p.get('upvotes',0)} up)")
    for v in raw_intel.get("youtube_viral_videos",[])[:10]:
        signal_lines.append(f"[YOUTUBE] {v.get('title','')} — {v.get('view_estimate','')}")
    for q in raw_intel.get("search_queries",[])[:12]:
        signal_lines.append(f"[SEARCH] {q}")
    for p in raw_intel.get("pain_points",[])[:8]:
        signal_lines.append(f"[PAIN] {p}")
    for t in raw_intel.get("trending_now",[])[:6]:
        signal_lines.append(f"[TREND] {t}")
    # Add live data
    for p in live_reddit[:10]:
        signal_lines.append(f"[REDDIT_LIVE] {p['title']} (score:{p['score']})")
    for v in live_yt[:8]:
        signal_lines.append(f"[YOUTUBE_LIVE] {v['title']} ({v['views']:,} views)")
    for kw in live_trends_kws[:8]:
        signal_lines.append(f"[GTRENDS_LIVE] {kw}")

    try:
        clusters = _gj(
            client,
            system="Expert content strategist. Return ONLY a valid JSON array.",
            user=(
                f"Niche: '{niche}'\n\n"
                f"Signals collected ({len(signal_lines)} total):\n"
                + "\n".join(signal_lines[:60]) +
                f"\n\nSynthesise into 6-8 distinct topic clusters. Return JSON array:\n"
                f'[{{"cluster":"Buying Advice",'
                f'"description":"What to consider before buying...",'
                f'"why_popular":"High purchase intent, people need guidance",'
                f'"content_potential":9,'
                f'"subtopics":["sub1","sub2","sub3","sub4","sub5"],'
                f'"platform_fit":{{"TikTok":8,"YouTube":9,"Instagram":6}},'
                f'"audience_intent":"commercial",'
                f'"pain_points":["pain1","pain2","pain3"],'
                f'"viral_angle":"The shocking truth nobody tells you about..."}}]'
            ),
            tokens=2500, temp=0.4,
        )
        if not isinstance(clusters, list):
            clusters = clusters.get("clusters", [])
    except Exception as e:
        print(f"[Agent1 clusters] {e}")
        clusters = []

    enrichment = {
        "reddit_hot":   raw_intel.get("reddit_hot_posts",[]) + live_reddit,
        "youtube_viral":raw_intel.get("youtube_viral_videos",[]) + live_yt,
        "search_queries":raw_intel.get("search_queries",[]) + live_trends_kws,
        "pain_points":  raw_intel.get("pain_points",[]),
        "questions":    raw_intel.get("common_questions",[]),
        "trending":     raw_intel.get("trending_now",[]),
        "controversial":raw_intel.get("controversial_angles",[]),
        "objections":   raw_intel.get("buyer_objections",[]),
        "signal_count": len(signal_lines),
    }

    cb(100, f"✅ {len(clusters)} clusters · {len(signal_lines)} signals")
    return clusters, enrichment


# ═════════════════════════════════════════════════════════════════════════════
# AGENT 2 — Keyword Expansion
# ═════════════════════════════════════════════════════════════════════════════

def agent_keyword_expansion(client, niche, clusters, enrichment, rapidapi_key="", cb=noop):
    """Returns {cluster_name: {keywords:[], total:N}}"""
    cb(0, "🔑 Expanding keywords for all clusters...")
    groups   = {}
    queries  = enrichment.get("search_queries",[])
    trending = enrichment.get("trending",[])

    for i, cluster in enumerate(clusters[:8]):
        cname    = cluster.get("cluster", f"Cluster {i+1}")
        subtopics= cluster.get("subtopics",[])
        pains    = cluster.get("pain_points",[])
        pct      = int(i / max(len(clusters),1) * 100)
        cb(pct, f"🔑 Expanding **{cname}** ({i+1}/{len(clusters)})...")

        try:
            result = _gj(
                client,
                system="SEO and content keyword expert. Return ONLY valid JSON.",
                user=(
                    f"Niche: '{niche}'\n"
                    f"Cluster: '{cname}'\n"
                    f"Subtopics: {', '.join(subtopics)}\n"
                    f"Pain points: {', '.join(pains[:3])}\n"
                    f"Known search queries in this niche: {', '.join(queries[:8])}\n"
                    f"Trending topics: {', '.join(trending[:5])}\n\n"
                    f"Generate 50 specific long-tail keywords a content creator would target.\n"
                    f"Include: how-to questions, comparisons (X vs Y), "
                    f"'best X for Y', 'cheap X', 'X for beginners', 'X 2025', "
                    f"'is X worth it', 'X mistakes to avoid'.\n\n"
                    f'{{"keywords":['
                    f'{{"kw":"best {niche} for first-time buyers",'
                    f'"intent":"commercial",'
                    f'"difficulty":"easy",'
                    f'"video_potential":8,'
                    f'"hook_angle":"The one thing every first-time buyer needs to know"}}]}}'
                ),
                tokens=2000, temp=0.4,
            )
            kw_list = result.get("keywords",[]) if isinstance(result,dict) else []
        except Exception as e:
            print(f"[Agent2 {cname}] {e}")
            kw_list = [
                {"kw": f"{sub} {niche}", "intent":"informational",
                 "difficulty":"medium","video_potential":6,"hook_angle":""}
                for sub in subtopics
            ]

        groups[cname] = {"cluster":cname, "keywords":kw_list[:55], "total":len(kw_list)}

    total = sum(g["total"] for g in groups.values())
    cb(100, f"✅ {total} keywords across {len(groups)} clusters")
    return groups


# ═════════════════════════════════════════════════════════════════════════════
# AGENT 3 — Trend Detection
# ═════════════════════════════════════════════════════════════════════════════

def agent_trend_detection(client, niche, keyword_groups, enrichment, rapidapi_key="", cb=noop):
    """Returns sorted list of trend dicts."""
    cb(5, "📈 Preparing keyword list for trend scoring...")

    # Flatten + top 30 by video_potential
    flat = []
    for grp in keyword_groups.values():
        for k in grp.get("keywords",[]):
            flat.append((k.get("kw",""), k.get("video_potential",5), grp["cluster"]))
    flat.sort(key=lambda x: -x[1])
    targets = flat[:30]

    # Live Reddit recency signal (optional enrichment)
    cb(15, "📡 Checking live Reddit velocity signals...")
    reddit_scores = {}
    for kw, _, _ in targets[:15]:
        posts = _live_reddit(kw, rapidapi_key, n=5)
        reddit_scores[kw] = sum(p.get("score",0) for p in posts)
        time.sleep(0.15)

    # Live Google Trends (optional)
    cb(35, "📈 Checking Google Trends velocity...")
    trends_rising = _live_trends(niche)

    cb(55, "🧠 Groq scoring all keywords for trend velocity...")

    trending_ctx  = enrichment.get("trending",[])
    questions_ctx = enrichment.get("questions",[])
    controversial = enrichment.get("controversial",[])

    # Build context for AI
    kw_lines = "\n".join(
        f"{kw} | cluster:{cls} | vp:{vp} | reddit_live:{reddit_scores.get(kw,0)} "
        f"| in_trends:{'yes' if kw in ' '.join(trends_rising).lower() else 'no'}"
        for kw, vp, cls in targets
    )

    try:
        scored = _gj(
            client,
            system=(
                "You are a trend analyst specialising in social media and search behaviour. "
                "Use the keyword signals plus your knowledge of current trends in this niche. "
                "Return ONLY valid JSON array."
            ),
            user=(
                f"Niche: '{niche}'\n\n"
                f"Known trending topics in this niche: {', '.join(trending_ctx[:8])}\n"
                f"Common questions people are asking: {', '.join(questions_ctx[:6])}\n"
                f"Controversial angles with high engagement: {', '.join(controversial[:4])}\n"
                f"Google Trends rising queries: {', '.join(trends_rising[:8])}\n\n"
                f"Keywords to score (vp=video_potential, reddit_live=live upvotes):\n{kw_lines}\n\n"
                f"Score each keyword for trend status. Return JSON array:\n"
                f'[{{"kw":"...",'
                f'"trend_score":75,'
                f'"status":"EMERGING",'
                f'"velocity":"fast",'
                f'"opportunity_window":"this week",'
                f'"why":"rising search intent due to...",'
                f'"content_urgency":"publish now",'
                f'"content_type_fit":"short-form/long-form/both"}}]\n\n'
                f"Status: EMERGING / GROWING / PEAK / STABLE / DECLINING\n"
                f"Velocity: explosive / fast / steady / slow\n"
                f"Be generous with EMERGING for keywords tied to known current trends."
            ),
            tokens=3000, temp=0.3,
        )
        score_map = {t["kw"]:t for t in (scored if isinstance(scored,list) else []) if "kw" in t}
    except Exception as e:
        print(f"[Agent3 score] {e}")
        score_map = {}

    trends = []
    for kw, vp, cls in targets:
        ai = score_map.get(kw, {})
        trends.append({
            "kw":               kw,
            "cluster":          cls,
            "trend_score":      ai.get("trend_score", vp * 9),
            "status":           ai.get("status","STABLE"),
            "velocity":         ai.get("velocity","steady"),
            "opportunity_window":ai.get("opportunity_window","this week"),
            "why":              ai.get("why",""),
            "content_urgency":  ai.get("content_urgency","plan ahead"),
            "content_type_fit": ai.get("content_type_fit","both"),
            "reddit_score":     reddit_scores.get(kw,0),
        })

    trends.sort(key=lambda x: -x["trend_score"])
    emerging = sum(1 for t in trends if t["status"] in ("EMERGING","GROWING"))
    cb(100, f"✅ {len(trends)} trends scored · {emerging} emerging/growing")
    return trends


# ═════════════════════════════════════════════════════════════════════════════
# AGENT 4 — Viral Hook Agent
# ═════════════════════════════════════════════════════════════════════════════

def agent_viral_hooks(client, niche, top_trends, enrichment, yt_key="", rapidapi_key="", cb=noop):
    """Returns hook intelligence dict."""
    cb(5, "🎣 Collecting viral content for hook analysis...")

    # Live YouTube viral titles
    live_yt = _live_youtube(f"{niche} viral best", yt_key, n=8)
    live_yt += _live_youtube(f"don't buy {niche}", yt_key, n=5)

    # AI-known viral titles from enrichment
    ai_yt  = enrichment.get("youtube_viral",[])
    ai_red = enrichment.get("reddit_hot",[])

    viral_context = "\n".join(
        f"[YT] {v.get('title','')} ({v.get('views',v.get('view_estimate',''))})"
        for v in (live_yt + ai_yt)[:20] if v.get("title")
    )
    viral_context += "\n" + "\n".join(
        f"[REDDIT] {p.get('title','')} (score:{p.get('score',p.get('upvotes',0))})"
        for p in ai_red[:15] if p.get("title")
    )

    cb(40, "🧠 Groq extracting hook patterns from viral content...")

    try:
        hook_analysis = _gj(
            client,
            system=(
                "You are a viral content psychologist and hook writing expert. "
                "Analyse viral titles to extract the psychological formulas. "
                "Return ONLY valid JSON."
            ),
            user=(
                f"Niche: '{niche}'\n\n"
                f"Viral content titles:\n{viral_context}\n\n"
                f"Also use your knowledge of what goes viral in this niche on TikTok and YouTube.\n\n"
                f"Extract and generate hook intelligence. Return:\n"
                f'{{"hook_patterns":['
                f'{{"pattern":"Don\'t [verb] [noun] until you [action]",'
                f'"psychology":"loss aversion + curiosity gap",'
                f'"examples":["Don\'t buy a used car until you watch this","Don\'t lease a car until you know this trick"],'
                f'"effectiveness":9,'
                f'"best_platforms":["TikTok","YouTube"]}}],'
                f'"viral_formulas":['
                f'{{"formula":"Number + Superlative + Noun + Nobody Tells You",'
                f'"example":"5 Car Dealership Tricks Nobody Tells You About",'
                f'"psychology":"social proof + exclusivity + curiosity"}}],'
                f'"top_emotions":["curiosity","FOMO","outrage","surprise"],'
                f'"niche_specific_hooks":['
                f'{{"hook":"...",'
                f'"why_works":"...",'
                f'"template":"[trigger] + [niche-specific pain] + [promise]"}}]}}'
            ),
            tokens=2500, temp=0.5,
        )
    except Exception as e:
        print(f"[Agent4 patterns] {e}")
        hook_analysis = {"hook_patterns":[],"viral_formulas":[],"top_emotions":[],"niche_specific_hooks":[]}

    # Custom hooks for each top trend
    cb(70, "✍️ Writing custom hooks for top trends...")
    trend_hooks = {}
    top5 = [t for t in top_trends if t.get("trend_score",0) >= 50][:5]
    for trend in top5:
        kw = trend["kw"]
        try:
            hooks = _gj(
                client,
                system="Expert viral hook writer. Return ONLY JSON array.",
                user=(
                    f"Niche: {niche}\nTrend keyword: '{kw}'\n"
                    f"Status: {trend.get('status','')}\nWhy trending: {trend.get('why','')}\n\n"
                    f"Write 5 scroll-stopping hooks for this SPECIFIC keyword.\n"
                    f'[{{"hook":"Tesla prices are crashing — here\'s exactly why",'
                    f'"type":"statement",'
                    f'"psychology":"creates urgency + positions speaker as informed insider",'
                    f'"platform":"Both"}}]'
                ),
                tokens=600, temp=0.6,
            )
            if isinstance(hooks, list):
                trend_hooks[kw] = hooks
        except Exception as e:
            print(f"[Agent4 hooks {kw}] {e}")
        time.sleep(0.2)

    result = {
        "patterns":       hook_analysis.get("hook_patterns",[]),
        "viral_formulas": hook_analysis.get("viral_formulas",[]),
        "top_emotions":   hook_analysis.get("top_emotions",[]),
        "niche_hooks":    hook_analysis.get("niche_specific_hooks",[]),
        "trend_hooks":    trend_hooks,
    }
    cb(100, f"✅ {len(result['patterns'])} patterns · {len(trend_hooks)} trend hook sets")
    return result


# ═════════════════════════════════════════════════════════════════════════════
# AGENT 5 — Script Generator
# ═════════════════════════════════════════════════════════════════════════════

PLATFORM_GUIDE = {
    "TikTok":         "15-60s · hook = first 3 words · punchy, conversational, fast cuts",
    "YouTube Shorts": "Under 60s · one surprising insight · high energy · no slow intros",
    "Instagram Reels":"15-30s · aesthetic, relatable storytelling · end with soft CTA",
    "YouTube Long":   "7-12min · structured value · chapters · detailed explanation",
    "LinkedIn":       "Thought leadership · data-backed · professional insight · story arc",
}

def agent_content_scripts(client, niche, top_trends, hook_data, platforms, brand_context="", cb=noop):
    """Returns list of {trend, cluster, status, scripts:{platform:text}}"""
    cb(0, "✍️ Starting script generation...")
    targets = [t for t in top_trends if t.get("trend_score",0) >= 40][:6] or top_trends[:4]

    hook_ctx = ""
    if hook_data.get("niche_hooks"):
        hook_ctx += "Proven hooks for this niche:\n"
        hook_ctx += "\n".join(f'  • "{h.get("hook","")}"' for h in hook_data["niche_hooks"][:4])
    if hook_data.get("viral_formulas"):
        hook_ctx += "\n\nViral formulas:\n"
        hook_ctx += "\n".join(f'  • {f.get("formula","")}: e.g. "{f.get("example","")}"' for f in hook_data["viral_formulas"][:3])

    brand_block = f"\n\nBrand context (align all scripts to this):\n{brand_context[:600]}" if brand_context else ""
    output = []

    for i, trend in enumerate(targets):
        kw     = trend["kw"]
        status = trend.get("status","")
        why    = trend.get("why","")
        pct    = int(i / len(targets) * 100)
        cb(pct, f"✍️ Writing scripts for **{kw}** ({i+1}/{len(targets)})...")

        th = hook_data.get("trend_hooks",{}).get(kw,[])
        hook_examples = "\n".join(f'  • "{h.get("hook","")}"' for h in th[:3])
        script_set = {"trend":kw, "cluster":trend.get("cluster",""), "status":status, "scripts":{}}

        for platform in platforms:
            guide = PLATFORM_GUIDE.get(platform,"Engaging, platform-native")
            try:
                script = _gt(
                    client,
                    system=(
                        f"You are an elite {platform} script writer. "
                        f"Write viral, publish-ready scripts. "
                        f"Always use clear sections: 🎣 HOOK / 📖 BODY / 🎯 CTA\n"
                        f"Then add: 📊 Framework used | 🧠 Why this works"
                        f"{brand_block}"
                    ),
                    user=(
                        f"Niche: {niche}\n"
                        f"Trend: '{kw}' [{status}]\n"
                        f"Why it's trending: {why}\n"
                        f"Platform: {platform} — {guide}\n\n"
                        f"{hook_ctx}\n"
                        + (f"Custom hooks for this trend:\n{hook_examples}\n" if hook_examples else "") +
                        f"\nWrite a complete, publish-ready {platform} script now."
                    ),
                    tokens=900, temp=0.72,
                )
                script_set["scripts"][platform] = script
            except Exception as e:
                script_set["scripts"][platform] = f"[Error generating script: {e}]"
            time.sleep(0.15)

        output.append(script_set)

    total_scripts = sum(len(s["scripts"]) for s in output)
    cb(100, f"✅ {total_scripts} scripts across {len(output)} trends")
    return output


# ═════════════════════════════════════════════════════════════════════════════
# AGENT 6 — Content Calendar
# ═════════════════════════════════════════════════════════════════════════════

def agent_content_calendar(client, niche, trends, scripts_data, platforms, weeks=4, ppw=5, cb=noop):
    """Returns list of week dicts."""
    cb(10, f"📅 Building {weeks}-week content calendar...")

    trend_ctx = "\n".join(
        f"[{t.get('status','')}] {t['kw']} | score:{t.get('trend_score',0)} | urgency:{t.get('content_urgency','')} | window:{t.get('opportunity_window','')}"
        for t in trends[:20]
    )
    scripts_ctx = "\n".join(
        f"• {s['trend']} ({s['cluster']}) — scripts ready for: {', '.join(s['scripts'].keys())}"
        for s in scripts_data[:8]
    )

    try:
        cb(40, "🧠 AI building optimised publishing schedule...")
        cal = _gj(
            client,
            system="Expert social media strategist and content planner. Return ONLY valid JSON.",
            user=(
                f"Niche: '{niche}'\n"
                f"Platforms: {', '.join(platforms)}\n\n"
                f"Available trends (sorted by score):\n{trend_ctx}\n\n"
                f"Scripts already written:\n{scripts_ctx}\n\n"
                f"Build a {weeks}-week content calendar with exactly {ppw} posts per week.\n\n"
                f"Rules:\n"
                f"- EMERGING and GROWING trends publish first (week 1-2)\n"
                f"- Vary content types each week: Educational, Entertainment, Controversy, Story, Social Proof\n"
                f"- Assign the best platform for each topic\n"
                f"- Spread across Mon/Wed/Fri/Sat + 1 more for {ppw} posts/week\n"
                f"- Include best posting time per platform\n\n"
                f'{{"weeks":[{{"week":1,"theme":"Week 1 theme headline",'
                f'"posts":[{{"day":"Monday","platform":"TikTok",'
                f'"topic":"specific topic title",'
                f'"trend_kw":"exact keyword from trends list",'
                f'"content_type":"Educational",'
                f'"hook":"exact scroll-stopping hook to use",'
                f'"caption_start":"First sentence of caption...",'
                f'"best_time":"7pm",'
                f'"urgency":"high"}}]}}]}}'
            ),
            tokens=4000, temp=0.55,
        )
        weeks_data = cal.get("weeks",[]) if isinstance(cal,dict) else []
    except Exception as e:
        print(f"[Agent6] {e}")
        # Deterministic fallback
        DAYS = ["Monday","Tuesday","Wednesday","Thursday","Friday"]
        weeks_data = []
        dc = 0
        for w in range(1, weeks+1):
            posts = []
            for j in range(ppw):
                t = trends[dc % len(trends)] if trends else {"kw":niche,"status":"STABLE"}
                p = platforms[dc % len(platforms)] if platforms else "TikTok"
                posts.append({
                    "day":DAYS[j % 5], "platform":p,
                    "topic":t["kw"], "trend_kw":t["kw"],
                    "content_type":["Educational","Entertainment","Story","Controversy","Social Proof"][j%5],
                    "hook":f"Nobody tells you this about {t['kw']}",
                    "caption_start":"Here's what you need to know...",
                    "best_time":"7pm", "urgency":t.get("content_urgency","medium"),
                })
                dc += 1
            weeks_data.append({"week":w,"theme":f"Week {w} — {niche}","posts":posts})

    total_posts = sum(len(w.get("posts",[])) for w in weeks_data)
    cb(100, f"✅ {total_posts} posts planned across {len(weeks_data)} weeks")
    return weeks_data


# ═════════════════════════════════════════════════════════════════════════════
# PIPELINE RUNNER
# ═════════════════════════════════════════════════════════════════════════════

def run_full_pipeline(
    client, niche, platforms,
    weeks=4, posts_per_week=5,
    yt_key="", rapidapi_key="",
    brand_context="",
    agent_progress_cb=None,   # (agent_num, pct, message)
):
    def _cb(n): return lambda p,m: (agent_progress_cb(n,p,m) if agent_progress_cb else None)

    agent_progress_cb and agent_progress_cb(1, 0, "Starting niche research...")
    clusters, enrichment = agent_niche_research(client, niche, yt_key, rapidapi_key, _cb(1))

    agent_progress_cb and agent_progress_cb(2, 0, "Starting keyword expansion...")
    keyword_groups = agent_keyword_expansion(client, niche, clusters, enrichment, rapidapi_key, _cb(2))

    agent_progress_cb and agent_progress_cb(3, 0, "Starting trend detection...")
    trends = agent_trend_detection(client, niche, keyword_groups, enrichment, rapidapi_key, _cb(3))

    agent_progress_cb and agent_progress_cb(4, 0, "Starting viral hook analysis...")
    hook_data = agent_viral_hooks(client, niche, trends, enrichment, yt_key, rapidapi_key, _cb(4))

    agent_progress_cb and agent_progress_cb(5, 0, "Starting script generation...")
    scripts_data = agent_content_scripts(client, niche, trends, hook_data, platforms, brand_context, _cb(5))

    agent_progress_cb and agent_progress_cb(6, 0, "Starting calendar generation...")
    calendar = agent_content_calendar(client, niche, trends, scripts_data, platforms, weeks, posts_per_week, _cb(6))

    return {
        "niche":          niche,
        "signal_count":   enrichment.get("signal_count",0),
        "clusters":       clusters,
        "keyword_groups": keyword_groups,
        "trends":         trends,
        "hook_data":      hook_data,
        "scripts_data":   scripts_data,
        "calendar":       calendar,
        "enrichment":     enrichment,
    }
