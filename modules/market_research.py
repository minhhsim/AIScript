# modules/market_research.py
"""
Market Research Engine — multi-source trend discovery.

Sources:
  - DuckDuckGo News  → breaking news & fresh trends
  - DuckDuckGo Text  → tips, FAQs, case studies, hot takes

Each card is AI-enriched with:
  - Content angle + hook idea
  - Viral potential score (0-100)
  - Brand relevance score (0-100) — how well it fits the brand RAG context
  - Brand content angle — specific angle that connects to THIS brand
  - Emotion + format fit + tags
"""

import re, json, time, hashlib
from datetime import datetime, timezone
from duckduckgo_search import DDGS


RESEARCH_CATEGORIES = {
    "🔥 Trending Now":       {"q": "trending viral {topic} 2025",               "src": "news"},
    "📈 Market Shifts":      {"q": "{topic} market trend industry shift",        "src": "news"},
    "💡 Tips & How-To":      {"q": "{topic} tips how to guide best practices",   "src": "text"},
    "😱 Hot Takes":          {"q": "{topic} controversy debate unpopular opinion","src": "text"},
    "✅ Success Stories":    {"q": "{topic} success story results case study",    "src": "text"},
    "❓ Pain Points & FAQs": {"q": "{topic} common problems questions mistakes",  "src": "text"},
    "🌍 Industry News":      {"q": "{topic} industry news announcement 2025",    "src": "news"},
    "💰 Money & Business":   {"q": "{topic} business money revenue growth",      "src": "news"},
}

PLATFORM_ANGLES = {
    "TikTok":            "short-form viral hook Gen Z trending",
    "Instagram Reels":   "aesthetic lifestyle visual entertaining",
    "YouTube Shorts":    "surprising fact quick educational",
    "YouTube Long-form": "in-depth story breakdown analysis",
    "LinkedIn":          "professional insight thought leadership B2B",
    "Twitter/X":         "hot take thread debate opinion",
}


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _ddg(query: str, src: str, n: int = 6) -> list:
    try:
        with DDGS() as d:
            return list(d.news(query, max_results=n) if src == "news"
                        else d.text(query, max_results=n))
    except Exception as e:
        print(f"[DDG {src}] {query[:50]}: {e}")
        return []


def _clean(t: str, n: int = 350) -> str:
    t = re.sub(r"<[^>]+>", " ", t or "")
    return re.sub(r"\s+", " ", t).strip()[:n]


def _uid(s: str) -> str:
    return hashlib.md5(s.encode()).hexdigest()[:10]


def _ago(ds: str) -> str:
    if not ds: return ""
    try:
        if "ago" in ds.lower(): return ds
        dt   = datetime.fromisoformat(ds.replace("Z", "+00:00"))
        now  = datetime.now(timezone.utc)
        diff = now - dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else now - dt
        h = int(diff.total_seconds() / 3600)
        if h < 1:   return "just now"
        if h < 24:  return f"{h}h ago"
        if h < 168: return f"{h//24}d ago"
        return f"{h//168}w ago"
    except Exception:
        return ds[:10] if ds else ""


# ─────────────────────────────────────────────────────────────────────────────
# Fetch
# ─────────────────────────────────────────────────────────────────────────────

def fetch_market_trends(topic: str, platform: str = "TikTok",
                        categories: list = None, max_per: int = 6) -> list:
    """Fetch raw research cards across selected categories."""
    cats  = categories or list(RESEARCH_CATEGORIES.keys())
    cards = []
    seen  = set()

    for cat in cats:
        cfg = RESEARCH_CATEGORIES.get(cat, {})
        q   = cfg.get("q", "{topic}").replace("{topic}", topic)
        src = cfg.get("src", "text")

        for r in _ddg(q, src, n=max_per):
            title = _clean(r.get("title",""), 120)
            if not title or title.lower() in seen:
                continue
            seen.add(title.lower())
            is_news = (src == "news")
            href    = r.get("url","") if is_news else r.get("href","")
            domain  = href.split("/")[2] if href.count("/") >= 2 else href

            cards.append({
                "id":               _uid(title),
                "title":            title,
                "body":             _clean(r.get("body",""), 400),
                "source":           r.get("source","") if is_news else domain,
                "url":              href,
                "date":             r.get("date","") if is_news else "",
                "time_ago":         _ago(r.get("date","")) if is_news else "",
                "image":            r.get("image","") if is_news else "",
                "category":         cat,
                "type":             "news" if is_news else "article",
                # enriched below
                "content_angle":    "",
                "hook_idea":        "",
                "content_score":    50,
                "brand_relevance":  0,
                "brand_angle":      "",
                "tags":             [],
                "emotion":          "",
                "format_fit":       "",
            })
        time.sleep(0.25)

    return cards


# ─────────────────────────────────────────────────────────────────────────────
# Enrich with AI — includes brand relevance scoring
# ─────────────────────────────────────────────────────────────────────────────

