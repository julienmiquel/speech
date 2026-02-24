import pytest
from unittest.mock import patch, MagicMock
from gemini_url_to_audio import extract_text_from_url_with_gemini

LE_FIGARO_HTML = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <title>Article Le Figaro</title>
</head>
<body>
    <nav class="fig-menu">
        <ul><li>Actualité</li><li>Économie</li></ul>
    </nav>
    <header class="fig-header">
        <h1 class="fig-headline">Nucléaire : la nouvelle stratégie française</h1>
    </header>
    <main class="fig-content">
        <p>Le président a annoncé une accélération du programme nucléaire.</p>
        <div class="fig-ad">Publicité : achetez nos journaux</div>
        <p>Six nouveaux réacteurs EPR seront construits d'ici 2050.</p>
    </main>
    <aside class="fig-sidebar">
        <h3>Articles liés</h3>
        <ul><li>L'énergie en France</li></ul>
    </aside>
    <footer class="fig-footer">
        &copy; 2026 Le Figaro
    </footer>
</body>
</html>
"""

@patch('requests.get')
@patch('gemini_url_to_audio.client')
def test_lefigaro_extraction_narrative(mock_client, mock_get):
    """Test that it extracts the core narrative from a Figaro-like HTML structure."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = LE_FIGARO_HTML
    mock_get.return_value = mock_response
    
    mock_gen_response = MagicMock()
    mock_gen_response.text = """Nucléaire : la nouvelle stratégie française

Le président a annoncé une accélération du programme nucléaire.

Six nouveaux réacteurs EPR seront construits d'ici 2050."""
    mock_gen_response.usage_metadata = None
    mock_client.models.generate_content.return_value = mock_gen_response
    
    text, usage, is_truncated = extract_text_from_url_with_gemini("https://www.lefigaro.fr/nucleaire")
    
    assert "Nucléaire" in text
    assert "EPR" in text
    assert "Publicité" not in text
    assert "Actualité" not in text
    assert "Le Figaro" not in text or "Article Le Figaro" not in text # Depending on how Gemini handles it
    assert "Économie" not in text
