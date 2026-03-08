import streamlit as st
import os

groq_key     = st.secrets.get("groq_key", os.environ.get("GROQ_API_KEY", ""))
rapidapi_key = st.secrets.get("rapidapi_key", os.environ.get("RAPIDAPI_KEY", ""))