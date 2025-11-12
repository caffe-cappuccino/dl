import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import difflib

# Optional imports
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


# ---------------------------- Helper functions ----------------------------
def load_glossary(csv_file):
    if csv_file is None:
        return pd.DataFrame(columns=["term", "term_lang", "canonical_form"])
    return pd.read_csv(csv_file)

def run_baseline_translation(text, src, tgt):
    if TRANS_AVAILABLE:
        model_name = f"Helsinki-NLP/opus-mt-{src}-{tgt}"
        try:
            pipe = pipeline("translation", model=model_name, src_lang=src, tgt_lang=tgt)
            out = pipe(text, max_length=512)
            return out[0]["translation_text"]
        except Exception:
            pass
    # fallback (mock translation)
    return " ".join(reversed(text.split())) + " (mock translation)"

def extract_entities(text):
    if not SPACY_AVAILABLE:
        return [w.strip(".,!?") for w in text.split() if w.istitle()]
    return [ent.text for ent in NLP(text).ents]

def retrieve_candidates(term, glossary_df, topk=3):
    if glossary_df.empty: return []
    scores = []
    for _, r in glossary_df.iterrows():
        sim = difflib.SequenceMatcher(None, term.lower(), str(r["term"]).lower()).ratio()
        scores.append((r["canonical_form"], sim))
    scores = sorted(scores, key=lambda x:x[1], reverse=True)
    return scores[:topk]

def enforce_entity_preservation(source, target, glossary_df):
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
    src_ents = extract_entities(source)
    bef = sum(1 for e in src_ents if e in baseline)/max(1,len(src_ents))
    aft = sum(1 for e in src_ents if e in corrected)/max(1,len(src_ents))
    return {"entity_preservation_before":bef,"entity_preservation_after":aft,
            "efc_composite":round(0.7*aft+0.3*(aft-bef),3)}


# ---------------------------- Streamlit UI ----------------------------
st.set_page_config(page_title="EACT + RG-CLD Demo", layout="wide")
st.title("🌐 EACT + RG-CLD + EFC — Interactive Demo")
st.write("Entity-aware, retrieval-guided translation prototype with EFC evaluation metric.")

src = st.selectbox("Source language",["en","hi","fr"],index=0)
tgt = st.selectbox("Target language",["hi","en","fr"],index=1)
glossary_file = st.file_uploader("Upload glossary CSV (term,term_lang,canonical_form)",type=["csv"])
glossary_df = load_glossary(glossary_file)

text = st.text_area("Enter text", "Dr. Anil Gupta visited AIIMS to discuss cardiac surgery.")

if st.button("Run Translation"):
    st.info("Running baseline translation …")
    base = run_baseline_translation(text, src, tgt)
    st.code(base)
    st.info("Applying EACT + RG-CLD post-processing …")
    corr, rep = enforce_entity_preservation(text, base, glossary_df)
    st.code(corr)
    st.json(rep)
    m = efc_metric(text, base, corr)
    st.write("**EFC Metrics:**", m)
    fig, ax = plt.subplots()
    ax.bar(["Before","After"],[m["entity_preservation_before"],m["entity_preservation_after"]])
    ax.set_ylim(0,1)
    ax.set_ylabel("Entity Preservation")
    ax.set_title("EFC Components")
    st.pyplot(fig)

st.caption("Upload your glossary CSV to activate retrieval-guided entity correction.")
