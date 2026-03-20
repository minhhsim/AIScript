# modules/social_scraper.py
"""
Social media trend scraper for TikTok and Instagram.
Multiple methods with automatic fallback:
  TikTok:    RapidAPI Tokapi → yt-dlp metadata → DuckDuckGo
  Instagram: RapidAPI Instagram → instaloader → DuckDuckGo
"""

import os
import json
import requests
import subprocess
from ddgs import DDGS


# ── TikTok Scraping ───────────────────────────────────────────────────────────

def scrape_tiktok_rapidapi(topic: str, rapidapi_key: str, count: int = 10) -> list:
    """Scrape TikTok trending videos via RapidAPI Tokapi."""
    if not rapidapi_key or rapidapi_key == "YOUR_RAPIDAPI_KEY":
        return []

    headers = {
        "X-RapidAPI-Key": rapidapi_key,
        "X-RapidAPI-Host": "tokapi-mobile-version.p.rapidapi.com"
    }
    results = []

    # Search videos
    try:
        r = requests.get(
            "https://tokapi-mobile-version.p.rapidapi.com/v1/search/video",
            headers=headers,
            params={"keyword": topic, "count": count, "offset": 0},
            timeout=10
        )
        data = r.json()
        videos = (
            data.get("video_list") or
            data.get("aweme_list") or
            data.get("data", {}).get("videos") or []
        )
        for v in videos:
            desc = (v.get("desc") or v.get("video", {}).get("desc") or
                    v.get("aweme_info", {}).get("desc") or "")
            stats = (v.get("statistics") or v.get("video", {}).get("statistics") or
                     v.get("aweme_info", {}).get("statistics") or {})
            if desc:
                results.append({
                    "platform": "TikTok",
                    "type": "video",
                    "description": desc,
                    "likes": stats.get("digg_count", 0),
                    "comments": stats.get("comment_count", 0),
                    "shares": stats.get("share_count", 0),
                    "views": stats.get("play_count", 0),
                })
    except Exception as e:
        print(f"[Scraper] TikTok video search error: {e}")

    # Search hashtags
    try:
        r = requests.get(
            "https://tokapi-mobile-version.p.rapidapi.com/v1/search/hashtag",
            headers=headers,
            params={"keyword": topic, "count": 5},
            timeout=10
        )
        data = r.json()
        hashtags = (
            data.get("hashtag_list") or
            data.get("data", {}).get("hashtags") or []
        )
        for h in hashtags:
            info = h.get("hashtag_info") or h.get("hashtag") or {}
            name = info.get("title") or info.get("name") or ""
            views = info.get("view_count") or info.get("video_count") or 0
            if name:
                results.append({
                    "platform": "TikTok",
                    "type": "hashtag",
                    "description": f"#{name}",
                    "views": views,
                    "likes": 0,
                    "comments": 0,
                    "shares": 0,
                })
    except Exception as e:
        print(f"[Scraper] TikTok hashtag search error: {e}")

    return results


def scrape_tiktok_ytdlp(topic: str, count: int = 8) -> list:
    """Scrape TikTok search results metadata via yt-dlp (no API key needed)."""
    results = []
    try:
        search_url = f"https://www.tiktok.com/search?q={topic.replace(' ', '+')}"
        cmd = ["yt-dlp", "--dump-json", "--flat-playlist",
               "--playlist-items", f"1:{count}", "--no-warnings", search_url]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        for line in proc.stdout.strip().split("\n"):
            if not line.strip():
                continue
            try:
                data = json.loads(line)
                title = data.get("title") or data.get("description") or ""
                if title:
                    results.append({
                        "platform": "TikTok",
                        "type": "video",
                        "description": title,
                        "views": data.get("view_count", 0),
                        "likes": data.get("like_count", 0),
                        "comments": data.get("comment_count", 0),
                        "shares": 0,
                        "url": data.get("url") or data.get("webpage_url") or "",
                    })
            except Exception:
                continue
    except Exception as e:
        print(f"[Scraper] yt-dlp TikTok error: {e}")
    return results


# ── Instagram Scraping ────────────────────────────────────────────────────────

def scrape_instagram_rapidapi(topic: str, rapidapi_key: str, count: int = 10) -> list:
    """Scrape Instagram trending posts via RapidAPI."""
    if not rapidapi_key or rapidapi_key == "YOUR_RAPIDAPI_KEY":
        return []

    results = []

    # Method 1: Instagram Scraper API
    try:
        headers = {
            "X-RapidAPI-Key": rapidapi_key,
            "X-RapidAPI-Host": "instagram-scraper-api2.p.rapidapi.com"
        }
        r = requests.get(
            "https://instagram-scraper-api2.p.rapidapi.com/v1/search_posts",
            headers=headers,
            params={"search_query": topic, "count": count},
            timeout=10
        )
        data = r.json()
        posts = (data.get("data", {}).get("items") or
                 data.get("items") or
                 data.get("posts") or [])
        for p in posts:
            caption = (p.get("caption") or {}).get("text") or p.get("text") or ""
            edge_media = p.get("edge_media_preview_like") or {}
            likes = edge_media.get("count") or p.get("like_count") or 0
            comments = (p.get("edge_media_to_comment") or {}).get("count") or p.get("comment_count") or 0
            views = p.get("video_view_count") or p.get("view_count") or 0
            if caption:
                results.append({
                    "platform": "Instagram",
                    "type": "reel" if views > 0 else "post",
                    "description": caption[:200],
                    "likes": likes,
                    "comments": comments,
                    "shares": 0,
                    "views": views,
                })
    except Exception as e:
        print(f"[Scraper] Instagram RapidAPI error: {e}")

    # Method 2: Hashtag search
    if not results:
        try:
            headers = {
                "X-RapidAPI-Key": rapidapi_key,
                "X-RapidAPI-Host": "instagram47.p.rapidapi.com"
            }
            r = requests.get(
                "https://instagram47.p.rapidapi.com/api/hashtag_posts",
                headers=headers,
                params={"hashtag": topic.replace(" ", ""), "count": count},
                timeout=10
            )
            data = r.json()
            posts = data.get("data") or data.get("posts") or []
            for p in posts[:count]:
                caption = p.get("caption") or p.get("text") or ""
                if caption:
                    results.append({
                        "platform": "Instagram",
                        "type": "post",
                        "description": str(caption)[:200],
                        "likes": p.get("like_count") or 0,
                        "comments": p.get("comment_count") or 0,
                        "shares": 0,
                        "views": p.get("view_count") or 0,
                    })
        except Exception as e:
            print(f"[Scraper] Instagram hashtag API error: {e}")

    return results


