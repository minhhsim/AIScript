# modules/social_trends.py
"""
Social Media Trend Scraper

Scrapes REAL social content from:
  ▸ Reddit        — JSON API (free, no auth)
  ▸ YouTube       — Data API v3 (trending + search)
  ▸ TikTok        — RapidAPI tokapi + yt-dlp fallback
  ▸ Instagram     — RapidAPI instagram-scraper-api2
  ▸ Twitter/X     — Nitter scraping + DDG "site:x.com" fallback
  ▸ Google Trends — pytrends (real-time rising queries)

Each result normalised to a common SocialPost dict:
  platform, post_id, title, body, author, url,
  likes, comments, shares, views, date, time_ago,
  hashtags, is_viral, engagement_rate, raw
"""

import re, json, time, hashlib, html
from datetime import datetime, timezone
from typing import Optional
import requests
from ddgs import DDGS

# ─────────────────────────────────────────────────────────────────────────────
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}
TIMEOUT = 10

def _uid(s: str) -> str:
    return hashlib.md5(s.encode()).hexdigest()[:10]

def _clean(t: str, n: int = 400) -> str:
    t = html.unescape(t or "")
    t = re.sub(r"<[^>]+>", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t[:n]

def _ago(ts) -> str:
    """Convert unix timestamp or ISO string → '3h ago'."""
    try:
        if isinstance(ts, (int, float)):
            diff = time.time() - float(ts)
        else:
            dt   = datetime.fromisoformat(str(ts).replace("Z","+00:00"))
            diff = datetime.now(timezone.utc).timestamp() - dt.timestamp()
        h = int(diff / 3600)
        if h < 1:   return "just now"
        if h < 24:  return f"{h}h ago"
        if h < 168: return f"{h//24}d ago"
        return f"{h//168}w ago"
    except Exception:
        return ""

def _fmt_num(n) -> str:
    try:
        n = int(n)
        if n >= 1_000_000: return f"{n/1_000_000:.1f}M"
        if n >= 1_000:     return f"{n/1_000:.1f}K"
        return str(n)
    except Exception:
        return str(n)

def _post(platform, post_id, title, body, author, url,
          likes=0, comments=0, shares=0, views=0,
          date="", hashtags=None, raw=None) -> dict:
    """Normalise into SocialPost dict."""
    eng = 0
    if views > 0:
        eng = round((likes + comments + shares) / views * 100, 2)
    elif likes + comments > 0:
        eng = 100  # no view count, assume engaged

    return {
        "id":               _uid(f"{platform}{post_id}"),
        "platform":         platform,
        "post_id":          post_id,
        "title":            _clean(title, 150),
        "body":             _clean(body, 400),
        "author":           author or "",
        "url":              url or "",
        "likes":            likes,
        "comments":         comments,
        "shares":           shares,
        "views":            views,
        "likes_fmt":        _fmt_num(likes),
        "comments_fmt":     _fmt_num(comments),
        "views_fmt":        _fmt_num(views) if views else "",
        "date":             date,
        "time_ago":         _ago(date) if date else "",
        "hashtags":         hashtags or [],
        "is_viral":         (likes >= 1000 or views >= 50000),
        "engagement_rate":  eng,
        "raw":              raw or {},
        # enriched later
        "content_score":    50,
        "brand_relevance":  0,
        "content_angle":    "",
        "hook_idea":        "",
        "brand_angle":      "",
        "emotion":          "",
        "format_fit":       "",
        "tags":             [],
    }


# ══════════════════════════════════════════════════════════════════════════════
# REDDIT (free JSON API — no key needed)
# ══════════════════════════════════════════════════════════════════════════════

REDDIT_SUBREDDITS = {
    "general":     ["r/trendingsubreddits", "r/popular"],
    "business":    ["r/entrepreneur", "r/startups", "r/business"],
    "tech":        ["r/technology", "r/artificial", "r/MachineLearning"],
    "fitness":     ["r/fitness", "r/loseit", "r/bodybuilding"],
    "finance":     ["r/personalfinance", "r/investing", "r/wallstreetbets"],
    "fashion":     ["r/malefashionadvice", "r/femalefashionadvice"],
    "food":        ["r/food", "r/EatCheapAndHealthy"],
    "gaming":      ["r/gaming", "r/pcgaming"],
    "beauty":      ["r/SkincareAddiction", "r/MakeupAddiction"],
    "travel":      ["r/travel", "r/solotravel"],
}

def scrape_reddit(topic: str, max_posts: int = 15) -> list:
    """
    Search Reddit for topic posts.
    Uses public /search.json endpoint — no OAuth needed.
    """
    posts = []
    seen  = set()

    # 1. Topic search across all Reddit
    urls = [
        f"https://www.reddit.com/search.json?q={requests.utils.quote(topic)}&sort=hot&limit={max_posts}&t=week",
        f"https://www.reddit.com/search.json?q={requests.utils.quote(topic)}&sort=top&limit={max_posts}&t=month",
    ]

    for url in urls:
        try:
            r = requests.get(url, headers={**HEADERS, "Accept":"application/json"},
                             timeout=TIMEOUT)
            if r.status_code != 200:
                continue
            data = r.json()
            children = data.get("data", {}).get("children", [])

            for child in children:
                d = child.get("data", {})
                pid = d.get("id","")
                if pid in seen or not d.get("title"):
                    continue
                seen.add(pid)

                hashtags = re.findall(r"#\w+", d.get("selftext","") + " " + d.get("title",""))
                posts.append(_post(
                    platform  = "Reddit",
                    post_id   = pid,
                    title     = d.get("title",""),
                    body      = _clean(d.get("selftext","") or d.get("url_overridden_by_dest",""), 350),
                    author    = d.get("author",""),
                    url       = f"https://reddit.com{d.get('permalink','')}",
                    likes     = d.get("score", 0),
                    comments  = d.get("num_comments", 0),
                    shares    = 0,
                    views     = d.get("view_count") or 0,
                    date      = d.get("created_utc", ""),
                    hashtags  = hashtags,
                    raw       = {
                        "subreddit":    d.get("subreddit_name_prefixed",""),
                        "flair":        d.get("link_flair_text",""),
                        "upvote_ratio": d.get("upvote_ratio", 0),
                        "awards":       d.get("total_awards_received", 0),
                    }
                ))
        except Exception as e:
            print(f"[Reddit] {e}")
        time.sleep(0.5)

    return posts[:max_posts]


# ══════════════════════════════════════════════════════════════════════════════
# YOUTUBE (Data API v3 — free 10k units/day)
# ══════════════════════════════════════════════════════════════════════════════

def scrape_youtube(topic: str, youtube_api_key: str, max_videos: int = 12) -> list:
    """
    Search YouTube for trending/viral videos on a topic.
    Falls back to yt-dlp if no API key.
    """
    posts = []

    if not youtube_api_key or youtube_api_key in ("", "YOUR_YOUTUBE_KEY"):
        # yt-dlp fallback
        return _youtube_ytdlp(topic, max_videos)

    try:
        url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            "key":        youtube_api_key,
            "q":          topic,
            "part":       "snippet",
            "type":       "video",
            "order":      "viewCount",
            "maxResults": max_videos,
            "videoDuration": "short",   # prefer short-form for trend signals
        }
        r    = requests.get(url, params=params, timeout=TIMEOUT)
        data = r.json()
        items = data.get("items", [])

        if not items:
            return _youtube_ytdlp(topic, max_videos)

        # Batch fetch statistics
        video_ids = [i["id"]["videoId"] for i in items if i.get("id",{}).get("videoId")]
        stats_map = {}
        if video_ids:
            sr = requests.get(
                "https://www.googleapis.com/youtube/v3/videos",
                params={"key": youtube_api_key, "id": ",".join(video_ids),
                        "part": "statistics,contentDetails"},
                timeout=TIMEOUT
            )
            for sv in sr.json().get("items", []):
                stats_map[sv["id"]] = sv.get("statistics", {})

        for item in items:
            vid    = item.get("id",{}).get("videoId","")
            snip   = item.get("snippet",{})
            stats  = stats_map.get(vid, {})
            title  = snip.get("title","")
            if not title:
                continue

            tags   = snip.get("tags",[]) if snip.get("tags") else []
            posts.append(_post(
                platform  = "YouTube",
                post_id   = vid,
                title     = title,
                body      = snip.get("description","")[:300],
                author    = snip.get("channelTitle",""),
                url       = f"https://youtube.com/watch?v={vid}",
                likes     = int(stats.get("likeCount", 0)),
                comments  = int(stats.get("commentCount", 0)),
                views     = int(stats.get("viewCount", 0)),
                date      = snip.get("publishedAt",""),
                hashtags  = [f"#{t}" for t in tags[:5]],
                raw       = {"channel": snip.get("channelTitle",""),
                             "thumbnail": snip.get("thumbnails",{}).get("high",{}).get("url","")}
            ))

    except Exception as e:
        print(f"[YouTube API] {e}")
        return _youtube_ytdlp(topic, max_videos)

    return posts


