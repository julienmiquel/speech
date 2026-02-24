# Implementation Plan: UI Localisation

This plan outlines the steps to implement a persistent UI localisation system using `locales.json` and a sidebar-based language selector.

## Phase 1: Localisation Core Infrastructure
- [ ] Task: Create Localisation Manager
    - [ ] Write tests for loading `locales.json`.
    - [ ] Implement `LocaleManager` to load and cache translations.
    - [ ] Write tests for the translation helper function (handling nested keys and fallbacks).
    - [ ] Implement the `_t()` helper function.
- [ ] Task: Implement Persistence Logic
    - [ ] Write tests for saving and loading language preferences.
    - [ ] Implement persistence using Streamlit session state and local storage/config.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Localisation Core Infrastructure' (Protocol in workflow.md)

## Phase 2: UI Integration & Sidebar Selector
- [ ] Task: Add Sidebar Language Selector
    - [ ] Implement the language selection combobox at the top of the sidebar.
    - [ ] Ensure the selector triggers a UI refresh upon change.
- [ ] Task: Localize Main UI Components
    - [ ] Replace hardcoded strings in the main application with `_t()` calls.
    - [ ] Cover all labels, buttons, and headers in the "Atelier" and "Playground".
- [ ] Task: Conductor - User Manual Verification 'Phase 2: UI Integration & Sidebar Selector' (Protocol in workflow.md)

## Phase 3: Comprehensive Localisation & Testing
- [ ] Task: Localize Messages, Status, and Reports
    - [ ] Update error handling and status messages to use the localisation system.
    - [ ] Localize benchmark reports and results display.
- [ ] Task: Final Verification & Fallback Check
    - [ ] Verify that adding a new language to `locales.json` works seamlessly.
    - [ ] Ensure missing keys fall back to the default language correctly.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Comprehensive Localisation & Testing' (Protocol in workflow.md)
