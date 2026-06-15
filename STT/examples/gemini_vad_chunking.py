import os
import sys
import asyncio

# Add project root to path to find STT module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from STT.stt_providers.gemini import GeminiSTTProvider

async def main():
    # Initialize provider
    provider = GeminiSTTProvider(model_name="gemini-2.5-flash")

    # Path to an audio file
    audio_file = "assets/batch/0-temp.wav"

    if not os.path.exists(audio_file):
        print(f"File {audio_file} not found. Please provide a valid audio file.")
        return

    print(f"Transcribing {audio_file} using VAD-based chunking strategy asynchronously...")

    # Using transcribe_async uses chunk_audio_with_vad internally
    # It splits the audio into voiced segments via WebRTCVAD and processes them in parallel
    result = await provider.transcribe_async(audio_file, aggressiveness=3)

    print("\nTranscription Result:")
    print(result)

    print("\nNote: This example demonstrates using the VAD (Voice Activity Detection) strategy. It slices the audio into chunks that contain active speech, skips silences, and transcribes the chunks concurrently, achieving faster wall-clock execution time.")

if __name__ == "__main__":
    asyncio.run(main())
