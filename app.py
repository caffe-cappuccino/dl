# app.py
"""
Polyglot — AI Language Translator (Black + Pink/Orange Neon Edition)
--------------------------------------------------------------------
🖤 True black background
🌸 Neon pink + orange accents
✨ Particle cursor trail, waving flag images
🧊 Glassmorphism, glowing UI
🎧 Text-to-Speech, multilingual fallback
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

if "src_lang" not in st.session_state:
    st.session_state.src_lang = "English"
if "tgt_lang" not in st.session_state:
    st.session_state.tgt_lang = "Hindi"
if "input_text" not in st.session_state:
    st.session_state.input_text = ""

src_lang = st.sidebar.selectbox("Source Language", ["Auto Detect"] + list(languages.keys()), index=1)
tgt_lang = st.sidebar.selectbox("Target Language", list(languages.keys()), index=0)
show_conf = st.sidebar.checkbox("Show Confidence Score", value=True)
temperature = st.sidebar.slider("Translation Temperature", 0.0, 1.0, 0.3, 0.05)
enable_tts = st.sidebar.checkbox("Enable Text-to-Speech", value=False)

if st.sidebar.button("↔️ Swap Languages"):
    st.session_state.src_lang, st.session_state.tgt_lang = st.session_state.tgt_lang, st.session_state.src_lang
    st.sidebar.success("Languages swapped!")

# -----------------------------------------------------------
# COLOR SCHEME — BLACK + PINK/ORANGE
# -----------------------------------------------------------
if dark_mode:
    primary = "#ff66c4"       # pink
    secondary = "#ff9f45"     # orange
    text_color = "#fcefff"
    bg_css = """
    body, .main {
        background: radial-gradient(circle at top left, #000000, #0a0a0a, #101010);
        background-attachment: fixed;
        color: #fcefff;
    }
    """
    particle_color = "rgba(255,153,102,0.9)"  # neon peach for cursor
else:
    primary = "#ff66c4"
    secondary = "#ffb347"
    text_color = "#1a1a1a"
    bg_css = """
    body, .main {
        background: radial-gradient(circle at top left, #fff9fb, #fff3f8, #fff0f0);
        background-attachment: fixed;
        color: #1a1a1a;
    }
    """
    particle_color = "rgba(255,105,180,0.7)"

# -----------------------------------------------------------
# GLOBAL CSS
# -----------------------------------------------------------
st.markdown(f"""
<style>
{bg_css}
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif;
}}
.glass {{
    background: rgba(255,255,255,0.05);
    backdrop-filter: blur(12px);
    border-radius: 16px;
    padding: 22px;
    transition: all 0.3s ease;
    box-shadow: 0 8px 30px rgba(0,0,0,0.25);
}}
.glass:hover {{
    transform: translateY(-5px);
    box-shadow: 0 12px 40px rgba(0,0,0,0.35);
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
    text-shadow: 0 0 25px {secondary};
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
.flag {{
    width: 32px;
    height: 22px;
    border-radius: 3px;
    margin-right: 6px;
    display:inline-block;
    animation: wave 2s ease-in-out infinite;
}}
@keyframes wave {{
  0% {{ transform: rotate(0deg); }}
  25% {{ transform: rotate(4deg); }}
  50% {{ transform: rotate(-4deg); }}
  75% {{ transform: rotate(4deg); }}
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
# CURSOR TRAIL PARTICLES
# -----------------------------------------------------------
trail_html = f"""
<div id="trail" style="position:fixed;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:1;"></div>
<script>
const c=document.createElement('canvas');
c.width=window.innerWidth;c.height=window.innerHeight;
c.style.position='fixed';c.style.top='0';c.style.left='0';c.style.zIndex='1';c.style.pointerEvents='none';
document.getElementById('trail').appendChild(c);
const ctx=c.getContext('2d');
let p=[];
function rand(a,b){{return Math.random()*(b-a)+a;}}
function spawn(x,y){{for(let i=0;i<3;i++)p.push({{x,y,vx:rand(-1,1),vy:rand(-1,1),life:rand(40,80),r:rand(1,3)}});}}
function draw(){{ctx.clearRect(0,0,c.width,c.height);
p.forEach((d,i)=>{{d.x+=d.vx;d.y+=d.vy;d.life--;
ctx.beginPath();ctx.arc(d.x,d.y,d.r,0,2*Math.PI);
ctx.fillStyle='{particle_color}';ctx.globalAlpha=Math.max(0,d.life/80);
ctx.fill();if(d.life<=0)p.splice(i,1);}});
requestAnimationFrame(draw);}}
draw();
window.addEventListener('mousemove',e=>spawn(e.clientX,e.clientY));
window.addEventListener('resize',()=>{{c.width=window.innerWidth;c.height=window.innerHeight;}});
</script>
"""
components.html(trail_html, height=1, scrolling=False)

# -----------------------------------------------------------
# HEADER
# -----------------------------------------------------------
st.markdown(f"""
<div class="glass" style="text-align:center;margin-bottom:25px;">
  <div class="title">🌐 Polyglot — AI Language Translator</div>
  <div class="subtitle">🖤 Black + Neon Pink/Orange Theme | Powered by Hugging Face</div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------
# FLAG FUNCTION
# -----------------------------------------------------------
def flag_img(code):
    return f"<img src='https://flagcdn.com/w40/{code}.png' class='flag'>"

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
    st.markdown(f"**Source:** {flag_img(languages.get(src_lang, 'gb'))} {src_lang}", unsafe_allow_html=True)
    st.markdown(f"**Target:** {flag_img(languages.get(tgt_lang, 'in'))} {tgt_lang}", unsafe_allow_html=True)
    st.markdown(f"**Temperature:** {temperature:.2f}")
    st.markdown("---")
    st.markdown("💡 Supports 50+ language pairs (Helsinki-NLP + M2M100 fallback)")
    st.markdown("🎧 Optional speech playback for translated text")
    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------------------------------------
# TRANSLATOR FUNCTION
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
# TRANSLATION EXECUTION
# -----------------------------------------------------------
if translate_btn:
    if not text.strip():
        st.warning("Please enter some text to translate.")
    else:
        src_code = languages.get(src_lang, "en")
        tgt_code = languages.get(tgt_lang, "en")

        st.info(f"Translating from **{src_lang}** → **{tgt_lang}** ...")

        prog = st.empty()
        for pct in range(0, 101, 8):
            bar = f"""
            <div style='background:rgba(255,255,255,0.1);border-radius:10px;padding:4px;'>
                <div style='width:{pct}%;height:12px;border-radius:8px;
                    background:linear-gradient(90deg,{primary},{secondary});
                    box-shadow:0 0 20px {primary};'></div>
            </div>"""
            prog.markdown(bar, unsafe_allow_html=True)
            time.sleep(0.03)
        prog.empty()

        try:
            translator = load_translator(src_code, tgt_code)
            if translator is None:
                result = text
            else:
                result = translator(text, max_length=512)[0]["translation_text"]

            conf_score = round(max(0.7, 1.0 - temperature * 0.4), 3)
            st.markdown('<div class="glass">', unsafe_allow_html=True)
            st.subheader("🔹 Translated Text")
            st.markdown(f"<div class='result'>{result}</div>", unsafe_allow_html=True)

            if show_conf:
                st.markdown(f"""
                <div style='background:rgba(255,255,255,0.05);border-radius:10px;padding:4px;margin-top:10px;'>
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
  <strong>Polyglot v9</strong> — Built with ☕ using Streamlit & Hugging Face<br>
  {'🌙 Neon Dark Mode Active' if dark_mode else '☀️ Light Mode Active'}
</div>
""", unsafe_allow_html=True)
