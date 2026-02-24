from google.cloud import texttospeech

client = texttospeech.TextToSpeechClient()

pronunciation_dict = texttospeech.CustomPronunciations(
    pronunciations=[
        texttospeech.CustomPronunciationParams(
            phrase="Fillon",
            pronunciation="Fi-yon",
            phonetic_encoding=texttospeech.CustomPronunciationParams.PhoneticEncoding.PHONETIC_ENCODING_UNSPECIFIED,
        )
    ]
)

try:
    synthesis_input = texttospeech.SynthesisInput(text="Bonjour Fillon.", custom_pronunciations=pronunciation_dict)
    voice = texttospeech.VoiceSelectionParams(language_code="fr-FR", name="fr-FR-Standard-A")
    audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
    response = client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)
    print("Success with non-IPA text")
except Exception as e:
    print(f"Error: {e}")
