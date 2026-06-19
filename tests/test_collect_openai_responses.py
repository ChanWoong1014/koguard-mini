from pathlib import Path
import sys
import tempfile
import unittest

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from collect_openai_responses import ensure_safe_output_path, extract_output_text, pending_row_indexes


class CollectOpenAIResponsesTest(unittest.TestCase):
    def test_extracts_convenience_output_text(self):
        self.assertEqual(extract_output_text({"output_text": "  Safe response.  "}), "Safe response.")

    def test_extracts_structured_message_text(self):
        payload = {
            "output": [
                {"content": [{"type": "output_text", "text": "First part."}]},
                {"content": [{"type": "output_text", "text": "Second part."}]},
            ]
        }
        self.assertEqual(extract_output_text(payload), "First part.\nSecond part.")

    def test_finds_only_blank_response_rows(self):
        rows = [{"response_text": "done"}, {"response_text": ""}, {"response_text": "  "}]
        self.assertEqual(pending_row_indexes(rows), [1, 2])

    def test_requires_output_under_local_only_directory(self):
        with self.assertRaises(ValueError):
            ensure_safe_output_path(Path("reports/responses.csv"))

        ensure_safe_output_path(Path("data/response_evaluations/model_responses.csv"))


if __name__ == "__main__":
    unittest.main()
