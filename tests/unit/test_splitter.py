import unittest

from laya_navigator.splitter import split_rows_by_app


class SplitterTests(unittest.TestCase):
    def test_apps_never_cross_splits(self):
        rows = [{"id": str(i), "app": app} for i, app in enumerate(["a", "b", "c", "d", "e", "f"])]
        splits = split_rows_by_app(rows, seed=3)
        memberships = {}
        for name, values in splits.items():
            for row in values:
                previous = memberships.setdefault(row["app"], name)
                self.assertEqual(previous, name)
        self.assertEqual(set(memberships), {"a", "b", "c", "d", "e", "f"})

    def test_same_seed_is_deterministic(self):
        rows = [{"id": str(i), "app": f"app-{i % 4}"} for i in range(20)]
        first = split_rows_by_app(rows, seed=42)
        second = split_rows_by_app(rows, seed=42)
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
