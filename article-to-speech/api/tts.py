import os
import wave
import io
import re
import logging
import base64
from abc import ABC, abstractmethod
from google.cloud import texttospeech
from google import genai
from google.genai import types
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception

from prompts import PROMPT_ANCHOR, PROMPT_REPORTER
from api.config import (
    vertex_client, DEFAULT_MODEL_SYNTH, DEFAULT_VOICE_MAIN, DEFAULT_VOICE_SIDEBAR
)
from api.scraper import _generate_content_with_retry
from api.dictionary import (
    load_pronunciation_dictionary, prepare_tts_dictionaries, 
    apply_pronunciation_dictionary, save_pronunciation_dictionary
)
from api.utils import split_text_into_chunks

class TTSProvider(ABC):
    @abstractmethod
    def synthesize_multi_speaker(self, dialogue, model=None, voice_main=None, voice_sidebar=None, output_file="output_multi.wav", strict_mode=False, prompt_main=PROMPT_ANCHOR, prompt_sidebar=PROMPT_REPORTER, seed=None, temperature=None, apply_dictionary=True, delay_seconds=0, language="fr-FR", progress_callback=None):
        pass

    @abstractmethod
    def synthesize_and_save(self, text, model=None, voice=None, output_file="output.wav", apply_dictionary=True, system_instruction=None, language="fr-FR", progress_callback=None):
        pass

    @abstractmethod
    def synthesize_replicated_voice(self, text, reference_audio_bytes, project_id, location="us-central1", output_file="output_cloned.wav", apply_dictionary=True, language="fr-FR"):
        pass

