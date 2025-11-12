# ---- Dark / Light Mode Toggle ----
dark_mode = st.sidebar.toggle("🌙 Dark Mode", value=False)

# Define color palettes
if dark_mode:
    # Full black background + neon accent
    COLORS = {
        "bg": "#0d1117",
        "card": "#161b22",
        "text": "#e6edf3",
        "accent": "#00d8ff"   # cyan accent
    }
else:
    # Muted navy-blue theme (no pure white)
    COLORS = {
        "bg": "#e9eef6",
        "card": "#f5f7fb",
        "text": "#0b1a33",
        "accent": "#3a7afe"   # royal-blue accent
    }

# Inject CSS to recolor the entire page
st.markdown(f"""
<style>
html, body, [class*="css"]  {{
    background-color: {COLORS['bg']} !important;
    color: {COLORS['text']} !important;
    font-family: 'Inter', sans-serif;
}}
section[data-testid="stSidebar"] {{
    background-color: {COLORS['card']} !important;
}}
div.block-container {{
    background-color: {COLORS['bg']} !important;
}}
/* Glass cards and buttons now inherit the global palette */
.glass {{
    background: {COLORS['card']};
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 4px 18px rgba(0,0,0,0.2);
}}
.stButton>button {{
    border: none;
    border-radius: 8px;
    background: linear-gradient(90deg, {COLORS['accent']}, #6c63ff);
    color: white;
    font-weight: 600;
    transition: all 0.2s ease;
}}
.stButton>button:hover {{
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
}}
a, .stDownloadButton>button {{
    color: {COLORS['accent']} !important;
}}
</style>
""", unsafe_allow_html=True)
