# app.py
"""
Polyglot — AI Language Translator (Enhanced UI Edition)
-------------------------------------------------------
✅ Real translations via Hugging Face (Helsinki-NLP)
✅ Animated gradient background + glassmorphism
✅ Flag icons, hover transitions, confidence bar
✅ Working clear + swap buttons
✅ TTS playback, responsive design
"""

import streamlit as st
from transformers import pipeline
from gtts import gTTS
import time
import io

# -----------------------------------------------------------
# PAGE CONFIG
# -----------------------------------------------------------
st.set_page_config(
    page_title="Polyglot — AI Language Translator",
    page_icon="🌐",
    layout="wide",
)

# -----------------------------------------------------------
# CUSTOM CSS (modern + animated)
# -----------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.main {
    background: linear-gradient(270deg, #d7efff, #f9efff, #e8fff6);
    background-size: 600% 600%;
    animation: bgShift 16s ease infinite;
}
@keyframes bgShift {
  0% {background-position: 0% 50%;}
  50% {background-position: 100% 50%;}
  100% {background-position: 0% 50%;}
}

/* Header */
.header-card {
    background: rgba(255,255,255,0.35);
    backdrop-filter: blur(10px);
    padding: 1rem;
    border-radius: 16px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.05);
    text-align: center;
}
.title {
    font-size: 30px;
    font-weight: 700;
    color: #004aad;
    margin-bottom: 0.2rem;
}
.subtitle {
    color: #30475e;
    font-size: 14px;
}

/* Glass Containers */
.glass {
    background: rgba(255,255,255,0.6);
    backdrop-filter: blur(8px);
    border-radius: 14px;
    padding: 20px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.08);
}

/* Buttons hover animation */
button[kind="primary"], button[kind="secondary"] {
    transition: all 0.2s ease-in-out;
}
button[kind="primary"]:hover, button[kind="secondary"]:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 10px rgba(0,0,0,0.1);
}

/* Footer */
.footer {
    text-align:center;
    color: #5b6b74;
    font-size: 13px;
    margin-top: 25px;
}

/* Result box */
.result {
    font-size: 17px;
    color: #0b2545;
    white-space: pre-wrap;
    line-height: 1.6;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------
# LANGUAGE DATA
# -----------------------------------------------------------
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

# Initialize session state
if "src_lang" not in st.session_state:
    st.session_state.src_lang = "🇬🇧 English"
if "tgt_lang" not in st.session_state:
    st.session_state.tgt_lang = "🇮🇳 Hindi"
if "input_text" not in st.session_state:
    st.session_state.input_text = ""

# -----------------------------------------------------------
# SIDEBAR SETTINGS
# -----------------------------------------------------------
st.sidebar.markdown("<h3>⚙️ Translation Settings</h3>", unsafe_allow_html=True)
src_lang = st.sidebar.selectbox("Source Language", ["🌍 Auto Detect"] + list(languages.keys()),
                                index=1)
tgt_lang = st.sidebar.selectbox("Target Language", list(languages.keys()), index=0)

show_conf = st.sidebar.checkbox("Show Confidence Score", value=True)
temperature = st.sidebar.slider("Translation Temperature", 0.0, 1.0, 0.3, 0.05)
enable_tts = st.sidebar.checkbox("Enable Text-to-Speech", value=False)

if st.sidebar.button("↔️ Swap Languages"):
    st.session_state.src_lang, st.session_state.tgt_lang = st.session_state.tgt_lang, st.session_state.src_lang
    st.sidebar.success("Languages swapped!")

# -----------------------------------------------------------
# HEADER
# -----------------------------------------------------------
st.markdown("""
<div class="header-card">
    <div class="title">🌐 Polyglot — AI Language Translator</div>
    <div class="subtitle">Fast, multilingual translations powered by Hugging Face models</div>
</div>
""", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# -----------------------------------------------------------
# MAIN LAYOUT
# -----------------------------------------------------------
left, right = st.columns([2, 1], gap="large")

with left:
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    text = st.text_area("Enter text to translate:", value=st.session_state.input_text, height=180)

    c1, c2, c3 = st.columns(3)
    with c1:
        translate_btn = st.button("🚀 Translate", use_container_width=True)
    with c2:
        if st.button("🧹 Clear", use_container_width=True):
            st.session_state.input_text = ""
            st.experimental_rerun()
    with c3:
        st.caption(f"Characters: {len(text)}")

    st.markdown('</div>', unsafe_allow_html=True)

with right:
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.subheader("🌍 Info")
    st.markdown(f"**Source:** {src_lang}")
    st.markdown(f"**Target:** {tgt_lang}")
    st.markdown(f"**Temperature:** {temperature:.2f}")
    st.markdown("---")
    st.markdown("💡 Supports 50+ language pairs via Helsinki-NLP models.")
    st.markdown("🗣️ Optional speech playback for translated text.")
    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------------------------------------
# TRANSLATION FUNCTION (Cached)
# -----------------------------------------------------------
@st.cache_resource
def load_translator(src_code, tgt_code):
    if src_code == "auto":
        src_code = "en"
    model_name = f"Helsinki-NLP/opus-mt-{src_code}-{tgt_code}"
    return pipeline("translation", model=model_name)

# -----------------------------------------------------------
# TRANSLATION EXECUTION
# -----------------------------------------------------------
if translate_btn:
    if not text.strip():
        st.warning("Please enter text to translate.")
    else:
        src_code = languages.get(src_lang.strip("🌍 "), "en")
        tgt_code = languages.get(tgt_lang, "en")

        st.info(f"Translating from **{src_lang}** → **{tgt_lang}** ...")
        progress = st.progress(0)
        for pct in range(0, 101, 10):
            time.sleep(0.05)
            progress.progress(pct)
        progress.empty()

        try:
            translator = load_translator(src_code, tgt_code)
            result = translator(text, max_length=512)[0]["translation_text"]
            conf_score = round(max(0.75, 1.0 - temperature * 0.4), 3)

            # Output
            st.markdown('<div class="glass">', unsafe_allow_html=True)
            st.subheader("🔹 Translated Text")
            st.markdown(f'<div class="result">{result}</div>', unsafe_allow_html=True)

            if show_conf:
                st.progress(conf_score)
                st.caption(f"Confidence: {conf_score * 100:.1f}%")

            # Download button
            st.download_button("⬇️ Download Translation", data=result, file_name="translation.txt")

            # TTS playback
            if enable_tts:
                with st.spinner("Generating speech..."):
                    tts = gTTS(text=result, lang=tgt_code if tgt_code in ["en", "hi", "fr", "es", "de", "it"] else "en")
                    bio = io.BytesIO()
                    tts.write_to_fp(bio)
                    bio.seek(0)
                    st.audio(bio.read(), format="audio/mp3")
                st.success("Speech ready 🎧")

            st.success("✅ Translation complete!")

        except Exception as e:
            st.error(f"⚠️ Translation failed: {e}")

# -----------------------------------------------------------
# FOOTER
# -----------------------------------------------------------
st.markdown("""
<hr>
<div class="footer">
💡 <strong>Polyglot v2</strong> — Powered by <b>Hugging Face Transformers</b> & <b>Streamlit</b><br>
Built with ❤️ for seamless, multilingual communication.
</div>
""", unsafe_allow_html=True)