class VertexTTSProvider(TTSProvider):
    def synthesize_multi_speaker(self, dialogue, model=None, voice_main=None, voice_sidebar=None, output_file="output_multi.wav", strict_mode=False, prompt_main=PROMPT_ANCHOR, prompt_sidebar=PROMPT_REPORTER, seed=None, temperature=None, apply_dictionary=True, delay_seconds=0, language="fr-FR", progress_callback=None):
        if model is None: model = DEFAULT_MODEL_SYNTH
        if voice_main is None: voice_main = DEFAULT_VOICE_MAIN
        if voice_sidebar is None: voice_sidebar = DEFAULT_VOICE_SIDEBAR
        
        if not vertex_client:
            return None, {"state": "error", "details": "Client not initialized"}, {}
            
        pseudo_dict = {}
        if apply_dictionary:
            p_dict = load_pronunciation_dictionary()
            pseudo_dict, _, _ = prepare_tts_dictionaries(p_dict, provider_type="vertexai")
        
        combined_audio = b""
        generation_status = {"state": "completed", "details": "All segments finished normally"}
        
        combined_usage = {
            "prompt_token_count": 0, "candidates_token_count": 0, "total_token_count": 0
        }

        for i, seg in enumerate(dialogue):
            text = apply_pronunciation_dictionary(seg["text"], pseudo_dict) if apply_dictionary else seg["text"]
            speaker = seg["speaker"]
            voice = voice_main if speaker == "R" else voice_sidebar
            
            if not text.strip():
                continue
                
            prompt_instruction = seg.get("prompt")
            if not prompt_instruction:
                 if speaker == "R": 
                     prompt_instruction = prompt_main
                 else: 
                     prompt_instruction = prompt_sidebar
            
            if strict_mode:
                prompt_instruction += " Read the text EXACTLY as written, word for word. Do not add or remove anything."

            try:
                config_params = {
                    "response_modalities": ["AUDIO"],
                    "speech_config": types.SpeechConfig(
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                voice_name=voice
                            )
                        ),
                        language_code=language
                    )
                }
                
                if seed is not None:
                    config_params["seed"] = seed
                    
                if temperature is not None:
                    config_params["temperature"] = temperature

                response = _generate_content_with_retry(
                    model=model,
                    contents=f"{prompt_instruction} Text to read: {text}",
                    config=types.GenerateContentConfig(**config_params)
                )
                
                if response.usage_metadata:
                    combined_usage["prompt_token_count"] += response.usage_metadata.prompt_token_count
                    combined_usage["candidates_token_count"] += response.usage_metadata.candidates_token_count
                    combined_usage["total_token_count"] += response.usage_metadata.total_token_count
                
                if response.candidates:
                    candidate = response.candidates[0]
                    if candidate.finish_reason != "STOP":
                        generation_status["state"] = "truncated"
                        generation_status["details"] = f"Segment {i} truncated. Reason: {candidate.finish_reason}"
                    
                    if candidate.content and candidate.content.parts:
                        for part in candidate.content.parts:
                            if part.inline_data:
                                with wave.open(io.BytesIO(part.inline_data.data), 'rb') as w:
                                    combined_audio += w.readframes(w.getnframes())
                    
                    if delay_seconds > 0 and i < len(dialogue) - 1:
                        silence_bytes = b'\x00' * int(delay_seconds * 48000)
                        combined_audio += silence_bytes
            except Exception as e:
                logging.error(f"Error generating audio for segment {i}: {e}")
                generation_status["state"] = "error"
                generation_status["details"] = str(e)
                
        if combined_audio:
             with wave.open(output_file, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(24000)
                wf.writeframes(combined_audio)
             return output_file, generation_status, combined_usage
             
        return None, generation_status, combined_usage

    def synthesize_and_save(self, text, model=None, voice=None, output_file="output.wav", apply_dictionary=True, system_instruction=None, language="fr-FR", progress_callback=None):
        if model is None: model = DEFAULT_MODEL_SYNTH
        if voice is None: voice = DEFAULT_VOICE_MAIN
        
        if not vertex_client:
            return None, {"state": "error", "details": "Client not initialized"}, {}
            
        if apply_dictionary:
            p_dict = load_pronunciation_dictionary()
            pseudo_dict, _, _ = prepare_tts_dictionaries(p_dict, provider_type="vertexai")
            text = apply_pronunciation_dictionary(text, pseudo_dict)
        
        text_chunks = split_text_into_chunks(text, max_len=3500)
        usage = {"prompt_token_count": 0, "candidates_token_count": 0, "total_token_count": 0}
        combined_audio_frames = b""
        
        try:
            for idx, chunk in enumerate(text_chunks):
                parts = []
                if system_instruction:
                    parts.append(f"Context: {system_instruction}\n\nTask: Read this text naturally.")
                else:
                     parts.append("Please read this text out loud naturally:")
                parts.append(chunk)

                response = _generate_content_with_retry(
                    model=model,
                    contents=parts,
                    config=types.GenerateContentConfig(
                        response_modalities=["AUDIO"],
                        speech_config=types.SpeechConfig(
                            voice_config=types.VoiceConfig(
                                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                    voice_name=voice
                                )
                            ),
                            language_code=language
                        )
                    )
                )

                if response.candidates and response.candidates[0].content.parts:
                     for part in response.candidates[0].content.parts:
                        if part.inline_data:
                            with wave.open(io.BytesIO(part.inline_data.data), 'rb') as w:
                                combined_audio_frames += w.readframes(w.getnframes())
                            
                     if response.usage_metadata:
                         usage["prompt_token_count"] += response.usage_metadata.prompt_token_count
                         usage["candidates_token_count"] += response.usage_metadata.candidates_token_count
                         usage["total_token_count"] += response.usage_metadata.total_token_count
                         
            if combined_audio_frames:
                with wave.open(output_file, "wb") as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(24000)
                    wf.writeframes(combined_audio_frames)
                return output_file, {"state": "completed"}, usage
            return None, {"state": "error", "details": "No audio content"}, usage
        except Exception as e:
            return None, {"state": "error", "details": str(e)}, usage

    def synthesize_replicated_voice(self, text, reference_audio_bytes, project_id, location="us-central1", output_file="output_cloned.wav", apply_dictionary=True, language="fr-FR"):
        try:
            if apply_dictionary:
                text = apply_pronunciation_dictionary(text)
            
            encoded_audio = base64.b64encode(reference_audio_bytes).decode("utf-8")
            local_client = genai.Client(vertexai=True, project=project_id, location=location)

            response = local_client.models.generate_content(
                model="gemini-2.5-flash-tts-eap-11-2025",
                contents=f"Say the following: {text}",
                config=types.GenerateContentConfig(
                    speech_config=types.SpeechConfig(
                        voice_config=types.VoiceConfig(
                            replicated_voice_config=types.ReplicatedVoiceConfig(
                                voice_sample_audio=encoded_audio
                            )
                        ),
                        language_code=language
                    ),
                    response_modalities=["AUDIO"],
                ),
            )

            if not response.candidates or not response.candidates[0].content.parts:
                 raise ValueError("No audio content generated.")

            audio_data = response.candidates[0].content.parts[0].inline_data.data
            
            with wave.open(output_file, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(24000)
                wf.writeframes(audio_data)
            
            usage = {
                "prompt_token_count": response.usage_metadata.prompt_token_count,
                "candidates_token_count": response.usage_metadata.candidates_token_count,
                "total_token_count": response.usage_metadata.total_token_count
            } if response.usage_metadata else {}

            return output_file, {"state": "completed"}, usage

        except Exception as e:
            return None, {"state": "error", "details": str(e)}, {}

class CloudTTSProvider(TTSProvider):
    def synthesize_multi_speaker(self, dialogue, model=None, voice_main=None, voice_sidebar=None, output_file="output_multi.wav", strict_mode=False, prompt_main=PROMPT_ANCHOR, prompt_sidebar=PROMPT_REPORTER, seed=None, temperature=None, apply_dictionary=True, delay_seconds=0, language="fr-FR", progress_callback=None):
        if model is None: model = DEFAULT_MODEL_SYNTH
        if voice_main is None: voice_main = DEFAULT_VOICE_MAIN
        if voice_sidebar is None: voice_sidebar = DEFAULT_VOICE_SIDEBAR
        
        try:
            client_cloud = texttospeech.TextToSpeechClient()
        except NameError:
            return None, {"state": "error", "details": "Dependency missing"}, {}
            
        custom_pronunciations = None
        pseudo_dict = {}
        applied_ipa = {}
        if apply_dictionary:
            p_dict = load_pronunciation_dictionary()
            pseudo_dict, ipa_params, applied_ipa = prepare_tts_dictionaries(p_dict, provider_type="cloudtts")
            
            if ipa_params:
                custom_pronunciations = texttospeech.CustomPronunciations(
                    pronunciations=ipa_params
                )

        prompt_instruction = prompt_main if dialogue and dialogue[0].get("speaker") == "R" else PROMPT_ANCHOR
        if strict_mode:
            prompt_instruction += " Read the text EXACTLY as written, word for word. Do not add or remove anything."
            
        is_flash_lite = ("flash-lite" in model.lower())
        if is_flash_lite and len(prompt_instruction.encode('utf-8')) > 200:
            prompt_instruction = "Read this text naturally."
            
        prompt_bytes = len(prompt_instruction.encode('utf-8'))
        max_batch_bytes = (480 if is_flash_lite else 3800) - prompt_bytes
        
        batches = []
        current_batch = []
        current_bytes = 0
        
        for i, seg in enumerate(dialogue):
            text = seg["text"]
            if pseudo_dict:
                text = apply_pronunciation_dictionary(text, pseudo_dict)
                
            speaker = seg["speaker"]
            if not text.strip(): continue
            
            alias = "Speaker1" if speaker == "R" else "Speaker2"
            
            safe_chunk_char_limit = int(max_batch_bytes / 2.5)
            for chunk in split_text_into_chunks(text, max_len=safe_chunk_char_limit):
                chunk_bytes = len(chunk.encode('utf-8'))
                if chunk_bytes > max_batch_bytes:
                    chunk = chunk[:int(max_batch_bytes/3)]
                    chunk_bytes = len(chunk.encode('utf-8'))
                
                if current_bytes + chunk_bytes > max_batch_bytes and current_batch:
                    batches.append(current_batch)
                    current_batch = []
                    current_bytes = 0
                    
                current_batch.append(texttospeech.MultiSpeakerMarkup.Turn(text=chunk, speaker=alias))
                current_bytes += chunk_bytes
                
        if current_batch:
            batches.append(current_batch)
            
        multi_speaker_voice_config = texttospeech.MultiSpeakerVoiceConfig(
            speaker_voice_configs=[
                texttospeech.MultispeakerPrebuiltVoice(speaker_alias="Speaker1", speaker_id=voice_main),
                texttospeech.MultispeakerPrebuiltVoice(speaker_alias="Speaker2", speaker_id=voice_sidebar),
            ]
        )
        
        voice = texttospeech.VoiceSelectionParams(
            language_code=language, model_name=model, multi_speaker_voice_config=multi_speaker_voice_config,
        )
        audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.LINEAR16, sample_rate_hertz=24000)
        
        combined_audio_frames = b""
        usage = {"prompt_token_count": 0, "candidates_token_count": 0, "total_token_count": 0}
        
        try:
            def should_retry_cloud_tts(exception):
                error_str = str(exception).lower()
                if "custom pronunciation phrases are invalid" in error_str: return False
                if "400 " in error_str and "sensitive" not in error_str: return False
                return True
                
            @retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=2, min=2, max=30), retry=retry_if_exception(should_retry_cloud_tts), reraise=True)
            def _synthesize_batch(s_input, v, a_config):
                return client_cloud.synthesize_speech(input=s_input, voice=v, audio_config=a_config)

            for b_idx, batch in enumerate(batches):
                synthesis_input = texttospeech.SynthesisInput(
                    multi_speaker_markup=texttospeech.MultiSpeakerMarkup(turns=batch),
                    prompt=prompt_instruction if "gemini" in model.lower() else None,
                    custom_pronunciations=custom_pronunciations
                )
                
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        response = _synthesize_batch(synthesis_input, voice, audio_config)
                        break
                    except Exception as e:
                        error_str = str(e)
                        match = re.search(r"custom pronunciation phrases are invalid:\s+(.*?)(?:\. Please|$)", error_str)
                        if match and custom_pronunciations and attempt < max_retries - 1:
                            invalid_phrases_raw = match.group(1)
                            invalid_phrases = [p.strip() for p in invalid_phrases_raw.split(',')]
                            new_pronunciations = [p for p in custom_pronunciations.pronunciations if p.phrase not in invalid_phrases]
                            
                            if apply_dictionary:
                                p_dict = load_pronunciation_dictionary()
                                updated = False
                                for bad_phrase in invalid_phrases:
                                    if bad_phrase in p_dict:
                                        del p_dict[bad_phrase]
                                        updated = True
                                if updated:
                                    save_pronunciation_dictionary(p_dict)
                            
                            if new_pronunciations:
                                custom_pronunciations = texttospeech.CustomPronunciations(pronunciations=new_pronunciations)
                                synthesis_input.custom_pronunciations = custom_pronunciations
                            else:
                                custom_pronunciations = None
                                synthesis_input = texttospeech.SynthesisInput(
                                    multi_speaker_markup=texttospeech.MultiSpeakerMarkup(turns=batch),
                                    prompt=prompt_instruction if "gemini" in model.lower() else None
                                )
                        else:
                            raise e
                
                with wave.open(io.BytesIO(response.audio_content), 'rb') as w:
                    combined_audio_frames += w.readframes(w.getnframes())
                
                if progress_callback:
                    progress_callback(b_idx + 1, len(batches), response.audio_content)
                
                if delay_seconds > 0 and b_idx < len(batches) - 1:
                    combined_audio_frames += b'\x00' * int(delay_seconds * 48000)
                    
            if combined_audio_frames:
                with wave.open(output_file, "wb") as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(24000)
                    wf.writeframes(combined_audio_frames)
            return output_file, {"state": "completed", "applied_ipa_phonemes": applied_ipa}, usage
        except Exception as e:
             return None, {"state": "error", "details": str(e)}, usage

    def synthesize_and_save(self, text, model=None, voice=None, output_file="output.wav", apply_dictionary=True, system_instruction=None, language="fr-FR", progress_callback=None):
        if model is None: model = DEFAULT_MODEL_SYNTH
        if voice is None: voice = DEFAULT_VOICE_MAIN
        
        try:
            client_cloud = texttospeech.TextToSpeechClient()
        except NameError:
            return None, {"state": "error", "details": "Dependency missing"}, {}
            
        custom_pronunciations = None
        pseudo_dict = {}
        applied_ipa = {}
        if apply_dictionary:
            p_dict = load_pronunciation_dictionary()
            pseudo_dict, ipa_params, applied_ipa = prepare_tts_dictionaries(p_dict, provider_type="cloudtts")
            if ipa_params:
                custom_pronunciations = texttospeech.CustomPronunciations(pronunciations=ipa_params)
    
        prompt_instruction = ""
        if system_instruction:
            prompt_instruction = f"Context: {system_instruction}\n\nTask: Read this text naturally."
        else:
            prompt_instruction = "Please read this text out loud naturally:"
            
        if pseudo_dict:
            text = apply_pronunciation_dictionary(text, pseudo_dict)
            
        is_flash_lite = ("flash-lite" in model.lower())
        if is_flash_lite and len(prompt_instruction.encode('utf-8')) > 200:
            prompt_instruction = "Read this text naturally."
            
        prompt_bytes = len(prompt_instruction.encode('utf-8'))
        max_batch_bytes = (480 if is_flash_lite else 3800) - prompt_bytes
        safe_chunk_char_limit = max(int(max_batch_bytes / 2.5), 50)
        
        text_chunks = split_text_into_chunks(text, safe_chunk_char_limit)
        
        voice_params = texttospeech.VoiceSelectionParams(language_code=language, name=voice, model_name=model)
        audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.LINEAR16, sample_rate_hertz=24000)
        
        usage = {"prompt_token_count": 0, "candidates_token_count": 0, "total_token_count": 0}
        combined_audio_frames = b""
        
        try:
            def should_retry_cloud_tts_single(exception):
                error_str = str(exception).lower()
                if "custom pronunciation phrases are invalid" in error_str: return False
                if "400 " in error_str and "sensitive" not in error_str: return False
                return True
                
            @retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=2, min=2, max=30), retry=retry_if_exception(should_retry_cloud_tts_single), reraise=True)
            def _synthesize_single_chunk(s_input, v, a_config):
                return client_cloud.synthesize_speech(input=s_input, voice=v, audio_config=a_config)

            for idx, chunk in enumerate(text_chunks):
                synthesis_input = texttospeech.SynthesisInput(text=chunk, prompt=prompt_instruction if system_instruction else None, custom_pronunciations=custom_pronunciations)
                
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        response = _synthesize_single_chunk(synthesis_input, voice_params, audio_config)
                        break
                    except Exception as e:
                        error_str = str(e)
                        match = re.search(r"custom pronunciation phrases are invalid:\s+(.*?)(?:\. Please|$)", error_str)
                        if match and custom_pronunciations and attempt < max_retries - 1:
                            invalid_phrases_raw = match.group(1)
                            invalid_phrases = [p.strip() for p in invalid_phrases_raw.split(',')]
                            new_pronunciations = [p for p in custom_pronunciations.pronunciations if p.phrase not in invalid_phrases]
                            
                            if apply_dictionary:
                                p_dict = load_pronunciation_dictionary()
                                updated = False
                                for bad_phrase in invalid_phrases:
                                    if bad_phrase in p_dict:
                                        del p_dict[bad_phrase]
                                        updated = True
                                if updated:
                                    save_pronunciation_dictionary(p_dict)
                            
                            if new_pronunciations:
                                custom_pronunciations = texttospeech.CustomPronunciations(pronunciations=new_pronunciations)
                                synthesis_input.custom_pronunciations = custom_pronunciations
                            else:
                                custom_pronunciations = None
                                synthesis_input.custom_pronunciations = None
                        else:
                            raise e
                with wave.open(io.BytesIO(response.audio_content), 'rb') as w:
                    combined_audio_frames += w.readframes(w.getnframes())
                    
                if progress_callback:
                    progress_callback(idx + 1, len(text_chunks), response.audio_content)

            if combined_audio_frames:
                with wave.open(output_file, "wb") as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(24000)
                    wf.writeframes(combined_audio_frames)
                    
            return output_file, {"state": "completed", "applied_ipa_phonemes": applied_ipa}, usage
        except Exception as e:
             return None, {"state": "error", "details": str(e)}, usage

    def synthesize_replicated_voice(self, text, reference_audio_bytes, project_id, location="us-central1", output_file="output_cloned.wav", apply_dictionary=True, language="fr-FR"):
        fallback_provider = VertexTTSProvider()
        return fallback_provider.synthesize_replicated_voice(
            text, reference_audio_bytes, project_id, location, output_file, apply_dictionary, language
        )

