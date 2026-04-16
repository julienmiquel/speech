# Article: Technical Deep Dive into the Project's TTS (Text-to-Speech) Capabilities

This document presents a detailed analysis of all the Text-to-Speech features implemented in the **Article-to-Speech** project, driven by Google Cloud and Vertex AI technologies. The platform's goal is to transform classic press article reading into a dynamic, professional, and multi-voice audio experience.

---

## 1. Synthesis Engines: The Factory Architecture

To guarantee flexibility and scalability in the face of limitations of different Google APIs, the application relies on a **Factory** design pattern (`TTSFactory` in `gemini_url_to_audio.py`). The system can switch from one provider ("Provider") to another transparently for the user interface, according to the `TTS_PROVIDER` environment variable.

### A. The Provider: `CloudTTSProvider` (Google Cloud Text-to-Speech)
Implementation relying on the native Google Cloud API (`google-cloud-texttospeech` library).
- **Industrial Reliability**: Designed for dense production scenarios requiring financial and operational predictability.
- **Exceeding the 4000-byte limit**: Google synthesis models are structurally limited to sending 4000 characters per packet. The `CloudTTSProvider` implements an *Intelligent Chunking* algorithm that cuts the long text of an article into safe chunks (~3500 characters), sends requests in fluid asynchronous flow, and then sews together the binary audio frames imperceptibly to generate a mega `.wav` file of several minutes.
- **Supported formats**: `VoiceSelectionParams` for classic single-speaker models, and the structured `MultiSpeakerMarkup` object which concatenates dialogues between two different speakers.

### B. The Provider: `VertexTTSProvider` (Gemini & Vertex AI)
Implementation relying on the Gemini generative AI ecosystem (`google-genai` library).
- **Experimental Prerogatives**: Mainly used to query Early Access Program (EAP) models such as `gemini-2.5-flash-tts-eap` (often exclusive to `us-central1`).
- **Voice Cloning (Voice Cloning)**: This provider is the only one capable of executing the experimental function `synthesize_replicated_voice()` which copies the timbre of a voice from an input audio file and applies this timbre to a new generated text (*zero-shot voice replication*).

---

## 2. The Hybrid Phonetic Dictionary (Management of 400 errors)

The pronunciation of proper names, acronyms, and foreign brands (e.g., "Shein", "Retailleau", "SaaS") is critical in a news podcast.
Classic APIs tend to invent or natively gallicize all foreign words.

To force the model's hand, we combine **two distinct and automated approaches**:

### The "Premium" API approach: International Phonetic Alphabet (IPA)
The Cloud TTS API accepts a list of exceptions via the `CustomPronunciations` parameter coupled with the `PHONETIC_ENCODING_IPA` constant. If the generated dictionary provides a strict IPA string (all lowercase with the right symbols, e.g., `fijɔ̃` for Fillon), this term is binary-encapsulated during transmission and the engine adjusts the waveform without touching the letters.
**Advantage**: Extremely pure sound rendering without choppiness.

### The "Legacy" approach: Regex Replacement (Pseudo-Phonetics)
However, the Cloud TTS API *crashes* (400 Error "Invalid Phrases") if it is provided with dashes, commas, or capital letters in the phoneme instruction (e.g., `Fi-yon` or `Chi-ine`).
In this case, the implementation conditionally filters these non-IPA words. It removes them from the `CustomPronunciations` request and applies instead a basic `Regex string replace` substitution (e.g., replaces the word "Shein" with the spelling "Chi-ine" directly in the text string sent to the model).
**Advantage**: Backward compatibility with pronunciations defined artisanally by humans.

### IPA Generation by Gemini
To fluidize this pipeline, when a user imports a new article, the application delegates to **Gemini 2.5 Flash** (coupled with the `Google Search` tool) the identification of ambiguous terms and automatically generates for each proper name the strict IPA rendering (e.g., `ʃi.in`). The generated request natively traces what was submitted in the historization JSON `applied_ipa_phonemes`.

---

## 3. The Multi-Speaker Architecture (Dialogue)

One of the product values of the application is the ability to convert a linear and chronological article into an interactive format with 2 speakers:
1. **The Anchor (The Presenter)**: Authoritative, steady, formal tone, to carry the plot and read the thread of a dispatch.
2. **The Reporter / The Expert**: Conversational and dynamic tone. It is used (via the Parser Analysis algorithm) to take back in vocal form the relevant quotes or "sidebars" of the article (*sidebars* in the middle of the HTML).

### Cloud TTS MultiSpeakerMarkup Format
The `synthesize_multi_speaker` method iterates on each JSON structure (Speaker "R" or "S") provided by Gemini after HTML extraction.
The text is segmented into **Turns** (speaker turns). Cloud TTS requires these *Turns* to be packaged in batches of maximum 4000 characters in binary format. Rather than synthesizing 50 micro WAV files, the algorithm "batches" the takes and inserts a structural delay (`delay_seconds`) between sentences as needed to simulate natural narrative silence.

---

## Conclusion
The project masters the entire end-to-end chain:
- From raw web URL to a structured JSON of cleaned data.
- From LLM engineering to extract critical phonetic cases and simulate a Google Search.
- From a distributed development pattern (`TTSProvider Interface`) that addresses the strict technical limitations of Cloud API endpoints to guarantee that no resource exceeds in length.
