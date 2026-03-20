# modules/creator_analyzer.py
"""
Creator account analyzer — TikTok, Instagram, YouTube.

APIs used:
  YouTube:   YouTube Data API v3 (free key from console.cloud.google.com)
             Fallback: yt-dlp subprocess
  TikTok:    RapidAPI tokapi-mobile-version
             Fallback: yt-dlp subprocess → DuckDuckGo
  Instagram: RapidAPI instagram-scraper-api2
             Fallback: instaloader → DuckDuckGo

Pattern extraction:
  Downloads top 3 videos via yt-dlp → Groq Whisper → AI style analysis
"""

import os, re, sys, json, shutil, subprocess, tempfile, time
import requests
from ddgs import DDGS


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def fmt_num(n):
    if not n: return "0"
    if n >= 1_000_000: return f"{n/1_000_000:.1f}M"
    if n >= 1_000:     return f"{n/1_000:.0f}K"
    return str(n)

def ytdlp_cmd():
    if shutil.which("yt-dlp"):
        return ["yt-dlp"]
    return [sys.executable, "-m", "yt_dlp"]

def run_ytdlp(args, timeout=90):
    """Run yt-dlp with args, return (stdout_lines, error_str)."""
    try:
        r = subprocess.run(
            ytdlp_cmd() + args,
            capture_output=True, text=True, timeout=timeout,
            env={**os.environ, "PYTHONIOENCODING": "utf-8"}
        )
        lines = [l for l in r.stdout.strip().split("\n") if l.strip()]
        return lines, r.stderr[:400] if r.returncode != 0 else ""
    except subprocess.TimeoutExpired:
        return [], "yt-dlp timed out"
    except Exception as e:
        return [], str(e)

def parse_ytdlp_video(data: dict, username: str = "") -> dict:
    """Normalize a yt-dlp flat-playlist JSON entry into our video schema."""
    vid_id = data.get("id") or data.get("display_id") or ""
    url    = (data.get("url") or data.get("webpage_url") or
              data.get("original_url") or "")
    if not url and vid_id:
        # Reconstruct URL from extractor
        extractor = (data.get("ie_key") or data.get("extractor") or "").lower()
        if "youtube" in extractor:
            url = f"https://www.youtube.com/watch?v={vid_id}"
        elif "tiktok" in extractor:
            url = f"https://www.tiktok.com/@{username}/video/{vid_id}"
    return {
        "video_id":    vid_id,
        "title":       (data.get("title") or data.get("description") or "")[:150],
        "description": (data.get("description") or "")[:200],
        "url":         url,
        "thumbnail":   data.get("thumbnail") or "",
        "views":       int(data.get("view_count") or 0),
        "likes":       int(data.get("like_count") or 0),
        "comments":    int(data.get("comment_count") or 0),
        "shares":      int(data.get("repost_count") or 0),
        "duration":    int(data.get("duration") or 0),
        "upload_date": (data.get("upload_date") or data.get("timestamp") or ""),
        "type":        "short" if int(data.get("duration") or 0) <= 60 else "video",
    }


# ─────────────────────────────────────────────────────────────────────────────
# YouTube
# ─────────────────────────────────────────────────────────────────────────────

def _yt_api(endpoint, params, api_key):
    params["key"] = api_key
    r = requests.get(
        f"https://www.googleapis.com/youtube/v3/{endpoint}",
        params=params, timeout=15
    )
    r.raise_for_status()
    return r.json()

