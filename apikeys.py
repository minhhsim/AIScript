# apikeys.py
import os

groq_key     = ""
rapidapi_key = ""
youtube_api_key = ""

# Try Streamlit Cloud secrets first
try:
    import streamlit as st
    groq_key        = st.secrets.get("groq_key", "")
    rapidapi_key    = st.secrets.get("rapidapi_key", "")
    youtube_api_key = st.secrets.get("youtube_api_key", "")
except Exception:
    pass

# Fallback to hardcoded values for local dev
if not groq_key:
    groq_key='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'
    # groq_key = "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"           # console.groq.com — free
if not rapidapi_key:
    rapidapi_key = "ad06fd8379mshd4b8c37a5f2656fp13508ejsna113052593fb"                          # rapidapi.com — for TikTok/Instagram
if not youtube_api_key:
    youtube_api_key = "AIzaSyC2_EvW45vOQpG8kd4v4CSHHSR1WhtygR8"                       # console.cloud.google.com — free 10k/day


