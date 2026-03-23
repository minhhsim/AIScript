# modules/auto_research.py
"""
Auto Research Scheduler
Runs trending content research automatically every 24h (or custom interval).
Results are persisted to disk so they survive app restarts.
Works inside Streamlit — no external cron needed.

Flow:
  1. User configures niches + platforms + interval in Settings tab
  2. On every page load, check if refresh is due
  3. If due → run scrape for all configured niches → save to disk
  4. Research page always loads from disk cache (instant) + shows last-updated time
  5. Manual refresh button always available
"""

import os, json, time, pickle
from datetime import datetime, timezone

# ── Paths ─────────────────────────────────────────────────────────────────────
_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_PATH    = os.path.join(_BASE, "auto_research_cache.pkl")
SETTINGS_PATH = os.path.join(_BASE, "auto_research_settings.json")

# ── Default settings ──────────────────────────────────────────────────────────
DEFAULT_SETTINGS = {
    "niches":         ["car dealership", "fitness motivation", "skincare routine"],
    "platforms":      ["YouTube", "TikTok", "Reddit"],
    "interval_hours": 24,
    "max_per_platform": 10,
    "enabled":        True,
    "last_run":       0.0,        # unix timestamp
    "last_run_label": "Never",
}


# ── Settings helpers ──────────────────────────────────────────────────────────

def load_settings() -> dict:
    try:
        if os.path.exists(SETTINGS_PATH):
            with open(SETTINGS_PATH, "r") as f:
                saved = json.load(f)
            s = {**DEFAULT_SETTINGS, **saved}
            return s
    except Exception:
        pass
    return dict(DEFAULT_SETTINGS)


def save_settings(settings: dict):
    try:
        with open(SETTINGS_PATH, "w") as f:
            json.dump(settings, f, indent=2)
    except Exception as e:
        print(f"[AutoResearch] save_settings error: {e}")


# ── Cache helpers ─────────────────────────────────────────────────────────────

def load_cache() -> dict:
    """
    Returns {
      "niches": {
        "car dealership": {
          "posts": [...],
          "fetched_at": 1710000000.0,
          "fetched_label": "2025-01-15 09:30 UTC",
          "platforms": ["YouTube","TikTok","Reddit"],
        },
        ...
      },
      "last_run": 1710000000.0,
    }
    """
    try:
        if os.path.exists(CACHE_PATH):
            with open(CACHE_PATH, "rb") as f:
                return pickle.load(f)
    except Exception:
        pass
    return {"niches": {}, "last_run": 0.0}


def save_cache(cache: dict):
    try:
        with open(CACHE_PATH, "wb") as f:
            pickle.dump(cache, f)
    except Exception as e:
        print(f"[AutoResearch] save_cache error: {e}")


def get_cached_posts(niche: str) -> list:
    cache = load_cache()
    return cache.get("niches", {}).get(niche, {}).get("posts", [])


def get_cache_age_hours(niche: str) -> float:
    cache = load_cache()
    ts = cache.get("niches", {}).get(niche, {}).get("fetched_at", 0.0)
    if not ts:
        return 999.0
    return (time.time() - ts) / 3600


def get_last_run_label() -> str:
    settings = load_settings()
    return settings.get("last_run_label", "Never")


# ── Core scraper ──────────────────────────────────────────────────────────────

def scrape_niche(niche: str, platforms: list, max_per: int,
                 yt_key: str = "", rapidapi_key: str = "") -> list:
    """Scrape all platforms for a niche, return merged + sorted post list."""
    from modules.social_trends import (
        scrape_youtube, scrape_tiktok, scrape_reddit, scrape_instagram,
    )
    all_posts = []
    for plat in platforms:
        try:
            if plat == "YouTube":
                posts = scrape_youtube(niche, yt_key, max_per)
            elif plat == "TikTok":
                posts = scrape_tiktok(niche, rapidapi_key, max_per)
            elif plat == "Instagram":
                posts = scrape_instagram(niche, rapidapi_key, max_per)
            elif plat == "Reddit":
                posts = scrape_reddit(niche, max_per)
            else:
                posts = []
            all_posts.extend(posts)
        except Exception as e:
            print(f"[AutoResearch] {plat}/{niche}: {e}")

    # Sort by viral signal
    all_posts.sort(
        key=lambda p: p.get("views", 0) + p.get("likes", 0) * 10,
        reverse=True
    )
    return all_posts


def run_auto_research(yt_key: str = "", rapidapi_key: str = "",
                      progress_cb=None) -> dict:
    """
    Run full auto-research for all configured niches.
    progress_cb(pct, message) — optional Streamlit progress callback.
    Returns the updated cache dict.
    """
    settings = load_settings()
    niches   = settings.get("niches", [])
    platforms= settings.get("platforms", ["YouTube","TikTok","Reddit"])
    max_per  = settings.get("max_per_platform", 10)

    cache = load_cache()
    if "niches" not in cache:
        cache["niches"] = {}

    now      = time.time()
    now_label= datetime.fromtimestamp(now, tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    for i, niche in enumerate(niches):
        pct = int(i / max(len(niches), 1) * 100)
        if progress_cb:
            progress_cb(pct, f"🔍 Fetching **{niche}** ({i+1}/{len(niches)})...")

        posts = scrape_niche(niche, platforms, max_per, yt_key, rapidapi_key)

        cache["niches"][niche] = {
            "posts":         posts,
            "fetched_at":    now,
            "fetched_label": now_label,
            "platforms":     platforms,
            "count":         len(posts),
        }

    cache["last_run"] = now
    save_cache(cache)

    # Update last_run in settings
    settings["last_run"]       = now
    settings["last_run_label"] = now_label
    save_settings(settings)

    if progress_cb:
        progress_cb(100, f"✅ {len(niches)} niches refreshed — {now_label}")

    return cache


# ── Auto-trigger check (call on every page load) ──────────────────────────────

def should_auto_refresh() -> bool:
    settings = load_settings()
    if not settings.get("enabled", True):
        return False
    interval_hours = settings.get("interval_hours", 24)
    last_run       = settings.get("last_run", 0.0)
    elapsed_hours  = (time.time() - last_run) / 3600
    return elapsed_hours >= interval_hours


def maybe_auto_refresh(yt_key: str = "", rapidapi_key: str = "") -> bool:
    """
    Call this on page load. Runs research silently if due.
    Returns True if research was run.
    """
    if should_auto_refresh():
        try:
            run_auto_research(yt_key, rapidapi_key)
            return True
        except Exception as e:
            print(f"[AutoResearch] auto-refresh error: {e}")
    return False


# ── Niche management helpers ──────────────────────────────────────────────────

def add_niche(niche: str):
    s = load_settings()
    if niche not in s["niches"]:
        s["niches"].append(niche)
        save_settings(s)


def remove_niche(niche: str):
    s = load_settings()
    s["niches"] = [n for n in s["niches"] if n != niche]
    save_settings(s)


def set_interval(hours: int):
    s = load_settings()
    s["interval_hours"] = hours
    save_settings(s)


def set_platforms(platforms: list):
    s = load_settings()
    s["platforms"] = platforms
    save_settings(s)


def set_enabled(enabled: bool):
    s = load_settings()
    s["enabled"] = enabled
    save_settings(s)
