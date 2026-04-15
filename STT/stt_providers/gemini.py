import asyncio
import io
from typing import List
from .base import BaseSTTProvider
from .vad import chunk_audio_with_vad

class GeminiSTTProvider(BaseSTTProvider):
    """
    STT Provider implementation using Gemini API.
    Since Gemini doesn't stream natively for audio STT, we use asyncio on VAD chunks.
    """

    def __init__(self, model_name: str, location: str = "us-central1"):
        self.model_name = model_name
        self.location = location
        # Assume Vertex AI initialization or standard google.generativeai setup
        # For the sake of standardizing the interface we mock the actual call,
        # but in reality it wraps vertexai.generative_models.GenerativeModel
        from vertexai.generative_models import GenerativeModel, Part
        self.model = GenerativeModel(self.model_name)

    def _call_gemini(self, audio_bytes: bytes) -> str:
        from vertexai.generative_models import Part
        audio_part = Part.from_data(audio_bytes, mime_type="audio/wav")
        # Assuming the prompt is simply to transcribe
        response = self.model.generate_content([audio_part, "Transcribe the following audio exactly: "])
        return response.text

    async def _async_call_gemini(self, audio_bytes: bytes) -> str:
        # Wrapping synchronous call in a thread pool for true concurrency
        return await asyncio.to_thread(self._call_gemini, audio_bytes)

    def transcribe(self, audio_path: str, aggressiveness: int = 3, **kwargs) -> str:
        chunks = chunk_audio_with_vad(audio_path, aggressiveness)
        results = []
        for chunk in chunks:
            try:
                res = self._call_gemini(chunk)
                results.append(res)
            except Exception as e:
                print(f"Error transcribing chunk: {e}")
        return " ".join(results)

    async def transcribe_async(self, audio_path: str, aggressiveness: int = 3, **kwargs) -> str:
        # 1. Chunk Audio (O(n))
        chunks = chunk_audio_with_vad(audio_path, aggressiveness)

        # 2. Parallel execution over all chunks (wall-clock time ~ O(1) chunks)
        tasks = [self._async_call_gemini(chunk) for chunk in chunks]

        results = []
        # Return results in order
        for res in await asyncio.gather(*tasks, return_exceptions=True):
            if isinstance(res, Exception):
                print(f"Error transcribing chunk async: {res}")
            else:
                results.append(res)

        return " ".join(results)
