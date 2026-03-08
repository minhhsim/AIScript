# apikeys.py
import os

# Default to empty
groq_key     = ""
rapidapi_key = ""

# Try Streamlit Cloud secrets first
try:
    import streamlit as st
    groq_key     = st.secrets.get("groq_key", "")
    rapidapi_key = st.secrets.get("rapidapi_key", "")
except Exception:
    pass

# Fall back to hardcoded values for local
if not groq_key:
    groq_key = "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"
if not rapidapi_key:
    rapidapi_key = "ad06fd8379mshd4b8c37a5f2656fp13508ejsna113052593fb"