# modules/creator_analyzer.py
"""
Creator account analyzer for TikTok, Instagram, and YouTube.
Fetches profile data, recent videos, content patterns,
then runs AI analysis on content strategy and growth opportunities.

Methods per platform:
  YouTube:   yt-dlp (no API key needed)
  TikTok:    RapidAPI Tokapi → yt-dlp search → DuckDuckGo fallback
  Instagram: RapidAPI → instaloader → DuckDuckGo fallback
"""

import os, re, sys, json, shutil, subprocess, tempfile
import requests
from duckduckgo_search import DDGS


# ── YouTube via yt-dlp ────────────────────────────────────────────────────────

def _ytdlp_cmd():
    if shutil.which("yt-dlp"):
        return ["yt-dlp"]
    return [sys.executable, "-m", "yt_dlp"]


def fetch_youtube_creator(username: str, max_videos: int = 15) -> dict:
    """
    Fetch YouTube channel profile + recent videos via yt-dlp.
    username can be @handle, channel name, or channel URL.
    """
    # Normalize to URL
    if username.startswith("http"):
        channel_url = username
    elif username.startswith("@"):
        channel_url = f"https://www.youtube.com/{username}/videos"
    else:
        channel_url = f"https://www.youtube.com/@{username}/videos"

    profile = {
        "platform":      "YouTube",
        "username":      username,
        "display_name":  "",
        "bio":           "",
        "followers":     0,
        "total_videos":  0,
        "videos":        [],
        "error":         None,
    }

    try:
        # Get channel metadata + recent video list
        result = subprocess.run(
            _ytdlp_cmd() + [
                "--dump-json", "--flat-playlist",
                "--playlist-items", f"1:{max_videos}",
                "--no-warnings", channel_url
            ],
            capture_output=True, text=True, timeout=60
        )

        lines = [l for l in result.stdout.strip().split("\n") if l.strip()]
        videos = []
        channel_info = {}

        for line in lines:
            try:
                data = json.loads(line)
                if data.get("_type") == "url" or data.get("ie_key"):
                    # It's a video entry from flat playlist
                    videos.append({
                        "title":      data.get("title", ""),
                        "url":        data.get("url") or data.get("webpage_url", ""),
                        "views":      data.get("view_count") or 0,
                        "likes":      data.get("like_count") or 0,
                        "comments":   data.get("comment_count") or 0,
                        "duration":   data.get("duration") or 0,
                        "upload_date":data.get("upload_date", ""),
                        "thumbnail":  data.get("thumbnail", ""),
                        "description":(data.get("description") or "")[:200],
                    })
                elif data.get("channel") or data.get("uploader"):
                    channel_info = data
            except Exception:
                continue

        if not videos and result.returncode != 0:
            profile["error"] = f"Could not fetch channel. Check the username spelling."
            return profile

        profile["display_name"] = channel_info.get("channel") or channel_info.get("uploader") or username
        profile["bio"]          = (channel_info.get("description") or "")[:500]
        profile["followers"]    = channel_info.get("channel_follower_count") or 0
        profile["total_videos"] = len(videos)
        profile["videos"]       = videos

    except Exception as e:
        profile["error"] = str(e)

    return profile


# ── TikTok ────────────────────────────────────────────────────────────────────

