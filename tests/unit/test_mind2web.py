import unittest

from laya_navigator.mind2web import normalize_trajectory, parse_action_repr


class Mind2WebNormalizerTests(unittest.TestCase):
    def test_parse_action_repr(self):
        parsed = parse_action_repr("[button] Submit application -> CLICK")
        self.assertEqual(parsed["role"], "button")
        self.assertEqual(parsed["action_type"], "click_element")

    def test_normalize_trajectory_emits_transition_records(self):
        item = {
            "website": "demo",
            "domain": "HR",
            "subdomain": "Recruiting",
            "annotation_id": "abc",
            "confirmed_task": "Apply for a job",
            "action_reprs": [
                "[button] Login -> CLICK",
                "[button] Apply -> CLICK",
                "[input] Resume -> TYPE: cv.pdf",
            ],
        }
        records = list(normalize_trajectory(item))
        self.assertEqual(len(records), 3)
        self.assertEqual(records[0]["label"]["next_action"], "click_element")
        self.assertEqual(records[2]["label"]["next_action"], "type_text")
        self.assertEqual(records[2]["state"]["history"], ["click_element", "click_element"])
        self.assertEqual(records[2]["label"]["completion_progress"], 1.0)


if __name__ == "__main__":
    unittest.main()
