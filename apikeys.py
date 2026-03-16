# apikeys.py — ContentIQ API Keys
# Keys are loaded in priority order:
#   1. Streamlit secrets  (.streamlit/secrets.toml or Streamlit Cloud dashboard)
#   2. Environment variables
#   3. Hardcoded fallback (for local dev only)

import os

def _get(key, fallback=""):
    """Try st.secrets first, then env var, then fallback."""
    # Streamlit secrets — try both UPPER and lower variants
    try:
        import streamlit as st
        for variant in [key, key.upper(), key.lower()]:
            val = st.secrets.get(variant)
            if val:
                return str(val).strip()
    except Exception:
        pass
    # Environment variable
    for variant in [key, key.upper(), key.lower()]:
        val = os.environ.get(variant, "")
        if val:
            return val.strip()
    return fallback

# ─── Keys ────────────────────────────────────────────────────────────────────
# Required — get free key at https://console.groq.com
groq_key = _get("GROQ_KEY", _get("groq_key", "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"))

# Optional — https://rapidapi.com (adds live Reddit/Google/TikTok data)
rapidapi_key = _get("RAPIDAPI_KEY", _get("rapidapi_key", "ad06fd8379mshd4b8c37a5f2656fp13508ejsna113052593fb"))

# Optional — https://console.cloud.google.com → YouTube Data API v3 (free 10k/day)
youtube_api_key = _get("YOUTUBE_API_KEY", _get("youtube_api_key", "AIzaSyC2_EvW45vOQpG8kd4v4CSHHSR1WhtygR8"))
