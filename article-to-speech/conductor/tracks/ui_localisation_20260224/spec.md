# Specification: UI Localisation with locales.json

## Overview
Implement a comprehensive UI localisation system for the article-to-speech generator. This system will allow users to switch the interface language dynamically using a combobox, leveraging the existing `locales.json` file for translations.

## Functional Requirements
- **Language Selection:**
    - Add a combobox at the top of the Streamlit sidebar for language selection.
    - Populate the combobox with available languages from `locales.json`.
- **Dynamic Translation:**
    - Implement a helper function (e.g., `_t(key)`) to retrieve translated strings based on the currently selected locale.
    - Cover UI labels, buttons, error messages, status updates, and reports.
- **Persistence:**
    - Persist the user's language preference across sessions (e.g., using Streamlit's session state and potentially a local config or browser storage).
- **Data Source:**
    - Use `locales.json` as the single source of truth for all UI translations.

## Non-Functional Requirements
- **Maintainability:** The localisation system should be easy to extend with new languages by simply updating `locales.json`.
- **Performance:** Translation lookups should be efficient and not cause noticeable UI lag.
- **Robustness:** Fall back gracefully to a default language (e.g., French or English) if a translation key is missing.

## Acceptance Criteria
- [ ] A language selection combobox is visible at the top of the sidebar.
- [ ] Changing the selection immediately updates all localized text in the UI.
- [ ] The language preference is remembered after a page refresh or restart.
- [ ] All scoped UI elements (labels, messages, reports) are correctly localized.
- [ ] Adding a new language to `locales.json` makes it automatically available in the combobox.

## Out of Scope
- Localisation of the generated audio content itself (this track focuses on the UI).
- Right-to-left (RTL) language support (unless already required by a specific locale).
- Automated translation of user-input articles.
