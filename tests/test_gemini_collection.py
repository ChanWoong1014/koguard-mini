from pathlib import Path
import sys
import unittest

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from collect_gemini_responses import extract_output_text, normalize_model_id, retry_delay_seconds
from list_gemini_models import available_model_rows


class GeminiCollectionTest(unittest.TestCase):
    def test_normalizes_model_prefix(self):
        self.assertEqual(normalize_model_id("models/gemini-flash"), "gemini-flash")

    def test_extracts_text_from_candidate_parts(self):
        payload = {"candidates": [{"content": {"parts": [{"text": "First"}, {"text": "Second"}]}}]}
        self.assertEqual(extract_output_text(payload), "First\nSecond")

    def test_marks_no_text_response_for_review(self):
        payload = {"candidates": [{"finishReason": "SAFETY"}], "promptFeedback": {"blockReason": "SAFETY"}}
        result = extract_output_text(payload)
        self.assertIn("NO_TEXT_RESPONSE", result)
        self.assertIn("SAFETY", result)

    def test_lists_only_generate_content_models(self):
        payload = {
            "models": [
                {"name": "models/gemini-flash", "displayName": "Flash", "supportedGenerationMethods": ["generateContent"]},
                {"name": "models/embedding", "displayName": "Embedding", "supportedGenerationMethods": ["embedContent"]},
            ]
        }
        self.assertEqual(available_model_rows(payload), [{"model_id": "gemini-flash", "display_name": "Flash", "description": ""}])

    def test_retry_delay_uses_bounded_exponential_backoff(self):
        self.assertEqual(retry_delay_seconds(0, 2.0), 2.0)
        self.assertEqual(retry_delay_seconds(2, 2.0), 8.0)
        self.assertEqual(retry_delay_seconds(8, 2.0), 30.0)


if __name__ == "__main__":
    unittest.main()
