import asyncio
import io
from .base import BaseSTTProvider

class GoogleSpeechV2Provider(BaseSTTProvider):
    """
    STT Provider implementation using Google Cloud Speech v2.
    Utilizes `StreamingRecognizeRequest` for native streaming, completely bypassing
    local chunking / `io.BytesIO` state bottlenecks.
    """

    def __init__(self, model_name: str, language_code: str = "fr-FR", location: str = "us-central1"):
        self.model_name = model_name
        self.language_code = language_code
        self.location = location

        from google.cloud.speech_v2 import SpeechClient
        from google.api_core.client_options import ClientOptions

        if "global" == location:
            self.client = SpeechClient()
        else:
            client_options = ClientOptions(api_endpoint=f"{location}-speech.googleapis.com")
            self.client = SpeechClient(client_options=client_options)

    def _create_recognition_config(self, project_id: str, sample_rate: int, channels: int):
        from google.cloud.speech_v2 import RecognitionConfig, AutoDetectDecodingConfig, RecognitionFeatures

        return RecognitionConfig(
            auto_decoding_config=AutoDetectDecodingConfig(),
            language_codes=[self.language_code],
            model=self.model_name,
            features=RecognitionFeatures(
                enable_automatic_punctuation=True,
                enable_word_time_offsets=False,
            ),
        )

    def _stream_generator(self, audio_path: str = None, audio_data: bytes = None, chunk_size: int = 4096):
        """Generator that yields StreamingRecognizeRequest objects."""
        from google.cloud.speech_v2 import StreamingRecognizeRequest, StreamingRecognitionConfig
        import wave
        from pydub import AudioSegment
        import tempfile
        import os

        # We need to extract sample rate and channels. Use pydub to convert to raw PCM wav if needed
        if audio_path:
            sound = AudioSegment.from_file(audio_path)
        elif audio_data:
            sound = AudioSegment.from_file(io.BytesIO(audio_data), format="wav")
        else:
            raise ValueError("Either audio_path or audio_data must be provided.")
            
        fd, temp_wav = tempfile.mkstemp(suffix=".wav")
        os.close(fd)

        try:
            sound.export(temp_wav, format="wav")

            # Read properties
            import wave
            with wave.open(temp_wav, "rb") as wf:
                sample_rate = wf.getframerate()
                channels = wf.getnchannels()

            # Hardcoding a default project ID for demo, in production it should be injected
            # In the context of this repository, default project is usually configured in environment
            # Alternatively we can extract it from google.auth
            import google.auth
            _, project_id = google.auth.default()
            if not project_id:
                project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
            if not project_id:
                raise ValueError("Google Cloud Project ID not found. Please set GOOGLE_CLOUD_PROJECT environment variable.")

            recognizer = f"projects/{project_id}/locations/{self.location}/recognizers/_"

            config = self._create_recognition_config(project_id, sample_rate, channels)
            streaming_config = StreamingRecognitionConfig(config=config)

            # Yield the first request with config
            yield StreamingRecognizeRequest(
                recognizer=recognizer,
                streaming_config=streaming_config,
            )

            # Yield subsequent requests with audio content
            with open(temp_wav, "rb") as f:
                while True:
                    data = f.read(chunk_size)
                    if not data:
                        break
                    yield StreamingRecognizeRequest(audio=data)
        finally:
            os.remove(temp_wav)

    def transcribe(self, audio_path: str = None, audio_data: bytes = None, **kwargs) -> str:
        requests = self._stream_generator(audio_path=audio_path, audio_data=audio_data)

        responses = self.client.streaming_recognize(requests=requests)

        transcripts = []
        for response in responses:
            for result in response.results:
                if result.is_final and result.alternatives:
                    transcripts.append(result.alternatives[0].transcript)

        return " ".join(transcripts)

    async def transcribe_async(self, audio_path: str, **kwargs) -> str:
        # For Google Speech v2, the asyncio equivalent would be to run the sync stream in a thread
        # since python standard google speech clients are primarily synchronous generators,
        # or use their async API if available. To ensure reliability, we run the blocking generator
        # and streaming call in a thread pool.
        return await asyncio.to_thread(self.transcribe, audio_path, **kwargs)