def fetch_tiktok_creator(username: str, rapidapi_key: str = "", max_videos: int = 15) -> dict:
    """Fetch TikTok creator profile + recent videos."""
    username = username.lstrip("@")

    profile = {
        "platform":     "TikTok",
        "username":     username,
        "display_name": "",
        "bio":          "",
        "followers":    0,
        "following":    0,
        "likes":        0,
        "total_videos": 0,
        "videos":       [],
        "error":        None,
        "method":       "",
    }

    # Method 1: RapidAPI Tokapi
    if rapidapi_key and rapidapi_key != "YOUR_RAPIDAPI_KEY":
        try:
            headers = {
                "X-RapidAPI-Key":  rapidapi_key,
                "X-RapidAPI-Host": "tokapi-mobile-version.p.rapidapi.com"
            }
            # Get user info
            r = requests.get(
                "https://tokapi-mobile-version.p.rapidapi.com/v1/user/@" + username,
                headers=headers, timeout=10
            )
            data = r.json()
            user = (data.get("user_info") or data.get("user") or
                    data.get("data", {}).get("user") or {})
            stats = user.get("stats") or user.get("user_stat") or {}

            if user:
                profile["display_name"] = user.get("nickname") or user.get("name") or username
                profile["bio"]          = user.get("signature") or user.get("bio") or ""
                profile["followers"]    = stats.get("followerCount") or stats.get("fans_count") or 0
                profile["following"]    = stats.get("followingCount") or 0
                profile["likes"]        = stats.get("heartCount") or stats.get("like_count") or 0
                profile["method"]       = "RapidAPI"

            # Get user videos
            r2 = requests.get(
                "https://tokapi-mobile-version.p.rapidapi.com/v1/post/user/@" + username,
                headers=headers,
                params={"count": max_videos, "offset": 0},
                timeout=10
            )
            vdata = r2.json()
            raw_videos = (vdata.get("aweme_list") or vdata.get("video_list") or
                          vdata.get("data", {}).get("videos") or [])

            for v in raw_videos:
                vstats = v.get("statistics") or v.get("stats") or {}
                desc   = v.get("desc") or v.get("title") or ""
                profile["videos"].append({
                    "title":       desc[:120],
                    "views":       vstats.get("play_count") or vstats.get("view_count") or 0,
                    "likes":       vstats.get("digg_count") or vstats.get("like_count") or 0,
                    "comments":    vstats.get("comment_count") or 0,
                    "shares":      vstats.get("share_count") or 0,
                    "duration":    (v.get("video") or {}).get("duration") or 0,
                    "upload_date": str(v.get("create_time", "")),
                })

            if profile["videos"]:
                profile["total_videos"] = len(profile["videos"])
                return profile

        except Exception as e:
            print(f"[TikTok RapidAPI] {e}")

    # Method 2: yt-dlp
    try:
        url = f"https://www.tiktok.com/@{username}"
        result = subprocess.run(
            _ytdlp_cmd() + [
                "--dump-json", "--flat-playlist",
                "--playlist-items", f"1:{max_videos}",
                "--no-warnings", url
            ],
            capture_output=True, text=True, timeout=60
        )
        for line in result.stdout.strip().split("\n"):
            if not line.strip():
                continue
            try:
                data = json.loads(line)
                title = data.get("title") or data.get("description") or ""
                if title:
                    profile["videos"].append({
                        "title":       title[:120],
                        "views":       data.get("view_count") or 0,
                        "likes":       data.get("like_count") or 0,
                        "comments":    data.get("comment_count") or 0,
                        "shares":      0,
                        "duration":    data.get("duration") or 0,
                        "upload_date": data.get("upload_date", ""),
                    })
                    if not profile["display_name"]:
                        profile["display_name"] = data.get("uploader") or username
            except Exception:
                continue

        if profile["videos"]:
            profile["total_videos"] = len(profile["videos"])
            profile["method"] = "yt-dlp"
            return profile

    except Exception as e:
        print(f"[TikTok yt-dlp] {e}")

    # Method 3: DuckDuckGo scrape for public info
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(f"site:tiktok.com @{username} videos", max_results=10))
        videos = []
        for r in results:
            body = r.get("body", "")
            if body:
                videos.append({
                    "title": body[:120], "views": 0, "likes": 0,
                    "comments": 0, "shares": 0, "duration": 0, "upload_date": "",
                })
        profile["videos"]       = videos
        profile["total_videos"] = len(videos)
        profile["method"]       = "DuckDuckGo (limited data)"
        if not videos:
            profile["error"] = "No data found. Try adding a RapidAPI key for full TikTok access."
    except Exception as e:
        profile["error"] = str(e)

    return profile


# ── Instagram ─────────────────────────────────────────────────────────────────