def _youtube_ytdlp(topic: str, max_videos: int = 10) -> list:
    """yt-dlp fallback for YouTube search."""
    import subprocess, sys, shutil
    posts = []
    try:
        cmd = ["yt-dlp"] if shutil.which("yt-dlp") else [sys.executable, "-m", "yt_dlp"]
        result = subprocess.run(
            cmd + [
                f"ytsearch{max_videos}:{topic}",
                "--dump-json", "--flat-playlist",
                "--no-warnings", "--quiet",
            ],
            capture_output=True, text=True, timeout=30,
            env={"PYTHONIOENCODING":"utf-8", **__import__("os").environ}
        )
        for line in result.stdout.strip().split("\n"):
            if not line.strip(): continue
            try:
                d = json.loads(line)
                posts.append(_post(
                    platform  = "YouTube",
                    post_id   = d.get("id",""),
                    title     = d.get("title",""),
                    body      = d.get("description","")[:300],
                    author    = d.get("uploader","") or d.get("channel",""),
                    url       = d.get("url","") or d.get("webpage_url",""),
                    views     = d.get("view_count") or 0,
                    likes     = d.get("like_count") or 0,
                    date      = str(d.get("upload_date","") or ""),
                    raw       = {"duration": d.get("duration",0)}
                ))
            except Exception:
                continue
    except Exception as e:
        print(f"[YouTube yt-dlp] {e}")
    return posts


