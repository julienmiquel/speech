"""
Logic for reviewing actor recordings using Gemini.
"""
import logging
from google.genai import types
from api.config import vertex_client

REVIEWER_PROMPT = """
You are an expert voice director reviewing an actor's performance.
Listen to the audio recording and evaluate how well the actor followed the target style prompt.

Target Style Prompt:
{prompt_used}

Please provide a review in the following format:
1. **Overall Score**: X/5
2. **Key Metrics**:
   - Pacing: X/5 (Comment on speed and rhythm)
   - Emotion: X/5 (Comment on tone and feeling)
   - Pronunciation: X/5 (Comment on clarity and correctness)
3. **Constructive Feedback**: What worked well and what could be improved.
"""

def review_recording(audio_bytes: bytes, prompt_used: str, mime_type: str = "audio/wav") -> str:
    """
    Reviews an audio recording against a target prompt using gemini-2.5-flash.
    """
    if not vertex_client:
        logging.error("Vertex AI client not initialized.")
        return "Error: Client not initialized."

    try:
        response = vertex_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                types.Part.from_bytes(data=audio_bytes, mime_type=mime_type),
                REVIEWER_PROMPT.format(prompt_used=prompt_used)
            ]
        )
        return response.text
    except Exception as e:
        logging.error(f"Error during audio review: {e}")
        return f"Error during review: {e}"
