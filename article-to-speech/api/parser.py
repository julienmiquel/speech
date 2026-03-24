import json
import logging
import re
from google.genai import types
from api.config import vertex_client, DEFAULT_MODEL_PARSE
from api.scraper import _generate_content_with_retry
from prompts import (
    SYSTEM_PROMPT_STANDARD, PARSING_INSTRUCTIONS_ENRICHED,
    PARSING_INSTRUCTIONS_STRICT, RESEARCH_PRONUNCIATION_PROMPT
)

def intelligent_chunk(text: str, max_length: int = 4000):
    if len(text) <= max_length:
        return [text]

    chunks = []
    def split_and_accumulate(current_text, delimiter):
        parts = current_text.split(delimiter)
        accumulated = []
        current_chunk = ""
        for part in parts:
            if len(part) > max_length:
                if current_chunk:
                    accumulated.append(current_chunk.strip())
                    current_chunk = ""
                accumulated.extend([p for p in [part] if p.strip()]) 
            else:
                candidate = current_chunk + (delimiter if current_chunk else "") + part
                if len(candidate) <= max_length:
                    current_chunk = candidate
                else:
                    if current_chunk:
                        accumulated.append(current_chunk.strip())
                    current_chunk = part
        if current_chunk:
            accumulated.append(current_chunk.strip())
        return accumulated

    paragraph_chunks = split_and_accumulate(text, "\n\n")
    line_chunks = []
    for pc in paragraph_chunks:
        if len(pc) > max_length:
            line_chunks.extend(split_and_accumulate(pc, "\n"))
        else:
            line_chunks.append(pc)
            
    final_chunks = []
    for lc in line_chunks:
        if len(lc) > max_length:
            sentence_chunks = split_and_accumulate(lc.replace(". ", ".|~|"), "|~|")
            for sc in sentence_chunks:
                if len(sc) > max_length:
                    for i in range(0, len(sc), max_length):
                        final_chunks.append(sc[i:i+max_length])
                else:
                    final_chunks.append(sc)
        else:
            final_chunks.append(lc)
            
    return [c for c in final_chunks if c.strip()]

def parse_text_structure(text: str, model: str = None, strict_mode: bool = False, system_prompt: str = None):
    if model is None:
        model = DEFAULT_MODEL_PARSE
    if not vertex_client:
        logging.error("Client not initialized.")
        return None, {}, False
    
    if system_prompt:
        prompt = system_prompt
    else:
        prompt = SYSTEM_PROMPT_STANDARD

        if not strict_mode:
            prompt += PARSING_INSTRUCTIONS_ENRICHED
        else:
            prompt += PARSING_INSTRUCTIONS_STRICT

    is_truncated = len(text) > 500000
    prompt += f"\nArticle Text:\n{text[:500000]}\n"
    
    try:
        response = _generate_content_with_retry(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )
        
        json_text = response.text
        if json_text.startswith("```json"):
            json_text = json_text[7:]
        if json_text.strip().endswith("```"):
            json_text = json_text.strip()[:-3]
            
        segments = json.loads(json_text)
        dialogue = []
        for seg in segments:
            speaker = "R" if seg.get("type") == "main" else "S"
            seg_text = seg.get("text", "")
            sub_segments = intelligent_chunk(seg_text, 4000)
            for sub_text in sub_segments:
                dialogue.append({"text": sub_text, "speaker": speaker})
        
        usage = {
            "prompt_token_count": response.usage_metadata.prompt_token_count,
            "candidates_token_count": response.usage_metadata.candidates_token_count,
            "total_token_count": response.usage_metadata.total_token_count
        } if response.usage_metadata else {}
            
        return dialogue, usage, is_truncated
    except Exception as e:
        logging.error(f"Error parsing text structure: {e}")
        return None, {}, False

def research_pronunciations(text: str, model: str = None, language: str = "fr-FR"):
    if model is None:
        model = DEFAULT_MODEL_PARSE
    if not vertex_client:
        return None, {}
        
    prompt = RESEARCH_PRONUNCIATION_PROMPT.format(text_snippet=text[:500000], language=language)
    
    try:
        response = vertex_client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())],
            )
        )
        
        text_response = response.text.strip()
        json_match = re.search(r"(\[.*\])", text_response, re.DOTALL)
        if json_match:
            text_response = json_match.group(1)
        else:
            if text_response.startswith("```json"):
                text_response = text_response[7:]
            if text_response.endswith("```"):
                text_response = text_response[:-3]
        
        usage = {
            "prompt_token_count": response.usage_metadata.prompt_token_count,
            "candidates_token_count": response.usage_metadata.candidates_token_count,
            "total_token_count": response.usage_metadata.total_token_count
        } if response.usage_metadata else {}
        
        return json.loads(text_response.strip()), usage
    except Exception as e:
        logging.error(f"Error researching pronunciations: {e}")
        return None, {}
