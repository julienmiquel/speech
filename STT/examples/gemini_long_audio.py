import os
import sys

# Add project root to path to find STT and benchmark modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from STT.stt_providers.gemini import GeminiSTTProvider
from benchmark.run_benchmark import process_local_file_by_chunk, get_audio_sequence_hard_split

def main():
    # Initialize provider
    provider = GeminiSTTProvider(model_name="gemini-2.5-flash")
    
    # Path to a long audio file (replace with your file)
    # This example assumes you have a long file or want to test with a short one first
    audio_file = "assets/batch/0-temp.wav" 
    
    if not os.path.exists(audio_file):
        print(f"File {audio_file} not found. Please provide a valid audio file.")
        return
        
    print(f"Transcribing {audio_file} with chunking for long audio...")
    
    # Use hard split strategy as an example
    split_strategy = get_audio_sequence_hard_split
    
    result = process_local_file_by_chunk(
        file_name=audio_file,
        _stt=provider,
        _split_sequence_strategy=split_strategy,
        prompt="Transcribe this audio.",
        model_name="gemini-2.5-flash"
    )
    
    print("\nTranscription Result:")
    print(result)
    
    print("\nNote: This approach scales to 15m, 30m, and 60m files by splitting them into manageable chunks using VAD or hard splits.")

if __name__ == "__main__":
    main()