class TTSFactory:
    @staticmethod
    def get_provider() -> TTSProvider:
        provider_type = os.getenv("TTS_PROVIDER", "cloudtts").lower()
        if provider_type == "cloudtts":
            return CloudTTSProvider()
        elif provider_type == "vertexai":
            return VertexTTSProvider()
        else:
            return None

def synthesize_multi_speaker(dialogue, model=None, voice_main=None, voice_sidebar=None, output_file="output_multi.wav", strict_mode=False, prompt_main=PROMPT_ANCHOR, prompt_sidebar=PROMPT_REPORTER, seed=None, temperature=None, apply_dictionary=True, delay_seconds=0, language="fr-FR", progress_callback=None):
    return TTSFactory.get_provider().synthesize_multi_speaker(dialogue, model, voice_main, voice_sidebar, output_file, strict_mode, prompt_main, prompt_sidebar, seed, temperature, apply_dictionary, delay_seconds, language, progress_callback)

def synthesize_and_save(text, model=None, voice=None, output_file="output.wav", apply_dictionary=True, system_instruction=None, language="fr-FR", progress_callback=None):
    return TTSFactory.get_provider().synthesize_and_save(text, model, voice, output_file, apply_dictionary, system_instruction, language, progress_callback)

def synthesize_replicated_voice(text, reference_audio_bytes, project_id, location="us-central1", output_file="output_cloned.wav", apply_dictionary=True, language="fr-FR"):
    return TTSFactory.get_provider().synthesize_replicated_voice(text, reference_audio_bytes, project_id, location, output_file, apply_dictionary, language)
