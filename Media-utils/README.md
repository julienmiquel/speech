# Media Utils

Collection of utilities for processing audio and video files.

## Features

*   **Audio to Video Conversion**: Transforms an audio file (MP3) into a video file (MP4) with a static background (e.g., white). Useful for uploading audios to video platforms or for using APIs that require a video stream.
*   **MP3 to WAV Conversion**: Converts MP3 files to WAV format (16kHz or mono) for processing by ASR (Speech-to-Text) models.

## Content

*   `audio-to-video.ipynb`: Jupyter notebook containing conversion scripts using `moviepy` and `pydub`.

## Prerequisites

*   Python 3
*   Libraries: `moviepy`, `pydub`, `ffmpeg-python`

## Installation

```bash
pip install moviepy pydub ffmpeg-python
```

(Also requires FFmpeg to be installed on the system).
