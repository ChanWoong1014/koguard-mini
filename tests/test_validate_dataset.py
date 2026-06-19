from pathlib import Path
import sys
import tempfile
import unittest

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from validate_dataset import validate


class ValidateDatasetTest(unittest.TestCase):
    def test_current_seed_dataset_is_valid(self):
        dataset_path = Path(__file__).resolve().parents[1] / "data" / "prompts_seed.csv"
        result = validate(dataset_path)

        self.assertTrue(result["valid"])
        self.assertEqual(result["row_count"], 100)
        self.assertEqual(result["error_count"], 0)

    def test_extended_dataset_is_valid(self):
        dataset_path = Path(__file__).resolve().parents[1] / "data" / "prompts_extended.csv"
        result = validate(dataset_path)

        self.assertTrue(result["valid"])
        self.assertEqual(result["row_count"], 200)
        self.assertEqual(result["error_count"], 0)

    def test_challenge_dataset_is_valid_when_present(self):
        dataset_path = Path(__file__).resolve().parents[1] / "data" / "prompts_challenge.csv"
        if not dataset_path.exists():
            self.skipTest("challenge dataset has not been generated yet")

        result = validate(dataset_path)

        self.assertTrue(result["valid"])
        self.assertEqual(result["row_count"], 80)
        self.assertEqual(result["error_count"], 0)

    def test_duplicate_id_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.csv"
            path.write_text(
                "id,language,attack_type,category,risk_label,prompt_text,notes\n"
                "x-001,en,benign,test,benign,hello,ok\n"
                "x-001,en,benign,test,benign,world,duplicate\n",
                encoding="utf-8",
            )

            result = validate(path)

        self.assertFalse(result["valid"])
        self.assertGreater(result["error_count"], 0)


if __name__ == "__main__":
    unittest.main()