# ══════════════════════════════════════════════════════════════════════════════
# TIKTOK (RapidAPI tokapi + yt-dlp fallback)
# ══════════════════════════════════════════════════════════════════════════════

def scrape_tiktok(topic: str, rapidapi_key: str = "", max_posts: int = 15) -> list:
    """
    Scrape TikTok trending/search results.
    Method 1: RapidAPI tokapi search endpoint
    Method 2: yt-dlp ytsearch on tiktok.com
    Method 3: DDG search for tiktok.com results
    """
    posts = []

    # ── Method 1: RapidAPI tokapi ────────────────────────────────────────────
    if rapidapi_key and rapidapi_key not in ("", "YOUR_RAPIDAPI_KEY"):
        # Try trending feed first
        endpoints = [
            {
                "url":    "https://tokapi-mobile-version.p.rapidapi.com/v1/feed/search",
                "params": {"keyword": topic, "count": max_posts, "offset": 0,
                           "region": "US", "with_pinned_posts": "1"},
                "host":   "tokapi-mobile-version.p.rapidapi.com",
            },
            {
                "url":    "https://tokapi-mobile-version.p.rapidapi.com/v1/hashtag/posts",
                "params": {"hashtag": topic.replace(" ","-"), "count": max_posts},
                "host":   "tokapi-mobile-version.p.rapidapi.com",
            },
        ]
        for ep in endpoints:
            try:
                r = requests.get(
                    ep["url"],
                    headers={"X-RapidAPI-Key":  rapidapi_key,
                             "X-RapidAPI-Host": ep["host"]},
                    params=ep["params"],
                    timeout=TIMEOUT,
                )
                if r.status_code != 200: continue
                data  = r.json()
                items = (data.get("aweme_list") or
                         data.get("posts") or
                         data.get("data", {}).get("aweme_list", []) or [])

                for item in items[:max_posts]:
                    vid   = item.get("aweme_id","") or item.get("id","")
                    desc  = item.get("desc","") or item.get("caption","")
                    stats = item.get("statistics",{}) or item.get("stats",{}) or {}
                    auth  = (item.get("author",{}) or {})
                    uname = auth.get("unique_id","") or auth.get("username","")
                    share_url = item.get("share_url","") or f"https://www.tiktok.com/@{uname}/video/{vid}"
                    hashtags  = [f"#{c['hashtag_name']}" for c in (item.get("text_extra",[]) or [])
                                 if c.get("hashtag_name")]

                    posts.append(_post(
                        platform  = "TikTok",
                        post_id   = vid,
                        title     = desc[:120],
                        body      = desc,
                        author    = uname,
                        url       = share_url,
                        likes     = int(stats.get("digg_count",0) or stats.get("like_count",0) or 0),
                        comments  = int(stats.get("comment_count",0) or 0),
                        shares    = int(stats.get("share_count",0) or 0),
                        views     = int(stats.get("play_count",0) or stats.get("view_count",0) or 0),
                        hashtags  = hashtags,
                        raw       = {"duration": item.get("video",{}).get("duration",0)}
                    ))
                if posts:
                    return posts
            except Exception as e:
                print(f"[TikTok RapidAPI] {e}")

    # ── Method 2: yt-dlp ─────────────────────────────────────────────────────
    import subprocess, sys, shutil
    try:
        cmd = ["yt-dlp"] if shutil.which("yt-dlp") else [sys.executable, "-m", "yt_dlp"]
        # Search TikTok via yt-dlp
        result = subprocess.run(
            cmd + [
                f"https://www.tiktok.com/search?q={requests.utils.quote(topic)}",
                "--dump-json", "--flat-playlist",
                "--no-warnings", "--quiet", "--max-downloads", str(max_posts),
            ],
            capture_output=True, text=True, timeout=45,
            env={"PYTHONIOENCODING":"utf-8", **__import__("os").environ}
        )
        for line in result.stdout.strip().split("\n"):
            if not line.strip(): continue
            try:
                d = json.loads(line)
                posts.append(_post(
                    platform = "TikTok",
                    post_id  = d.get("id",""),
                    title    = d.get("title","") or d.get("description",""),
                    body     = d.get("description",""),
                    author   = d.get("uploader","") or d.get("creator",""),
                    url      = d.get("webpage_url","") or d.get("url",""),
                    views    = d.get("view_count") or 0,
                    likes    = d.get("like_count") or 0,
                    comments = d.get("comment_count") or 0,
                    raw      = {}
                ))
            except Exception:
                continue
        if posts:
            return posts
    except Exception as e:
        print(f"[TikTok yt-dlp] {e}")

    # ── Method 3: DDG fallback ────────────────────────────────────────────────
    return _ddg_social_fallback("TikTok", topic, "site:tiktok.com", max_posts)


# ══════════════════════════════════════════════════════════════════════════════
# INSTAGRAM (RapidAPI + DDG fallback)
# ══════════════════════════════════════════════════════════════════════════════

