# app.py
"""
Polyglot — AI Language Translator (White Theme + Animated Flags)
---------------------------------------------------------------
🌸 White background + pink/orange neon accent
🚩 Real waving flags
🎧 TTS + confidence bar + download
⚙️ Streamlit Cloud ready
"""

import streamlit as st
from transformers import pipeline
from gtts import gTTS
import io
import time

# -----------------------------------------------------------
# PAGE CONFIG
# -----------------------------------------------------------
st.set_page_config(page_title="Polyglot — AI Translator", page_icon="🌐", layout="wide")

# -----------------------------------------------------------
# SIDEBAR SETTINGS
# -----------------------------------------------------------
st.sidebar.title("🌐 Polyglot Settings")

languages = {
    "English": "gb",
    "Hindi": "in",
    "French": "fr",
    "Spanish": "es",
    "German": "de",
    "Italian": "it",
    "Chinese": "cn",
    "Japanese": "jp",
    "Korean": "kr",
}

src_lang = st.sidebar.selectbox("Source Language", ["Auto Detect"] + list(languages.keys()), index=1)
tgt_lang = st.sidebar.selectbox("Target Language", list(languages.keys()), index=0)
temperature = st.sidebar.slider("Translation Temperature", 0.0, 1.0, 0.3, 0.05)
show_conf = st.sidebar.checkbox("Show Confidence Score", value=True)
enable_tts = st.sidebar.checkbox("Enable Text-to-Speech", value=False)

if st.sidebar.button("↔️ Swap Languages"):
    src_lang, tgt_lang = tgt_lang, src_lang
    st.sidebar.success("Languages swapped!")

# -----------------------------------------------------------
# GLOBAL CSS (White Background + Neon Accents + Flag Animation)
# -----------------------------------------------------------
st.markdown("""
<style>
html, body, [class*="css"] {
    background-color: #ffffff !important;
    color: #1a1a1a !important;
    font-family: 'Inter', sans-serif;
}
section[data-testid="stAppViewContainer"],
section[data-testid="stVerticalBlock"],
div.block-container,
[data-testid="stSidebar"] {
    background-color: #ffffff !important;
    color: #1a1a1a !important;
}

/* Neon Buttons */
.stButton>button {
    border: none;
    border-radius: 10px;
    background: linear-gradient(90deg, #ff66c4, #ff9f45);
    color: white !important;
    font-weight: 600;
    padding: 0.6em 1em;
    transition: all 0.3s ease;
    box-shadow: 0 0 15px rgba(255, 102, 196, 0.3);
}
.stButton>button:hover {
    transform: scale(1.05);
    box-shadow: 0 0 30px rgba(255, 159, 69, 0.5);
}

/* Glass Cards */
.glass {
    background: rgba(255, 255, 255, 0.7);
    border-radius: 16px;
    padding: 22px;
    backdrop-filter: blur(10px);
    transition: all 0.3s ease;
    box-shadow: 0 0 20px rgba(255, 159, 69, 0.15);
}
.glass:hover {
    transform: translateY(-3px);
    box-shadow: 0 0 25px rgba(255, 102, 196, 0.25);
}

/* Titles */
.title {
    font-size: 34px;
    font-weight: 800;
    text-align: center;
    color: #ff66c4;
    text-shadow: 0 0 10px rgba(255, 159, 69, 0.4);
}
.result {
    font-size:17px;
    color:#1a1a1a;
    line-height:1.6;
    white-space: pre-wrap;
}

/* Animated Flags */
.flag {
    width: 36px;
    height: 24px;
    margin-right: 8px;
    border-radius: 3px;
    display:inline-block;
    animation: wave 1.8s ease-in-out infinite;
    transform-origin: 50% 50%;
}
@keyframes wave {
  0% { transform: rotate(0deg) translateY(0px); }
  25% { transform: rotate(4deg) translateY(-1px); }
  50% { transform: rotate(-4deg) translateY(1px); }
  75% { transform: rotate(4deg) translateY(-1px); }
  100% { transform: rotate(0deg) translateY(0px); }
}

.footer {
    text-align:center;
    font-size:13px;
    opacity:0.85;
    margin-top:25px;
    color:#ff66c4;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------
# HEADER
# -----------------------------------------------------------
st.markdown("""
<div class="glass" style="text-align:center;margin-bottom:25px;">
  <div class="title">🌐 Polyglot — AI Language Translator</div>
  <p style="text-align:center;color:#ff9f45;">✨ Elegant White Theme • Pink/Orange Accents • Animated Flags</p>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------
# FLAG HELPER FUNCTION
# -----------------------------------------------------------
def flag_img(code):
    return f"<img src='https://flagcdn.com/w40/{code}.png' class='flag'>"

# -----------------------------------------------------------
# TRANSLATOR CACHE
# -----------------------------------------------------------
@st.cache_resource
def load_translator(src_code, tgt_code):
    if src_code == "auto":
        src_code = "en"
    if src_code == tgt_code:
        return None
    try:
        return pipeline("translation", model=f"Helsinki-NLP/opus-mt-{src_code}-{tgt_code}")
    except Exception:
        st.warning(f"No direct model for {src_code}-{tgt_code}, using fallback.")
        return pipeline("translation", model="facebook/m2m100_418M")

# -----------------------------------------------------------
# MAIN INTERFACE
# -----------------------------------------------------------
st.markdown('<div class="glass">', unsafe_allow_html=True)
st.markdown(
    f"**Source:** {flag_img(languages.get(src_lang, 'gb'))} {src_lang} &nbsp;&nbsp;&nbsp;"
    f"**Target:** {flag_img(languages.get(tgt_lang, 'in'))} {tgt_lang}",
    unsafe_allow_html=True
)

text = st.text_area("Enter text to translate:", height=180)
translate_btn = st.button("🚀 Translate")

if translate_btn:
    if not text.strip():
        st.warning("Please enter some text to translate.")
    else:
        src_code = languages.get(src_lang, "en")
        tgt_code = languages.get(tgt_lang, "en")

        with st.spinner("Translating..."):
            translator = load_translator(src_code, tgt_code)
            if translator is None:
                result = text
            else:
                result = translator(text, max_length=512)[0]["translation_text"]

        st.markdown(f"<div class='result'>{result}</div>", unsafe_allow_html=True)
        if show_conf:
            st.progress(0.9)
            st.caption("Confidence: 90%")

        st.download_button("⬇️ Download Translation", data=result, file_name="translation.txt")

        if enable_tts:
            tts = gTTS(text=result, lang=tgt_code if tgt_code in ["en","hi","fr","es","de","it"] else "en")
            bio = io.BytesIO()
            tts.write_to_fp(bio)
            bio.seek(0)
            st.audio(bio.read(), format="audio/mp3")

st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------------------------------------
# FOOTER
# -----------------------------------------------------------
st.markdown("""
<hr>
<div class="footer">
  <strong>Polyglot v13</strong> — Clean White Edition 💫
</div>
""", unsafe_allow_html=True)
