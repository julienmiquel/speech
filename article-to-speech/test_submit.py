import sys
import logging
logging.basicConfig(level=logging.DEBUG)

from job_manager import manager
from async_helpers import async_single_voice

dialogue = [{"text": "Hello world", "speaker": "R"}]

job_id = manager.submit_job(
    async_single_voice,
    dialogue,
    "gemini-2.5-pro-tts",
    "Aoede",
    False,
    "Prompt",
    "en-US",
    "test_out.wav"
)

import time
while manager.get_job(job_id)["status"] == "running":
    time.sleep(0.5)

print(manager.get_job(job_id))