def fetch_instagram_creator(username: str, rapidapi_key: str = "", max_videos: int = 15) -> dict:
    """Fetch Instagram creator profile + recent posts."""
    username = username.lstrip("@")

    profile = {
        "platform":     "Instagram",
        "username":     username,
        "display_name": "",
        "bio":          "",
        "followers":    0,
        "following":    0,
        "posts_count":  0,
        "total_videos": 0,
        "videos":       [],
        "error":        None,
        "method":       "",
    }

    # Method 1: RapidAPI
    if rapidapi_key and rapidapi_key != "YOUR_RAPIDAPI_KEY":
        # Try instagram-scraper-api2
        try:
            headers = {
                "X-RapidAPI-Key":  rapidapi_key,
                "X-RapidAPI-Host": "instagram-scraper-api2.p.rapidapi.com"
            }
            r = requests.get(
                "https://instagram-scraper-api2.p.rapidapi.com/v1/info",
                headers=headers,
                params={"username_or_id_or_url": username},
                timeout=10
            )
            data = r.json().get("data", {})
            if data:
                profile["display_name"] = data.get("full_name") or username
                profile["bio"]          = data.get("biography") or ""
                profile["followers"]    = data.get("follower_count") or 0
                profile["following"]    = data.get("following_count") or 0
                profile["posts_count"]  = data.get("media_count") or 0
                profile["method"]       = "RapidAPI"

            # Get posts
            r2 = requests.get(
                "https://instagram-scraper-api2.p.rapidapi.com/v1/posts",
                headers=headers,
                params={"username_or_id_or_url": username, "count": max_videos},
                timeout=10
            )
            posts = r2.json().get("data", {}).get("items") or []
            for p in posts:
                caption  = (p.get("caption") or {}).get("text") or ""
                is_video = p.get("media_type") == 2 or p.get("is_video")
                profile["videos"].append({
                    "title":       caption[:120],
                    "views":       p.get("view_count") or p.get("video_view_count") or 0,
                    "likes":       p.get("like_count") or 0,
                    "comments":    p.get("comment_count") or 0,
                    "shares":      0,
                    "duration":    p.get("video_duration") or 0,
                    "upload_date": str(p.get("taken_at", "")),
                    "type":        "reel" if is_video else "post",
                })

            if profile["videos"]:
                profile["total_videos"] = len(profile["videos"])
                return profile

        except Exception as e:
            print(f"[Instagram RapidAPI] {e}")

    # Method 2: instaloader
    try:
        import instaloader
        L = instaloader.Instaloader()
        ig_profile = instaloader.Profile.from_username(L.context, username)
        profile["display_name"] = ig_profile.full_name or username
        profile["bio"]          = ig_profile.biography or ""
        profile["followers"]    = ig_profile.followers
        profile["following"]    = ig_profile.followees
        profile["posts_count"]  = ig_profile.mediacount
        profile["method"]       = "instaloader"

        for i, post in enumerate(ig_profile.get_posts()):
            if i >= max_videos:
                break
            caption = post.caption or ""
            profile["videos"].append({
                "title":       caption[:120],
                "views":       post.video_view_count if post.is_video else 0,
                "likes":       post.likes,
                "comments":    post.comments,
                "shares":      0,
                "duration":    0,
                "upload_date": post.date_utc.strftime("%Y%m%d") if post.date_utc else "",
                "type":        "reel" if post.is_video else "post",
            })

        profile["total_videos"] = len(profile["videos"])
        return profile

    except ImportError:
        print("[Instagram] instaloader not installed")
    except Exception as e:
        print(f"[Instagram instaloader] {e}")

    # Method 3: DuckDuckGo
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(f"instagram.com/{username} posts reels", max_results=10))
        for r in results:
            body = r.get("body", "")
            if body:
                profile["videos"].append({
                    "title": body[:120], "views": 0, "likes": 0,
                    "comments": 0, "shares": 0, "duration": 0,
                    "upload_date": "", "type": "post",
                })
        profile["total_videos"] = len(profile["videos"])
        profile["method"]       = "DuckDuckGo (limited data)"
        if not profile["videos"]:
            profile["error"] = "No data found. Add RapidAPI key or install instaloader for full access."
    except Exception as e:
        profile["error"] = str(e)

    return profile


# ── AI Analysis Engine ────────────────────────────────────────────────────────

