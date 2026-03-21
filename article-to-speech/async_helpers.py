import time
import logging
from gemini_url_to_audio import (
    get_cached_text, save_to_cache, extract_text_from_url_with_gemini,
    extract_text_from_url, research_pronunciations, update_pronunciation_dictionary,
    parse_text_structure, synthesize_multi_speaker, synthesize_and_save
)

def async_automation(updater, manual_text_input, text_content, source_option, url, extraction_method, model_parse, language, strict_mode, preset_system_prompt, opt_manual, opt_url, opt_rss):
    result = {
        "text_content": text_content,
        "pronunciation_guides": None,
        "dialogue": None,
        "added_dict": 0,
        "total_usage": {"prompt_token_count": 0, "candidates_token_count": 0, "total_token_count": 0},
        "truncated": False
    }
    
    def add_usage(u):
        if u:
            for k in result["total_usage"]: result["total_usage"][k] += u.get(k, 0)

    # 1. Extraction
    updater(0.1, "1. Préparation du texte...")
    if source_option == opt_manual:
        if manual_text_input and manual_text_input.strip() != (text_content or "").strip():
            result["text_content"] = manual_text_input
    elif not text_content and source_option in [opt_url, opt_rss]:
        cached_text = get_cached_text(url)
        if cached_text:
            result["text_content"] = cached_text
        else:
            if "gemini" in extraction_method.lower():
                text, u, is_truncated = extract_text_from_url_with_gemini(url, parsing_model=model_parse)
                add_usage(u)
                if not text:
                    text = extract_text_from_url(url)
                if is_truncated: result["truncated"] = True
            else:
                text = extract_text_from_url(url)
            if text:
                result["text_content"] = text
                save_to_cache(url, text)

    if result["text_content"]:
        # 2. Pronunciation
        updater(0.4, "2. Recherche de prononciation...")
        guides, u = research_pronunciations(result["text_content"], model=model_parse, language=language)
        add_usage(u)
        if guides:
            result["pronunciation_guides"] = guides
            added = update_pronunciation_dictionary(guides)
            result["added_dict"] = added
        
        # 3. Structuration
        updater(0.7, "3. Analyse de la structure...")
        dialogue, u, is_truncated = parse_text_structure(result["text_content"], model=model_parse, strict_mode=strict_mode, system_prompt=preset_system_prompt)
        add_usage(u)
        if is_truncated: result["truncated"] = True
        if dialogue:
            result["dialogue"] = dialogue

    updater(1.0, "Automatisation terminée !")
    return result

def async_dual_voice(updater, dialogue, model_synth, voice_main, voice_sidebar, strict_mode, prompt_main, prompt_sidebar, seed, temperature, apply_dictionary, delay_seconds, language, outfile_name):
    def progress_cb(current, total, audio_bytes=None):
        pct = current / total if total > 0 else 0
        updater(pct, f"Synthèse vocale (Lot {current}/{total})...")

    start_time = time.time()
    outfile, status, usage = synthesize_multi_speaker(
        dialogue, 
        model=model_synth, 
        voice_main=voice_main, 
        voice_sidebar=voice_sidebar,
        output_file=outfile_name,
        strict_mode=strict_mode,
        prompt_main=prompt_main,
        prompt_sidebar=prompt_sidebar,
        seed=seed,
        temperature=temperature,
        apply_dictionary=apply_dictionary,
        delay_seconds=delay_seconds,
        language=language,
        progress_callback=progress_cb
    )
    duration = time.time() - start_time
    return {
        "outfile": outfile, "status": status, "usage": usage, "duration": duration
    }

def async_single_voice(updater, dialogue, model_synth, voice_main, apply_dictionary, prompt_main, language, outfile_name):
    def progress_cb(current, total, audio_bytes=None):
        pct = current / total if total > 0 else 0
        updater(pct, f"Synthèse vocale (Lot {current}/{total})...")

    start_time = time.time()
    text_to_read = "\n\n".join([d["text"] for d in dialogue])
    outfile, status, usage = synthesize_and_save(
        text=text_to_read,
        model=model_synth,
        voice=voice_main,
        output_file=outfile_name,
        apply_dictionary=apply_dictionary,
        system_instruction=prompt_main,
        language=language,
        progress_callback=progress_cb
    )
    duration = time.time() - start_time
    return {
        "outfile": outfile, "status": status, "usage": usage, "duration": duration
    }
