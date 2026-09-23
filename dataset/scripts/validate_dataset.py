#!/usr/bin/env python
"""Validate a normalized workflow JSONL file."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from laya_navigator.dataset_tools import validate_record


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    args = parser.parse_args()
    errors: list[str] = []
    count = 0
    with args.path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            count += 1
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                errors.append(f"line {line_number}: invalid JSON: {exc}")
                continue
            errors.extend(f"line {line_number}: {error}" for error in validate_record(record))
    if errors:
        print("validation failed")
        print("\n".join(errors[:20]))
        return 1
    print(f"validated {count} records")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
