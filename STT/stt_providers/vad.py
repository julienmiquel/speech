import wave
import contextlib
import webrtcvad
from typing import List, Tuple
from pydub import AudioSegment
import io
import os

def read_wave(path: str):
    """Reads a .wav file.
    Takes the path, and returns (PCM audio data, sample rate).
    """
    with contextlib.closing(wave.open(path, 'rb')) as wf:
        num_channels = wf.getnchannels()
        assert num_channels == 1, "WebRTC VAD requires mono audio."
        sample_width = wf.getsampwidth()
        assert sample_width == 2, "WebRTC VAD requires 16-bit audio."
        sample_rate = wf.getframerate()
        assert sample_rate in (8000, 16000, 32000, 48000), "WebRTC VAD requires 8kHz, 16kHz, 32kHz, or 48kHz."
        pcm_data = wf.readframes(wf.getnframes())
        return pcm_data, sample_rate

class Frame:
    """Represents a "frame" of audio data."""
    def __init__(self, bytes, timestamp, duration):
        self.bytes = bytes
        self.timestamp = timestamp
        self.duration = duration

def frame_generator(frame_duration_ms, audio, sample_rate):
    """Generates audio frames from PCM audio data.
    Takes the desired frame duration in milliseconds, the PCM data, and
    the sample rate.
    Yields Frames of the requested duration.
    """
    n = int(sample_rate * (frame_duration_ms / 1000.0) * 2)
    offset = 0
    timestamp = 0.0
    duration = (float(n) / sample_rate) / 2.0
    while offset + n <= len(audio):
        yield Frame(audio[offset:offset + n], timestamp, duration)
        timestamp += duration
        offset += n

def vad_collector(sample_rate, frame_duration_ms, padding_duration_ms, vad, frames):
    """Filters out non-voiced audio frames.
    Given a webrtcvad.Vad and a source of audio frames, yields only
    the voiced audio.
    Uses a padded, sliding window algorithm over the audio frames.
    """
    import collections
    num_padding_frames = int(padding_duration_ms / frame_duration_ms)
    ring_buffer = collections.deque(maxlen=num_padding_frames)
    triggered = False

    voiced_frames = []

    start_timestamp = 0.0

    for frame in frames:
        is_speech = vad.is_speech(frame.bytes, sample_rate)

        if not triggered:
            ring_buffer.append((frame, is_speech))
            num_voiced = len([f for f, speech in ring_buffer if speech])
            if num_voiced > 0.9 * ring_buffer.maxlen:
                triggered = True
                start_timestamp = ring_buffer[0][0].timestamp
                for f, s in ring_buffer:
                    voiced_frames.append(f)
                ring_buffer.clear()
        else:
            voiced_frames.append(frame)
            ring_buffer.append((frame, is_speech))
            num_unvoiced = len([f for f, speech in ring_buffer if not speech])
            if num_unvoiced > 0.9 * ring_buffer.maxlen:
                triggered = False
                end_timestamp = frame.timestamp + frame.duration
                yield (start_timestamp, end_timestamp)
                ring_buffer.clear()
                voiced_frames = []

    if triggered:
        yield (start_timestamp, frame.timestamp + frame.duration)

def extract_speech_segments(audio_path: str, aggressiveness: int = 3) -> List[Tuple[int, int]]:
    """
    Uses WebRTCVAD to extract speech segments from an audio file.
    Returns a list of tuples (start_ms, end_ms) representing speech segments.
    """
    # Load audio, ensure it's mono 16kHz for VAD
    sound = AudioSegment.from_file(audio_path)

    import tempfile

    # Webrtc VAD requires mono and 16000Hz (or 8, 32, 48)
    vad_sound = sound.set_channels(1).set_frame_rate(16000).set_sample_width(2)

    # Use a secure temporary file
    fd, temp_wav = tempfile.mkstemp(suffix=".wav")
    os.close(fd)

    try:
        vad_sound.export(temp_wav, format="wav")
        audio, sample_rate = read_wave(temp_wav)
        vad = webrtcvad.Vad(aggressiveness)

        frames = frame_generator(30, audio, sample_rate)
        frames = list(frames)

        segments = list(vad_collector(sample_rate, 30, 300, vad, frames))
    finally:
        os.remove(temp_wav)

    # Convert seconds to ms
    segments_ms = [(int(start * 1000), int(end * 1000)) for start, end in segments]

    # Merge segments that are too close (e.g. less than 500ms apart)
    if not segments_ms:
        return [(0, len(sound))]

    merged = [segments_ms[0]]
    for start, end in segments_ms[1:]:
        prev_start, prev_end = merged[-1]
        if start - prev_end < 500: # Merge if gap is small
            merged[-1] = (prev_start, end)
        else:
            merged.append((start, end))

    # Chunking limits to around 55s to avoid hitting Google Speech API limits
    final_chunks = []
    MAX_CHUNK_DURATION = 55000

    for start, end in merged:
        if end - start > MAX_CHUNK_DURATION:
            # Sub-divide
            cur = start
            while cur < end:
                nxt = min(cur + MAX_CHUNK_DURATION, end)
                final_chunks.append((cur, nxt))
                cur = nxt
        else:
            final_chunks.append((start, end))

    return final_chunks

def chunk_audio_with_vad(audio_path: str, aggressiveness: int = 3) -> List[bytes]:
    """
    Returns a list of raw audio bytes (wav format) for each voiced chunk.
    """
    sound = AudioSegment.from_file(audio_path)
    segments = extract_speech_segments(audio_path, aggressiveness)

    chunks = []
    for start, end in segments:
        chunk_audio = sound[start:end]
        buf = io.BytesIO()
        chunk_audio.export(buf, format="wav")
        chunks.append(buf.getvalue())

    return chunks