def scrape_instagram(topic: str, rapidapi_key: str = "", max_posts: int = 12) -> list:
    """
    Scrape Instagram hashtag/explore results.
    Method 1: RapidAPI instagram-scraper-api2 hashtag search
    Method 2: DDG "site:instagram.com" fallback
    """
    posts = []

    if rapidapi_key and rapidapi_key not in ("", "YOUR_RAPIDAPI_KEY"):
        hashtag = topic.replace(" ","").lower()
        endpoints = [
            {
                "url":    "https://instagram-scraper-api2.p.rapidapi.com/v1/hashtag",
                "params": {"hashtag": hashtag},
                "host":   "instagram-scraper-api2.p.rapidapi.com",
            },
            {
                "url":    "https://instagram230.p.rapidapi.com/hashtag/medias",
                "params": {"tag": hashtag, "count": max_posts},
                "host":   "instagram230.p.rapidapi.com",
            },
        ]
        for ep in endpoints:
            try:
                r = requests.get(
                    ep["url"],
                    headers={"X-RapidAPI-Key":  rapidapi_key,
                             "X-RapidAPI-Host": ep["host"]},
                    params=ep["params"],
                    timeout=TIMEOUT,
                )
                if r.status_code != 200: continue
                data = r.json()
                # Handle multiple possible response shapes
                items = (
                    data.get("data", {}).get("items") or
                    data.get("items") or
                    data.get("medias") or
                    data.get("edge_hashtag_to_media", {}).get("edges",[]) or
                    []
                )
                for raw_item in items[:max_posts]:
                    item  = raw_item.get("node", raw_item)
                    pid   = item.get("id","") or item.get("pk","")
                    sc    = item.get("shortcode","") or item.get("code","")
                    cap   = (item.get("caption") or {})
                    if isinstance(cap, dict):
                        cap = cap.get("text","")
                    elif not isinstance(cap, str):
                        cap = ""
                    caption = _clean(cap, 300)

                    # edge_media_to_caption
                    if not caption:
                        edges = (item.get("edge_media_to_caption") or {}).get("edges",[])
                        if edges:
                            caption = edges[0].get("node",{}).get("text","")[:300]

                    likes    = (item.get("like_count") or
                                item.get("edge_media_preview_like",{}).get("count",0) or 0)
                    comments = (item.get("comment_count") or
                                item.get("edge_media_to_comment",{}).get("count",0) or 0)
                    username = (item.get("user",{}) or {}).get("username","")
                    url      = f"https://www.instagram.com/p/{sc}/" if sc else ""
                    hashtags = re.findall(r"#\w+", caption)

                    alt_text = item.get("alt_text","")
                    if not caption and not alt_text:
                        continue
                    posts.append(_post(
                        platform  = "Instagram",
                        post_id   = pid,
                        title     = (caption[:100] if caption else alt_text[:100] or f"Instagram post by @{username}"),
                        body      = caption,
                        author    = username,
                        url       = url,
                        likes     = int(likes),
                        comments  = int(comments),
                        hashtags  = hashtags[:8],
                        raw       = {"shortcode": sc,
                                     "thumbnail": item.get("thumbnail_src","") or
                                                  item.get("display_url","")}
                    ))
                if posts:
                    return posts
            except Exception as e:
                print(f"[Instagram RapidAPI] {e}")

    return _ddg_social_fallback("Instagram", topic, "site:instagram.com", max_posts)


# ══════════════════════════════════════════════════════════════════════════════
# TWITTER / X  (Nitter RSS + DDG fallback)
# ══════════════════════════════════════════════════════════════════════════════

NITTER_INSTANCES = [
    "https://nitter.poast.org",
    "https://nitter.privacydev.net",
    "https://lightbrd.com",
    "https://nitter.cz",
]

