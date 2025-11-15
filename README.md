# Neural Machine Translation App 🌐

A modern, user-friendly Streamlit application for neural machine translation between multiple languages using state-of-the-art transformer models.

## Features

- 🌐 **Multi-language Support**: Translate between 28+ languages including English, Spanish, French, German, Italian, Portuguese, Russian, Chinese, Japanese, Korean, Arabic, Hindi, and many more
- ⚡ **High-Quality Models**: Uses Helsinki-NLP OPUS-MT models for accurate translations
- 🎨 **Beautiful UI**: Clean and intuitive interface built with Streamlit
- 💾 **Export Options**: Download translations as text files
- 🚀 **Fast Performance**: Optimized with model caching for quick translations

## Supported Languages

The app supports translation between the following languages:

- English, Spanish, French, German, Italian, Portuguese
- Russian, Chinese, Japanese, Korean, Arabic, Hindi
- Dutch, Polish, Turkish, Czech, Romanian, Finnish
- Swedish, Norwegian, Greek, Bulgarian, Croatian, Hungarian
- Indonesian, Vietnamese, Thai, Ukrainian

## Installation

1. **Clone or download this repository**

2. **Install the required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Streamlit app:**
   ```bash
   streamlit run translation_app.py
   ```

4. **Open your browser** and navigate to the URL shown in the terminal (usually `http://localhost:8501`)

## Usage

1. Select the **source language** from the dropdown in the sidebar
2. Select the **target language** from the dropdown in the sidebar
3. Enter or paste the text you want to translate in the input area
4. Click the **"🔄 Translate"** button
5. View the translation in the output area
6. Optionally download the translation using the download button

## Technical Details

- **Framework**: Streamlit
- **Models**: Helsinki-NLP OPUS-MT models from Hugging Face
- **Library**: Transformers library by Hugging Face
- **Backend**: PyTorch

## Notes

- The first translation may take longer as the model needs to be downloaded and loaded
- Models are cached after the first use for faster subsequent translations
- Some language pairs may not be directly supported and will show an error message
- For best results, translate shorter sentences or paragraphs

## Requirements

- Python 3.8 or higher
- Internet connection (for downloading models on first use)
- Sufficient disk space (models can be several hundred MB each)

## License

This project uses models from Helsinki-NLP which are licensed under the Apache 2.0 license.

## Acknowledgments

- [Helsinki-NLP](https://github.com/Helsinki-NLP) for the OPUS-MT models
- [Hugging Face](https://huggingface.co/) for the Transformers library
- [Streamlit](https://streamlit.io/) for the web framework