def fetch_youtube_creator(username: str, api_key: str = "", max_videos: int = 20) -> dict:
    profile = {
        "platform": "YouTube", "username": username.lstrip("@"),
        "display_name": "", "bio": "",
        "subscribers": 0, "total_video_count": 0,
        "videos": [], "error": None, "method": "",
        "debug": [],
    }

    # ── YouTube Data API v3 ───────────────────────────────────────────────────
    if api_key:
        try:
            handle = username.lstrip("@")
            # Search for channel
            search = _yt_api("search", {
                "part": "snippet", "q": handle,
                "type": "channel", "maxResults": 3
            }, api_key)
            channel_id = None
            for item in search.get("items", []):
                if item.get("id", {}).get("channelId"):
                    channel_id = item["id"]["channelId"]
                    break
            if not channel_id:
                profile["debug"].append("YouTube API: channel not found in search")
            else:
                # Get channel details
                ch = _yt_api("channels", {
                    "part": "snippet,statistics,contentDetails",
                    "id": channel_id
                }, api_key)
                ch_item = (ch.get("items") or [{}])[0]
                snip  = ch_item.get("snippet", {})
                stats = ch_item.get("statistics", {})
                cd    = ch_item.get("contentDetails", {})

                profile["display_name"]      = snip.get("title", username)
                profile["bio"]               = snip.get("description", "")[:600]
                profile["subscribers"]       = int(stats.get("subscriberCount") or 0)
                profile["total_video_count"] = int(stats.get("videoCount") or 0)
                profile["method"]            = "YouTube Data API v3"

                uploads_id = cd.get("relatedPlaylists", {}).get("uploads", "")
                if not uploads_id:
                    uploads_id = "UU" + channel_id[2:]

                # Fetch videos in batches
                videos, next_page = [], None
                while len(videos) < max_videos:
                    pl_params = {
                        "part": "snippet,contentDetails",
                        "playlistId": uploads_id,
                        "maxResults": min(50, max_videos - len(videos))
                    }
                    if next_page:
                        pl_params["pageToken"] = next_page
                    pl = _yt_api("playlistItems", pl_params, api_key)
                    vid_ids = [
                        i["contentDetails"]["videoId"]
                        for i in pl.get("items", [])
                        if i.get("contentDetails", {}).get("videoId")
                    ]
                    if not vid_ids:
                        break

                    vstat = _yt_api("videos", {
                        "part": "statistics,contentDetails,snippet",
                        "id": ",".join(vid_ids)
                    }, api_key)

                    for v in vstat.get("items", []):
                        s  = v.get("statistics", {})
                        cd2 = v.get("contentDetails", {})
                        sn = v.get("snippet", {})
                        dr = cd2.get("duration", "PT0S")
                        dm = re.search(r'(\d+)M', dr)
                        ds = re.search(r'(\d+)S', dr)
                        dur = (int(dm.group(1)) * 60 if dm else 0) + (int(ds.group(1)) if ds else 0)
                        videos.append({
                            "video_id":    v["id"],
                            "title":       sn.get("title", ""),
                            "description": sn.get("description", "")[:200],
                            "url":         f"https://www.youtube.com/watch?v={v['id']}",
                            "thumbnail":   sn.get("thumbnails", {}).get("medium", {}).get("url", ""),
                            "views":       int(s.get("viewCount") or 0),
                            "likes":       int(s.get("likeCount") or 0),
                            "comments":    int(s.get("commentCount") or 0),
                            "shares":      0,
                            "duration":    dur,
                            "upload_date": sn.get("publishedAt", "")[:10],
                            "type":        "short" if dur <= 60 else "video",
                        })
                    next_page = pl.get("nextPageToken")
                    if not next_page:
                        break

                profile["videos"] = videos[:max_videos]
                if videos:
                    return profile
                else:
                    profile["debug"].append("YouTube API: no videos found in uploads playlist")
        except Exception as e:
            profile["debug"].append(f"YouTube API error: {e}")

    # ── yt-dlp fallback ────────────────────────────────────────────────────────
    handle = username.strip()
    if not handle.startswith("http"):
        if not handle.startswith("@"):
            handle = "@" + handle
        channel_url = f"https://www.youtube.com/{handle}/videos"
    else:
        channel_url = handle

    profile["debug"].append(f"yt-dlp fetching: {channel_url}")
    lines, err = run_ytdlp([
        "--dump-json", "--flat-playlist",
        "--playlist-items", f"1:{max_videos}",
        "--no-warnings", channel_url
    ])
    profile["debug"].append(f"yt-dlp returned {len(lines)} lines, err: {err[:100] if err else 'none'}")

    videos = []
    for line in lines:
        try:
            data = json.loads(line)
            v = parse_ytdlp_video(data, profile["username"])
            if v["title"] or v["video_id"]:
                videos.append(v)
                if not profile["display_name"]:
                    profile["display_name"] = data.get("channel") or data.get("uploader") or username
        except Exception:
            continue

    profile["videos"] = videos
    profile["method"] = "yt-dlp"
    if not videos:
        profile["error"] = f"No videos found. yt-dlp error: {err}" if err else \
                           "No videos found — channel may be private or handle incorrect."
    return profile


# ─────────────────────────────────────────────────────────────────────────────
# TikTok
# ─────────────────────────────────────────────────────────────────────────────

