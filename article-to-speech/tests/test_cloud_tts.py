import os
from gemini_url_to_audio import TTSFactory

os.environ["TTS_PROVIDER"] = "cloudtts"

provider = TTSFactory.get_provider()
print(f"Provider: {type(provider).__name__}")

# Text to speech
text = "Bonjour, ceci est un test de l'API Google Cloud Text-to-Speech via notre nouveau design pattern Factory."
outfile, status, usage = provider.synthesize_and_save(text, output_file="assets/tmp/test_cloud.wav")
print(outfile, status, usage)

# Multi-speaker
dialogue = [
    {"text": "Bonjour Monsieur, comment allez-vous aujourd'hui?", "speaker": "R"},
    {"text": "Très bien, je vous remercie. C'est une belle journée.", "speaker": "S"}
]
outfile2, status2, usage2 = provider.synthesize_multi_speaker(dialogue, output_file="assets/tmp/test_cloud_multi.wav")
print(outfile2, status2, usage2)
