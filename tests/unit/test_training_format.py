import unittest

from laya_navigator.training_format import build_training_row


class TrainingFormatTests(unittest.TestCase):
    def test_build_training_row_moves_candidates_into_question_options(self):
        record = {
            "id": "x1",
            "app": "demo",
            "workflow": "checkout",
            "state": {
                "route": "/pay",
                "page_title": "Payment",
                "history": ["/cart"],
                "visible_elements": [
                    {"role": "button", "name": "Pay now", "actionable": True},
                    {"role": "button", "name": "Cancel", "actionable": True},
                ],
                "event_log": [],
                "last_action": None,
                "errors": [],
            },
            "label": {
                "next_action": "click_element",
                "operation": "click_element",
                "target_element": {"role": "button", "name": "Pay now"},
            },
        }
        row = build_training_row(record)
        self.assertIsNotNone(row)
        self.assertEqual(row["state"]["route"], "/pay")
        self.assertNotIn("visible_elements", row["state"])
        self.assertIn("target_element", row["questions"])
        self.assertEqual(row["gold"]["operation"]["choice"], "click_element")
        self.assertEqual(row["gold"]["target_element"]["choice"], "e0")

    def test_unmatched_target_is_skipped(self):
        record = {
            "id": "x2",
            "app": "demo",
            "state": {"visible_elements": [{"role": "button", "name": "Other"}]},
            "label": {
                "operation": "click_element",
                "target_element": {"role": "button", "name": "Missing"},
            },
        }
        self.assertIsNone(build_training_row(record))

    def test_large_candidate_list_keeps_target_without_forcing_last_slot(self):
        candidates = [
            {"role": "button", "name": f"Option {i}"}
            for i in range(50)
        ]
        record = {
            "id": "large-candidates",
            "app": "demo",
            "state": {"visible_elements": candidates},
            "label": {
                "operation": "click_element",
                "target_element": {"role": "button", "name": "Option 47"},
            },
        }
        row = build_training_row(record, max_candidates=10)
        self.assertIsNotNone(row)
        options = row["questions"]["target_element"]["criteria"]
        target = row["gold"]["target_element"]["choice"]
        self.assertEqual(len(options), 10)
        self.assertIn(target, options)


if __name__ == "__main__":
    unittest.main()
