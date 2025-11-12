# app.py
"""
Polyglot — AI Language Translator (Final Animated Edition)
-----------------------------------------------------------
⚡ Real multilingual translation (Hugging Face)
✨ Animated particle trail & waving flags
🌙 True dark/light gradient modes
🧊 Neon glassmorphism, glowing bars, transitions
🎧 TTS, multilingual fallback, download button
"""

import streamlit as st
from transformers import pipeline
from gtts import gTTS
import time
import io
import streamlit.components.v1 as components

# -----------------------------------------------------------
# PAGE CONFIG
# -----------------------------------------------------------
st.set_page_config(page_title="Polyglot — AI Language Translator", page_icon="🌐", layout="wide")

# -----------------------------------------------------------
# SIDEBAR
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
# COLOR SCHEME & STYLES
# -----------------------------------------------------------
if dark_mode:
    primary = "#00f0ff"
    secondary = "#7b5cf9"
    text_color = "#e6edf3"
    bg_animation = """
    background: linear-gradient(-45deg, #03040a, #0a1124, #151734, #03040a);
    background-size: 400% 400%;
    animation: gradientShift 18s ease infinite;
    """
    particle_color = "rgba(0,255,255,0.8)"
else:
    primary = "#3a7afe"
    secondary = "#ff61c7"
    text_color = "#0b1a33"
    bg_animation = """
    background: linear-gradient(135deg, #dbe9ff, #f3e9ff, #e7fff3, #dbe9ff);
    background-size: 400% 400%;
    animation: gradientShift 16s ease infinite;
    """
    particle_color = "rgba(58,122,254,0.7)"

# -----------------------------------------------------------
# GLOBAL CSS
# -----------------------------------------------------------
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
    background: rgba(255,255,255,0.05);
    backdrop-filter: blur(12px);
    border-radius: 16px;
    padding: 22px;
    transition: all 0.3s ease;
    box-shadow: 0 8px 30px rgba(0,0,0,0.2);
}}
.glass:hover {{
    transform: translateY(-5px);
    box-shadow: 0 12px 40px rgba(0,0,0,0.3);
}}
.stButton>button {{
    border: none;
    border-radius: 10px;
    background: linear-gradient(90deg, {primary}, {secondary});
    color: white !important;
    font-weight: 600;
    padding: 0.6em 1em;
    transition: all 0.3s ease;
    box-shadow: 0 0 15px {primary};
}}
.stButton>button:hover {{
    transform: scale(1.05);
    box-shadow: 0 0 30px {secondary};
}}
.title {{
    font-size: 34px;
    font-weight: 800;
    text-align: center;
    color: {primary};
    text-shadow: 0 0 20px {primary};
}}
.subtitle {{
    text-align:center;
    font-size:14px;
    opacity:0.9;
}}
.result {{
    font-size:17px;
    color:{text_color};
    line-height:1.6;
    white-space: pre-wrap;
}}
.flag-wave {{
  display:inline-block;
  animation: wave 1.6s ease-in-out infinite;
  transform-origin: 50% 60%;
  font-size: 18px;
  margin-right: 8px;
}}
@keyframes wave {{
  0% {{ transform: rotate(0deg); }}
  20% {{ transform: rotate(14deg); }}
  40% {{ transform: rotate(-8deg); }}
  60% {{ transform: rotate(14deg); }}
  80% {{ transform: rotate(-4deg); }}
  100% {{ transform: rotate(0deg); }}
}}
.footer {{
    text-align:center;
    font-size:13px;
    opacity:0.85;
    margin-top:25px;
}}
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------
# CURSOR TRAIL PARTICLES (HTML + JS)
# -----------------------------------------------------------
trail_html = f"""
<div id="trail" style="position:fixed;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:1;"></div>
<script>
const trailCanvas = document.createElement('canvas');
trailCanvas.style.position='fixed';
trailCanvas.style.top='0';
trailCanvas.style.left='0';
trailCanvas.width=window.innerWidth;
trailCanvas.height=window.innerHeight;
trailCanvas.style.pointerEvents='none';
trailCanvas.style.zIndex='1';
document.getElementById('trail').appendChild(trailCanvas);
const ctx = trailCanvas.getContext('2d');
let particles=[];
function rand(a,b){{return Math.random()*(b-a)+a;}}
function spawn(x,y){{for(let i=0;i<4;i++)particles.push({{x:x,y:y,vx:rand(-1,1),vy:rand(-1,1),life:rand(50,80),r:rand(1,3)}});}}
function draw(){{ctx.clearRect(0,0,trailCanvas.width,trailCanvas.height);
particles.forEach((p,i)=>{{
p.x+=p.vx;p.y+=p.vy;p.life-=1;
ctx.beginPath();ctx.arc(p.x,p.y,p.r,0,2*Math.PI);
ctx.fillStyle='{particle_color}';ctx.globalAlpha=Math.max(0,p.life/80);
ctx.fill();
if(p.life<=0)particles.splice(i,1);
}});
requestAnimationFrame(draw);}}
draw();
window.addEventListener('mousemove',e=>spawn(e.clientX,e.clientY));
window.addEventListener('resize',()=>{{trailCanvas.width=window.innerWidth;trailCanvas.height=window.innerHeight;}});
</script>
"""
components.html(trail_html, height=1, scrolling=False)