def fetch_tiktok_creator(username: str, rapidapi_key: str = "", max_videos: int = 20) -> dict:
    username = username.lstrip("@")
    profile = {
        "platform": "TikTok", "username": username,
        "display_name": "", "bio": "", "avatar": "",
        "followers": 0, "following": 0, "likes": 0,
        "total_video_count": 0, "videos": [],
        "error": None, "method": "", "debug": [],
    }

    # ── RapidAPI Tokapi ───────────────────────────────────────────────────────
    if rapidapi_key and rapidapi_key not in ("", "YOUR_RAPIDAPI_KEY"):
        hdr = {
            "X-RapidAPI-Key":  rapidapi_key,
            "X-RapidAPI-Host": "tokapi-mobile-version.p.rapidapi.com"
        }

        # Fetch user profile
        try:
            r    = requests.get(
                f"https://tokapi-mobile-version.p.rapidapi.com/v1/user/@{username}",
                headers=hdr, timeout=12
            )
            data = r.json()
            # Handle multiple response shapes
            user = (data.get("user_info") or
                    data.get("user") or
                    (data.get("data") or {}).get("user") or {})
            st   = (user.get("stats") or user.get("user_stat") or
                    user.get("statistics") or {})
            if user:
                profile["display_name"] = user.get("nickname") or username
                profile["bio"]          = user.get("signature") or ""
                profile["followers"]    = int(st.get("followerCount") or st.get("fans_count") or 0)
                profile["following"]    = int(st.get("followingCount") or 0)
                profile["likes"]        = int(st.get("heartCount") or st.get("like_count") or 0)
            profile["debug"].append(f"RapidAPI profile: display={profile['display_name']}, followers={profile['followers']}")
        except Exception as e:
            profile["debug"].append(f"RapidAPI profile error: {e}")

        # Fetch videos — try multiple endpoints
        for ep, params in [
            (f"https://tokapi-mobile-version.p.rapidapi.com/v1/post/user/@{username}",
             {"count": max_videos, "offset": 0}),
            (f"https://tokapi-mobile-version.p.rapidapi.com/v1/user/posts",
             {"unique_id": username, "count": max_videos, "cursor": 0}),
        ]:
            try:
                r    = requests.get(ep, headers=hdr, params=params, timeout=12)
                body = r.json()
                raw  = (body.get("aweme_list") or body.get("video_list") or
                        (body.get("data") or {}).get("videos") or
                        body.get("items") or [])
                profile["debug"].append(f"RapidAPI videos ep={ep.split('/')[-1]}: {len(raw)} items")
                if not raw:
                    continue

                videos = []
                for v in raw:
                    s      = v.get("statistics") or v.get("stats") or {}
                    vid    = v.get("video") or {}
                    vid_id = str(v.get("aweme_id") or v.get("id") or "")
                    desc   = v.get("desc") or v.get("title") or ""
                    dur    = int(vid.get("duration") or v.get("duration") or 0)
                    cover  = vid.get("cover") or {}
                    thumb  = (cover.get("url_list") or [""])[0] if isinstance(cover, dict) else ""
                    videos.append({
                        "video_id":    vid_id,
                        "title":       desc[:150],
                        "description": desc[:200],
                        "url":         f"https://www.tiktok.com/@{username}/video/{vid_id}" if vid_id else "",
                        "thumbnail":   thumb,
                        "views":       int(s.get("play_count") or s.get("view_count") or 0),
                        "likes":       int(s.get("digg_count") or s.get("like_count") or 0),
                        "comments":    int(s.get("comment_count") or 0),
                        "shares":      int(s.get("share_count") or 0),
                        "duration":    dur,
                        "upload_date": str(v.get("create_time") or ""),
                        "type":        "video",
                    })
                if videos:
                    profile["videos"]            = videos
                    profile["total_video_count"] = len(videos)
                    profile["method"]            = "RapidAPI Tokapi"
                    return profile
            except Exception as e:
                profile["debug"].append(f"RapidAPI videos error: {e}")

    # ── yt-dlp fallback ────────────────────────────────────────────────────────
    profile["debug"].append(f"Trying yt-dlp for @{username}")
    lines, err = run_ytdlp([
        "--dump-json", "--flat-playlist",
        "--playlist-items", f"1:{max_videos}",
        "--no-warnings", "--no-check-certificates",
        f"https://www.tiktok.com/@{username}"
    ])
    profile["debug"].append(f"yt-dlp: {len(lines)} lines, err: {err[:80] if err else 'none'}")

    videos = []
    for line in lines:
        try:
            data = json.loads(line)
            v    = parse_ytdlp_video(data, username)
            if v["title"] or v["video_id"]:
                videos.append(v)
                if not profile["display_name"]:
                    profile["display_name"] = data.get("uploader") or username
        except Exception:
            continue

    if videos:
        profile["videos"]            = videos
        profile["total_video_count"] = len(videos)
        profile["method"]            = "yt-dlp"
        return profile

    # ── DuckDuckGo last resort ─────────────────────────────────────────────────
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(f'tiktok.com "@{username}"', max_results=15))
        videos = []
        for r in results:
            href = r.get("href", "")
            body = r.get("body", "")
            if "tiktok.com" in href and "/video/" in href and body:
                vid_id = href.split("/video/")[-1].split("?")[0].split("/")[0]
                videos.append({
                    "video_id": vid_id, "title": body[:150],
                    "description": body[:200], "url": href, "thumbnail": "",
                    "views": 0, "likes": 0, "comments": 0, "shares": 0,
                    "duration": 0, "upload_date": "", "type": "video",
                })
        profile["videos"]            = videos
        profile["total_video_count"] = len(videos)
        profile["method"]            = "DuckDuckGo (no stats — add RapidAPI key for full data)"
        if not videos:
            profile["error"] = "No TikTok data. Add RapidAPI key in apikeys.py for full access."
    except Exception as e:
        profile["error"] = str(e)

    return profile


