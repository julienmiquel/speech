# Track Specification: Finalize core audio generation features

## Overview
This track focuses on solidifying the core audio generation capabilities of the Article-to-Speech application. Building upon the existing foundation, we will ensure robust extraction, narrative structuring, and high-quality synthesis using Google Cloud TTS and Gemini.

## Requirements
- Ensure reliable extraction of news content from URLs, specifically targeting Le Figaro as a primary source.
- Validate and refine the multi-speaker narrative structuring (Narrator vs. Reporter).
- Optimize the phonetic dictionary management for accurate IPA-based pronunciation.
- Confirm the modular architecture (Factory pattern) correctly handles different TTS providers.
- Implement comprehensive error handling for network requests and API calls.

## Acceptance Criteria
- Successfully generate a 2-minute multi-speaker audio from a given Le Figaro URL.
- All extracted text is narrative and free of UI elements/ads.
- Pronunciation of brands like "Shein" or "Temu" follows the specified IPA rules.
- System handles API rate limits and connection issues gracefully.