def scrape_instagram_instaloader(topic: str, count: int = 8) -> list:
    """Scrape Instagram hashtag posts via instaloader (no login needed for public posts)."""
    results = []
    try:
        import instaloader
        L = instaloader.Instaloader()
        hashtag = topic.replace(" ", "").replace("#", "")
        posts = instaloader.Hashtag.from_name(L.context, hashtag).get_posts()
        for i, post in enumerate(posts):
            if i >= count:
                break
            caption = post.caption or ""
            results.append({
                "platform": "Instagram",
                "type": "reel" if post.is_video else "post",
                "description": caption[:200],
                "likes": post.likes,
                "comments": post.comments,
                "shares": 0,
                "views": post.video_view_count if post.is_video else 0,
                "url": f"https://www.instagram.com/p/{post.shortcode}/",
            })
    except ImportError:
        print("[Scraper] instaloader not installed: pip install instaloader")
    except Exception as e:
        print(f"[Scraper] instaloader error: {e}")
    return results


# ── DuckDuckGo fallback ───────────────────────────────────────────────────────

def scrape_ddg_fallback(topic: str, platform: str = "TikTok", count: int = 8) -> list:
    """Web search fallback when platform APIs are unavailable."""
    results = []
    try:
        with DDGS() as ddgs:
            query = f"{topic} {platform} trending viral 2025"
            res = list(ddgs.text(query, max_results=count))
            for r in res:
                if r.get("body"):
                    results.append({
                        "platform": platform,
                        "type": "web_result",
                        "description": r["body"],
                        "likes": 0,
                        "comments": 0,
                        "shares": 0,
                        "views": 0,
                        "url": r.get("href", ""),
                    })
    except Exception as e:
        print(f"[Scraper] DDG fallback error: {e}")
    return results


# ── Main scraper entry point ──────────────────────────────────────────────────

def scrape_social_trends(
    topic: str,
    platforms: list = ["TikTok"],
    rapidapi_key: str = "",
    count: int = 10
) -> dict:
    """
    Master scraper. Returns dict with platform keys and list of trend items.
    Automatically falls back through methods if primary fails.

    Returns:
    {
        "TikTok": [ { platform, type, description, likes, comments, shares, views } ],
        "Instagram": [ ... ],
        "summary": "formatted string for AI prompt injection"
    }
    """
    all_results = {}
    summary_parts = []

    for platform in platforms:
        items = []

        if platform == "TikTok":
            # Method 1: RapidAPI
            items = scrape_tiktok_rapidapi(topic, rapidapi_key, count)
            if not items:
                # Method 2: yt-dlp
                items = scrape_tiktok_ytdlp(topic, count)
            if not items:
                # Method 3: DDG
                items = scrape_ddg_fallback(topic, "TikTok", count)

        elif platform == "Instagram":
            # Method 1: RapidAPI
            items = scrape_instagram_rapidapi(topic, rapidapi_key, count)
            if not items:
                # Method 2: instaloader
                items = scrape_instagram_instaloader(topic, count)
            if not items:
                # Method 3: DDG
                items = scrape_ddg_fallback(topic, "Instagram", count)

        all_results[platform] = items

        # Build summary string
        if items:
            platform_lines = [f"\n=== {platform} Trends for '{topic}' ==="]
            for item in items[:8]:
                desc = item.get("description", "")[:120]
                likes = item.get("likes", 0)
                views = item.get("views", 0)
                itype = item.get("type", "")
                line = f"[{itype}] {desc}"
                if likes: line += f" | ❤️ {likes:,}"
                if views: line += f" | 👁️ {views:,}"
                platform_lines.append(line)
            summary_parts.append("\n".join(platform_lines))

    all_results["summary"] = "\n\n".join(summary_parts) if summary_parts else "No trend data found."
    return all_results


def format_trends_for_display(trends: dict) -> list:
    """Format trend data into cards for Streamlit display."""
    cards = []
    for platform, items in trends.items():
        if platform == "summary" or not isinstance(items, list):
            continue
        for item in items:
            if not item.get("description"):
                continue
            cards.append({
                "platform": item.get("platform", platform),
                "type": item.get("type", "post"),
                "description": item.get("description", ""),
                "likes": item.get("likes", 0),
                "comments": item.get("comments", 0),
                "shares": item.get("shares", 0),
                "views": item.get("views", 0),
                "url": item.get("url", ""),
            })
    return cards