# ─────────────────────────────────────────────────────────────────────────────
# Instagram
# ─────────────────────────────────────────────────────────────────────────────

def fetch_instagram_creator(username: str, rapidapi_key: str = "", max_videos: int = 20) -> dict:
    username = username.lstrip("@")
    profile = {
        "platform": "Instagram", "username": username,
        "display_name": "", "bio": "", "avatar": "",
        "followers": 0, "following": 0, "posts_count": 0,
        "total_video_count": 0, "videos": [],
        "error": None, "method": "", "debug": [],
    }

    # ── RapidAPI ──────────────────────────────────────────────────────────────
    if rapidapi_key and rapidapi_key not in ("", "YOUR_RAPIDAPI_KEY"):
        api_configs = [
            {
                "host":        "instagram-scraper-api2.p.rapidapi.com",
                "profile_url": "https://instagram-scraper-api2.p.rapidapi.com/v1/info",
                "posts_url":   "https://instagram-scraper-api2.p.rapidapi.com/v1/posts",
                "param":       "username_or_id_or_url",
            },
            {
                "host":        "instagram230.p.rapidapi.com",
                "profile_url": "https://instagram230.p.rapidapi.com/user/info",
                "posts_url":   "https://instagram230.p.rapidapi.com/user/posts",
                "param":       "username",
            },
        ]
        for cfg in api_configs:
            try:
                hdr = {"X-RapidAPI-Key": rapidapi_key, "X-RapidAPI-Host": cfg["host"]}

                # Profile
                r  = requests.get(cfg["profile_url"], headers=hdr,
                                  params={cfg["param"]: username}, timeout=12)
                u  = r.json().get("data") or r.json().get("user") or r.json() or {}
                if u.get("pk") or u.get("id") or u.get("username"):
                    profile.update({
                        "display_name": u.get("full_name") or username,
                        "bio":          u.get("biography") or u.get("bio") or "",
                        "followers":    int(u.get("follower_count") or
                                           (u.get("edge_followed_by") or {}).get("count") or 0),
                        "following":    int(u.get("following_count") or 0),
                        "posts_count":  int(u.get("media_count") or 0),
                    })

                # Posts
                r2   = requests.get(cfg["posts_url"], headers=hdr,
                                    params={cfg["param"]: username, "count": max_videos}, timeout=12)
                body = r2.json()
                raw  = (body.get("data", {}).get("items") or
                        body.get("items") or body.get("posts") or [])
                profile["debug"].append(f"Instagram {cfg['host']}: {len(raw)} posts")

                videos = []
                for p in raw:
                    cap      = p.get("caption") or {}
                    cap_text = (cap.get("text") if isinstance(cap, dict) else str(cap or "")) or ""
                    is_vid   = p.get("media_type") in [2, "video", "reel"] or p.get("is_video")
                    pid      = p.get("pk") or p.get("id") or ""
                    sc       = p.get("code") or p.get("shortcode") or str(pid)
                    img_ver  = p.get("image_versions2") or {}
                    thumb    = (img_ver.get("candidates") or [{}])[0].get("url", "") \
                               if isinstance(img_ver, dict) else ""
                    videos.append({
                        "video_id":    str(pid),
                        "title":       cap_text[:150],
                        "description": cap_text[:200],
                        "url":         f"https://www.instagram.com/p/{sc}/",
                        "thumbnail":   thumb,
                        "views":       int(p.get("view_count") or p.get("video_view_count") or 0),
                        "likes":       int(p.get("like_count") or 0),
                        "comments":    int(p.get("comment_count") or 0),
                        "shares":      0,
                        "duration":    int(p.get("video_duration") or 0),
                        "upload_date": str(p.get("taken_at") or "")[:10],
                        "type":        "reel" if is_vid else "post",
                    })
                if videos:
                    profile["videos"]            = videos
                    profile["total_video_count"] = len(videos)
                    profile["method"]            = f"RapidAPI ({cfg['host']})"
                    return profile
            except Exception as e:
                profile["debug"].append(f"RapidAPI {cfg.get('host','')}: {e}")
                continue

    # ── instaloader fallback ──────────────────────────────────────────────────
    try:
        import instaloader
        L  = instaloader.Instaloader(quiet=True, download_pictures=False,
                                     download_videos=False, download_video_thumbnails=False)
        ig = instaloader.Profile.from_username(L.context, username)
        profile.update({
            "display_name": ig.full_name or username,
            "bio":          ig.biography or "",
            "followers":    ig.followers,
            "following":    ig.followees,
            "posts_count":  ig.mediacount,
        })
        videos = []
        for i, post in enumerate(ig.get_posts()):
            if i >= max_videos:
                break
            cap = post.caption or ""
            videos.append({
                "video_id":    post.shortcode,
                "title":       cap[:150],
                "description": cap[:200],
                "url":         f"https://www.instagram.com/p/{post.shortcode}/",
                "thumbnail":   post.url or "",
                "views":       post.video_view_count if post.is_video else 0,
                "likes":       post.likes,
                "comments":    post.comments,
                "shares":      0, "duration": 0,
                "upload_date": post.date_utc.strftime("%Y-%m-%d") if post.date_utc else "",
                "type":        "reel" if post.is_video else "post",
            })
        profile["videos"]            = videos
        profile["total_video_count"] = len(videos)
        profile["method"]            = "instaloader"
        return profile
    except ImportError:
        profile["debug"].append("instaloader not installed: pip install instaloader")
    except Exception as e:
        profile["debug"].append(f"instaloader error: {e}")

    # ── DuckDuckGo last resort ─────────────────────────────────────────────────
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(f'site:instagram.com/{username}', max_results=15))
        videos = []
        for r in results:
            href = r.get("href", "")
            body = r.get("body", "")
            if "instagram.com" in href and "/p/" in href and body:
                sc = href.split("/p/")[-1].strip("/").split("?")[0]
                videos.append({
                    "video_id": sc, "title": body[:150], "description": body[:200],
                    "url": f"https://www.instagram.com/p/{sc}/", "thumbnail": "",
                    "views": 0, "likes": 0, "comments": 0, "shares": 0,
                    "duration": 0, "upload_date": "", "type": "post",
                })
        profile["videos"]            = videos
        profile["total_video_count"] = len(videos)
        profile["method"]            = "DuckDuckGo (limited — add RapidAPI key)"
        if not videos:
            profile["error"] = "No Instagram data. Add RapidAPI key or run: pip install instaloader"
    except Exception as e:
        profile["error"] = str(e)

    return profile


