# Technology Stack

## Core Language & Runtime
- **Python 3.13**: The primary programming language used for the backend logic and Streamlit interface.

## User Interface
- **Streamlit**: Used to build the web-based interactive "Atelier" and "Playground" dashboards.

## Artificial Intelligence & LLMs
- **Google Gemini (GenAI SDK)**: Used for intelligent HTML parsing, text extraction, narrative structuring, and automated IPA pronunciation research.

## Speech Synthesis (TTS)
- **Google Cloud Text-to-Speech**: The primary high-volume engine, supporting multi-speaker dialogues and IPA-based custom pronunciations.
- **Vertex AI (Gemini TTS)**: Used for experimental voice configurations and advanced speech generation.

## Cloud & Storage
- **Google Cloud Storage**: For storing generated audio assets and metadata.
- **Firebase (Admin SDK)**: Used for managing remote cache and asset storage.
- **Google Cloud Vertex AI**: For accessing advanced AI models and TTS capabilities.

## Libraries & Utilities
- **BeautifulSoup4**: For robust HTML parsing during the text extraction phase.
- **Pydub**: For audio file manipulation and processing.
- **python-dotenv**: For environment-based configuration management.
