#!/usr/bin/env python
"""Run base Laya next-action baseline on normalized Mind2Web records."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import laya

ACTIONS = {
    "click_element": "Click the target element",
    "type_text": "Type text into the target field",
    "select_option": "Select an option",
    "press_key": "Press a keyboard key",
    "scroll": "Scroll the page",
    "hover": "Hover over the target",
}

QUESTIONS = {
    "next_action": {
        "type": "choice",
        "instructions": "What action should the browser agent take next?",
        "criteria": ACTIONS,
    }
}


def answer(result: dict) -> str | None:
    value = result.get("answers", result).get("next_action", {})
    return value.get("choice") if isinstance(value, dict) else None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=Path("dataset/processed/mind2web_train_0_1000.jsonl"))
    parser.add_argument("--output", type=Path, default=Path("benchmark/reports/mind2web_base_laya.json"))
    parser.add_argument("--limit", type=int, default=25)
    args = parser.parse_args()

    records = [
        json.loads(line)
        for line in args.input.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ][: args.limit]
    agent = laya.load(device="cpu")
    results = agent.predict_batch(
        [record["state"] for record in records], QUESTIONS, batch_size=8
    )
    correct = sum(answer(result) == record["label"]["next_action"] for record, result in zip(records, results))
    report = {
        "model": "convaiinnovations/laya",
        "dataset": "osunlp/Mind2Web",
        "records": len(records),
        "next_action_correct": correct,
        "next_action_accuracy": correct / len(records) if records else 0,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
