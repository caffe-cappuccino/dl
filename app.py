# app.py
"""
Polyglot — AI Language Translator (Black + Orange Neon Edition)
---------------------------------------------------------------
🖤 Entire page black
🟠 Everything else orange glow
💫 Particle cursor trail
🎧 Text-to-Speech + Download
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
st.set_page_config(page_title="Polyglot — AI Translator", page_icon="🌐", layout="wide")

# -----------------------------------------------------------
# SIDEBAR
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
# STYLES — FULL BLACK + ORANGE EVERYTHING
# -----------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

html, body, [class*="css"] {
    background-color: #000000 !important;
    color: #FFA500 !important;
    font-family: 'Inter', sans-serif;
}

section[data-testid="stAppViewContainer"],
section[data-testid="stVerticalBlock"],
div.block-container,
[data-testid="stSidebar"],
.main {
    background-color: #000000 !important;
    color: #FFA500 !important;
}

.stButton>button {
    border: 2px solid #FFA500;
    border-radius: 10px;
    background: transparent;
    color: #FFA500 !important;
    font-weight: 600;
    padding: 0.6em 1em;
    transition: all 0.3s ease;
    box-shadow: 0 0 20px #ff8800;
}
.stButton>button:hover {
    background: #FFA500;
    color: #000 !important;
    box-shadow: 0 0 30px #ff9900;
    transform: scale(1.05);
}

.glass {
    background: rgba(255, 165, 0, 0.05);
    border: 1px solid rgba(255, 165, 0, 0.3);
    border-radius: 16px;
    padding: 22px;
    backdrop-filter: blur(10px);
    transition: all 0.3s ease;
    box-shadow: 0 0 25px rgba(255, 165, 0, 0.2);
}
.glass:hover {
    transform: translateY(-4px);
    box-shadow: 0 0 40px rgba(255, 165, 0, 0.4);
}

.title {
    font-size: 34px;
    font-weight: 800;
    text-align: center;
    color: #FFA500;
    text-shadow: 0 0 25px #ff8800;
}
.subtitle {
    text-align:center;
    font-size:14px;
    opacity:0.9;
    color:#FFA500;
}
.result {
    font-size:17px;
    color:#FFA500;
    line-height:1.6;
    white-space: pre-wrap;
}
.footer {
    text-align:center;
    font-size:13px;
    opacity:0.9;
    margin-top:25px;
    color:#FFA500;
}
.flag {
    width: 32px;
    height: 22px;
    border-radius: 3px;
    margin-right: 6px;
    display:inline-block;
    animation: wave 2s ease-in-out infinite;
}
@keyframes wave {
  0% { transform: rotate(0deg); }
  25% { transform: rotate(4deg); }
  50% { transform: rotate(-4deg); }
  75% { transform: rotate(4deg); }
  100% { transform: rotate(0deg); }
}
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------
# CURSOR TRAIL (Orange)
# -----------------------------------------------------------
trail_html = """
<script>
const c=document.createElement('canvas');
c.width=window.innerWidth;c.height=window.innerHeight;
c.style.position='fixed';c.style.top='0';c.style.left='0';
c.style.zIndex='1';c.style.pointerEvents='none';
document.body.appendChild(c);
const ctx=c.getContext('2d');let p=[];
function rand(a,b){return Math.random()*(b-a)+a;}
function spawn(x,y){for(let i=0;i<3;i++)p.push({x,y,vx:rand(-1,1),vy:rand(-1,1),life:rand(40,80),r:rand(1,3)});}
function draw(){ctx.clearRect(0,0,c.width,c.height);
p.forEach((d,i)=>{d.x+=d.vx;d.y+=d.vy;d.life--;
ctx.beginPath();ctx.arc(d.x,d.y,d.r,0,2*Math.PI);
ctx.fillStyle='rgba(255,165,0,0.9)';ctx.globalAlpha=Math.max(0,d.life/80);
ctx.fill();if(d.life<=0)p.splice(i,1);});
requestAnimationFrame(draw);}
draw();
window.addEventListener('mousemove',e=>spawn(e.clientX,e.clientY));
</script>
"""
components.html(trail_html, height=1, scrolling=False)

# -----------------------------------------------------------
# HEADER
# -----------------------------------------------------------
st.markdown("""
<div class="glass" style="text-align:center;margin-bottom:25px;">
  <div class="title">🌐 Polyglot — AI Language Translator</div>
  <div class="subtitle">🖤 Fully Black Interface | 🟠 Orange Neon Accents</div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------
# FLAG ICONS
# -----------------------------------------------------------
def flag_img(code):
    return f"<img src='https://flagcdn.com/w40/{code}.png' class='flag'>"

# -----------------------------------------------------------
# TRANSLATOR
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
# MAIN LAYOUT
# -----------------------------------------------------------
text = st.text_area("Enter text to translate:", height=180, placeholder="Type here...")

if st.button("🚀 Translate"):
    if not text.strip():
        st.warning("Please enter some text.")
    else:
        src_code = languages.get(src_lang, "en")
        tgt_code = languages.get(tgt_lang, "en")

        with st.spinner("Translating..."):
            translator = load_translator(src_code, tgt_code)
            if translator is None:
                result = text
            else:
                result = translator(text, max_length=512)[0]["translation_text"]

        conf_score = round(max(0.7, 1.0 - temperature * 0.4), 3)
        st.markdown(f"<div class='glass'><div class='result'>{result}</div></div>", unsafe_allow_html=True)

        if show_conf:
            st.progress(conf_score)
            st.caption(f"Confidence: {conf_score*100:.1f}%")

        st.download_button("⬇️ Download Translation", data=result, file_name="translation.txt")

        if enable_tts:
            tts = gTTS(text=result, lang=tgt_code if tgt_code in ["en","hi","fr","es","de","it"] else "en")
            bio = io.BytesIO()
            tts.write_to_fp(bio)
            bio.seek(0)
            st.audio(bio.read(), format="audio/mp3")

# -----------------------------------------------------------
# FOOTER
# -----------------------------------------------------------
st.markdown("""
<hr>
<div class="footer">
  <strong>Polyglot v12</strong> — All Orange Everything 🔥 | Made with ❤️ using Streamlit
</div>
""", unsafe_allow_html=True)
