import unittest

from laya_navigator.dataset_tools import generate_records, validate_record


class DatasetToolsTests(unittest.TestCase):
    def test_generator_is_deterministic_and_returns_valid_records(self):
        first = generate_records(12, seed=7)
        second = generate_records(12, seed=7)
        self.assertEqual(first, second)
        self.assertEqual(len(first), 12)
        self.assertEqual(validate_record(first[0]), [])

    def test_validator_rejects_unknown_action(self):
        record = generate_records(1, seed=1)[0]
        record["label"]["next_action"] = "invented_action"
        errors = validate_record(record)
        self.assertTrue(any("next_action" in error for error in errors))

    def test_validator_rejects_progress_outside_range(self):
        record = generate_records(1, seed=1)[0]
        record["label"]["completion_progress"] = 2
        errors = validate_record(record)
        self.assertTrue(any("completion_progress" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
