# Gemini Speech-to-Text (STT)

Experiments and usage examples of Google Gemini models for automatic speech recognition (ASR).

## Features

*   **Modular Architecture**: Uses the Strategy pattern with `BaseSTTProvider` to support different transcription engines.
*   **SDK Migration**: Uses the new `google-genai` SDK.
*   **VAD Optimization**: Optimized in-memory Voice Activity Detection (VAD) without temporary file creation.
*   **Input Management**: Supports both file paths and in-memory byte streams.

## Content

*   `stt_providers/`: Provider implementations (e.g., `gemini.py`).
*   `vad.py`: Voice Activity Detection functions.
*   `STT gemini ASR examples.ipynb`: Demonstration notebook.
*   `examples/`: Example scripts for short and long audio processing.

## Examples

*   `examples/gemini_short_audio.py`: Demonstrates how to transcribe a short audio file directly using `GeminiSTTProvider`.
*   `examples/gemini_long_audio.py`: Demonstrates how to process long audio files (15m, 30m, 60m) by chunking the audio using VAD or hard splits with Gemini.
*   `examples/google_v2_short_audio.py`: Demonstrates how to transcribe a short audio file using `GoogleSpeechV2Provider`.
*   `examples/google_v2_long_audio.py`: Demonstrates how to process long audio files with chunking using `GoogleSpeechV2Provider`.

## Prerequisites

*   Google Cloud Platform account.
*   Access to Gemini APIs.
*   Python libraries: `google-genai`, `pydub`, `webrtcvad`, `setuptools<81`
