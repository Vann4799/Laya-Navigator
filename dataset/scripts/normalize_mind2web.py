#!/usr/bin/env python
"""Download and normalize one Mind2Web shard without loading it into RAM."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from laya_navigator.mind2web import normalize_trajectory
from laya_navigator.source_io import download_url, iter_json_array

BASE_URL = "https://huggingface.co/datasets/osunlp/Mind2Web/resolve/main/data/train/{shard}.json?download=true"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--shard", default="train_0")
    parser.add_argument("--raw-dir", type=Path, default=Path("dataset/raw/mind2web"))
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("dataset/processed/mind2web_train_0.jsonl"),
    )
    parser.add_argument("--limit", type=int, default=0, help="0 means all trajectories")
    args = parser.parse_args()

    raw_path = args.raw_dir / f"{args.shard}.json"
    if not raw_path.exists():
        print(f"downloading {args.shard}")
        download_url(BASE_URL.format(shard=args.shard), raw_path)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    records = 0
    with args.output.open("w", encoding="utf-8", newline="\n") as output:
        for item in iter_json_array(raw_path):
            for record in normalize_trajectory(item):
                output.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")
                records += 1
            count += 1
            if args.limit and count >= args.limit:
                break
    print(f"normalized trajectories={count}, records={records}, output={args.output}")


if __name__ == "__main__":
    main()
