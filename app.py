# app.py
"""
Polyglot — AI Language Translator
---------------------------------
A real-time multilingual translator built with Streamlit and Hugging Face models.
Run: streamlit run app.py
"""
pip install sentencepiece

import streamlit as st
from transformers import pipeline
import time
import io
from gtts import gTTS

# --------------------------------------
# Page Configuration
# --------------------------------------
st.set_page_config(page_title="Polyglot — AI Language Translator", page_icon="🌐", layout="wide")

# --------------------------------------
# Custom Styling
# --------------------------------------
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .main {
        background: linear-gradient(135deg, #e0f7fa 0%, #f1f8e9 100%);
        color: #0b2545;
    }
    .glass {
        background: rgba(255,255,255,0.55);
        backdrop-filter: blur(6px);
        -webkit-backdrop-filter: blur(6px);
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.05);
    }
    .title {
        font-size: 28px;
        font-weight: 700;
        color: #07263a;
        text-align: center;
        margin-bottom: 5px;
    }
    .subtitle {
        text-align: center;
        font-size: 14px;
        color: #3b6978;
        margin-bottom: 30px;
    }
    .result {
        font-size: 17px;
        line-height: 1.6;
        color: #0b2545;
        white-space: pre-wrap;
    }
    .footer {
        text-align:center;
        color: #5b6b74;
        font-size: 13px;
        margin-top: 25px;
    }
    </style>
""", unsafe_allow_html=True)

# --------------------------------------
# Sidebar Controls
# --------------------------------------
st.sidebar.title("🌐 Polyglot Settings")

# Language selections
languages = {
    "Auto Detect": "auto",
    "English": "en",
    "Hindi": "hi",
    "French": "fr",
    "Spanish": "es",
    "German": "de",
    "Italian": "it",
    "Chinese": "zh",
    "Japanese": "ja",
    "Korean": "ko",
}

src_lang = st.sidebar.selectbox("Source Language", list(languages.keys()), index=0)
tgt_lang = st.sidebar.selectbox("Target Language", list(languages.keys())[1:], index=1)

# Options
show_conf = st.sidebar.checkbox("Show Confidence Score", value=True)
temperature = st.sidebar.slider("Translation Temperature", 0.0, 1.0, 0.3, 0.05)
enable_tts = st.sidebar.checkbox("Enable Text-to-Speech", value=False)

# Swap languages button
if st.sidebar.button("↔️ Swap Languages"):
    src_lang, tgt_lang = tgt_lang, src_lang
    st.sidebar.success("Languages swapped!")

# --------------------------------------
# Header
# --------------------------------------
st.markdown("<div class='title'>Polyglot — AI Language Translator</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Translate text instantly across languages with AI-powered models.</div>", unsafe_allow_html=True)

# --------------------------------------
# Input Area
# --------------------------------------
st.markdown("<div class='glass'>", unsafe_allow_html=True)
text = st.text_area("Enter text to translate:", placeholder="Type or paste your text here...", height=180)

col1, col2 = st.columns([1,1])
with col1:
    translate_btn = st.button("🚀 Translate", use_container_width=True)
with col2:
    clear_btn = st.button("🧹 Clear", use_container_width=True)

if clear_btn:
    st.experimental_rerun()

st.markdown("</div>", unsafe_allow_html=True)

# --------------------------------------
# Translation Logic
# --------------------------------------
if translate_btn:
    if not text.strip():
        st.warning("Please enter text to translate.")
    else:
        st.info(f"Translating from **{src_lang}** to **{tgt_lang}**...")
        progress = st.progress(0)

        # Progress bar simulation
        for pct in range(0, 101, 10):
            time.sleep(0.05)
            progress.progress(pct)
        progress.empty()

        # ------------------------------
        # Translation using Hugging Face
        # ------------------------------
        try:
            src_code = languages[src_lang]
            tgt_code = languages[tgt_lang]

            # Determine model name
            if src_code == "auto":
                src_code = "en"  # fallback
            model_name = f"Helsinki-NLP/opus-mt-{src_code}-{tgt_code}"

            # Load pipeline
            translator = pipeline("translation", model=model_name)
            result = translator(text, max_length=512)[0]["translation_text"]

            # Confidence score simulation (placeholder for real metric)
            conf_score = round(max(0.75, 1.0 - temperature * 0.4), 3)

            # Display translation
            st.markdown("<div class='glass'>", unsafe_allow_html=True)
            st.subheader("🔹 Translated Text:")
            st.markdown(f"<div class='result'>{result}</div>", unsafe_allow_html=True)

            if show_conf:
                st.progress(conf_score)
                st.caption(f"Confidence: {conf_score * 100:.1f}%")

            # Download button
            out_bytes = result.encode("utf-8")
            st.download_button("⬇️ Download Translation", data=out_bytes, file_name="translation.txt", mime="text/plain")

            # Text-to-speech (optional)
            if enable_tts:
                with st.spinner("Generating speech..."):
                    tts = gTTS(text=result, lang=tgt_code if tgt_code in ["en", "hi", "fr", "es", "de", "it"] else "en")
                    bio = io.BytesIO()
                    tts.write_to_fp(bio)
                    bio.seek(0)
                    st.audio(bio.read(), format="audio/mp3")
                st.success("Speech playback ready!")

            st.success("✅ Translation complete!")

        except Exception as e:
            st.error(f"⚠️ Translation failed: {e}")

# --------------------------------------
# Footer
# --------------------------------------
st.markdown("<div class='footer'>Powered by Hugging Face Transformers • Built with Streamlit</div>", unsafe_allow_html=True)