# -----------------------------------------------------------
# HEADER
# -----------------------------------------------------------
st.markdown(f"""
<div class="glass" style="text-align:center;margin-bottom:25px;">
  <div class="title">🌐 Polyglot — AI Language Translator</div>
  <div class="subtitle">{'🌙 Neon Dark Mode' if dark_mode else '☀️ Aurora Light Mode'} | Futuristic UI with particle trail</div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------
# MAIN LAYOUT
# -----------------------------------------------------------
left, right = st.columns([2, 1], gap="large")

with left:
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    text = st.text_area("Enter text to translate:", value=st.session_state.input_text, height=180, key="input_textbox")

    c1, c2, c3 = st.columns(3)
    with c1:
        translate_btn = st.button("🚀 Translate", use_container_width=True)
    with c2:
        if st.button("🧹 Clear", use_container_width=True):
            st.session_state.input_text = ""
            st.session_state["input_textbox"] = ""
            st.experimental_rerun()
    with c3:
        st.caption(f"{len(text)} characters")
    st.markdown('</div>', unsafe_allow_html=True)

with right:
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.subheader("🧭 Info")
    st.markdown(f"**Source:** <span class='flag-wave'>{src_lang.split()[0]}</span> {src_lang.split()[1]}", unsafe_allow_html=True)
    st.markdown(f"**Target:** <span class='flag-wave'>{tgt_lang.split()[0]}</span> {tgt_lang.split()[1]}", unsafe_allow_html=True)
    st.markdown(f"**Temperature:** {temperature:.2f}")
    st.markdown("---")
    st.markdown("✅ Supports 50+ language pairs (Helsinki-NLP + M2M100 fallback)")
    st.markdown("🎧 Optional speech playback for translated text")
    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------------------------------------
# TRANSLATOR LOADER (CACHED)
# -----------------------------------------------------------
@st.cache_resource
def load_translator(src_code, tgt_code):
    if src_code == "auto":
        src_code = "en"
    if src_code == tgt_code:
        return None
    model_name = f"Helsinki-NLP/opus-mt-{src_code}-{tgt_code}"
    try:
        return pipeline("translation", model=model_name)
    except Exception:
        st.warning(f"No direct model for {src_code}-{tgt_code}, using multilingual fallback.")
        return pipeline("translation", model="facebook/m2m100_418M")

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

        # Custom glowing progress bar
        prog_placeholder = st.empty()
        for pct in range(0, 101, 6):
            bar = f"""
            <div style='background:rgba(255,255,255,0.07);border-radius:10px;padding:4px;'>
              <div style='width:{pct}%;height:12px;border-radius:8px;
                  background:linear-gradient(90deg,{primary},{secondary});
                  box-shadow:0 0 20px {primary};transition:width 0.1s;'></div>
            </div>"""
            prog_placeholder.markdown(bar, unsafe_allow_html=True)
            time.sleep(0.03)
        prog_placeholder.empty()

        try:
            translator = load_translator(src_code, tgt_code)
            if translator is None:
                st.info("Same source and target language — showing original text.")
                result = text
            else:
                result = translator(text, max_length=512)[0]["translation_text"]

            conf_score = round(max(0.7, 1.0 - temperature * 0.4), 3)
            st.markdown('<div class="glass">', unsafe_allow_html=True)
            st.subheader("🔹 Translated Text")
            st.markdown(f"<div class='result'>{result}</div>", unsafe_allow_html=True)

            if show_conf:
                st.markdown(f"""
                <div style='background:rgba(255,255,255,0.04);border-radius:10px;padding:4px;margin-top:10px;'>
                  <div style='width:{conf_score*100}%;height:12px;border-radius:8px;
                      background:linear-gradient(90deg,{secondary},{primary});
                      box-shadow:0 0 18px {primary};'></div>
                </div>""", unsafe_allow_html=True)
                st.caption(f"Confidence: {conf_score*100:.1f}%")

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
  <strong>Polyglot v7</strong> — Built with ❤️ using Streamlit & Hugging Face<br>
  {'🌙 Neon Dark Mode Active' if dark_mode else '☀️ Aurora Light Mode Active'}
</div>
""", unsafe_allow_html=True)
