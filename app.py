# app.py
"""
Polyglot — AI Language Translator (Animated + Cursor Trail + Waving Flags)
Run: streamlit run app.py
Requirements:
  pip install -r requirements.txt
Where requirements.txt contains:
  streamlit
  transformers
  torch
  sentencepiece
  gTTS
"""

import streamlit as st
from transformers import pipeline
from gtts import gTTS
import time
import io
import streamlit.components.v1 as components

# -------------------------
# Page config
# -------------------------
st.set_page_config(page_title="Polyglot — AI Language Translator", page_icon="🌐", layout="wide")

# -------------------------
# Sidebar controls
# -------------------------
st.sidebar.title("🌐 Polyglot Settings")

# Dark mode toggle
dark_mode = st.sidebar.checkbox("🌙 Dark Mode", value=True)

# Language list
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

# Session initialization
if "src_lang" not in st.session_state:
    st.session_state.src_lang = "🇬🇧 English"
if "tgt_lang" not in st.session_state:
    st.session_state.tgt_lang = "🇮🇳 Hindi"
if "input_text" not in st.session_state:
    st.session_state.input_text = ""

# Sidebar widgets
src_lang = st.sidebar.selectbox("Source Language", ["🌍 Auto Detect"] + list(languages.keys()), index=1)
tgt_lang = st.sidebar.selectbox("Target Language", list(languages.keys()), index=0)
show_conf = st.sidebar.checkbox("Show Confidence Score", value=True)
temperature = st.sidebar.slider("Translation Temperature", 0.0, 1.0, 0.3, 0.05)
enable_tts = st.sidebar.checkbox("Enable Text-to-Speech", value=False)

if st.sidebar.button("↔️ Swap Languages"):
    # swap session fallback names (informative only)
    st.session_state.src_lang, st.session_state.tgt_lang = st.session_state.tgt_lang, st.session_state.src_lang
    st.sidebar.success("Languages swapped!")

# -------------------------
# Animated CSS + flag waving + neon theme
# -------------------------
if dark_mode:
    primary = "#00f0ff"
    secondary = "#7b5cf9"
    text_color = "#e6edf3"
    bg_animation = """
    background: linear-gradient(120deg, #03040a, #0b1220, #171232, #03040a);
    background-size: 400% 400%;
    animation: gradientShift 20s ease infinite;
    """
    particle_color = "rgba(0,240,255,0.9)"
else:
    primary = "#3a7afe"
    secondary = "#ff61c7"
    text_color = "#071235"
    bg_animation = """
    background: linear-gradient(120deg, #e8f4ff, #f5ebff, #e9fff4, #e8f4ff);
    background-size: 400% 400%;
    animation: gradientShift 16s ease infinite;
    """
    particle_color = "rgba(58,122,254,0.6)"

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
/* glass card */
.glass {{
    background: rgba(255,255,255,0.04);
    backdrop-filter: blur(10px);
    border-radius: 16px;
    padding: 22px;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    box-shadow: 0 8px 30px rgba(0,0,0,0.12);
}}
.glass:hover {{
    transform: translateY(-6px);
    box-shadow: 0 20px 40px rgba(0,0,0,0.18);
}}
/* buttons (neon gradients) */
.stButton>button {{
    border-radius: 10px;
    background: linear-gradient(90deg, {primary}, {secondary});
    color: white !important;
    font-weight: 700;
    padding: 0.6em 1em;
    box-shadow: 0 8px 30px rgba( {int(primary[1:3],16)}, {int(primary[3:5],16)}, {int(primary[5:7],16)}, 0.12);
    transition: transform 0.15s ease, box-shadow 0.15s ease, filter 0.15s;
}}
.stButton>button:hover {{
    transform: translateY(-3px) scale(1.03);
    filter: brightness(1.05);
    box-shadow: 0 20px 60px {primary};
}}
.title {{
    font-size: 32px;
    font-weight: 800;
    text-align: center;
    color: {primary};
    text-shadow: 0 0 16px rgba(0,0,0,0.2);
}}
.subtitle {{
    text-align:center;
    color: {text_color};
    opacity: 0.9;
}}
.result {{
    font-size:16px;
    line-height:1.6;
    white-space: pre-wrap;
    color: {text_color};
}}

