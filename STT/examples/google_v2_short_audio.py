import os
import sys

# Add project root to path to find STT module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from STT.stt_providers.google_v2 import GoogleSpeechV2Provider

def main():
    # Initialize provider
    # Use 'long' model and 'global' location to support fr-FR
    provider = GoogleSpeechV2Provider(model_name="long", location="global")
    
    # Path to a short audio file (replace with your file)
    audio_file = "assets/batch/0-temp.wav" 
    
    if not os.path.exists(audio_file):
        print(f"File {audio_file} not found. Please provide a valid audio file.")
        return
        
    print(f"Transcribing {audio_file} using Google Speech v2...")
    result = provider.transcribe(audio_file)
    
    print("\nTranscription Result:")
    print(result)

if __name__ == "__main__":
    main()
