from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class BaseSTTProvider(ABC):
    """
    Abstract base class for Speech-to-Text providers.
    Enforces a standardized Strategy Pattern for STT processing.
    """

    @abstractmethod
    def transcribe(self, audio_path: str, **kwargs) -> str:
        """
        Synchronously transcribes the given audio file.

        Args:
            audio_path (str): The path to the audio file.
            **kwargs: Additional provider-specific parameters.

        Returns:
            str: The transcribed text.
        """
        pass

    @abstractmethod
    async def transcribe_async(self, audio_path: str, **kwargs) -> str:
        """
        Asynchronously transcribes the given audio file, potentially
        using parallel processing for chunks if not natively streaming.

        Args:
            audio_path (str): The path to the audio file.
            **kwargs: Additional provider-specific parameters.

        Returns:
            str: The transcribed text.
        """
        pass
