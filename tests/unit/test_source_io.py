import tempfile
import unittest
from pathlib import Path

from laya_navigator.source_io import iter_json_array


class StreamingJsonTests(unittest.TestCase):
    def test_iter_json_array_reads_large_style_array_incrementally(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "rows.json"
            path.write_text('[{"id": 1}, {"id": 2}, {"id": 3}]', encoding="utf-8")
            self.assertEqual(list(iter_json_array(path, chunk_size=8)), [{"id": 1}, {"id": 2}, {"id": 3}])


if __name__ == "__main__":
    unittest.main()
