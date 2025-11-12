# app.py
"""
Polyglot — AI Language Translator (Animated Dark/Light Edition)
---------------------------------------------------------------
✅ Real translations (Hugging Face)
✅ True full-page dark/light mode
✅ Animated gradient background
✅ Glowing buttons & smooth hover transitions
✅ Glass cards with subtle movement
✅ Works perfectly on Streamlit Cloud
"""

import streamlit as st
from transformers import pipeline
from gtts import gTTS
import time
import io

# -----------------------------------------------------------
# PAGE CONFIG
# -----------------------------------------------------------
st.set_page_config(page_title="Polyglot — AI Language Translator", page_icon="🌐", layout="wide")

# -----------------------------------------------------------
# SIDEBAR CONTROLS
# -----------------------------------------------------------
st.sidebar.title("🌐 Polyglot Settings")

dark_mode = st.sidebar.toggle("🌙 Dark Mode", value=True)

languages = {
    "🇬🇧 English": "en",
    "🇮🇳 Hindi": "hi",
    "🇫🇷 French": "fr",
    "🇪🇸 Spanish": "es",
    "🇩🇪 German": "de",
    "🇮🇹 Italian": "it",
    "🇨🇳 Chinese": "zh",
    "🇯🇵 Japanese": "ja",
    "🇰🇷 Korean": "ko",
}

if "src_lang" not in st.session_state:
    st.session_state.src_lang = "🇬🇧 English"
if "tgt_lang" not in st.session_state:
    st.session_state.tgt_lang = "🇮🇳 Hindi"
if "input_text" not in st.session_state:
    st.session_state.input_text = ""

src_lang = st.sidebar.selectbox("Source Language", ["🌍 Auto Detect"] + list(languages.keys()), index=1)
tgt_lang = st.sidebar.selectbox("Target Language", list(languages.keys()), index=0)
show_conf = st.sidebar.checkbox("Show Confidence Score", value=True)
temperature = st.sidebar.slider("Translation Temperature", 0.0, 1.0, 0.3, 0.05)
enable_tts = st.sidebar.checkbox("Enable Text-to-Speech", value=False)

if st.sidebar.button("↔️ Swap Languages"):
    st.session_state.src_lang, st.session_state.tgt_lang = st.session_state.tgt_lang, st.session_state.src_lang
    st.sidebar.success("Languages swapped!")

# -----------------------------------------------------------
# ANIMATED STYLE SYSTEM
# -----------------------------------------------------------
if dark_mode:
    # Neon dark mode
    primary = "#00ffff"
    secondary = "#7b5cf9"
    text_color = "#e6edf3"
    bg_animation = """
    background: linear-gradient(-45deg, #0d1117, #1b2430, #2b3467, #0d1117);
    background-size: 400% 400%;
    animation: gradientShift 18s ease infinite;
    """
else:
    # Energetic light mode
    primary = "#3a7afe"
    secondary = "#ff61c7"
    text_color = "#0b1a33"
    bg_animation = """
    background: linear-gradient(135deg, #dbe9ff, #f3e9ff, #e7fff3, #dbe9ff);
    background-size: 400% 400%;
    animation: gradientShift 16s ease infinite;
    """

# Inject global CSS
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif;
    color: {text_color};
}}
.main {{
    {bg_animation}
}}
@keyframes gradientShift {{
  0% {{background-position: 0% 50%;}}
  50% {{background-position: 100% 50%;}}
  100% {{background-position: 0% 50%;}}
}}
.glass {{
    background: rgba(255, 255, 255, 0.08);
    backdrop-filter: blur(12px);
    border-radius: 16px;
    padding: 24px;
    transition: transform 0.3s ease;
}}
.glass:hover {{
    transform: translateY(-3px);
}}
.stButton>button {{
    border: none;
    border-radius: 8px;
    background: linear-gradient(90deg, {primary}, {secondary});
    color: white !important;
    font-weight: 600;
    padding: 0.6em 1em;
    transition: all 0.3s ease;
    box-shadow: 0 0 12px rgba(0,0,0,0.25);
}}
.stButton>button:hover {{
    transform: scale(1.05);
    box-shadow: 0 0 20px {primary};
}}
.title {{
    font-size: 32px;
    font-weight: 700;
    text-align: center;
    color: {primary};
    margin-bottom: 5px;
    text-shadow: 0 0 20px
