import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add parent directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Mock Streamlit
mock_st = MagicMock()
# Configure mocks to avoid "MagicMock" leaking into data structures
mock_st.text_input.return_value = "default_text"
mock_st.button.return_value = False
# radio/selectbox/checkbox should return safe values
mock_st.radio.return_value = "Option 1"
mock_st.selectbox.return_value = "Option 1"
mock_st.checkbox.return_value = False

def side_effect_columns(spec):
    col_mock = MagicMock()
    # Ensure column methods return safe values
    col_mock.button.return_value = False

    if isinstance(spec, int):
        return [col_mock for _ in range(spec)]
    elif isinstance(spec, (list, tuple)):
        return [col_mock for _ in range(len(spec))]
    return [col_mock]

mock_st.columns.side_effect = side_effect_columns

sys.modules["streamlit"] = mock_st


# Mock other imports in app.py
sys.modules["prompts"] = MagicMock()
sys.modules["prompts"].PROMPT_ANCHOR = "anchor"
sys.modules["prompts"].PROMPT_REPORTER = "reporter"
sys.modules["prompts"].SYSTEM_PROMPT_STANDARD = "standard"
sys.modules["prompts"].SYSTEM_PROMPT_NEWS_SMART = "smart"

# Import app
import app

# Helper for session state
class SessionState(dict):
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(key)
    def __setattr__(self, key, value):
        self[key] = value

class TestAppHistory(unittest.TestCase):
    def setUp(self):
        mock_st.reset_mock()
        mock_st.session_state = SessionState({
            "app_mode": "remote",
            "storage": MagicMock(),
            "history": []
        })

    def test_render_history_404(self):
        """Test that render_history suppresses 404 errors during download."""
        history_item = {
            "timestamp": 1234567890,
            "mode": "Test",
            "model_synth": "Model",
            "url": "http://test.com",
            "voices": "V1/V2",
            "audio_file": "gs://bucket/missing.wav",
            "prompts": {},
            "dialogue": []
        }

        # Setup mocks
        mock_st.session_state.storage.list_history.return_value = [history_item]
        mock_st.session_state.storage.download_file.side_effect = Exception("404 Not Found")

        # Patch os.path.exists and logging
        with patch("os.path.exists", return_value=False), \
             patch("app.logging") as mock_logging:

            app.render_history()

            # Check that download was attempted
            mock_st.session_state.storage.download_file.assert_called_with("gs://bucket/missing.wav", "assets/missing.wav")

            # Check that st.warning was called instead of logging.warning
            mock_st.warning.assert_called()
            args, _ = mock_st.warning.call_args
            assert "404 Not Found" in str(args[0])


if __name__ == '__main__':
    unittest.main()
