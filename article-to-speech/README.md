# Gemini TTS Factory

Interactive Streamlit-based application to transform articles (from a URL or raw text) into high-quality audio files, using Google Gemini and Google Cloud Text-to-Speech capabilities.

## Features

*   **Content Extraction**: Automatic retrieval of article text from URLs (supports BeautifulSoup and Gemini for intelligent parsing).
*   **Pronunciation Lookup**: Uses Google Search and Gemini to identify and suggest correct pronunciation of proper names and technical terms.
*   **Dictionary Management**: Interface to add, edit, and delete custom pronunciation rules.
*   **Intelligent Structuring**: Text analysis by Gemini to add pauses, stage directions (emotions), and assign speakers (Speaker 1 / Speaker 2).
*   **Speech Synthesis (TTS)**: Multi-speaker audio generation via Google Cloud TTS (Vertex AI, Journey models, etc.). Supports voice cloning (experimental).
*   **History**: Save and replay generated audio files.

## Prerequisites

*   Python 3.10+
*   A Google Cloud project with enabled APIs (Vertex AI, Text-to-Speech).
*   Configured authentication (e.g., `gcloud auth application-default login`).

## Installation

```bash
cd article-to-speech
pip install -r requirements.txt
```

## Usage

Launch the full application (FastAPI + Streamlit):

```bash
./run.sh
```

The interface will be accessible in your browser (default `http://localhost:8501`) and the API at `http://localhost:8000`.

# Article-to-Speech: Audio Generator for Press Articles

Article-to-Speech is a powerful Streamlit application that automates text extraction from news article URLs and synthesizes them into audio files (podcasts, news flashes, briefs) using Google's state-of-the-art AI models (Gemini and Cloud TTS).

## Main Features

- **Intelligent Text Extraction**: Uses Gemini 2.5 Flash to analyze the HTML structure, extract the main narrative content, and discard menus, ads, and superfluous elements.
- **Semantic Analysis and Structuring**: Splits the extracted article into a structured dialogue (Main Narrator vs. Secondary Reporter) to make listening more dynamic.
- **Automated Pronunciation Lookup**: Analyzes the text to identify proper names, brands (e.g., Shein, Temu), or technical terms, and uses Gemini coupled with Google Search to generate the exact pronunciation in **International Phonetic Alphabet (IPA)**.
- **Hybrid Phonetic Dictionary**: Automatically manages a dictionary to enforce pronunciation of complex words using the Cloud TTS `CustomPronunciations` API for IPA, and a Regex replacement for basic phonetic rules (e.g., dashes/capitals).
- **Modular Synthesis Architecture (Factory Pattern)**: Support for multiple providers and rendering engines:
  - **Google Cloud Text-to-Speech**: Ideal for high continuous production volumes, manages Multi-Speaker, and natively avoids the 4000-byte limitation via an intelligent asynchronous chunking system.
  - **Vertex AI (Gemini TTS)**: Supports advanced voice configurations and experimental pre-generations.
- **Remote Save & Cache**: All extracted texts are cached. Configurable application to easily switch from `local` to `remote` (Google Cloud Storage / Firebase) for assets and prompts.

## Architecture & Installation

The project relies on **Python 3.13** and requires a virtual environment.

```bash
# 1. Create and activate the virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch the application
./run.sh
# The script launches both the FastAPI backend (port 8000) and the Streamlit frontend (port 8501).
```

### Global Configuration (`.env`)

The application is fully configurable via a `.env` file at the root:

```env
APP_MODE=local                # local or remote
TTS_PROVIDER=cloud            # 'cloud' (Google Cloud TTS) or 'vertex' (Vertex AI)
LOCATION=europe-west1         # Google Cloud Region (e.g., europe-west1, us-central1)
GOOGLE_CLOUD_PROJECT=...      # Your Google Cloud Project ID
```

## Project Structure

- `app.py`: The main entry point (Streamlit user interface).
- `gemini_url_to_audio.py`: The backend engine managing LLM orchestration, parsing, caching, and the TTS "Factory" architecture.
- `prompts.py`: Configuration file isolating all system instructions (Prompts) given to Gemini for extraction and generation.
- `phonetic_dictionary_guide.md`: Technical guide dedicated to explaining the subtleties of the phonetic engine and the difference between Cloud TTS (IPA) and Regex.
- `assets/`: Local storage directory for generated `.wav` audios and `.json` metadata.
- `brain/`: Directory for artifacts and logs of Antigravity (the project's AI assistant).

## Use Cases & Demos

The application interface allows: 
1. **"Generator" Workshop**: Paste any URL to automate the whole chain (Extraction -> Pronunciation -> Structure -> Audio).
2. **"Playground" Workshop**: Enter arbitrary raw text to directly test voices and adjust tags (`[pause]`, `<speak>`).
3. **"Audio" Playground**: Laboratory to test single-speaker voices, pitch adjustment, Auto-tune, and speaking rate.
