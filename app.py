import streamlit as st
from transformers import MarianMTModel, MarianTokenizer
import torch

# Page configuration
st.set_page_config(
    page_title="Neural Machine Translation",
    page_icon="🌐",
    layout="wide"
)

# Title and description
st.title("🌐 Neural Machine Translation App")
st.markdown("Translate text between multiple languages using state-of-the-art neural machine translation models.")

# Supported languages with their codes
LANGUAGES = {
    "English": "en",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Italian": "it",
    "Portuguese": "pt",
    "Russian": "ru",
    "Chinese": "zh",
    "Japanese": "ja",
    "Korean": "ko",
    "Arabic": "ar",
    "Hindi": "hi",
    "Dutch": "nl",
    "Polish": "pl",
    "Turkish": "tr",
    "Czech": "cs",
    "Romanian": "ro",
    "Finnish": "fi",
    "Swedish": "sv",
    "Norwegian": "no",
    "Greek": "el",
    "Bulgarian": "bg",
    "Croatian": "hr",
    "Hungarian": "hu",
    "Indonesian": "id",
    "Vietnamese": "vi",
    "Thai": "th",
    "Ukrainian": "uk"
}

# Model mapping for common language pairs
# Using Helsinki-NLP models which are well-supported
MODEL_MAP = {
    ("en", "es"): "Helsinki-NLP/opus-mt-en-es",
    ("es", "en"): "Helsinki-NLP/opus-mt-es-en",
    ("en", "fr"): "Helsinki-NLP/opus-mt-en-fr",
    ("fr", "en"): "Helsinki-NLP/opus-mt-fr-en",
    ("en", "de"): "Helsinki-NLP/opus-mt-en-de",
    ("de", "en"): "Helsinki-NLP/opus-mt-de-en",
    ("en", "it"): "Helsinki-NLP/opus-mt-en-it",
    ("it", "en"): "Helsinki-NLP/opus-mt-it-en",
    ("en", "pt"): "Helsinki-NLP/opus-mt-en-pt",
    ("pt", "en"): "Helsinki-NLP/opus-mt-pt-en",
    ("en", "ru"): "Helsinki-NLP/opus-mt-en-ru",
    ("ru", "en"): "Helsinki-NLP/opus-mt-ru-en",
    ("en", "zh"): "Helsinki-NLP/opus-mt-en-zh",
    ("zh", "en"): "Helsinki-NLP/opus-mt-zh-en",
    ("en", "ja"): "Helsinki-NLP/opus-mt-en-jap",
    ("ja", "en"): "Helsinki-NLP/opus-mt-jap-en",
    ("en", "ko"): "Helsinki-NLP/opus-mt-en-ko",
    ("ko", "en"): "Helsinki-NLP/opus-mt-ko-en",
    ("en", "ar"): "Helsinki-NLP/opus-mt-en-ar",
    ("ar", "en"): "Helsinki-NLP/opus-mt-ar-en",
    ("en", "hi"): "Helsinki-NLP/opus-mt-en-hi",
    ("hi", "en"): "Helsinki-NLP/opus-mt-hi-en",
    ("en", "nl"): "Helsinki-NLP/opus-mt-en-nl",
    ("nl", "en"): "Helsinki-NLP/opus-mt-nl-en",
    ("en", "pl"): "Helsinki-NLP/opus-mt-en-pl",
    ("pl", "en"): "Helsinki-NLP/opus-mt-pl-en",
    ("en", "tr"): "Helsinki-NLP/opus-mt-en-tr",
    ("tr", "en"): "Helsinki-NLP/opus-mt-tr-en",
    ("en", "cs"): "Helsinki-NLP/opus-mt-en-cs",
    ("cs", "en"): "Helsinki-NLP/opus-mt-cs-en",
    ("en", "ro"): "Helsinki-NLP/opus-mt-en-ro",
    ("ro", "en"): "Helsinki-NLP/opus-mt-ro-en",
    ("en", "fi"): "Helsinki-NLP/opus-mt-en-fi",
    ("fi", "en"): "Helsinki-NLP/opus-mt-fi-en",
    ("en", "sv"): "Helsinki-NLP/opus-mt-en-sv",
    ("sv", "en"): "Helsinki-NLP/opus-mt-sv-en",
    ("en", "no"): "Helsinki-NLP/opus-mt-en-no",
    ("no", "en"): "Helsinki-NLP/opus-mt-no-en",
    ("en", "el"): "Helsinki-NLP/opus-mt-en-el",
    ("el", "en"): "Helsinki-NLP/opus-mt-el-en",
    ("en", "bg"): "Helsinki-NLP/opus-mt-en-bg",
    ("bg", "en"): "Helsinki-NLP/opus-mt-bg-en",
    ("en", "hr"): "Helsinki-NLP/opus-mt-en-hr",
    ("hr", "en"): "Helsinki-NLP/opus-mt-hr-en",
    ("en", "hu"): "Helsinki-NLP/opus-mt-en-hu",
    ("hu", "en"): "Helsinki-NLP/opus-mt-hu-en",
    ("en", "id"): "Helsinki-NLP/opus-mt-en-id",
    ("id", "en"): "Helsinki-NLP/opus-mt-id-en",
    ("en", "vi"): "Helsinki-NLP/opus-mt-en-vi",
    ("vi", "en"): "Helsinki-NLP/opus-mt-vi-en",
    ("en", "th"): "Helsinki-NLP/opus-mt-en-th",
    ("th", "en"): "Helsinki-NLP/opus-mt-th-en",
    ("en", "uk"): "Helsinki-NLP/opus-mt-en-uk",
    ("uk", "en"): "Helsinki-NLP/opus-mt-uk-en",
}

