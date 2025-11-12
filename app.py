import streamlit as st
from transformers import pipeline
import pandas as pd
import io
import os
import tempfile
import base64
import difflib

# Audio / speech-related imports (optional)
try:
    import speech_recognition as sr
    SR_AVAILABLE = True
except Exception:
    SR_AVAILABLE = False

try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except Exception:
    PYDUB_AVAILABLE = False

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except Exception:
    GTTS_AVAILABLE = False

# Optional browser recorder component (if installed on Streamlit Cloud)
try:
    from streamlit_audiorecorder import audiorecorder
    RECORDER_AVAILABLE = True
except Exception:
    RECORDER_AVAILABLE = False

# --------------------- Helper utilities ---------------------
LANG_NAME_TO_CODE = {
    "English": "en",
    "Hindi": "hi",
    "French": "fr",
    "German": "de",
    "Spanish": "es",
    # extend as needed
}

GTTS_LANG_MAP = {
    "English": "en",
    "Hindi": "hi",
    "French": "fr",
    "German": "de",
    "Spanish": "es",
}

def get_translation_model(src_code, tgt_code):
    """Return a Hugging Face pipeline for the language pair if available."""
    model_name = f"Helsinki-NLP/opus-mt-{src_code}-{tgt_code}"
    try:
        translator = pipeline("translation", model=model_name)
        return translator
    except Exception as e:
        st.warning(f"Model {model_name} not available: {e}")
        return None

def translate_text(translator, text):
    if translator is None:
        # fallback: return same text
        return text
    out = translator(text, max_length=1024)
    return out[0]["translation_text"]

def save_bytes_to_file(b: bytes, suffix: str = ".wav"):
    f = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    f.write(b)
    f.flush()
    f.close()
    return f.name

def convert_audio_to_wav(src_path: str) -> str:
    """
    Convert audio (mp3, m4a, etc.) to wav using pydub if available.
    Returns path to wav file.
    """
    if not PYDUB_AVAILABLE:
        raise RuntimeError("pydub not available; upload WAV files only.")
    audio = AudioSegment.from_file(src_path)
    wav_path = tempfile.NamedTemporaryFile(delete=False, suffix=".wav").name
    audio.export(wav_path, format="wav")
    return wav_path

def transcribe_wav_file(wav_path: str) -> str:
    if not SR_AVAILABLE:
        raise RuntimeError("speech_recognition not installed. Unable to transcribe.")
    r = sr.Recognizer()
    with sr.AudioFile(wav_path) as source:
        audio_data = r.record(source)
    # Use Google's free web API (requires internet)
    return r.recognize_google(audio_data)

def synthesize_tts(text: str, lang_name: str) -> bytes:
    if not GTTS_AVAILABLE:
        raise RuntimeError("gTTS not installed. Install gTTS to enable TTS.")
    lang = GTTS_LANG_MAP.get(lang_name, "en")
    tts = gTTS(text=text, lang=lang)
    b = io.BytesIO()
    tts.write_to_fp(b)
    b.seek(0)
    return b.read()

def make_download_link(bytes_data: bytes, filename: str, label: str):
    b64 = base64.b64encode(bytes_data).decode()
    href = f'<a href="data:audio/mp3;base64,{b64}" download="{filename}">{label}</a>'
    return href

# --------------------- Streamlit UI ---------------------
st.set_page_config(page_title="AI Translator + Speech", layout="wide", page_icon="🌍")
st.title("🌍 Neural Translator — Text + Speech (Input & Output)")

st.markdown(
    """
    **Features**
    - Type or paste text and translate.
    - Upload audio (wav/mp3) or record (browser recorder component if available) and auto-transcribe → translate.
    - Download or play synthesized translated audio (gTTS).
    """
)

# Sidebar settings
with st.sidebar:
    st.header("Settings")
    src_lang = st.selectbox("Source language", list(LANG_NAME_TO_CODE.keys()), index=0)
    tgt_lang = st.selectbox("Target language", list(LANG_NAME_TO_CODE.keys()), index=1)
    st.write("Model backend: Helsinki-NLP opus-mt translation pipelines (Hugging Face).")
    st.markdown("---")
    st.subheader("Optional: Glossary")
    st.info("This app currently performs raw translation. For entity-aware behavior, add glossary integration later.")

# Map to codes
src_code = LANG_NAME_TO_CODE[src_lang]
tgt_code = LANG_NAME_TO_CODE[tgt_lang]

# Load model (lazy)
translator = None
if st.button("Load translation model"):
    with st.spinner("Loading model (may take ~10–30s first time)..."):
        translator = get_translation_model(src_code, tgt_code)
        if translator:
            st.success("Model loaded. You can now translate.")
        else:
            st.error("Model could not be loaded. Will attempt to translate but may fallback.")

