import unittest
from unittest.mock import MagicMock
import sys
import os

# Add parent directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Mock Streamlit
mock_st = MagicMock()
# Configure mocks to avoid "MagicMock" leaking into logic
mock_st.text_input.return_value = "" # Empty string is Falsy
mock_st.button.return_value = False
mock_st.checkbox.return_value = False
mock_st.selectbox.return_value = "Option 1"
mock_st.radio.return_value = "Option 1"
mock_st.columns.return_value = [MagicMock(), MagicMock(), MagicMock()] # Usually returns list of cols
# Handle variable columns
def side_effect_columns(spec):
    if isinstance(spec, int):
        return [MagicMock() for _ in range(spec)]
    return [MagicMock() for _ in range(len(spec))]
mock_st.columns.side_effect = side_effect_columns

sys.modules["streamlit"] = mock_st

# Mock Google libs
sys.modules["google"] = MagicMock()
sys.modules["google.genai"] = MagicMock()
sys.modules["google.cloud"] = MagicMock()
sys.modules["google.cloud.texttospeech"] = MagicMock()
sys.modules["storage"] = MagicMock()
sys.modules["dotenv"] = MagicMock()

# Mock prompts
sys.modules["prompts"] = MagicMock()

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

class TestTokenUsage(unittest.TestCase):
    def setUp(self):
        # Reset session state for each test
        mock_st.session_state = SessionState({
            "token_usage": {"prompt": 0, "candidates": 0, "total": 0},
            "app_mode": "local",
            "history": []
        })
        # Reset mock calls
        mock_st.reset_mock()

    def test_update_token_usage_none(self):
        """Test update_token_usage with None values in usage dict."""
        usage = {
            "prompt_token_count": 10,
            "candidates_token_count": None,
            "total_token_count": 10
        }

        app.update_token_usage(usage)

        # Verify correct behavior (None treated as 0)
        self.assertEqual(mock_st.session_state.token_usage["prompt"], 10)
        self.assertEqual(mock_st.session_state.token_usage["candidates"], 0) # Should add 0
        self.assertEqual(mock_st.session_state.token_usage["total"], 10)

    def test_update_token_usage_normal(self):
        """Test update_token_usage with normal values."""
        usage = {
            "prompt_token_count": 10,
            "candidates_token_count": 20,
            "total_token_count": 30
        }
        app.update_token_usage(usage)
        self.assertEqual(mock_st.session_state.token_usage["prompt"], 10)
        self.assertEqual(mock_st.session_state.token_usage["candidates"], 20)
        self.assertEqual(mock_st.session_state.token_usage["total"], 30)

if __name__ == '__main__':
    unittest.main()
