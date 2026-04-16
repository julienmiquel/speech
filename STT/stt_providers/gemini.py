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
        from google import genai
        import os
        project = os.environ.get("GOOGLE_CLOUD_PROJECT", "customer-demo-01")
        self.client = genai.Client(vertexai=True, project=project, location=self.location)

    def _call_gemini(self, audio_bytes: bytes, prompt: str) -> str:
        from google.genai import types
        audio_part = types.Part.from_bytes(data=audio_bytes, mime_type="audio/wav")
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=[audio_part, prompt]
        )
        return response.text

    async def _async_call_gemini(self, audio_bytes: bytes, prompt: str) -> str:
        # Wrapping synchronous call in a thread pool for true concurrency
        return await asyncio.to_thread(self._call_gemini, audio_bytes, prompt)

    def transcribe(self, audio_path: str = None, audio_data: bytes = None, aggressiveness: int = 3, **kwargs) -> str:
        chunks = chunk_audio_with_vad(audio_path=audio_path, audio_data=audio_data, aggressiveness=aggressiveness)
        results = []
        prompt = kwargs.get("prompt", "Transcribe the following audio exactly: ")
        for chunk in chunks:
            try:
                res = self._call_gemini(chunk, prompt=prompt)
                results.append(res)
            except Exception as e:
                print(f"Error transcribing chunk: {e}")
        return " ".join(results)

    async def transcribe_async(self, audio_path: str = None, audio_data: bytes = None, aggressiveness: int = 3, **kwargs) -> str:
        # 1. Chunk Audio (O(n))
        chunks = chunk_audio_with_vad(audio_path=audio_path, audio_data=audio_data, aggressiveness=aggressiveness)
        prompt = kwargs.get("prompt", "Transcribe the following audio exactly: ")

        # 2. Parallel execution over all chunks (wall-clock time ~ O(1) chunks)
        tasks = [self._async_call_gemini(chunk, prompt=prompt) for chunk in chunks]

        results = []
        # Return results in order
        for res in await asyncio.gather(*tasks, return_exceptions=True):
            if isinstance(res, Exception):
                print(f"Error transcribing chunk async: {res}")
            else:
                results.append(res)

        return " ".join(results)