# Function to get model name
def get_model_name(source_lang, target_lang):
    """Get the model name for a language pair, or use a multilingual model as fallback."""
    key = (source_lang, target_lang)
    if key in MODEL_MAP:
        return MODEL_MAP[key]
    # Fallback to multilingual model if direct pair not available
    return "Helsinki-NLP/opus-mt-mul-en" if target_lang == "en" else None

# Function to load model
@st.cache_resource
def load_model(model_name):
    """Load the translation model and tokenizer."""
    try:
        tokenizer = MarianTokenizer.from_pretrained(model_name)
        model = MarianMTModel.from_pretrained(model_name)
        return tokenizer, model
    except Exception as e:
        st.error(f"Error loading model: {str(e)}")
        return None, None

# Function to translate text
def translate_text(text, tokenizer, model, max_length=512):
    """Translate text using the loaded model."""
    if not text.strip():
        return ""
    
    # Tokenize input
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=max_length)
    
    # Generate translation
    with torch.no_grad():
        translated = model.generate(**inputs, max_length=max_length, num_beams=4, early_stopping=True)
    
    # Decode output
    translated_text = tokenizer.decode(translated[0], skip_special_tokens=True)
    return translated_text

# Sidebar for settings
with st.sidebar:
    st.header("⚙️ Settings")
    source_lang = st.selectbox("Source Language", list(LANGUAGES.keys()), index=0)
    target_lang = st.selectbox("Target Language", list(LANGUAGES.keys()), index=1)
    
    st.markdown("---")
    st.markdown("### 📊 Model Info")
    st.info("Using Helsinki-NLP OPUS-MT models for high-quality neural machine translation.")
    
    st.markdown("---")
    st.markdown("### ℹ️ About")
    st.markdown("""
    This app uses state-of-the-art neural machine translation models 
    from Hugging Face Transformers to translate between multiple languages.
    """)

# Main translation interface
col1, col2 = st.columns(2)

with col1:
    st.subheader(f"📝 Input ({source_lang})")
    input_text = st.text_area(
        "Enter text to translate",
        height=300,
        placeholder="Type or paste your text here...",
        label_visibility="collapsed"
    )

with col2:
    st.subheader(f"🌍 Translation ({target_lang})")
    
    if st.button("🔄 Translate", type="primary", use_container_width=True):
        if not input_text.strip():
            st.warning("Please enter some text to translate.")
        else:
            source_code = LANGUAGES[source_lang]
            target_code = LANGUAGES[target_lang]
            
            if source_code == target_code:
                st.warning("Source and target languages cannot be the same.")
            else:
                with st.spinner("Loading model and translating..."):
                    model_name = get_model_name(source_code, target_code)
                    
                    if model_name is None:
                        st.error(f"Translation from {source_lang} to {target_lang} is not currently supported. Please try a different language pair.")
                    else:
                        tokenizer, model = load_model(model_name)
                        
                        if tokenizer is not None and model is not None:
                            # Handle long text by splitting into sentences
                            sentences = input_text.split('. ')
                            translations = []
                            
                            for sentence in sentences:
                                if sentence.strip():
                                    translated = translate_text(sentence, tokenizer, model)
                                    translations.append(translated)
                            
                            result = '. '.join(translations)
                            st.text_area(
                                "Translation result",
                                value=result,
                                height=300,
                                label_visibility="collapsed"
                            )
                            
                            # Download button
                            st.download_button(
                                label="📥 Download Translation",
                                data=result,
                                file_name=f"translation_{source_lang}_to_{target_lang}.txt",
                                mime="text/plain"
                            )
                        else:
                            st.error("Failed to load the translation model. Please try again.")

# Additional features
st.markdown("---")
st.subheader("✨ Features")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    **🌐 Multi-language Support**
    - Translate between 28+ languages
    - High-quality neural models
    """)

with col2:
    st.markdown("""
    **⚡ Fast & Accurate**
    - State-of-the-art OPUS-MT models
    - Real-time translation
    """)

with col3:
    st.markdown("""
    **💾 Export Options**
    - Download translations
    - Copy to clipboard
    """)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>"
    "Powered by Hugging Face Transformers | Helsinki-NLP OPUS-MT Models"
    "</div>",
    unsafe_allow_html=True
)

