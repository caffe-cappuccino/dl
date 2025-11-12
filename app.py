# app.py
"""
Polyglot — AI Language Translator (single-file Streamlit app)

Run:
    streamlit run app.py

Features:
- Modern, minimalistic UI with soft gradient + glassmorphism.
- Sidebar controls: source (Auto Detect), target, toggle confidence, temperature slider.
- Main UI: input text area, Translate button, Swap Languages button, translation box with download.
- Simulated progress + confidence score (placeholders) and clear integration points for real translation APIs.
- Optional voice input (upload) + TTS playback if gTTS installed.
- Responsive layout using Streamlit columns and tabs.

Notes for developers:
- Replace `translate_via_api(...)` with actual integration to Google Translate API, Hugging Face, or your own model server.
- `simulate_confidence(...)` is a placeholder; replace with model-reported confidence if available.
- For TTS, gTTS is optionally supported. If you want live browser recording, add a recorder component and transcription backend (Whisper / Speech-to-Text API).
"""

from typing import Tuple, Optional, Dict
import streamlit as st
import time
import random
import io

# Optional audio libs (used only if present)
try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except Exception:
    GTTS_AVAILABLE = False

try:
    import speech_recognition as sr
    SR_AVAILABLE = True
except Exception:
    SR_AVAILABLE = False

# -------------------------
# Page config & styling
# -------------------------
st.set_page_config(page_title="Polyglot — AI Language Translator",
                   page_icon="🌐",
                   layout="wide",
                   initial_sidebar_state="expanded")

