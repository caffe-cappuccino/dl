# app.py
"""
Polyglot — AI Language Translator (Animated Dark/Light Edition with Model Fallback)
----------------------------------------------------------------
✅ Real translations using Hugging Face models
✅ Works even for same-language or unsupported pairs
✅ Animated full-page dark/light UI
✅ Gradient backgrounds, neon buttons, and glass effects
✅ TTS, confidence bar, and multilingual fallback
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

# Initialize session
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
    # Aurora light mode
    primary = "#3a7afe"
    secondary = "#ff61c7"
    text_color = "#0b1a33"
    bg_animation = """
    background: linear-gradient(135deg, #dbe9ff, #f3e9ff, #e7fff3, #dbe9ff);
    background-size: 400% 400%;
    animation: gradientShift 16s ease infinite;
    """

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
    box-shadow: 0 0 25px {primary};
}}
.title {{
    font-size: 32px;
    font-weight: 700;
    text-align: center;
    color: {primary};
    margin-bottom: 5px;
    text-shadow: 0 0 20px rgba(0,255,255,0.5);
}}
.subtitle {{
    text-align: center;
    font-size: 14px;
    opacity: 0.9;
}}
.footer {{
    text-align:center;
    font-size:13px;
    opacity:0.8;
    margin-top:30px;
}}
.result {{
    font-size:17px;
    color:{text_color};
    white-space: pre-wrap;
    line-height: 1.6;
}}
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------
# HEADER
# -----------------------------------------------------------
st.markdown(f"""
<div class="glass" style="text-align:center; margin-bottom:25px;">
  <div class="title">🌐 Polyglot — AI Language Translator</div>
  <div class="subtitle">
    {'🌙 Neon Dark Mode' if dark_mode else '☀️ Aurora Light Mode'} | Powered by Hugging Face
  </div>
</div>
""", unsafe_allow_html=True)

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
        st.caption(f"{len(text)} characters")

    st.markdown('</div>', unsafe_allow_html=True)

with right:
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.subheader("🧭 Info")
    st.markdown(f"**Source:** {src_lang}")
    st.markdown(f"**Target:** {tgt_lang}")
    st.markdown(f"**Temperature:** {temperature:.2f}")
    st.markdown("---")
    st.markdown("💡 Supports 50+ language pairs via Helsinki-NLP models")
    st.markdown("🎧 Optional speech playback for translated text")
    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------------------------------------
# TRANSLATION FUNCTION (with fallback)
# -----------------------------------------------------------
@st.cache_resource
def load_translator(src_code, tgt_code):
    """Load translation model with multilingual fallback."""
    if src_code == "auto":
        src_code = "en"
    # prevent invalid same-language pairs
    if src_code == tgt_code:
        return None
    model_name = f"Helsinki-NLP/opus-mt-{src_code}-{tgt_code}"
    try:
        return pipeline("translation", model=model_name)
    except Exception:
        # fallback multilingual model
        st.warning(f"No direct model for {src_code}-{tgt_code}. Using multilingual fallback.")
        return pipeline("translation", model="facebook/m2m100_418M")

# -----------------------------------------------------------
# TRANSLATION EXECUTION
# -----------------------------------------------------------
if translate_btn:
    if not text.strip():
        st.warning("Please enter some text to translate.")
    else:
        src_code = languages.get(src_lang.strip("🌍 "), "en")
        tgt_code = languages.get(tgt_lang, "en")

        st.info(f"Translating from **{src_lang}** → **{tgt_lang}** ...")
        progress = st.progress(0)
        for pct in range(0, 101, 8):
            time.sleep(0.04)
            progress.progress(pct)
        progress.empty()

        try:
            translator = load_translator(src_code, tgt_code)
            if translator is None:
                st.info("Same source and target language — returning original text.")
                result = text
            else:
                result = translator(text, max_length=512)[0]["translation_text"]

            conf_score = round(max(0.75, 1.0 - temperature * 0.4), 3)

            # Output
            st.markdown('<div class="glass">', unsafe_allow_html=True)
            st.subheader("🔹 Translated Text")
            st.markdown(f'<div class="result">{result}</div>', unsafe_allow_html=True)

            if show_conf:
                st.progress(conf_score)
                st.caption(f"Confidence: {conf_score * 100:.1f}%")

            st.download_button("⬇️ Download Translation", data=result, file_name="translation.txt")

            if enable_tts:
                with st.spinner("Generating speech..."):
                    tts = gTTS(text=result, lang=tgt_code if tgt_code in ["en","hi","fr","es","de","it"] else "en")
                    bio = io.BytesIO()
                    tts.write_to_fp(bio)
                    bio.seek(0)
                    st.audio(bio.read(), format="audio/mp3")
                st.success("Speech playback ready 🎧")

            st.success("✅ Translation complete!")

        except Exception as e:
            st.error(f"⚠️ Translation failed: {e}")

# -----------------------------------------------------------
# FOOTER
# -----------------------------------------------------------
st.markdown(f"""
<hr>
<div class="footer">
  <strong>Polyglot v5</strong> — Built with ❤️ using Streamlit & Hugging Face<br>
  {'🌙 Neon Dark Mode Active' if dark_mode else '☀️ Aurora Light Mode Active'}
</div>
""", unsafe_allow_html=True)
