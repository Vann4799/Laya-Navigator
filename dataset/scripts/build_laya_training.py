#!/usr/bin/env python
"""Build official-style Laya typed-decision JSONL rows."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from laya_navigator.training_format import build_training_row, to_laya_jsonl


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--max-candidates", type=int, default=64)
    args = parser.parse_args()
    total = kept = 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.input.open(encoding="utf-8") as source, args.output.open("w", encoding="utf-8") as target:
        for line in source:
            if not line.strip():
                continue
            total += 1
            row = build_training_row(json.loads(line), max_candidates=args.max_candidates)
            if row is None:
                continue
            target.write(to_laya_jsonl(row) + "\n")
            kept += 1
    print(f"kept={kept} total={total} skipped={total-kept} output={args.output}")


if __name__ == "__main__":
    main()
