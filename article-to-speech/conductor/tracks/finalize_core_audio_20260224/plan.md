# Implementation Plan: Finalize core audio generation features

## Phase 1: Core Functionality Validation [checkpoint: 641f6e6]
- [x] **Task: Validate URL Extraction Logic** 408d723
    - [x] Write unit tests for Gemini-based HTML parsing.
    - [x] Verify extraction of core narrative from Le Figaro URLs.
- [x] **Task: Refine Narrative Structuring** 3e81f9e
    - [x] Write tests for the Narrator vs. Reporter dialogue generation.
    - [x] Implement improvements to the structuring prompt.
- [x] Task: Conductor - User Manual Verification 'Phase 1: Core Functionality Validation' (Protocol in workflow.md)

## Phase 2: Synthesis and Pronunciation
- [ ] **Task: Optimize Phonetic Dictionary**
    - [ ] Write integration tests for IPA custom pronunciations.
    - [ ] Ensure the hybrid dictionary (Regex + IPA) correctly applies rules.
- [ ] **Task: Factory Pattern & Provider Check**
    - [ ] Write tests to verify provider switching (Cloud TTS vs Vertex AI).
    - [ ] Confirm seamless handling of the 4000-byte TTS limit via chunking.
- [ ] **Task: Conductor - User Manual Verification 'Phase 2: Synthesis and Pronunciation' (Protocol in workflow.md)**

## Phase 3: Robustness and Caching
- [ ] **Task: Implement Enhanced Error Handling**
    - [ ] Add retry logic for transient API failures.
    - [ ] Log extraction and synthesis errors for debugging.
- [ ] **Task: Validate Storage and Cache**
    - [ ] Write tests for remote caching (GCS/Firebase).
    - [ ] Confirm assets are correctly retrieved from cache when available.
- [ ] **Task: Conductor - User Manual Verification 'Phase 3: Robustness and Caching' (Protocol in workflow.md)**