def scrape_twitter(topic: str, rapidapi_key: str = "", max_posts: int = 12) -> list:
    """
    Scrape Twitter/X posts.
    Method 1: Nitter search RSS (various public instances)
    Method 2: RapidAPI twitter241 (if key provided)
    Method 3: DDG "site:twitter.com OR site:x.com" fallback
    """
    posts = []

    # ── Method 1: Nitter RSS ─────────────────────────────────────────────────
    encoded = requests.utils.quote(topic)
    for base in NITTER_INSTANCES:
        try:
            rss_url = f"{base}/search/rss?f=tweets&q={encoded}&lang=en"
            r = requests.get(rss_url, headers=HEADERS, timeout=8)
            if r.status_code != 200: continue

            # Parse RSS/XML
            items_text = re.findall(r"<item>(.*?)</item>", r.text, re.DOTALL)
            for raw in items_text[:max_posts]:
                title_m    = re.search(r"<title><!\[CDATA\[(.*?)\]\]></title>",  raw, re.DOTALL)
                link_m     = re.search(r"<link>(.*?)</link>",                    raw)
                desc_m     = re.search(r"<description><!\[CDATA\[(.*?)\]\]></description>", raw, re.DOTALL)
                author_m   = re.search(r"<dc:creator><!\[CDATA\[(.*?)\]\]></dc:creator>",   raw, re.DOTALL)
                date_m     = re.search(r"<pubDate>(.*?)</pubDate>",              raw)

                title  = _clean(title_m.group(1)  if title_m  else "", 150)
                link   = (link_m.group(1)    if link_m    else "").strip()
                desc   = _clean(desc_m.group(1)  if desc_m   else "", 350)
                author = (author_m.group(1)  if author_m  else "").strip()
                date   = (date_m.group(1)    if date_m    else "").strip()

                if not (title or desc):
                    continue

                # Convert nitter link to twitter link
                link = link.replace(base, "https://x.com")
                hashtags = re.findall(r"#\w+", f"{title} {desc}")

                # Estimate likes from description if present
                likes_m = re.search(r"(\d+)\s+(?:likes?|♥)", desc, re.IGNORECASE)
                rt_m    = re.search(r"(\d+)\s+(?:retweets?|🔁)", desc, re.IGNORECASE)
                likes   = int(likes_m.group(1)) if likes_m else 0
                rts     = int(rt_m.group(1))    if rt_m    else 0

                posts.append(_post(
                    platform  = "Twitter/X",
                    post_id   = _uid(link),
                    title     = title or desc[:100],
                    body      = desc,
                    author    = author,
                    url       = link,
                    likes     = likes,
                    shares    = rts,
                    date      = date,
                    hashtags  = hashtags,
                    raw       = {"nitter_instance": base}
                ))

            if posts:
                return posts
        except Exception as e:
            print(f"[Nitter {base}] {e}")
        time.sleep(0.3)

    # ── Method 2: RapidAPI Twitter ───────────────────────────────────────────
    if rapidapi_key and rapidapi_key not in ("", "YOUR_RAPIDAPI_KEY"):
        try:
            r = requests.get(
                "https://twitter241.p.rapidapi.com/search-v2",
                headers={"X-RapidAPI-Key":  rapidapi_key,
                         "X-RapidAPI-Host": "twitter241.p.rapidapi.com"},
                params={"type":"Top", "count": max_posts, "query": topic},
                timeout=TIMEOUT,
            )
            if r.status_code == 200:
                data   = r.json()
                tweets = (data.get("result",{}).get("timeline",{})
                              .get("instructions",[{}])[0]
                              .get("entries",[]))
                for entry in tweets:
                    tweet = (entry.get("content",{}).get("itemContent",{})
                                  .get("tweet_results",{}).get("result",{}))
                    legacy = tweet.get("legacy",{})
                    if not legacy: continue
                    uid    = legacy.get("id_str","")
                    uname  = tweet.get("core",{}).get("user_results",{}).get("result",{}).get("legacy",{}).get("screen_name","")
                    posts.append(_post(
                        platform  = "Twitter/X",
                        post_id   = uid,
                        title     = legacy.get("full_text","")[:150],
                        body      = legacy.get("full_text",""),
                        author    = f"@{uname}",
                        url       = f"https://x.com/{uname}/status/{uid}",
                        likes     = legacy.get("favorite_count",0),
                        shares    = legacy.get("retweet_count",0),
                        date      = legacy.get("created_at",""),
                        hashtags  = [f"#{e['text']}" for e in legacy.get("entities",{}).get("hashtags",[])],
                        raw       = {}
                    ))
                if posts:
                    return posts
        except Exception as e:
            print(f"[Twitter RapidAPI] {e}")

    # ── Method 3: DDG fallback ────────────────────────────────────────────────
    return _ddg_social_fallback("Twitter/X", topic, "site:x.com OR site:twitter.com", max_posts)


# ══════════════════════════════════════════════════════════════════════════════
# GOOGLE TRENDS (pytrends — free, no API key)
# ══════════════════════════════════════════════════════════════════════════════

def scrape_google_trends(topic: str, max_items: int = 10) -> list:
    """
    Fetch rising search queries related to the topic via pytrends.
    Falls back to DDG news if pytrends not available or fails.
    """
    posts = []
    try:
        from pytrends.request import TrendReq  # pip install pytrends
        pt = TrendReq(hl="en-US", tz=360, timeout=(10,25))
        pt.build_payload([topic], cat=0, timeframe="now 7-d", geo="")

        # Rising related queries
        related = pt.related_queries()
        rising  = related.get(topic, {}).get("rising")
        if rising is not None and not rising.empty:
            for _, row in rising.iterrows():
                q     = str(row.get("query",""))
                value = row.get("value", 0)
                if not q: continue
                posts.append(_post(
                    platform  = "Google Trends",
                    post_id   = _uid(q),
                    title     = f'Rising search: "{q}"',
                    body      = f'People are increasingly searching for "{q}" related to {topic}. Relative breakout value: {value}.',
                    author    = "Google Trends",
                    url       = f"https://trends.google.com/trends/explore?q={requests.utils.quote(q)}",
                    likes     = int(value),
                    raw       = {"query": q, "breakout_value": value}
                ))
                if len(posts) >= max_items:
                    break

        # Trending Now (real-time)
        if len(posts) < max_items:
            try:
                trending = pt.trending_searches(pn="united_states")
                for t in trending.iloc[:, 0].tolist()[:5]:
                    if topic.lower() in t.lower() or any(w in t.lower() for w in topic.lower().split()):
                        posts.append(_post(
                            platform  = "Google Trends",
                            post_id   = _uid(t),
                            title     = f'🔥 Trending: "{t}"',
                            body      = f'"{t}" is currently trending on Google in the US.',
                            author    = "Google Trends",
                            url       = f"https://trends.google.com/trends/trendingsearches/daily?geo=US",
                            likes     = 999,  # trending = high signal
                            raw       = {"trending_search": t}
                        ))
            except Exception:
                pass

    except ImportError:
        print("[Google Trends] pytrends not installed — using DDG news fallback")
        return _ddg_social_fallback("Google Trends", f"{topic} trending", "", max_items, news=True)
    except Exception as e:
        print(f"[Google Trends] {e}")
        return _ddg_social_fallback("Google Trends", f"{topic} trending google", "", max_items, news=True)

    return posts