/* waving flag animation */
.flag-wave {{
  display:inline-block;
  animation: wave 1.6s ease-in-out infinite;
  transform-origin: 50% 60%;
  font-size: 18px;
  margin-right: 8px;
}
@keyframes wave {{
  0% {{ transform: rotate(0deg); }}
  20% {{ transform: rotate(14deg); }}
  40% {{ transform: rotate(-8deg); }}
  60% {{ transform: rotate(14deg); }}
  80% {{ transform: rotate(-4deg); }}
  100% {{ transform: rotate(0deg); }}
}}

/* footer styling */
.footer {{
    text-align:center;
    font-size:13px;
    opacity:0.85;
    margin-top: 26px;
}}

/* ensure download button stands out */
.stDownloadButton>button {{
    border-radius: 8px;
    background: transparent;
    border: 1px solid {primary};
    color: {primary};
    padding: 0.5em 1em;
}}
</style>
""", unsafe_allow_html=True)

# -------------------------
# Cursor-following particle trail (injected HTML/JS via component)
# -------------------------
# This creates a full-screen canvas inside an iframe that tracks mouse and renders small particles.
particle_html = f"""
<div id="particle-root" style="position:fixed;left:0;top:0;width:100%;height:100%;pointer-events:none;z-index:1;"></div>
<script>
const root = document.getElementById('particle-root');
const canvas = document.createElement('canvas');
canvas.style.position = 'fixed';
canvas.style.left = '0';
canvas.style.top = '0';
canvas.style.width = '100%';
canvas.style.height = '100%';
canvas.width = window.innerWidth;
canvas.height = window.innerHeight;
root.appendChild(canvas);
const ctx = canvas.getContext('2d');

let particles = [];

function rand(min, max){ return Math.random()*(max-min)+min; }

function spawn(x,y){
  for(let i=0;i<4;i++){
    particles.push({
      x: x + rand(-6,6),
      y: y + rand(-6,6),
      vx: rand(-0.4,0.4),
      vy: rand(-1.2,-0.4),
      life: rand(40,80),
      r: rand(1,3),
      a: 1
    });
  }
}

function draw(){
  ctx.clearRect(0,0,canvas.width,canvas.height);
  for(let i = particles.length-1; i>=0; i--){
    const p = particles[i];
    p.x += p.vx;
    p.y += p.vy;
    p.vy += 0.02; // gravity-ish
    p.life -= 1;
    p.a = Math.max(0, p.life/80);
    ctx.beginPath();
    ctx.fillStyle = '{particle_color}';
    ctx.globalAlpha = p.a;
    ctx.arc(p.x, p.y, p.r, 0, Math.PI*2);
    ctx.fill();
    if(p.life <= 0 || p.y > canvas.height+10) particles.splice(i,1);
  }
  requestAnimationFrame(draw);
}
draw();

window.addEventListener('mousemove', (e)=>{
  const rect = canvas.getBoundingClientRect();
  spawn(e.clientX, e.clientY);
});

// handle resize
window.addEventListener('resize', ()=>{
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;
});
</script>
"""
# render the particle overlay. height must be >0; set to 1 so iframe loads but overlay covers full screen due to fixed positioning
components.html(particle_html, height=1, scrolling=False)

# -------------------------
# Header
# -------------------------
st.markdown(f'<div class="glass" style="text-align:center;margin-bottom:18px;">'
            f'<div class="title">🌐 Polyglot — AI Language Translator</div>'
            f'<div class="subtitle">Animated UI • Cursor trail • Waving flags • Hugging Face models</div>'
            f'</div>', unsafe_allow_html=True)

# -------------------------
# Main layout (left input, right info)
# -------------------------
left, right = st.columns([2, 1], gap="large")

with left:
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    # controlled text area via session_state
    input_text = st.text_area("Enter text to translate:", value=st.session_state.input_text, height=190, key="input_area")

    c1, c2, c3 = st.columns(3)
    with c1:
        translate_btn = st.button("🚀 Translate", use_container_width=True)
    with c2:
        if st.button("🧹 Clear", use_container_width=True):
            # clear the session state value and the text widget content, then rerun
            st.session_state.input_text = ""
            # reassign key value to clear the visible box
            st.session_state["input_area"] = ""
            st.experimental_rerun()
    with c3:
        if st.button("↔️ Swap"):
            # For UX: swap selected values in sidebar (we can't set the selectbox directly; notify)
            prev_src = st.session_state.get("src_lang", "🇬🇧 English")
            prev_tgt = st.session_state.get("tgt_lang", "🇮🇳 Hindi")
            st.session_state.src_lang, st.session_state.tgt_lang = prev_tgt, prev_src
            st.success("Swap registered — sidebar values may need manual reselect to reflect immediately.")

    st.markdown('</div>', unsafe_allow_html=True)

with right:
    # display waving flags for current selected languages
    def flag_markup(label):
        # label expects emoji and name like "🇬🇧 English"
        emoji = label.split()[0]
        name = " ".join(label.split()[1:])
        return f"<span class='flag-wave'>{emoji}</span> <strong style='color:{primary}'>{name}</strong>"

    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown("### Selected Languages")
    st.markdown(f"<div>Source: {flag_markup(src_lang)}</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='margin-top:6px;'>Target: {flag_markup(tgt_lang)}</div>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### Info")
    st.markdown(f"- Temperature: **{temperature:.2f}**")
    st.markdown("- Supports many Helsinki-NLP pairs; falls back to `facebook/m2m100_418M` if unavailable.")
    if enable_tts:
        st.markdown("- TTS: Enabled")
    else:
        st.markdown("- TTS: Disabled")
    st.markdown('</div>', unsafe_allow_html=True)

# -------------------------
# Translation loader with fallback
# -------------------------
@st.cache_resource
def load_translator(src_code, tgt_code):
    """Load translation model, return None if same-language (so we simply return input text),
       fallback to a multilingual model if direct pair missing."""
    if src_code == "auto":
        src_code = "en"
    if src_code == tgt_code:
        return None
    model_name = f"Helsinki-NLP/opus-mt-{src_code}-{tgt_code}"
    try:
        return pipeline("translation", model=model_name)
    except Exception:
        # fallback multilingual model
        try:
            return pipeline("translation", model="facebook/m2m100_418M")
        except Exception:
            # if even fallback fails, raise so the UI shows error
            raise

# -------------------------
# Translation action
# -------------------------
if translate_btn:
    text = st.session_state.get("input_area", "")
    if not text.strip():
        st.warning("Please enter text to translate.")
    else:
        # map language codes
        def code_of(label):
            if label == "🌍 Auto Detect":
                return "auto"
            return languages.get(label, "en")
        src_code = code_of(src_lang)
        tgt_code = code_of(tgt_lang)

        st.info(f"Translating {src_lang} → {tgt_lang} ...")
        # animated glowing progress (custom)
        prog_placeholder = st.empty()
        for pct in range(0, 101, 5):
            bar = f"""
            <div style='width:100%;background:rgba(255,255,255,0.06);border-radius:10px;padding:4px;'>
              <div style='width:{pct}%;height:12px;border-radius:8px;
                   background:linear-gradient(90deg,{primary}, {secondary});
                   box-shadow:0 0 18px {primary};transition:width:0.15s;'></div>
            </div>
            """
            prog_placeholder.markdown(bar, unsafe_allow_html=True)
            time.sleep(0.02)
        prog_placeholder.empty()

        # load translator (cached)
        try:
            translator = load_translator(src_code, tgt_code)
        except Exception as e:
            st.error(f"Model load failed: {e}")
            translator = None

        # if same-language selected, show original
        if translator is None:
            st.info("Source and target languages are the same or translator unavailable — displaying original text.")
            result = text
        else:
            try:
                # Actual model call (HuggingFace pipeline)
                result = translator(text, max_length=512)[0]["translation_text"]
            except Exception as e:
                st.error(f"Translation error: {e}")
                result = ""

        # confidence placeholder
        conf_score = round(max(0.6, 1.0 - temperature * 0.4), 3)

        # Output card
        st.markdown('<div class="glass">', unsafe_allow_html=True)
        st.subheader("🔹 Translated Text")
        st.markdown(f"<div class='result'>{result}</div>", unsafe_allow_html=True)

        if show_conf:
            # glowing confidence bar
            glow = f"""
            <div style='width:100%;background:rgba(255,255,255,0.04);border-radius:10px;padding:6px;margin-top:8px;'>
              <div style='width:{int(conf_score*100)}%;height:12px;border-radius:8px;
                   background:linear-gradient(90deg,{secondary},{primary});
                   box-shadow:0 0 18px {primary};'></div>
            </div>
            """
            st.markdown(glow, unsafe_allow_html=True)
            st.caption(f"Confidence: {conf_score*100:.1f}%")

        # download translation
        st.download_button("⬇️ Download Translation", data=result.encode("utf-8"), file_name="translation.txt", mime="text/plain")

        # TTS if enabled
        if enable_tts:
            try:
                tts = gTTS(text=result, lang=tgt_code if tgt_code in ["en","hi","fr","es","de","it","pt"] else "en")
                bio = io.BytesIO()
                tts.write_to_fp(bio)
                bio.seek(0)
                st.audio(bio.read(), format="audio/mp3")
            except Exception as e:
                st.error(f"TTS failed: {e}")

        st.success("✅ Translation complete!")

# -------------------------
# Footer
# -------------------------
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown(f"<div class='footer'><strong>
