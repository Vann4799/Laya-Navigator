#!/usr/bin/env python
"""Generate deterministic synthetic workflow JSONL records."""

from __future__ import annotations

import argparse
from pathlib import Path

from laya_navigator.dataset_tools import generate_records, write_jsonl


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("dataset/processed/synthetic_v0.jsonl"),
    )
    args = parser.parse_args()
    records = generate_records(args.count, seed=args.seed)
    write_jsonl(records, args.output)
    print(f"wrote {len(records)} records to {args.output}")


if __name__ == "__main__":
    main()
