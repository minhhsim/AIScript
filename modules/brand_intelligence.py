# modules/brand_intelligence.py
"""
Live brand intelligence engine.

Given a brand name, topic, or product:
  1. Runs 6-8 targeted DuckDuckGo searches
  2. Fetches and parses key pages
  3. Runs AI extraction → structured brand profile
  4. Returns an injection-ready context block for script generation

No API key needed — uses DuckDuckGo + web fetch.
"""

import re
import json
import requests
from duckduckgo_search import DDGS


# ─────────────────────────────────────────────────────────────────────────────
# Web search helpers
# ─────────────────────────────────────────────────────────────────────────────

def _ddg_search(query: str, max_results: int = 5) -> list[dict]:
    """Run a DuckDuckGo text search. Returns list of {title, href, body}."""
    try:
        with DDGS() as ddgs:
            return list(ddgs.text(query, max_results=max_results))
    except Exception as e:
        print(f"[DDG] {query}: {e}")
        return []


def _fetch_page(url: str, max_chars: int = 3000) -> str:
    """Fetch a URL and return cleaned text content."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        r = requests.get(url, headers=headers, timeout=8, allow_redirects=True)
        r.raise_for_status()
        text = r.text

        # Strip HTML tags
        text = re.sub(r"<script[^>]*>.*?</script>", " ", text, flags=re.DOTALL)
        text = re.sub(r"<style[^>]*>.*?</style>",  " ", text, flags=re.DOTALL)
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text).strip()

        return text[:max_chars]
    except Exception:
        return ""


def _search_and_collect(queries: list[str], results_per_query: int = 4) -> str:
    """
    Run multiple searches and collect snippets into one text block.
    Returns combined text, deduplicated by URL.
    """
    seen_urls = set()
    chunks    = []

    for query in queries:
        results = _ddg_search(query, max_results=results_per_query)
        for r in results:
            url  = r.get("href", "")
            body = r.get("body", "").strip()
            title= r.get("title", "").strip()
            if url in seen_urls or not body:
                continue
            seen_urls.add(url)
            chunks.append(f"[{title}] {body}")

    return "\n\n".join(chunks)


# ─────────────────────────────────────────────────────────────────────────────
# Main research function
# ─────────────────────────────────────────────────────────────────────────────

RESEARCH_ANGLES = [
    "{brand} brand values mission tagline",
    "{brand} products services what they offer",
    "{brand} target audience customer reviews",
    "{brand} marketing campaigns advertising",
    "{brand} latest news 2024 2025",
    "{brand} vs competitors differentiator",
    "{brand} social media content strategy",
    "{brand} customer pain points problems solved",
]


def research_brand(groq_client, brand_name: str) -> dict:
    """
    Full live research on a brand/topic.
    Returns structured dict with brand intelligence + injection prompt.
    """
    result = {
        "brand_name":    brand_name,
        "raw_research":  "",
        "profile":       {},
        "injection_block": "",
        "error":         None,
        "sources_count": 0,
    }

    # ── Step 1: Multi-angle web research ────────────────────────────────────
    queries = [q.replace("{brand}", brand_name) for q in RESEARCH_ANGLES]
    raw_text = _search_and_collect(queries, results_per_query=4)

    if not raw_text.strip():
        result["error"] = "No web data found for this brand/topic."
        return result

    result["raw_research"]  = raw_text
    result["sources_count"] = raw_text.count("[")  # rough count

    # ── Step 2: AI extraction ────────────────────────────────────────────────
    prompt = f"""You are a brand strategist. Extract structured intelligence from this raw web research about "{brand_name}".

RAW RESEARCH DATA:
{raw_text[:6000]}

