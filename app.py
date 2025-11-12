import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import difflib
import requests

# Optional imports (safe fallbacks)
try:
    from transformers import pipeline
    TRANS_AVAILABLE = True
except Exception:
    TRANS_AVAILABLE = False

try:
    import spacy
    NLP = spacy.load("en_core_web_sm")
    SPACY_AVAILABLE = True
except Exception:
    NLP = None
    SPACY_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    SBERT = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    SBERT_AVAILABLE = True
except Exception:
    SBERT = None
    SBERT_AVAILABLE = False


# ---------------------------- Helper Functions ----------------------------
def load_default_glossary():
    """Loads glossary from GitHub raw file as default"""
    try:
        url = "https://raw.githubusercontent.com/caffe-cappuccino/dl/refs/heads/main/glossary.csv"
        df = pd.read_csv(url)
        return df
    except Exception:
        return pd.DataFrame(columns=["term", "term_lang", "canonical_form"])

def load_uploaded_glossary(file):
    """Loads glossary from uploaded CSV"""
    if file is not None:
        return pd.read_csv(file)
    return load_default_glossary()

def run_baseline_translation(text, src, tgt):
    """Run translation using HuggingFace or fallback"""
    if TRANS_AVAILABLE:
        model_name = f"Helsinki-NLP/opus-mt-{src}-{tgt}"
        try:
            pipe = pipeline("translation", model=model_name, src_lang=src, tgt_lang=tgt)
            out = pipe(text, max_length=512)
            return out[0]["translation_text"]
        except Exception:
            pass
    # Fallback mock translation
    return " ".join(reversed(text.split())) + " (mock translation)"

def extract_entities(text):
    """Extract entities using spaCy or fallback heuristic"""
    if not SPACY_AVAILABLE:
        return [w.strip(".,!?") for w in text.split() if w.istitle()]
    return [ent.text for ent in NLP(text).ents]

def retrieve_candidates(term, glossary_df, topk=3):
    """Simple fuzzy retrieval for glossary matches"""
    if glossary_df.empty: return []
    scores = []
    for _, r in glossary_df.iterrows():
        sim = difflib.SequenceMatcher(None, term.lower(), str(r["term"]).lower()).ratio()
        scores.append((r["canonical_form"], sim))
    scores = sorted(scores, key=lambda x:x[1], reverse=True)
    return scores[:topk]

def enforce_entity_preservation(source, target, glossary_df):
    """Simulate RG-CLD style correction"""
    src_ents = extract_entities(source)
    corrected = target
    report = {"src_entities": src_ents, "fixes":[]}
    for e in src_ents:
        if e not in corrected:
            cands = retrieve_candidates(e, glossary_df)
            if cands:
                best, sc = cands[0]
                if sc > 0.6:
                    corrected += f" [{best}]"
                    report["fixes"].append({"entity":e,"applied":best,"score":sc})
    return corrected, report

def efc_metric(source, baseline, corrected):
    """Compute simplified EFC metric"""
    src_ents = extract_entities(source)
    bef = sum(1 for e in src_ents if e in baseline)/max(1,len(src_ents))
    aft = sum(1 for e in src_ents if e in corrected)/max(1,len(src_ents))
    return {"entity_preservation_before":bef,"entity_preservation_after":aft,
            "efc_composite":round(0.7*aft+0.3*(aft-bef),3)}


# ---------------------------- Streamlit UI ----------------------------
st.set_page_config(page_title="EACT + RG-CLD Demo", layout="wide")
st.title("🌐 EACT + RG-CLD + EFC — Interactive Demo")
st.markdown("**Entity-Aware and Retrieval-Guided Translation Prototype**")

with st.sidebar:
    st.header("⚙️ Configuration")
    src = st.selectbox("Source language",["en","hi","fr"],index=0)
    tgt = st.selectbox("Target language",["hi","en","fr"],index=1)
    glossary_file = st.file_uploader("Upload your own glossary CSV",type=["csv"])
    glossary_df = load_uploaded_glossary(glossary_file)
    st.success(f"Loaded {len(glossary_df)} glossary terms")

st.markdown("### ✍️ Input Text")
text = st.text_area("Enter text to translate:",
    "Dr. Anil Gupta visited AIIMS on January 15 to discuss cardiac surgery.")

if st.button("🚀 Run Translation"):
    with st.spinner("Translating using baseline model..."):
        base = run_baseline_translation(text, src, tgt)
        st.subheader("🔹 Baseline Translation")
        st.code(base)

    with st.spinner("Applying EACT + RG-CLD corrections..."):
        corr, rep = enforce_entity_preservation(text, base, glossary_df)
        st.subheader("🔹 Corrected Translation (Entity-Aware)")
        st.code(corr)

        st.markdown("### 🧠 Correction Report")
        st.json(rep)

        m = efc_metric(text, base, corr)
        st.markdown("### 📊 EFC Metrics")
        st.write(m)
        fig, ax = plt.subplots()
        ax.bar(["Before","After"],[m["entity_preservation_before"],m["entity_preservation_after"]],
               color=["#ff6f61","#6fa8dc"])
        ax.set_ylim(0,1)
        ax.set_ylabel("Entity Preservation")
        ax.set_title("EFC Components")
        st.pyplot(fig)

st.caption("This demo auto-loads a default glossary from GitHub. Upload your own to test custom retrieval.")