# ══════════════════════════════════════════════════════════════════════════════
# FACEBOOK (RapidAPI + instaloader-style cookies + DDG fallback)
# ══════════════════════════════════════════════════════════════════════════════

def scrape_facebook(topic: str, rapidapi_key: str = "",
                    fb_cookies: dict = None, max_posts: int = 12) -> list:
    """
    Scrape Facebook posts about a topic.
    Method 1: RapidAPI facebook-pages-scraper / facebook-data-scraper
    Method 2: Facebook Graph-style search via cookies (if provided)
    Method 3: DDG "site:facebook.com" fallback
    """
    posts = []

    # ── Method 1: RapidAPI ───────────────────────────────────────────────────
    if rapidapi_key and rapidapi_key not in ("", "YOUR_RAPIDAPI_KEY"):
        endpoints = [
            {
                "url":    "https://facebook-data-scraper.p.rapidapi.com/search_posts",
                "params": {"query": topic, "type": "POST"},
                "host":   "facebook-data-scraper.p.rapidapi.com",
            },
            {
                "url":    "https://facebook-pages-scraper.p.rapidapi.com/search",
                "params": {"query": topic, "type": "posts"},
                "host":   "facebook-pages-scraper.p.rapidapi.com",
            },
        ]
        for ep in endpoints:
            try:
                r = requests.get(
                    ep["url"],
                    headers={"X-RapidAPI-Key":  rapidapi_key,
                             "X-RapidAPI-Host": ep["host"]},
                    params=ep["params"],
                    timeout=TIMEOUT,
                )
                if r.status_code != 200:
                    continue
                data  = r.json()
                items = (data.get("data") or data.get("results") or
                         data.get("posts") or [])
                for item in items[:max_posts]:
                    pid     = str(item.get("post_id","") or item.get("id","") or _uid(str(item)))
                    message = _clean(item.get("message","") or item.get("text","") or item.get("title",""), 400)
                    if not message:
                        continue
                    author  = (item.get("from",{}) or {}).get("name","") or item.get("page_name","")
                    url     = item.get("permalink_url","") or item.get("url","") or f"https://facebook.com/{pid}"
                    likes   = int(item.get("likes","0") or item.get("like_count","0") or 0)
                    comments= int(item.get("comments","0") or item.get("comment_count","0") or 0)
                    shares  = int(item.get("shares","0") or item.get("share_count","0") or 0)
                    date    = item.get("created_time","") or item.get("date","")
                    hashtags= re.findall(r"#\w+", message)
                    posts.append(_post(
                        platform="Facebook", post_id=pid, title=message[:120],
                        body=message, author=author, url=url,
                        likes=likes, comments=comments, shares=shares,
                        date=date, hashtags=hashtags, raw=item,
                    ))
                if posts:
                    return posts
            except Exception as e:
                print(f"[Facebook RapidAPI {ep['host']}] {e}")

    # ── Method 2: Session cookies (user logged in) ────────────────────────────
    if fb_cookies and isinstance(fb_cookies, dict) and fb_cookies.get("c_user"):
        try:
            sess = requests.Session()
            sess.headers.update(HEADERS)
            for k, v in fb_cookies.items():
                sess.cookies.set(k, v, domain=".facebook.com")

            encoded = requests.utils.quote(topic)
            r = sess.get(
                f"https://www.facebook.com/search/posts?q={encoded}",
                timeout=TIMEOUT,
            )
            if r.status_code == 200 and "login" not in r.url:
                # Extract post data from embedded JSON
                json_blobs = re.findall(r'{"__typename":"Story".*?}(?=,\{"__typename"|$)', r.text)
                for blob in json_blobs[:max_posts]:
                    try:
                        d   = json.loads(blob)
                        msg = _clean(d.get("message",{}).get("text",""), 400)
                        if not msg: continue
                        pid_  = d.get("id","")
                        actor = d.get("actors",[{}])[0].get("name","") if d.get("actors") else ""
                        url_  = d.get("wwwURL","") or d.get("url","")
                        posts.append(_post(
                            platform="Facebook", post_id=pid_, title=msg[:120],
                            body=msg, author=actor, url=url_,
                            hashtags=re.findall(r"#\w+", msg), raw={}
                        ))
                    except Exception:
                        continue
        except Exception as e:
            print(f"[Facebook session] {e}")

    if posts:
        return posts

    # ── Method 3: DDG fallback ────────────────────────────────────────────────
    return _ddg_social_fallback("Facebook", topic, "site:facebook.com", max_posts)