Extract everything relevant. Return ONLY valid JSON:
{{
  "brand_name": "{brand_name}",
  "tagline": "their official or commonly used tagline",
  "mission": "what they stand for / their purpose",
  "brand_voice": "how they communicate (e.g. bold and irreverent / warm and educational / premium and exclusive)",
  "core_values": ["value1", "value2", "value3"],
  "products_services": ["main product/service 1", "main product/service 2", "main product/service 3"],
  "key_features": ["standout feature/USP 1", "USP 2", "USP 3"],
  "target_audience": "description of who they sell to",
  "audience_pain_points": ["pain point 1", "pain point 2", "pain point 3"],
  "audience_desires": ["what audience wants 1", "desire 2", "desire 3"],
  "competitors": ["competitor 1", "competitor 2"],
  "differentiators": ["what sets them apart 1", "differentiator 2"],
  "recent_news_angles": ["recent event or campaign 1", "angle 2"],
  "social_proof_signals": ["review/stat/award that builds trust 1", "signal 2"],
  "content_themes": ["topic they talk about 1", "theme 2", "theme 3"],
  "forbidden_claims": ["anything to avoid saying e.g. medical claims, competitor attacks"],
  "emotional_hooks": ["emotional angle that resonates with their audience 1", "angle 2"],
  "cta_style": "what kind of CTA works for this brand (e.g. 'Try free', 'Shop now', 'Learn more')",
  "brand_color_feeling": "color/aesthetic vibe e.g. 'dark premium', 'bright playful', 'clean minimal'",
  "confidence": 0-100
}}"""

    try:
        resp = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "Brand intelligence analyst. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500,
            temperature=0.2
        )
        raw = resp.choices[0].message.content.strip()
        raw = re.sub(r"^```json\s*", "", raw)
        raw = re.sub(r"^```\s*",     "", raw)
        raw = re.sub(r"\s*```$",     "", raw)
        profile = json.loads(raw)
        result["profile"] = profile
    except Exception as e:
        result["error"]  = f"AI extraction failed: {e}"
        result["profile"] = {}
        return result

    # ── Step 3: Build injection block for script generation ──────────────────
    p = result["profile"]

    injection_lines = [
        f"BRAND: {p.get('brand_name', brand_name)}",
        f"TAGLINE: {p.get('tagline', '')}",
        f"MISSION: {p.get('mission', '')}",
        f"VOICE: {p.get('brand_voice', '')}",
        f"VALUES: {', '.join(p.get('core_values', []))}",
        "",
        f"PRODUCTS/SERVICES: {', '.join(p.get('products_services', []))}",
        f"KEY USPs: {', '.join(p.get('key_features', []))}",
        f"DIFFERENTIATORS: {', '.join(p.get('differentiators', []))}",
        "",
        f"TARGET AUDIENCE: {p.get('target_audience', '')}",
        f"AUDIENCE PAIN POINTS: {', '.join(p.get('audience_pain_points', []))}",
        f"AUDIENCE DESIRES: {', '.join(p.get('audience_desires', []))}",
        "",
        f"EMOTIONAL HOOKS THAT WORK: {', '.join(p.get('emotional_hooks', []))}",
        f"SOCIAL PROOF: {', '.join(p.get('social_proof_signals', []))}",
        f"CONTENT THEMES: {', '.join(p.get('content_themes', []))}",
        f"CTA STYLE: {p.get('cta_style', '')}",
    ]
    if p.get("recent_news_angles"):
        injection_lines += ["", f"CURRENT ANGLES: {', '.join(p['recent_news_angles'])}"]
    if p.get("forbidden_claims"):
        injection_lines += ["", f"DO NOT CLAIM: {', '.join(p['forbidden_claims'])}"]

    result["injection_block"] = "\n".join(l for l in injection_lines if l.strip() or l == "")
    return result


def get_topic_research(groq_client, topic: str) -> str:
    """
    Lighter research for a content topic (not a brand).
    Returns a plain text context block.
    Used when no brand name is given but topic needs real data.
    """
    queries = [
        f"{topic} statistics facts 2024 2025",
        f"{topic} trends social media",
        f"{topic} common misconceptions truth",
        f"{topic} audience pain points questions",
    ]
    raw = _search_and_collect(queries, results_per_query=3)
    if not raw:
        return ""

    try:
        resp = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "Extract the most useful facts, stats, and angles for content creation. Be concise."},
                {"role": "user", "content": f"Topic: {topic}\n\nRaw research:\n{raw[:4000]}\n\nExtract: key stats, surprising facts, trending angles, common questions, emotional hooks. Format as bullet points."}
            ],
            max_tokens=600,
            temperature=0.2
        )
        return resp.choices[0].message.content.strip()
    except Exception:
        return raw[:1000]
