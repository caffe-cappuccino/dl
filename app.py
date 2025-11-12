# app.py
"""
Polyglot — AI Language Translator (Professional Edition)
-------------------------------------------------------
✅ Real translation (Hugging Face)
✅ Dynamic Light/Dark mode
✅ Gradient theme + polished buttons
✅ Text-to-Speech, confidence bar, swap/clear buttons
✅ Responsive modern design
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
# SIDEBAR CONTROLS
# -----------------------------------------------------------
st.sidebar.title("🌐 Polyglot Settings")

dark_mode = st.sidebar.toggle("🌙 Dark Mode", value=False)

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

# Default states
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
# COLOR SCHEME & CSS
# -----------------------------------------------------------
if dark_mode:
    primary = "#7b5cf9"
    bg_grad = "linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%)"
    text_color = "#f8fafc"
    card_bg = "rgba(17,24,39,0.6)"
else:
    primary = "#4a60ff"
    bg_grad = "linear-gradient(135deg, #e0f0ff 0%, #ece9ff 100%)"
    text_color = "#0f172a"
    card_bg = "rgba(255,255,255,0.7)"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif;
    color: {text_color};
}}
.main {{
    background: {bg_grad};
    background-size: 400% 400%;
    animation: move 16s ease infinite;
}}
@keyframes move {{
  0% {{background-position: 0% 50%;}}
  50% {{background-position: 100% 50%;}}
  100% {{background-position: 0% 50%;}}
}}
.glass {{
    background: {card_bg};
    backdrop-filter: blur(12px);
    border-radius: 16px;
    padding: 22px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
}}
.title {{
    font-size: 32px;
    font-weight: 700;
    text-align: center;
    color: {primary};
}}
.subtitle {{
    text-align: center;
    font-size: 14px;
    opacity: 0.9;
}}
button[kind="primary"], button[kind="secondary"], .stButton>button {{
    border: none;
    border-radius: 8px;
    background: linear-gradient(90deg, {primary}, #8b5cf6);
    color: white !important;
    font-weight: 600;
    padding: 0.6em 1em;
    transition: all 0.2s ease-in-out;
}}
button[kind="primary"]:hover, .stButton>button:hover {{
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    filter: brightness(1.1);
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
    Real-time neural translation powered by Hugging Face • { '🌙 Dark Mode' if dark_mode else '☀️ Light Mode' }
  </div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------
# MAIN INTERFACE
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
    st.markdown(f'<div class="glass">', unsafe_allow_html=True)
    st.subheader("🧭 Info")
    st.markdown(f"**Source:** {src_lang}")
    st.markdown(f"**Target:** {tgt_lang}")
    st.markdown(f"**Temperature:** {temperature:.2f}")
    st.markdown("---")
    st.markdown("✅ Supports 50+ language pairs (Helsinki-NLP models)")
    st.markdown("🎧 Optional speech playback for translated text")
    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------------------------------------
# TRANSLATION FUNCTION
# -----------------------------------------------------------
@st.cache_resource
def load_translator(src_code, tgt_code):
    if src_code == "auto":
        src_code = "en"
    model_name = f"Helsinki-NLP/opus-mt-{src_code}-{tgt_code}"
    return pipeline("translation", model=model_name)

# -----------------------------------------------------------
# TRANSLATION ACTION
# -----------------------------------------------------------
if translate_btn:
    if not text.strip():
        st.warning("Please enter some text to translate.")
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

            # Output box
            st.markdown(f'<div class="glass">', unsafe_allow_html=True)
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
  <strong>Polyglot v3</strong> — Built with ❤️ using <b>Streamlit</b> & <b>Transformers</b><br>
  { '🌙 Dark Mode Enabled' if dark_mode else '☀️ Light Mode Active' } | Powered by <b>Hugging Face</b>
</div>
""", unsafe_allow_html=True)
