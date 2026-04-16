# Gemini TTS API: The Deep Dive

> **This guide is designed for developers who want to exploit 100% of Gemini's vocal capabilities (models `gemini-2.5-pro` / `gemini-2.5-flash`), including hidden features and audio "prompt engineering" techniques.**

---

## 1. The "Audio-First" Philosophy

Unlike classic TTS APIs (Google Cloud TTS, AWS Polly) which are parametric (`rate=1.2`, `pitch=-2.0`), Gemini is a **generative multimodal** model.

This means that **control is done through context and prompt**, not by sliders.
- **Want it to speak fast?** Tell it it's in a hurry.
- **Want it to whisper?** Put it in a secret situation.

---

## 2. Complete Configuration Structure

Here is the maximal configuration object that can be passed to `client.models.generate_content`.

```python
from google.genai import types

config = types.GenerateContentConfig(
    # 1. Enable TTS
    response_modalities=["AUDIO"], 

    # 2. Temporal Metadata (Subtitles / Lip-sync)
    audio_timestamp=True, 

    # 3. Vocal Configuration (One OR the other)
    speech_config=types.SpeechConfig(
        # --- OPTION A: Single Voice (Standard) ---
        voice_config=types.VoiceConfig(
            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                voice_name="Aoede"
            )
        ),
        
        # --- OR OPTION B: Cloned Voice (Deep) ---
        # voice_config=types.VoiceConfig(
        #     replicated_voice_config=types.ReplicatedVoiceConfig(
        #         voice_sample_audio=b"...", # WAV file bytes
        #         mime_type="audio/wav"
        #     )
        # ),

        # --- OR OPTION C: Multi-Speaker (Native) ---
        # multi_speaker_voice_config=types.MultiSpeakerVoiceConfig(
        #     speaker_voice_configs=[
        #         types.SpeakerVoiceConfig(
        #             speaker="Narrator",
        #             voice_config=types.VoiceConfig(prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Fenrir"))
        #         ),
        #         types.SpeakerVoiceConfig(
        #             speaker="Alice",
        #             voice_config=types.VoiceConfig(prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Kore"))
        #         )
        #     ]
        # ),

        # 4. Language (Accent/Pronunciation)
        language_code="fr-FR" 
    ),

    # 5. Style Directives (The "real" prosodic control)
    system_instruction="""
    You are a professional audiobook reader.
    Your tone is calm, steady, and engaging.
    Mark clear pauses after each sentence.
    """
)
```

---

## 3. The Prosody "Hack" (Audio Prompt Engineering)

Since there are no `speed` or `emotion` parameters, you must simulate them via the `system_instruction` or the user prompt.

### Technique A: The Set Director
Give explicit scene instructions before the text.

**Prompt:**
```text
(Context: Breaking News, High Urgency, Fast Pace)
Special Flash: A storm is approaching the coast...
```

### Technique B: Voice Tags (Markup Tags) - OFFICIAL
Officially documented by Google, these bracketed tags act in 4 modes:

**1. Non-Verbal Sounds (Mode 1)**
The tag is replaced by a sound, it is not read.
- `[laughing]`: Laughter
- `[sigh]`: Sigh
- `[uhm]`: Hesitation

**2. Style Modifiers (Mode 2)**
The tag modifies how the following text is spoken, without being read.
- `[whispering]`: Whisper
- `[shouting]`: Shout
- `[sarcasm]`: Sarcastic tone
- `[robotic]`: Robotic voice
- `[extremely fast]`: Very fast rate

**3. Pauses and Rhythm (Mode 4)**
Explicit timing control.
- `[short pause]`: Short pause
- `[medium pause]`: Medium pause
- `[long pause]`: Long pause

**⚠ Warning (Mode 3 - Vocalized)**: Some tags like `[scared]`, `[curious]`, or `[bored]` risk being **read out loud** by the model instead of being played. For these emotions, prefer the *System Prompt* (Technique A).

### Technique C: Rhythmic Punctuation
Use punctuation to force rhythm.
- `...` = Medium pause
- `—` = Tone change or interruption
- `\n\n` = Long pause (paragraph)