# ─────────────────────────────────────────────────────────────────────────────
# Transcription
# ─────────────────────────────────────────────────────────────────────────────

def transcribe_top_videos(groq_client, videos: list, n: int = 3) -> list:
    """Download audio from top N videos by views, transcribe with Whisper."""
    # Only videos with real downloadable URLs
    downloadable = [
        v for v in videos
        if v.get("url") and any(
            d in v["url"] for d in ["youtube.com", "youtu.be", "tiktok.com"]
        ) and v.get("video_id")  # must have an ID to download
    ]
    top = sorted(downloadable, key=lambda x: x.get("views", 0), reverse=True)[:n]
    results = []

    with tempfile.TemporaryDirectory() as tmpdir:
        for v in top:
            transcript = ""
            try:
                out_tmpl = os.path.join(tmpdir, "%(id)s.%(ext)s")
                lines, err = run_ytdlp([
                    "--extract-audio", "--audio-format", "mp3",
                    "--audio-quality", "96K", "--no-playlist",
                    "--max-filesize", "25m", "--no-warnings",
                    "-o", out_tmpl, v["url"]
                ], timeout=120)

                mp3_files = [f for f in os.listdir(tmpdir) if f.endswith(".mp3")]
                for mp3 in mp3_files:
                    fpath = os.path.join(tmpdir, mp3)
                    with open(fpath, "rb") as af:
                        tr = groq_client.audio.transcriptions.create(
                            file=(mp3, af.read()),
                            model="whisper-large-v3",
                            response_format="text"
                        )
                    transcript = tr if isinstance(tr, str) else str(tr)
                    os.remove(fpath)
                    break
            except Exception as e:
                transcript = f"[Transcription failed: {e}]"

            results.append({
                "title":      v.get("title", ""),
                "url":        v.get("url", ""),
                "views":      v.get("views", 0),
                "likes":      v.get("likes", 0),
                "duration":   v.get("duration", 0),
                "transcript": transcript,
            })
            time.sleep(1)

    return results


