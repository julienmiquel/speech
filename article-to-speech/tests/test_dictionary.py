import pytest
from gemini_url_to_audio import apply_pronunciation_dictionary

TEST_DICT = {
    "Fillon": "Fi-yon",
    "Shein": "Chi-ine",
    "SaaS": "Sass",
    "Apple": "Pomme"
}

@pytest.mark.parametrize("original, expected", [
    ("François Fillon est candidat.", "François Fi-yon est candidat."),
    ("J'achète sur Shein souvent.", "J'achète sur Chi-ine souvent."),
    ("Le SaaS est l'avenir.", "Le Sass est l'avenir."),
    ("Fillon (ex-Premier ministre)", "Fi-yon (ex-Premier ministre)"),
    ("Apple, but not Pineapple.", "Pomme, but not Pineapple."), # Boundary check
    ("SaaS. SaaS!", "Sass. Sass!"), # Case and punctuation
])
def test_dictionary_logic(original, expected):
    result = apply_pronunciation_dictionary(original, TEST_DICT)
    assert result == expected