# Custom CSS for gradient background, glass card, subtle animations
st.markdown(
    """
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
      html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

      /* page background */
      .reportview-container .main {
        background: linear-gradient(135deg, #f7fbff 0%, #f0fff9 50%, #fff7ff 100%);
      }

      /* container card */
      .glass {
        background: rgba(255,255,255,0.6);
        border-radius: 12px;
        padding: 18px;
        box-shadow: 0 6px 18px rgba(16,24,40,0.06);
        backdrop-filter: blur(6px);
        border: 1px solid rgba(255,255,255,0.6);
      }

      .title {
        font-size: 26px;
        font-weight: 700;
        color: #07263a;
      }

      .subtitle {
        color: #27496d;
        margin-top: 4px;
        font-size: 13px;
      }

      .translate-result {
        font-size: 15px;
        line-height: 1.6;
        color: #0b2545;
        white-space: pre-wrap;
      }

      .btn-swap {
        background: linear-gradient(90deg,#a1c4fd,#c2e9fb);
        border-radius: 8px;
        padding: 6px 10px;
      }

      .footer {
        color: #5b6b74;
        font-size: 13px;
        text-align: center;
        padding-top: 14px;
      }

      /* subtle hover */
      button[sb-kind="primary"]:hover { transform: translateY(-1px); transition: all .12s ease-in; }

      /* responsive tweaks */
      @media (max-width: 640px) {
        .title { font-size: 20px; }
      }
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------------
# Helper / Placeholder Logic
# -------------------------
# Language list and mapping to codes (expandable)
LANGUAGES = [
    ("Auto Detect", "auto"),
    ("English", "en"),
    ("Hindi", "hi"),
    ("French", "fr"),
    ("Spanish", "es"),
    ("German", "de"),
    ("Bengali", "bn"),
    ("Chinese (Simplified)", "zh"),
    ("Portuguese", "pt"),
    ("Arabic", "ar"),
]

LANG_NAME_TO_CODE = {name: code for name, code in LANGUAGES}
LANG_CODE_TO_NAME = {code: name for name, code in LANGUAGES}

def simulate_progress(duration: float = 1.0):
    """
    Small helper to show a progress spinner-like animation.
    Use st.progress for a visible bar.
    """
    progress = st.progress(0)
    steps = 20
    for i in range(steps + 1):
        progress.progress(min(100, int(i / steps * 100)))
        time.sleep(duration / steps)
    progress.empty()

def simulate_confidence(text: str, temperature: float) -> float:
    """
    Placeholder heuristic for a 'confidence' score.
    Replace with model-provided confidence if available.
    """
    if not text.strip():
        return 0.0
    base = max(0.1, 1.0 - (len(text) / 1200.0))
    noise = random.uniform(-0.05, 0.05)
    temp_effect = (1.0 - temperature) * 0.1  # lower temperature -> slightly higher confidence
    score = min(0.99, max(0.01, base + temp_effect + noise))
    return round(score, 3)

# -------------------------
# TRANSLATION API placeholder
# -------------------------
def translate_via_api(text: str,
                      src_code: str,
                      tgt_code: str,
                      temperature: float = 0.2) -> Tuple[str, float]:
    """
    Integrate your actual translation model or API here.

    Example integration points:
    - Google Translate API: call Google Cloud Translate and return translated text (confidence may not be provided).
    - Hugging Face: use transformers pipeline (AutoModelForSeq2SeqLM) to generate translation and compute/logit-based confidence.
    - Custom backend: POST to your model server (FastAPI/Flask) that returns {"translation": "...", "confidence": 0.92}.

    For this deliverable, this function simulates translation and returns (translated_text, confidence_score).

    Replace the body with actual HTTP requests or local model code.
    """
    # --- SIMULATED TRANSLATION (demo) ---
    # Very simple "pseudo-translation" to make the UI feel real:
    words = text.strip().split()
    if not words:
        return "", 0.0

    # Demo behaviors:
    # - For "auto" source, pretend detection to English
    if src_code == "auto":
        detected = "en"
    else:
        detected = src_code

    # Create a mock translated string with simple token transforms
    translated_tokens = []
    for i, w in enumerate(words):
        # rotate case and reverse short tokens to simulate transformation
        if len(w) <= 3:
            token = w[::-1]
        else:
            token = w.capitalize() if i % 2 == 0 else w.lower()
        translated_tokens.append(token)
    translated_text = " ".join(translated_tokens)

    # append small tag to indicate language and temperature
    translated_text = f"{translated_text}  [{detected}->{tgt_code} | temp={temperature:.2f}]"

    # simulated confidence
    conf = simulate_confidence(text, temperature)
    return translated_text, conf

# -------------------------
# UI: SIDEBAR
# -------------------------
with st.sidebar:
    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    st.markdown("<div style='display:flex;align-items:center;gap:10px'>"
                "<div style='font-weight:700;font-size:18px'>Polyglot</div>"
                "<div style='color:#536b7a;font-size:12px;margin-left:6px'>AI Language Translator</div></div>",
                unsafe_allow_html=True)
    st.markdown("---")

    # Source language (with Auto Detect option)
    src_name = st.selectbox("Source language", [name for name, _ in LANGUAGES], index=0)
    src_code = LANG_NAME_TO_CODE.get(src_name, "auto")

    # Target language
    targ_names = [name for name, _ in LANGUAGES if name != "Auto Detect"]
    tgt_name = st.selectbox("Target language", targ_names, index=0)
    tgt_code = LANG_NAME_TO_CODE.get(tgt_name, "en")

    st.markdown("---")
    # Toggle for confidence score
    show_confidence = st.checkbox("Show Confidence Score", value=True)

    # Temperature slider (0.0 - 1.0)
    temperature = st.slider("Translation Temperature", min_value=0.0, max_value=1.0, value=0.2, step=0.05,
                            help="Higher temperature -> more diverse translations; lower -> more deterministic")

    st.markdown("---")
    st.markdown("Accessibility & extras")
    enable_voice = st.checkbox("Enable voice input (upload)", value=False)
    enable_tts = st.checkbox("Enable text-to-speech (gTTS)", value=False if not GTTS_AVAILABLE else True)
    st.markdown("---")
    st.caption("Replace the translation function with a real model or API in translate_via_api().")
    st.markdown("</div>", unsafe_allow_html=True)

# -------------------------
# MAIN: Header & Layout
# -------------------------
st.markdown("""
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">
      <div>
        <div style="font-weight:700;font-size:26px;color:#07263a">Polyglot — AI Language Translator</div>
        <div style="color:#27496d;margin-top:4px">Fast, modern, and accessible translations — powered by your models.</div>
      </div>
      <div style="text-align:right;color:#27496d;font-size:13px">
        <strong>Target:</strong> {tgt} &nbsp; • &nbsp; <strong>Temp:</strong> {temp:.2f}
      </div>
    </div>
""".format(tgt=tgt_name, temp=temperature), unsafe_allow_html=True)

# Columns: input + controls / info
col_input, col_info = st.columns([3, 1], gap="large")

with col_input:
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    # Input text area
    placeholder = "Enter text to translate..."
    input_text = st.text_area("Source text", placeholder=placeholder, height=200, key="input_text")

    # Row of action buttons: Swap and Translate
    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        if st.button("↔️ Swap Languages"):
            # Swap displayed languages in the sidebar selections
            # Note: This is a UI convenience — we update session_state and rerun so sidebar reflects swap
            prev_src = src_name
            prev_tgt = tgt_name
            # Update session state to swap (these keys will be used below)
            st.session_state["swap_from"] = prev_src
            st.session_state["swap_to"] = prev_tgt
            # Because we cannot directly set sidebar selectbox values from here,
            # we suggest refreshing the page; but we can store swap instruction and inform user.
            st.info("Languages swapped in memory. Re-open the sidebar to confirm. (Refresh to apply.)")

    with c2:
        translate_pressed = st.button("🚀 Translate")

    with c3:
        # Clear text button
        if st.button("🧹 Clear"):
            st.experimental_set_query_params()  # no-op to trigger session update
            # clear input by setting session state
            st.session_state["input_text"] = ""
            # direct assign not always effective due to key naming; instruct user
            st.info("Cleared input (you may need to remove leftover text manually).")

    st.markdown("</div>", unsafe_allow_html=True)

    # Voice input upload (optional)
    if enable_voice:
        st.markdown("<div style='margin-top:10px'>", unsafe_allow_html=True)
        uploaded_audio = st.file_uploader("Upload audio (wav/mp3) for speech-to-text (optional)", type=["wav", "mp3", "m4a"], accept_multiple_files=False)
        if uploaded_audio is not None:
            if not SR_AVAILABLE:
                st.warning("Speech recognition library not installed. Transcription will not run. Install `speech_recognition` and required system deps.")
            else:
                st.info("Audio uploaded. Transcription will run upon Translate.")
        st.markdown("</div>", unsafe_allow_html=True)

    # Result area container
    result_container = st.empty()

with col_info:
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown("### Info")
    st.markdown(f"- **Source:** {src_name}")
    st.markdown(f"- **Target:** {tgt_name}")
    st.markdown(f"- **Temperature:** {temperature:.2f}")
    st.markdown("- **Supported languages:** " + ", ".join([name for name, _ in LANGUAGES if name != "Auto Detect"]))
    st.markdown("---")
    st.markdown("### Accuracy note")
    st.markdown("Translation accuracy depends on the underlying model or API. For high-fidelity translations, integrate a production MT model or a cloud translation service.")
    st.markdown("---")
    st.markdown("### Accessibility")
    if enable_tts:
        st.markdown("- Text-to-speech enabled (gTTS).")
    else:
        st.markdown("- Text-to-speech disabled.")
    st.markdown("</div>", unsafe_allow_html=True)

# -------------------------
# TRANSLATION ACTION
# -------------------------
if translate_pressed:
    if not input_text.strip():
        st.warning("Please enter some text to translate.")
    else:
        # If voice file uploaded, you could transcribe first — placeholder behavior:
        transcribed_from_audio = None
        if enable_voice and 'uploaded_audio' in locals() and uploaded_audio is not None and SR_AVAILABLE:
            # Simple transcription using speech_recognition (Google) - note: network call
            try:
                with st.spinner("Transcribing audio..."):
                    r = sr.Recognizer()
                    # Save to temporary file-like object
                    audio_bytes = uploaded_audio.read()
                    audio_file = io.BytesIO(audio_bytes)
                    audio_file.seek(0)
                    with sr.AudioFile(audio_file) as source:
                        audio_data = r.record(source)
                    transcribed_from_audio = r.recognize_google(audio_data)
                    st.success("Audio transcribed.")
                    # Use transcribed text as input if present
                    full_input_text = transcribed_from_audio
                # show transcribed text
                result_container.info("Transcribed audio: " + transcribed_from_audio)
            except Exception as e:
                st.error(f"Audio transcription failed: {e}")
                full_input_text = input_text
        else:
            full_input_text = input_text

        # simulate progress / spinner
        with st.spinner("Translating..."):
            # show short simulated progress bar depending on temperature (more accurate -> slower)
            dur = 0.9 + (0.6 * temperature)
            simulate_progress(duration=dur)
            # Call the translation function (placeholder)
            translated_text, confidence = translate_via_api(full_input_text, src_code, tgt_code, temperature)

        # Render output in glass card
        with result_container:
            st.markdown('<div class="glass">', unsafe_allow_html=True)
            st.markdown("### Translated text")
            st.markdown(f'<div class="translate-result">{translated_text}</div>', unsafe_allow_html=True)

            # Show confidence if requested
            if show_confidence:
                conf_pct = int(round(confidence * 100))
                st.markdown(f"**Confidence:** {conf_pct}%")
                st.progress(conf_pct / 100.0)

            # Download button for translated text
            out_bytes = translated_text.encode("utf-8")
            st.download_button("⬇️ Download translation (.txt)", data=out_bytes, file_name="translation.txt", mime="text/plain")

            # Optional: TTS playback
            if enable_tts and GTTS_AVAILABLE:
                try:
                    tts = gTTS(text=translated_text, lang=LANG_NAME_TO_CODE.get(tgt_name, "en"))
                    bio = io.BytesIO()
                    tts.write_to_fp(bio)
                    bio.seek(0)
                    st.audio(bio.read(), format="audio/mp3")
                except Exception as e:
                    st.error(f"TTS failed: {e}")
            elif enable_tts and not GTTS_AVAILABLE:
                st.info("gTTS not available in this environment. Install gTTS for TTS support.")

            st.markdown("</div>", unsafe_allow_html=True)

        # Notify success (use toast if available else success)
        try:
            if hasattr(st, "toast"):
                st.toast("Translation complete 🎉")
            else:
                st.success("Translation complete 🎉")
        except Exception:
            st.success("Translation complete 🎉")

# -------------------------
# Footer
# -------------------------
st.markdown("---")
st.markdown('<div class="footer">Polyglot — AI Language Translator • Powered by AI Translation • Built with Streamlit</div>', unsafe_allow_html=True)