---

## 4. Voice Catalog (Full List)

These names are to be passed in `voice_name`.

| Name | Gender | Style / Personality | Recommended Usage |
| :--- | :--- | :--- | :--- |
| **Aoede** | Female | Professional, Clear, Steady | News, Documentaries, Assistants |
| **Fenrir** | Male | Deep, Authoritative, "Radio" | Epic narration, Thriller, News |
| **Charon** | Male | Grave, Calm, Reassuring | Meditation, Bedtime stories |
| **Kore** | Female | Soft, Soothing, Maternal | Well-being, Children's stories |
| **Puck** | Male | Energetic, Playful, Fast | Gaming, Dynamic tutorials, Ads |
| **Zephyr** | Female | Light, Airy, Soft | Poetry, Nature, Romance |
| **Léda** | Female | Balanced, Standard | General usage |
| **Orus** | Male | Balanced, Standard | General usage |
| **Achernar** | Female | High-pitched, Sparkling | Young characters |
| **Achird** | Male | Young, Dynamic | Teens, Tech |
| **Algenib** | Male | Baritone, Deep | Imposing characters |

> **Tip**: Combine `Fenrir` (Narrator) and `Aoede` (Journalist) for a very professional rendering.

---

## 5. Multi-Speaker: The Secret Weapon

To create a realistic conversation without generating X separate audio files.

**Scenario: Interview**

```python
contents = """
Journalist: Good morning Mr. President.
President: Good morning to you.
Journalist: Is the situation under control?
President: [hesitant] Well... it's complex.
"""

# Config
# Speaker "Journalist" -> Aoede
# Speaker "President" -> Fenrir
```

The model will automatically:
1. Detect speaker turns based on names defined in `speaker_voice_configs`.
2. Change voice instantly.
3. Manage interruptions or slight overlaps if the prompt suggests it.

---

## 6. Voice Cloning (ReplicatedVoiceConfig)

**Status: Experimental / Restricted**

Allows cloning a voice with a few seconds of audio.

**Technical Constraints:**
- **Format:** WAV (PCM 16-bit recommended) or MP3.
- **Size:** Ideally < 5MB for latency.
- **Quality:** The sample must be clean, with no background noise.

```python
types.ReplicatedVoiceConfig(
    voice_sample_audio=open("my_voice.wav", "rb").read(),
    mime_type="audio/wav"
)
```

---

## 7. Retrieving Audio Timestamps

If `audio_timestamp=True`, the response contains a list of `TimeSegment` mapping text and time.

**Response Structure (JSON-like):**
```json
"voice_metadata": [
    {"start_offset": "0s", "end_offset": "0.5s", "word": "Hello"},
    {"start_offset": "0.5s", "end_offset": "0.8s", "word": ","},
    {"start_offset": "0.9s", "end_offset": "1.2s", "word": "this"}
]
```
*Note: The exact structure may vary slightly depending on the API version (`video_metadata` or `voice_metadata`).*

---

## 8. Limitations & Best Practices

1. **Length**: Gemini has a huge context window, but for audio, avoid generating more than 5-10 minutes at a time to avoid HTTP timeouts. Split long texts.
2. **Sound Hallucinations**: Sometimes the model may "laugh" or make mouth sounds if the text is ambiguous. `strict_mode` via prompt ("Do not add sound effects") helps.
3. **Languages**: If the text is in FR but `language_code="en-US"`, it will read French with a strong American accent. Always match the language.

---

## 9. Audio Response Structure (`AudioChunk`)

API inspection confirms that the audio response is encapsulated in `AudioChunk` objects (via `part.inline_data`).

**Detected Fields in `AudioChunk`:**
- `data` (`bytes`): Raw audio data (PCM/WAV).
- `mime_type` (`str`): MIME type (e.g., `audio/pcm`, `audio/wav`).
- `source_metadata`: Metadata about the source (if mixing or multi-source).

> **Final Confirmation**: Full SDK inspection (`inspect_broad.py`) confirms that **NO** hidden classes exist to adjust rate, pitch, or volume. Everything definitely relies on **Prompt Engineering** and **Markup Tags**.
