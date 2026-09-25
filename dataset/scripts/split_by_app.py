#!/usr/bin/env python
"""Split Laya training JSONL by app/website."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from laya_navigator.splitter import split_rows_by_app


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    rows = [
        json.loads(line)
        for line in args.input.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    splits = split_rows_by_app(rows, seed=args.seed)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {"seed": args.seed, "splits": {}}
    for name, values in splits.items():
        path = args.output_dir / f"{name}.jsonl"
        with path.open("w", encoding="utf-8", newline="\n") as handle:
            for value in values:
                handle.write(json.dumps(value, ensure_ascii=False, separators=(",", ":")) + "\n")
        manifest["splits"][name] = {
            "rows": len(values),
            "apps": sorted({value.get("app", "unknown") for value in values}),
        }
    (args.output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps({name: details["rows"] for name, details in manifest["splits"].items()}))


if __name__ == "__main__":
    main()