def enrich_cards(groq_client, cards: list, topic: str, platform: str,
                 brand_context: str = "") -> list:
    """
    Single AI call enriches all cards with:
      - content_angle, hook_idea, content_score, tags, emotion, format_fit
      - brand_relevance (0-100): how well this trend fits the brand
      - brand_angle: specific angle connecting this trend to the brand
    """
    if not cards:
        return cards

    brand_section = ""
    if brand_context.strip():
        brand_section = f"""
BRAND CONTEXT (use to score brand_relevance and generate brand_angle):
{brand_context[:800]}
"""

    lines = [
        f"{i}: {c['title'][:90]} || {c['body'][:120]}"
        for i, c in enumerate(cards[:24])
    ]

    prompt = f"""You are an expert viral content strategist.
Topic: "{topic}" | Platform: {platform}
{brand_section}
Analyze these {len(lines)} research cards.

CARDS:
{chr(10).join(lines)}

Return ONLY a valid JSON array — one object per card:
[
  {{
    "index": 0,
    "content_angle": "punchy specific viral angle (e.g. 'The dark truth about X nobody talks about')",
    "hook_idea": "first 8-12 words of a scroll-stopping hook for this card",
    "content_score": <integer 0-100, viral potential for {platform}>,
    "brand_relevance": <integer 0-100, how relevant this trend is to the brand — 0 if no brand context>,
    "brand_angle": "specific way to connect this trend to the brand (empty string if no brand context)",
    "tags": ["tag1", "tag2", "tag3"],
    "emotion": "one of: Curiosity / Surprise / FOMO / Fear / Inspiration / Validation / Outrage / Hope",
    "format_fit": "one of: Talking Head / Voiceover / Listicle / Story / Controversy / Tutorial / Reaction"
  }}
]

Scoring:
- content_score: novelty (30%) + emotional punch (30%) + {platform} fit (25%) + shareability (15%)
- brand_relevance: how directly this trend topic connects to the brand's products, values, audience, or messaging
- brand_angle: a concrete sentence showing HOW the brand can use this trend (e.g. "Position [brand] as the solution to [trend problem]")"""

    try:
        resp = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "Expert content strategist. Return only valid JSON array, no markdown."},
                {"role": "user",   "content": prompt}
            ],
            max_tokens=2800, temperature=0.3
        )
        raw = resp.choices[0].message.content.strip()
        raw = re.sub(r"^```json\s*","",raw)
        raw = re.sub(r"^```\s*","",raw)
        raw = re.sub(r"\s*```$","",raw)
        enrichments = json.loads(raw)
        em = {e["index"]: e for e in enrichments if isinstance(e.get("index"), int)}

        for i, card in enumerate(cards[:24]):
            e = em.get(i, {})
            card["content_angle"]   = e.get("content_angle","")
            card["hook_idea"]       = e.get("hook_idea","")
            card["content_score"]   = int(e.get("content_score", 50))
            card["brand_relevance"] = int(e.get("brand_relevance", 0))
            card["brand_angle"]     = e.get("brand_angle","")
            card["tags"]            = e.get("tags",[])[:4]
            card["emotion"]         = e.get("emotion","")
            card["format_fit"]      = e.get("format_fit","")

    except Exception as ex:
        print(f"[enrich_cards] {ex}")
        for card in cards:
            for k, v in [("content_score",50),("brand_relevance",0),("brand_angle",""),
                         ("hook_idea",""),("content_angle",""),("tags",[]),("emotion",""),("format_fit","")]:
                card.setdefault(k, v)

    # Sort: blend of content_score + brand_relevance (if brand context present)
    if brand_context.strip():
        cards.sort(key=lambda x: x.get("content_score",0)*0.5 + x.get("brand_relevance",0)*0.5, reverse=True)
    else:
        cards.sort(key=lambda x: x.get("content_score",0), reverse=True)

    return cards


# ─────────────────────────────────────────────────────────────────────────────
# Script brief builder
# ─────────────────────────────────────────────────────────────────────────────

def build_script_brief(card: dict, answers: dict) -> str:
    """Merge card data + user Q&A into a rich brief for the generator."""
    parts = [
        f"RESEARCH TOPIC: {card.get('title','')}",
        f"CONTENT ANGLE: {card.get('content_angle','')}",
        f"SUGGESTED HOOK: {card.get('hook_idea','')}",
        f"SOURCE CONTEXT: {card.get('body','')}",
        f"SOURCE: {card.get('source','')} — {card.get('url','')}",
    ]
    if card.get("brand_angle"):
        parts.append(f"BRAND ANGLE: {card.get('brand_angle','')}")
    parts += [
        "",
        "SCRIPT PREFERENCES (from user):",
        f"• Tone:           {answers.get('tone','Conversational')}",
        f"• Humor:          {answers.get('humor','No')}",
        f"• Social proof:   {answers.get('social_proof','No')}",
        f"• Statistics:     {answers.get('use_stats','Yes — use real numbers from the source')}",
        f"• Personal story: {answers.get('personal_story','No')}",
        f"• Controversy:    {answers.get('controversy','Low')}",
        f"• CTA:            {answers.get('cta_type','Follow for more')}",
        f"• Target emotion: {answers.get('target_emotion', card.get('emotion','Curiosity'))}",
        f"• Extra notes:    {answers.get('extra_notes','')}",
    ]
    return "\n".join(l for l in parts if l.strip() or l == "")
