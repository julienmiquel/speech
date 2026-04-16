import os
import sys

# Add project root to path to find STT and benchmark modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from STT.stt_providers.google_v2 import GoogleSpeechV2Provider
from benchmark.run_benchmark import process_local_file_by_chunk, get_audio_sequence_hard_split

def main():
    # Initialize provider
    # Use 'long' model and 'global' location to support fr-FR
    provider = GoogleSpeechV2Provider(model_name="long", location="global")
    
    # Path to a long audio file (replace with your file)
    audio_file = "assets/batch/0-temp.wav" 
    
    if not os.path.exists(audio_file):
        print(f"File {audio_file} not found. Please provide a valid audio file.")
        return
        
    print(f"Transcribing {audio_file} with chunking for long audio using Google Speech v2...")
    
    # Use hard split strategy as an example
    split_strategy = get_audio_sequence_hard_split
    
    result = process_local_file_by_chunk(
        file_name=audio_file,
        _stt=provider,
        _split_sequence_strategy=split_strategy,
        prompt="Transcribe this audio.",
        model_name="long"
    )
    
    print("\nTranscription Result:")
    print(result)
    
    print("\nNote: This approach scales to 15m, 30m, and 60m files by splitting them into manageable chunks using VAD or hard splits.")

if __name__ == "__main__":
    main()
