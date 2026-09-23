#!/usr/bin/env python
"""Filter normalized records that have a concrete target element label."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    total = kept = 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.input.open(encoding="utf-8") as source, args.output.open("w", encoding="utf-8") as target:
        for line in source:
            if not line.strip():
                continue
            total += 1
            record = json.loads(line)
            label = record.get("label", {}).get("target_element", {})
            if label.get("name"):
                target.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")
                kept += 1
    print(f"kept={kept} total={total} filtered={total-kept}")


if __name__ == "__main__":
    main()