# ══════════════════════════════════════════════════════════════════════════════
# INSTAGRAM with session cookies (instaloader)
# ══════════════════════════════════════════════════════════════════════════════

def scrape_instagram_auth(topic: str, ig_username: str = "", ig_password: str = "",
                          ig_sessionid: str = "", max_posts: int = 12) -> list:
    """
    Scrape Instagram hashtag with authenticated session via instaloader.
    Falls back to RapidAPI / DDG if credentials not provided.
    """
    if not (ig_sessionid or (ig_username and ig_password)):
        return []

    posts = []
    try:
        import instaloader
        L = instaloader.Instaloader(
            download_pictures=False, download_videos=False,
            download_video_thumbnails=False, download_geotags=False,
            download_comments=False, save_metadata=False,
            quiet=True,
        )
        if ig_sessionid:
            # Use session cookie directly (safer)
            L.context._session.cookies.set("sessionid", ig_sessionid,
                                            domain=".instagram.com")
            L.context.username = ig_username or "user"
        else:
            L.login(ig_username, ig_password)

        hashtag = topic.replace(" ","").replace("#","").lower()
        tag = instaloader.Hashtag.from_name(L.context, hashtag)

        for post in tag.get_top_posts():
            try:
                caption = _clean(post.caption or "", 400)
                posts.append(_post(
                    platform  = "Instagram",
                    post_id   = str(post.mediaid),
                    title     = caption[:120] or f"Instagram post by @{post.owner_username}",
                    body      = caption,
                    author    = post.owner_username,
                    url       = f"https://www.instagram.com/p/{post.shortcode}/",
                    likes     = post.likes,
                    comments  = post.comments,
                    date      = str(post.date_utc.timestamp()) if post.date_utc else "",
                    hashtags  = [f"#{t}" for t in (post.caption_hashtags or [])],
                    raw       = {"shortcode": post.shortcode,
                                 "typename": post.typename}
                ))
                if len(posts) >= max_posts:
                    break
            except Exception:
                continue
    except Exception as e:
        print(f"[Instagram instaloader] {e}")

    return posts


# ══════════════════════════════════════════════════════════════════════════════
# DDG SOCIAL FALLBACK (when platform scraping fails)
# ══════════════════════════════════════════════════════════════════════════════

def _ddg_social_fallback(platform: str, topic: str, site_filter: str,
                          max_posts: int = 10, news: bool = False) -> list:
    """
    DDG text/news search as last resort when direct platform scraping fails.
    Returns posts marked with the platform but sourced from DDG.
    """
    posts = []
    query = f"{topic} {site_filter}" if site_filter else topic
    try:
        with DDGS() as d:
            results = list(d.news(query, max_results=max_posts) if news
                           else d.text(query, max_results=max_posts))
        for r in results:
            title = _clean(r.get("title",""), 150)
            body  = _clean(r.get("body",""), 350)
            url   = r.get("url","") or r.get("href","")
            if not title: continue
            posts.append(_post(
                platform  = platform,
                post_id   = _uid(url),
                title     = title,
                body      = body,
                author    = r.get("source",""),
                url       = url,
                date      = r.get("date",""),
                hashtags  = re.findall(r"#\w+", f"{title} {body}"),
                raw       = {"source": "ddg_fallback"}
            ))
    except Exception as e:
        print(f"[DDG fallback {platform}] {e}")
    return posts


# ══════════════════════════════════════════════════════════════════════════════
# ORCHESTRATOR — fetch all selected platforms
# ══════════════════════════════════════════════════════════════════════════════

PLATFORM_CONFIG = {
    "Reddit":        {"icon": "🟠", "color": "#ff4500", "needs_key": False},
    "YouTube":       {"icon": "🔴", "color": "#ff0000", "needs_key": "youtube"},
    "TikTok":        {"icon": "⚫", "color": "#1d9bf0", "needs_key": "rapidapi"},
    "Instagram":     {"icon": "🟣", "color": "#e1306c", "needs_key": "rapidapi"},
    "Facebook":      {"icon": "🔵", "color": "#1877f2", "needs_key": "optional"},
    "Twitter/X":     {"icon": "🐦", "color": "#1da1f2", "needs_key": False},
    "Google Trends": {"icon": "📈", "color": "#4285f4", "needs_key": False},
}