# ─────────────────────────────────────────────────────────────────────────────
# Pattern Extraction
# ─────────────────────────────────────────────────────────────────────────────

def extract_creator_patterns(groq_client, transcribed_videos: list, profile: dict) -> dict:
    """Analyze transcripts → reusable style profile for script generation."""
    block = ""
    for i, v in enumerate(transcribed_videos):
        t = (v.get("transcript") or "").strip()
        if not t or t.startswith("[Transcription failed"):
            continue
        block += f"\n\n--- VIDEO {i+1}: \"{v.get('title','')}\" ({fmt_num(v.get('views',0))} views) ---\n{t}"

    if not block.strip():
        return {"error": "No transcripts available — videos may not be downloadable via yt-dlp"}

    prompt = f"""You are a creator linguistics and performance expert.

CREATOR: @{profile.get("username","")} on {profile.get("platform","")}

Analyze these transcripts from their top videos and extract every pattern of how they talk and perform:
{block[:5000]}

Return ONLY valid JSON:
{{
  "opening_patterns": ["exact structure 1 e.g. 'Okay so [relatable situation]...'", "structure 2", "structure 3"],
  "hook_formulas":    ["formula 1 e.g. 'Did you know [fact]? Because [twist]'", "formula 2", "formula 3"],
  "transition_phrases": ["phrase between points e.g. 'and here is the thing'", "phrase 2"],
  "closing_patterns": ["how they end e.g. 'So if you ever [situation], remember [lesson]'", "CTA style"],
  "vocabulary_style": "simple and casual / Gen Z slang / technical / polished / street",
  "sentence_length":  "short punchy (3-8 words) / medium / long detailed / mixed",
  "speaking_pace":    "slow deliberate / medium / fast conversational / very fast",
  "energy_level":     "calm quiet / moderate / high enthusiastic / hyper intense",
  "signature_phrases": ["exact phrase they repeat 1", "phrase 2"],
  "storytelling_structure": "e.g. 'Hook question -> personal story -> surprising twist -> takeaway -> CTA'",
  "audience_address": "guys / y all / you / everyone / bro / bestie / etc.",
  "humor_style":      "none / dry deadpan / self-deprecating / absurdist / observational",
  "content_format":   "talking head / voiceover b-roll / mixed / performance / narration",
  "use_of_numbers":   "e.g. 'uses specific numbers for credibility: 3 steps, 47% faster'",
  "emotional_triggers": ["main lever 1 e.g. FOMO", "lever 2 e.g. relatability"],
  "pacing_technique": "e.g. 'rapid-fire questions then slow dramatic pause before answer'",
  "style_summary": "2-3 sentence fingerprint of their unique voice",
  "script_injection_prompt": "A 60-80 word prompt written as instructions for an AI to replicate this exact style. Example format: 'Write exactly like @creator: Use [specific sentence length]. Always open with [specific structure]. Address viewers as [word]. Transition with phrases like [phrase]. Their humor is [type]. End every video with [CTA style]. Match their [energy] energy throughout.'"
}}"""

    try:
        resp = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "Creator linguistics expert. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500, temperature=0.2
        )
        raw = resp.choices[0].message.content.strip()
        raw = re.sub(r"^```json\s*", "", raw)
        raw = re.sub(r"^```\s*",     "", raw)
        raw = re.sub(r"\s*```$",     "", raw)
        return json.loads(raw)
    except Exception as e:
        return {"error": str(e)}