# Text translation section
st.header("1) Text translation")
text_input = st.text_area("Enter text to translate:", height=160)

col1, col2 = st.columns(2)
with col1:
    if st.button("Translate typed text"):
        if text_input.strip() == "":
            st.warning("Enter some text first.")
        else:
            # try to load model if not already
            if translator is None:
                translator = get_translation_model(src_code, tgt_code)
            if translator is None:
                st.info("Translator not available for this pair on HF. Using simple fallback (returns original).")
            with st.spinner("Translating..."):
                translated_text = translate_text(translator, text_input)
                st.subheader("Translated text")
                st.code(translated_text)
                # synthesize TTS button
                if GTTS_AVAILABLE:
                    try:
                        audio_bytes = synthesize_tts(translated_text, tgt_lang)
                        st.audio(audio_bytes, format="audio/mp3")
                        st.markdown(make_download_link(audio_bytes, "translated_audio.mp3", "⬇️ Download TTS (mp3)"), unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"TTS failed: {e}")
                else:
                    st.info("gTTS not available; TTS disabled.")
with col2:
    st.markdown("**Translation notes**")
    st.write("- Models: Helsinki-NLP/opus-mt-<src>-<tgt>. Not all pairs exist; fallback used when model missing.")
    st.write("- For better quality, consider fine-tuned models or larger models (mBART, M2M100).")
    st.write("- TTS powered by gTTS (Google TTS).")

st.markdown("---")

# Audio input / transcription section
st.header("2) Speech input → Transcribe & Translate")

st.markdown("**Option A — Upload an audio file** (WAV preferred; mp3/m4a supported if pydub installed)")
uploaded_file = st.file_uploader("Upload audio file (wav/mp3/m4a)", type=["wav", "mp3", "m4a", "ogg"])

transcribed_text = None
if uploaded_file is not None:
    st.info("Processing uploaded audio...")
    # Save upload to a temp file
    raw_bytes = uploaded_file.read()
    suffix = os.path.splitext(uploaded_file.name)[1] or ".wav"
    src_path = save_bytes_to_file(raw_bytes, suffix=suffix)
    try:
        if suffix.lower() != ".wav":
            if PYDUB_AVAILABLE:
                wav_path = convert_audio_to_wav(src_path)
            else:
                st.warning("Uploaded file is not WAV and pydub is not installed — please upload a WAV file or enable pydub.")
                wav_path = src_path  # try anyway
        else:
            wav_path = src_path

        if SR_AVAILABLE:
            with st.spinner("Transcribing uploaded audio using Google Speech recognition..."):
                try:
                    transcribed_text = transcribe_wav_file(wav_path)
                    st.success("Transcription complete")
                    st.write("**Transcribed text:**")
                    st.code(transcribed_text)
                except Exception as e:
                    st.error(f"Transcription failed: {e}")
        else:
            st.error("speech_recognition library not installed — transcription disabled.")
    finally:
        # try to cleanup temp files
        try:
            os.remove(src_path)
        except Exception:
            pass

# Option B: Browser recorder (if the component is installed)
if RECORDER_AVAILABLE:
    st.markdown("**Option B — Record in browser**")
    audio_bytes = audiorecorder("Click to record", "Recording...")  # returns bytes or None
    if audio_bytes:
        st.info("Recorded audio received; converting & transcribing...")
        try:
            path = save_bytes_to_file(audio_bytes, suffix=".wav")
            if SR_AVAILABLE:
                transcribed_text = transcribe_wav_file(path)
                st.success("Transcription complete")
                st.code(transcribed_text)
            else:
                st.error("speech_recognition not installed — cannot transcribe.")
        except Exception as e:
            st.error(f"Recording handling failed: {e}")
        finally:
            try:
                os.remove(path)
            except Exception:
                pass
else:
    st.info("Browser recording component not installed. You can upload an audio file instead.")

# If we got a transcription, auto-translate and offer TTS
if transcribed_text:
    st.markdown("### Translate transcription and synthesize TTS")
    if st.button("Translate transcription"):
        if translator is None:
            translator = get_translation_model(src_code, tgt_code)
        with st.spinner("Translating transcription..."):
            translated_text = translate_text(translator, transcribed_text)
            st.subheader("Translated text")
            st.code(translated_text)

            # TTS
            if GTTS_AVAILABLE:
                try:
                    audio_bytes = synthesize_tts(translated_text, tgt_lang)
                    st.audio(audio_bytes, format="audio/mp3")
                    st.markdown(make_download_link(audio_bytes, "translated_audio.mp3", "⬇️ Download TTS (mp3)"), unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"TTS failed: {e}")
            else:
                st.info("gTTS not available; TTS disabled.")

st.markdown("---")
st.caption("Notes: For transcription we use the Google Web Speech API via `speech_recognition`. In production, consider a paid ASR for higher reliability. For TTS we use gTTS (Google).")
