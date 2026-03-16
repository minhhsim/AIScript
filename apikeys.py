# apikeys.py
# NOTE: groq_key is intentionally NOT loaded here.
# main.py reads it directly from st.secrets after page config
# so that st.secrets is fully initialized before the read.
#
# This file is only used for the optional API keys (RapidAPI, YouTube).

import os

def _get(name, fallback=""):
    try:
        import streamlit as st
        for k in (name, name.upper(), name.lower()):
            v = st.secrets.get(k, "")
            if v: return str(v).strip()
    except Exception:
        pass
    for k in (name, name.upper(), name.lower()):
        v = os.environ.get(k, "")
        if v: return v.strip()
    return fallback

# Optional keys — add to Streamlit secrets as RAPIDAPI_KEY and YOUTUBE_API_KEY
rapidapi_key    = _get("RAPIDAPI_KEY",    _get("rapidapi_key", "ad06fd8379mshd4b8c37a5f2656fp13508ejsna113052593fb"))
youtube_api_key = _get("YOUTUBE_API_KEY", _get("youtube_api_key", ""))

# groq_key is defined here only as a fallback for any module that imports it directly
# The real loading happens in main.py via _load_groq_key()
groq_key = _get("GROQ_KEY", _get("groq_key", "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"))
