# STT Benchmark

Tools and scripts to evaluate and compare the quality of transcription models (ASR).

## Objectives

*   Compare the performance of Gemini models (1.5 Pro, Flash, etc.) and Google Speech-to-Text.
*   Measure accuracy via WER (Word Error Rate).
*   Evaluate semantic similarity (Semantic Textual Similarity) to go beyond simple word-to-word matching.

## Content

*   `STT benchmark gemini ASR.ipynb`: Benchmark specific to Gemini models.
*   `STT benchmark google speech.ipynb`: Benchmark for Google Cloud Speech-to-Text API (STT V1/V2).
*   `run_benchmark.py`: Main script to orchestrate the benchmark.

## Metrics Used

*   **WER (Word Error Rate)**: Standard error rate (Insertions, Deletions, Substitutions).
*   **Semantic Similarity**: Measure of meaning proximity between transcription and ground truth.

## Audio Splitting Strategies

To handle long audio files, the benchmark supports different splitting strategies defined in `run_benchmark.py`:

*   **No Split (`no_split`)**: Processes the entire audio file as a single chunk. Best for short files that fit within the model's token limit.
*   **Hard Split (`hard_split`)**: Strictly splits the audio into fixed-size chunks (default 59 seconds). Simple and predictable, but may cut words.
*   **Split by Silences (`split_by_silences`)**: Uses silence detection to split at pauses (default at least 600ms of silence). Best for natural speech to avoid cutting in the middle of sentences.

### Strategy Recommendations

*   **For Natural Speech (Interviews, Podcasts)**: Use **`split_by_silences`**. It delivers the best quality by keeping phrases intact.
*   **For Short Clips (< 1-2 min)**: Use **`no_split`** to preserve maximum context without splitting artifacts.
*   **For Continuous Sound / Music**: Use **`hard_split`** as a fallback if there are no distinct pauses to detect.

> [!NOTE]
> Recent benchmark results on short synthetic test files (approx. 3s) confirmed that all strategies perform perfectly (WER: 0.0) for short audio clips, as expected when the entire audio fits in a single chunk.

## Usage

The scripts and notebooks require a test dataset (audio files + reference transcriptions) stored on Google Cloud Storage (GCS) or locally in `assets/batch`.

To run the benchmark using the shell script:
```bash
./run_benchmark.sh
```

## Prerequisites

*   Python 3
*   A Google Cloud Platform account with a configured project.
*   Enabled APIs: Vertex AI, Google Cloud Storage, and BigQuery.
*   Configured authentication (e.g., `gcloud auth application-default login`).

## Installation

It is recommended to create a virtual environment.

```bash
pip install --upgrade datasets nltk evaluate tokenizers seqeval sequence-evaluate sentence-transformers rouge jiwer pydub google-genai librosa protobuf google-cloud-storage google-cloud-bigquery webrtcvad "setuptools<81"
```
