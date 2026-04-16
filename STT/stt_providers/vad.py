import wave
import contextlib
import webrtcvad
from typing import List, Tuple
from pydub import AudioSegment
import io
import os



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

def extract_speech_segments(audio_path: str = None, audio_data: bytes = None, aggressiveness: int = 3) -> List[Tuple[int, int]]:
    """
    Uses WebRTCVAD to extract speech segments from an audio file or data.
    Returns a list of tuples (start_ms, end_ms) representing speech segments.
    """
    # Load audio
    if audio_path:
        sound = AudioSegment.from_file(audio_path)
    elif audio_data:
        import io
        sound = AudioSegment.from_file(io.BytesIO(audio_data), format="wav")
    else:
        raise ValueError("Either audio_path or audio_data must be provided.")

    # Webrtc VAD requires mono and 16000Hz (or 8, 32, 48)
    vad_sound = sound.set_channels(1).set_frame_rate(16000).set_sample_width(2)

    audio = vad_sound.raw_data
    sample_rate = vad_sound.frame_rate
    vad = webrtcvad.Vad(aggressiveness)

    frames = frame_generator(30, audio, sample_rate)
    frames = list(frames)

    segments = list(vad_collector(sample_rate, 30, 300, vad, frames))

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

def chunk_audio_with_vad(audio_path: str = None, audio_data: bytes = None, aggressiveness: int = 3) -> List[bytes]:
    """
    Returns a list of raw audio bytes (wav format) for each voiced chunk.
    """
    if audio_path:
        sound = AudioSegment.from_file(audio_path)
    elif audio_data:
        sound = AudioSegment.from_file(io.BytesIO(audio_data), format="wav")
    else:
        raise ValueError("Either audio_path or audio_data must be provided.")
        
    segments = extract_speech_segments(audio_path=audio_path, audio_data=audio_data, aggressiveness=aggressiveness)

    chunks = []
    for start, end in segments:
        chunk_audio = sound[start:end]
        buf = io.BytesIO()
        chunk_audio.export(buf, format="wav")
        chunks.append(buf.getvalue())

    return chunks
