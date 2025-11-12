# app.py
"""
NeuraLingua — AI Translation Studio (single-file Streamlit app)

Run:
    streamlit run app.py

Notes:
- This is a fully runnable UI with dummy model functions (translate_dummy_*).
- Replace the dummy translate functions (marked below) with actual model calls or API requests
  to your EACT, RG-CLD, and EFC implementations.
- Requires streamlit>=1.30.0
"""

import streamlit as st
import time
import random
import io
from typing import Tuple, Dict

# -----------------------------
# Page config & global styling
# -----------------------------
st.set_page_config(
    page_title="NeuraLingua — AI Translation Studio",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inject custom CSS for gradient background, fonts, glassmorphism, responsive layout
st.markdown(
    """
    <style>
    /* Import a clean font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
    }

    /* Soft gradient background */
    .main > div.block-container {
        background: linear-gradient(135deg, rgba(250,245,255,0.6), rgba(232,250,255,0.6));
        padding: 1.5rem 2rem;
        border-radius: 12px;
    }

    /* Header styling */
    .neural-header {
        display:flex; align-items:center; justify-content:space-between;
        gap:12px; margin-bottom: 18px;
    }
    .neural-title {
        font-size:28px; font-weight:700; color:#0b2545;
    }
    .neural-sub {
        color:#27496d; opacity:0.9; margin-top:4px; font-size:13px;
    }

    /* Glass card */
    .glass {
      background: rgba(255, 255, 255, 0.55);
      box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.08);
      backdrop-filter: blur(6px);
      -webkit-backdrop-filter: blur(6px);
      border-radius: 12px;
      border: 1px solid rgba(255,255,255,0.6);
      padding: 18px;
    }

    /* Output text styling */
    .translation-text {
        font-size:16px; line-height:1.5; color:#071235;
        white-space:pre-wrap;
    }

    /* Confidence bar wrapper */
    .conf-wrap { width:100%; margin-top:10px; }

    /* Footer */
    .footer { color:#5b6b74; font-size:12px; padding-top:10px; margin-top:18px; text-align:center; }

    /* Responsive tweaks */
    @media (max-width: 640px) {
        .neural-title { font-size:20px; }
        .glass { padding:14px; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# Utility / Dummy model logic
# -----------------------------
def simulate_progress(speed_mode: int, description: str = "Translating") -> None:
    """
    Simulate a progress bar animation.
    speed_mode: 0 balanced, 1 fast, 2 accurate (slower)
    """
    prog = st.progress(0)
    # Deterministic but different durations based on speed_mode
    if speed_mode == 1:
        steps = 6
        delay = 0.10
    elif speed_mode == 2:
        steps = 18
        delay = 0.12
    else:
        steps = 10
        delay = 0.10

    for i in range(steps + 1):
        prog.progress(min(100, int(i / steps * 100)))
        # small random jitter for liveliness
        time.sleep(delay + (random.random() - 0.5) * 0.02)
    prog.empty()

def compute_confidence_base(text: str) -> float:
    """
    Heuristic confidence score based on text features.
    Replace with real model-provided confidences later.
    """
    if not text.strip():
        return 0.0
    # Favor shorter sentences slightly; penalize many punctuation marks
    length_score = max(0.15, min(0.95, 1.0 - (len(text) / 1000)))
    punct_penalty = text.count('?') * 0.02 + text.count('!') * 0.01
    entropy_noise = random.uniform(-0.05, 0.05)
    score = length_score - punct_penalty + entropy_noise
    return max(0.02, min(0.99, score))

# Dummy inference functions for each model:
# Replace the body with actual model calls to your trained EACT / RG-CLD / EFC systems.
def translate_dummy_eact(text: str, src: str, tgt: str, speed: int) -> Tuple[str, float]:
    """
    Simulated EACT (Entity-Aware Contrastive Tuning) translation.
    Returns (translated_text, confidence_score)
    """
    # Very simple pseudo-translation: reverse words + stylized tag
    words = text.split()
    translated = " ".join(words[::-1])
    # Pretend EACT preserves entities -> wrap capitalized tokens with <>
    translated = " ".join([f"<{w}>" if w.istitle() else w for w in translated.split()])
    # Slightly higher confidence for 'accurate' mode
    base = compute_confidence_base(text)
    confidence = min(0.995, base + (0.08 if speed == 2 else 0.02))
    return f"[EACT] {translated}", round(confidence, 3)

def translate_dummy_rgcld(text: str, src: str, tgt: str, speed: int) -> Tuple[str, float]:
    """
    Simulated RG-CLD (Retrieval-Guided Constrained Decoding) translation.
    Returns (translated_text, confidence_score)
    """
    words = text.split()
    # naive paraphrase: swap adjacent words, attempt to 'recover' entities by capitalization
    swapped = []
    for i in range(0, len(words), 2):
        if i + 1 < len(words):
            swapped.extend([words[i+1], words[i]])
        else:
            swapped.append(words[i])
    translated = " ".join(swapped)
    # Add notice about retrieval guidance
    translated = translated + " [retrieved-terms-checked]"
    base = compute_confidence_base(text)
    confidence = min(0.995, base + (0.06 if speed == 2 else (0.03 if speed == 1 else 0.01)))
    return f"[RG-CLD] {translated}", round(confidence, 3)

def translate_dummy_efc(text: str, src: str, tgt: str, speed: int) -> Tuple[str, float]:
    """
    Simulated EFC (Entity-Factuality Composite evaluation aware) translation.
    Returns (translated_text, confidence_score)
    """
    # naive 'synonymize' simulation by alternating token case and adding factual tag
    tokens = [t.lower() if i % 2 == 0 else t.upper() for i, t in enumerate(text.split())]
    translated = " ".join(tokens) + " [factuality-checked]"
    base = compute_confidence_base(text)
    # EFC focuses on factuality: mid-high confidence in accurate mode.
    confidence = min(0.995, base + (0.12 if speed == 2 else 0.04))
    return f"[EFC] {translated}", round(confidence, 3)

# Single wrapper to pick model
MODEL_MAP = {
    "EACT": translate_dummy_eact,
    "RG-CLD": translate_dummy_rgcld,
    "EFC": translate_dummy_efc,
}

# -----------------------------
# Sidebar Controls (per spec)
# -----------------------------
with st.sidebar:
    st.markdown("<div style='display:flex;align-items:center;gap:10px'><h2 style='margin:0'>NeuraLingua</h2></div>", unsafe_allow_html=True)
    st.markdown("**AI Translation Studio**")
    st.markdown("---")

    # Source language: include Auto-detect option
    src_lang = st.selectbox("Source language", ["Auto-detect", "English", "Hindi", "French", "Spanish", "German"], index=0)

    target_options = ["English", "Hindi", "French", "Spanish", "German"]
    tgt_lang = st.selectbox("Target language", target_options, index=0)

    model_choice = st.radio("Select model", ["EACT", "RG-CLD", "EFC"], index=0, help="Choose which model pipeline to run")

    speed_label = st.select_slider("Translation Speed (0=balanced,1=fast,2=accurate)", options=[0,1,2], value=0)
    # Show confidence
    show_conf = st.checkbox("Show Confidence Score", value=True)

    st.markdown("---")
    st.markdown("**Interface options**")
    auto_play = st.checkbox("Auto-simulate progress animation", value=True)
    allow_download = st.checkbox("Enable download button", value=True)
    st.markdown("---")
    st.info("This UI uses dummy inference by default. Replace the functions inside app.py (translate_dummy_*) with actual model calls to EACT / RG-CLD / EFC backends.")

# -----------------------------
# Main content area
# -----------------------------
# Header area
st.markdown(
    """
    <div class="neural-header">
      <div>
        <div class="neural-title">NeuraLingua — AI Translation Studio</div>
        <div class="neural-sub">Real-time Neural Machine Translation interface — EACT · RG-CLD · EFC</div>
      </div>
      <div style="text-align:right; font-size:13px; color:#1f3a57;">
        <strong>Model:</strong> {model} &nbsp; • &nbsp; <strong>Speed:</strong> {spd}
      </div>
    </div>
    """.format(model=model_choice, spd={0:"Balanced",1:"Fast",2:"Accurate"}[speed_label]),
    unsafe_allow_html=True,
)

# Layout: main column with input and right column with quick info
col_main, col_side = st.columns([3, 1], gap="large")

with col_main:
    st.markdown("### Enter text to translate")
    placeholder = "Type or paste text here. E.g., 'Dr. Anil Gupta visited AIIMS on January 15 to discuss cardiac surgery.'"
    user_text = st.text_area("Source text", value="", placeholder=placeholder, height=180, key="input_text")

    # Translate button (triggers inference)
    do_translate = st.button("🚀 Translate", use_container_width=True)

    # Keep session state for last translation outputs
    if "history" not in st.session_state:
        st.session_state["history"] = []  # list of dicts

    # Output area (glass card)
    out_slot = st.container()

    if do_translate:
        if not user_text.strip():
            st.warning("Please type or paste some text to translate.")
        else:
            # Simulate progress if requested
            if auto_play:
                with st.spinner("Preparing translation..."):
                    time.sleep(0.2)
                simulate_progress(speed_label, description="Translating")

            # Run the chosen dummy model
            translate_fn = MODEL_MAP.get(model_choice)
            # The real integration should call your model's inference function here, for example:
            # translated_text, confidence = eact_infer(user_text, src_lang_code, tgt_lang_code, speed_label)
            translated_text, confidence = translate_fn(user_text, src_lang, tgt_lang, speed_label)

            # Save to session history
            st.session_state["history"].append({
                "model": model_choice,
                "source": user_text,
                "translation": translated_text,
                "confidence": confidence,
                "src_lang": src_lang,
                "tgt_lang": tgt_lang,
                "speed": speed_label,
                "timestamp": time.time()
            })

            # Render output with glass effect
            with out_slot:
                st.markdown('<div class="glass">', unsafe_allow_html=True)
                st.markdown("**Translated output**", unsafe_allow_html=True)
                st.markdown(f'<div class="translation-text">{translated_text}</div>', unsafe_allow_html=True)

                # Confidence UI
                if show_conf:
                    conf_pct = int(confidence * 100)
                    st.markdown(f"<div class='conf-wrap'><small>Confidence: {conf_pct}%</small></div>", unsafe_allow_html=True)
                    # visual bar - use st.progress but style it with emoji for more control
                    progress_str = "█" * int(conf_pct / 6) + "░" * int((100 - conf_pct) / 6)
                    st.markdown(f"<div style='font-family:monospace; font-size:12px; padding-top:6px'>{progress_str}  {conf_pct}%</div>", unsafe_allow_html=True)

                # Download
                if allow_download:
                    b = translated_text.encode("utf-8")
                    st.download_button("⬇️ Download translation (.txt)", data=b, file_name="translation.txt", mime="text/plain")
                st.markdown("</div>", unsafe_allow_html=True)

            # Toast / success
            st.success("Translation complete", icon="✅")

with col_side:
    st.markdown("### Quick tips")
    st.markdown("- Use **Auto-detect** when you're unsure of the source language (demo only).")
    st.markdown("- **Speed** trades off latency vs. 'accuracy' in this demo; set to *Accurate* for more careful output.")
    st.markdown("- **Enable confidence** to visualize model trust in the translation.")
    st.markdown("---")
    st.markdown("### Latest runs")
    # Show last 3 runs
    runs = st.session_state.get("history", [])[-3:][::-1]
    if runs:
        for r in runs:
            st.markdown(f"**{r['model']}** → {r['tgt_lang']} • {int(r['confidence']*100)}%")
            st.caption((r['source'][:60] + '...') if len(r['source']) > 60 else r['source'])
    else:
        st.info("No translations yet — try the Translate button!")

# -----------------------------
# Secondary Tab: Compare Models
# -----------------------------
st.markdown("---")
tab1, tab2 = st.tabs(["Single Translate", "Compare Models"])

with tab1:
    st.info("Single-model translation is above. Use the Compare tab to see side-by-side outputs from all 3 demo models.")

with tab2:
    st.markdown("## Compare model outputs side-by-side")
    compare_text = st.text_area("Enter text to compare outputs (same input run for all models):", value="", height=140, key="compare_input")

    if st.button("Compare now"):
        if not compare_text.strip():
            st.warning("Please enter text to compare.")
        else:
            # optionally simulate a short progress
            simulate_progress(speed_label, description="Running comparisons")
            results = {}
            confidences = {}
            for mname, fn in MODEL_MAP.items():
                out, conf = fn(compare_text, src_lang, tgt_lang, speed_label)
                results[mname] = out
                confidences[mname] = conf

            # Layout three columns for outputs
            c1, c2, c3 = st.columns(3)
            for col, mname in zip((c1, c2, c3), MODEL_MAP.keys()):
                with col:
                    st.markdown(f"### {mname}")
                    st.markdown('<div class="glass">', unsafe_allow_html=True)
                    st.markdown(f'<div class="translation-text">{results[mname]}</div>', unsafe_allow_html=True)
                    if show_conf:
                        cpct = int(confidences[mname] * 100)
                        st.caption(f"Confidence: {cpct}%")
                    st.markdown("</div>", unsafe_allow_html=True)

            # Bar chart for confidences (simple ASCII-like chart)
            st.markdown("### Confidence comparison")
            max_conf = max(confidences.values())
            for m, v in confidences.items():
                bar = "█" * int(v / max_conf * 30)
                st.markdown(f"**{m}** | {bar} {int(v*100)}%")

# -----------------------------
# Footer credits and model info
# -----------------------------
st.markdown("---")
st.markdown(
    """
    <div class="footer">
      NeuraLingua — AI Translation Studio • Demo UI for EACT · RG-CLD · EFC integration<br/>
      Built with Streamlit • Replace dummy functions with your real model inference endpoints for production.
    </div>
    """,
    unsafe_allow_html=True,
)