def analyze_creator(groq_client, profile: dict) -> dict:
    """
    Deep AI analysis of creator profile and content strategy.
    Returns structured insights report.
    """
    platform = profile.get("platform", "")
    username = profile.get("username", "")
    videos   = profile.get("videos", [])

    # Build video summary for prompt
    video_lines = []
    for i, v in enumerate(videos[:20]):
        title    = v.get("title", "")[:80]
        views    = v.get("views", 0)
        likes    = v.get("likes", 0)
        comments = v.get("comments", 0)
        dur      = v.get("duration", 0)
        vtype    = v.get("type", "")
        views_str = f"{views/1000:.0f}K" if views >= 1000 else str(views)
        likes_str = f"{likes/1000:.0f}K" if likes >= 1000 else str(likes)
        line = f"{i+1}. [{vtype or 'video'}] {title}"
        if views: line += f" | 👁️{views_str}"
        if likes: line += f" | ❤️{likes_str}"
        if comments: line += f" | 💬{comments}"
        if dur:   line += f" | ⏱️{dur}s"
        video_lines.append(line)

    video_summary = "\n".join(video_lines) if video_lines else "No video data available"

    followers   = profile.get("followers", 0)
    bio         = profile.get("bio", "")
    total_vids  = profile.get("total_videos", 0)

    prompt = f"""You are an elite social media strategist and creator analytics expert.
Analyze this {platform} creator account and provide deep strategic insights.

CREATOR PROFILE:
Platform:  {platform}
Username:  @{username}
Name:      {profile.get("display_name", username)}
Bio:       {bio[:300]}
Followers: {followers:,}
Videos:    {total_vids}

RECENT CONTENT ({len(videos)} videos):
{video_summary}

Provide a comprehensive creator analysis. Return ONLY valid JSON, no markdown:
{{
  "creator_archetype": "e.g. 'The Educator', 'The Entertainer', 'The Storyteller', 'The Expert', etc.",
  "content_pillars": ["main topic 1", "main topic 2", "main topic 3"],
  "posting_style": "description of their format style (e.g. 'fast-cut tutorials with text overlay')",
  "audience_profile": "who their audience likely is",
  "tone": "brand voice description",
  "strengths": ["strength 1", "strength 2", "strength 3"],
  "weaknesses": ["weakness 1", "weakness 2", "weakness 3"],
  "growth_opportunities": ["opportunity 1", "opportunity 2", "opportunity 3"],
  "top_performing_themes": ["theme from highest engagement videos"],
  "content_gaps": ["topics they're missing that their audience would love"],
  "hook_patterns": "what opening patterns they use most",
  "engagement_rate": "estimated engagement rate based on likes/views data",
  "posting_frequency": "estimated frequency based on video count and dates",
  "viral_formula": "what pattern their best content follows",
  "monetization_potential": "Low/Medium/High/Very High",
  "collaboration_fit": "what type of brands or creators they'd work well with",
  "next_3_video_ideas": [
    {{"title": "video idea 1", "hook": "opening hook", "why": "why this would perform well"}},
    {{"title": "video idea 2", "hook": "opening hook", "why": "why this would perform well"}},
    {{"title": "video idea 3", "hook": "opening hook", "why": "why this would perform well"}}
  ],
  "overall_score": 0-100,
  "tier": "Nano/Micro/Mid/Macro/Mega",
  "summary": "2-3 sentence executive summary of this creator"
}}"""

    try:
        resp = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a creator analytics expert. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.3
        )
        raw = resp.choices[0].message.content.strip()
        raw = re.sub(r"^```json\s*", "", raw)
        raw = re.sub(r"^```\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
        return json.loads(raw)
    except Exception as e:
        print(f"[CreatorAnalysis] {e}")
        return {"error": str(e), "summary": "Analysis failed"}


def compute_video_stats(videos: list) -> dict:
    """Compute aggregate stats from video list."""
    if not videos:
        return {}

    views_list    = [v.get("views", 0) for v in videos if v.get("views", 0) > 0]
    likes_list    = [v.get("likes", 0) for v in videos if v.get("likes", 0) > 0]
    comments_list = [v.get("comments", 0) for v in videos if v.get("comments", 0) > 0]
    durations     = [v.get("duration", 0) for v in videos if v.get("duration", 0) > 0]

    def safe_avg(lst):
        return int(sum(lst) / len(lst)) if lst else 0

    total_views = sum(views_list)
    avg_views   = safe_avg(views_list)
    avg_likes   = safe_avg(likes_list)

    # Engagement rate = (likes + comments) / views
    total_likes    = sum(likes_list)
    total_comments = sum(comments_list)
    eng_rate       = ((total_likes + total_comments) / total_views * 100) if total_views > 0 else 0

    # Top videos by views
    top_videos = sorted(videos, key=lambda x: x.get("views", 0), reverse=True)[:5]

    return {
        "total_views":    total_views,
        "avg_views":      avg_views,
        "avg_likes":      avg_likes,
        "avg_comments":   safe_avg(comments_list),
        "avg_duration":   safe_avg(durations),
        "engagement_rate": round(eng_rate, 2),
        "top_videos":     top_videos,
        "total_likes":    total_likes,
        "total_comments": total_comments,
    }