def fetch_social_trends(
    topic: str,
    platforms: list,
    rapidapi_key: str = "",
    youtube_api_key: str = "",
    max_per_platform: int = 10,
    # account credentials
    ig_username: str = "",
    ig_password: str = "",
    ig_sessionid: str = "",
    fb_cookies: dict = None,
) -> list:
    """
    Fetch posts from all selected platforms and return combined list.
    Supports authenticated scraping for Instagram and Facebook.
    """
    all_posts = []
    seen_ids  = set()

    for platform in platforms:
        try:
            if platform == "Reddit":
                new = scrape_reddit(topic, max_per_platform)
            elif platform == "YouTube":
                new = scrape_youtube(topic, youtube_api_key, max_per_platform)
            elif platform == "TikTok":
                new = scrape_tiktok(topic, rapidapi_key, max_per_platform)
            elif platform == "Instagram":
                # Try authenticated first if credentials provided
                auth_posts = []
                if ig_sessionid or (ig_username and ig_password):
                    auth_posts = scrape_instagram_auth(
                        topic, ig_username, ig_password, ig_sessionid, max_per_platform
                    )
                new = auth_posts if auth_posts else scrape_instagram(topic, rapidapi_key, max_per_platform)
            elif platform == "Facebook":
                new = scrape_facebook(topic, rapidapi_key, fb_cookies, max_per_platform)
            elif platform == "Twitter/X":
                new = scrape_twitter(topic, rapidapi_key, max_per_platform)
            elif platform == "Google Trends":
                new = scrape_google_trends(topic, max_per_platform)
            else:
                continue

            for p in new:
                if p["id"] not in seen_ids:
                    seen_ids.add(p["id"])
                    all_posts.append(p)

        except Exception as e:
            print(f"[{platform}] Scraper error: {e}")
        time.sleep(0.4)

    return all_posts


# ══════════════════════════════════════════════════════════════════════════════
# AI ENRICHMENT (same pattern as market_research.py)
# ══════════════════════════════════════════════════════════════════════════════

def enrich_social_posts(groq_client, posts: list, topic: str,
                         target_platform: str, brand_context: str = "") -> list:
    """
    AI enrichment: content_angle, hook_idea, content_score,
    brand_relevance, brand_angle, emotion, format_fit, tags.
    """
    if not posts:
        return posts

    brand_section = ""
    if brand_context.strip():
        brand_section = f"\nBRAND CONTEXT (score brand_relevance and brand_angle against this):\n{brand_context[:700]}\n"

    lines = [
        f"{i}: [{p['platform']}] {p['title'][:80]} | {p['body'][:100]} | likes={p['likes']} views={p['views']}"
        for i, p in enumerate(posts[:24])
    ]

    prompt = f"""Expert viral content strategist.
Research topic: "{topic}" | Target platform for scripts: {target_platform}
{brand_section}
Enrich these {len(lines)} social media posts. Return ONLY a JSON array:

{chr(10).join(lines)}

[
  {{
    "index": 0,
    "content_angle": "specific punchy viral angle based on this post",
    "hook_idea": "first 8-12 words of a scroll-stopping hook using this content",
    "content_score": <0-100, viral potential as {target_platform} content>,
    "brand_relevance": <0-100, fit with brand context — 0 if no brand given>,
    "brand_angle": "how to connect this trend to the brand (empty if no brand)",
    "emotion": "Curiosity / Surprise / FOMO / Fear / Inspiration / Validation / Outrage / Hope",
    "format_fit": "Talking Head / Voiceover / Listicle / Story / Controversy / Tutorial / Reaction",
    "tags": ["tag1", "tag2", "tag3"]
  }}
]

Scoring:
- content_score: engagement signal strength (30%) + novelty (25%) + {target_platform} fit (25%) + shareability (20%)
- brand_relevance: direct relevance of this trend to the brand's products, audience, or values"""

    try:
        resp = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role":"system","content":"Expert content strategist. Return ONLY valid JSON array, no markdown, no text."},
                {"role":"user","content":prompt}
            ],
            max_tokens=2800, temperature=0.3
        )
        raw = resp.choices[0].message.content.strip()
        raw = re.sub(r"^```json\s*","",raw); raw = re.sub(r"^```\s*","",raw); raw = re.sub(r"\s*```$","",raw)
        enrichments = json.loads(raw)
        em = {e["index"]: e for e in enrichments if isinstance(e.get("index"), int)}
        for i, post in enumerate(posts[:24]):
            e = em.get(i, {})
            post["content_angle"]  = e.get("content_angle","")
            post["hook_idea"]      = e.get("hook_idea","")
            post["content_score"]  = int(e.get("content_score", 50))
            post["brand_relevance"]= int(e.get("brand_relevance", 0))
            post["brand_angle"]    = e.get("brand_angle","")
            post["emotion"]        = e.get("emotion","")
            post["format_fit"]     = e.get("format_fit","")
            post["tags"]           = e.get("tags",[])[:4]
    except Exception as ex:
        print(f"[enrich_social_posts] {ex}")
        for p in posts:
            p.setdefault("content_score",50); p.setdefault("brand_relevance",0)
            p.setdefault("content_angle",""); p.setdefault("hook_idea","")
            p.setdefault("brand_angle",""); p.setdefault("emotion","")
            p.setdefault("format_fit",""); p.setdefault("tags",[])

    if brand_context.strip():
        posts.sort(key=lambda x: x.get("content_score",0)*0.5 + x.get("brand_relevance",0)*0.5, reverse=True)
    else:
        posts.sort(key=lambda x: x.get("content_score",0), reverse=True)

    return posts