# ─────────────────────────────────────────────────────────────────────────────
# Strategic Analysis
# ─────────────────────────────────────────────────────────────────────────────

def analyze_creator(groq_client, profile: dict) -> dict:
    videos   = profile.get("videos", [])
    platform = profile.get("platform", "")
    username = profile.get("username", "")
    followers = profile.get("followers", 0) or profile.get("subscribers", 0)

    lines = []
    for i, v in enumerate(videos[:25]):
        parts = [f"{i+1}. [{v.get('type','')}] {(v.get('title') or '')[:70]}"]
        if v.get("views"):    parts.append(f"👁️{fmt_num(v['views'])}")
        if v.get("likes"):    parts.append(f"❤️{fmt_num(v['likes'])}")
        if v.get("comments"): parts.append(f"💬{v['comments']}")
        if v.get("duration"): parts.append(f"⏱️{v['duration']}s")
        lines.append(" | ".join(parts))

    prompt = f"""Creator strategy analyst. Platform: {platform}
Creator: @{username} | Followers: {fmt_num(followers)}
Bio: {profile.get("bio","")[:250]}
Recent videos:
{chr(10).join(lines) if lines else "No video data available"}

Return ONLY valid JSON:
{{
  "creator_archetype": "The Educator / Entertainer / Storyteller / Expert / Comedian / Influencer / etc.",
  "tier": "Nano (<10K) / Micro (10K-100K) / Mid (100K-500K) / Macro (500K-5M) / Mega (5M+)",
  "content_pillars": ["pillar 1","pillar 2","pillar 3"],
  "posting_style": "format and style description",
  "audience_profile": "who watches this",
  "tone": "brand voice",
  "strengths": ["s1","s2","s3"],
  "weaknesses": ["w1","w2","w3"],
  "growth_opportunities": ["o1","o2","o3"],
  "top_performing_themes": ["t1","t2","t3"],
  "content_gaps": ["gap1","gap2"],
  "viral_formula": "pattern of best content",
  "hook_patterns": "hook styles used",
  "monetization_potential": "Low/Medium/High/Very High",
  "collaboration_fit": "brand/creator fit",
  "next_3_video_ideas": [
    {{"title":"idea","hook":"opening line","why":"why it works"}},
    {{"title":"idea","hook":"opening line","why":"why it works"}},
    {{"title":"idea","hook":"opening line","why":"why it works"}}
  ],
  "overall_score": 0-100,
  "summary": "2-3 sentence executive summary"
}}"""

    try:
        resp = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "Creator strategy expert. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000, temperature=0.3
        )
        raw = resp.choices[0].message.content.strip()
        raw = re.sub(r"^```json\s*", "", raw)
        raw = re.sub(r"^```\s*",     "", raw)
        raw = re.sub(r"\s*```$",     "", raw)
        return json.loads(raw)
    except Exception as e:
        return {"error": str(e), "summary": "Analysis failed — check API key"}


def compute_video_stats(videos: list) -> dict:
    if not videos:
        return {}
    vl  = [v.get("views", 0)    for v in videos if v.get("views", 0)    > 0]
    ll  = [v.get("likes", 0)    for v in videos if v.get("likes", 0)    > 0]
    cl  = [v.get("comments", 0) for v in videos if v.get("comments", 0) > 0]
    dl  = [v.get("duration", 0) for v in videos if v.get("duration", 0) > 0]
    avg = lambda l: int(sum(l) / len(l)) if l else 0
    tv  = sum(vl); tl = sum(ll); tc = sum(cl)
    return {
        "total_views":     tv,
        "avg_views":       avg(vl),
        "avg_likes":       avg(ll),
        "avg_comments":    avg(cl),
        "avg_duration":    avg(dl),
        "engagement_rate": round((tl + tc) / tv * 100, 2) if tv > 0 else 0,
        "top_videos":      sorted(videos, key=lambda x: x.get("views", 0), reverse=True)[:5],
        "total_likes":     tl,
        "total_comments":  tc,
    }
