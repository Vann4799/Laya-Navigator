#!/usr/bin/env python
"""Run a base-Laya workflow decision baseline over normalized JSONL."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import laya

QUESTIONS = {
    "page_state": {
        "type": "choice",
        "instructions": "What page state is this?",
        "criteria": {
            "landing": "Landing page",
            "login": "Login page",
            "dashboard": "Dashboard",
            "job_list": "Job list",
            "job_detail": "Job detail",
            "application_form": "Application form",
            "cv_uploaded": "CV uploaded",
            "success": "Success page",
            "error": "Error page",
        },
    },
    "goal": {
        "type": "choice",
        "instructions": "What is the main user goal?",
        "criteria": {
            "login_user": "Log in",
            "apply_job": "Apply for a job",
            "upload_cv": "Upload a CV",
            "submit_application": "Submit an application",
        },
    },
    "next_action": {
        "type": "choice",
        "instructions": "What should the user do next?",
        "criteria": {
            "click_login": "Click login",
            "submit_login": "Submit login",
            "open_job": "Open a job",
            "start_application": "Start application",
            "upload_cv": "Upload CV",
            "submit_application": "Submit application",
            "retry_action": "Retry",
        },
    },
}


def _answer(result: dict[str, Any], name: str) -> str | None:
    answers = result.get("answers", result)
    value = answers.get(name, {}) if isinstance(answers, dict) else {}
    if isinstance(value, dict):
        return value.get("choice") or value.get("value")
    return value if isinstance(value, str) else None


def evaluate(records: list[dict[str, Any]], results: list[dict[str, Any]]) -> dict[str, Any]:
    metrics: dict[str, dict[str, int]] = {
        name: {"correct": 0, "total": len(records)} for name in QUESTIONS
    }
    for record, result in zip(records, results):
        for name in QUESTIONS:
            if _answer(result, name) == record["label"][name]:
                metrics[name]["correct"] += 1
    for metric in metrics.values():
        metric["accuracy"] = metric["correct"] / metric["total"] if metric["total"] else 0
    return {"records": len(records), "metrics": metrics}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=Path("dataset/processed/synthetic_v0.jsonl"))
    parser.add_argument("--output", type=Path, default=Path("benchmark/reports/base_laya.json"))
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--batch-size", type=int, default=8)
    args = parser.parse_args()

    records = [
        json.loads(line)
        for line in args.input.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ][: args.limit]
    agent = laya.load(device="cpu")
    results = agent.predict_batch(
        [record["state"] for record in records], QUESTIONS, batch_size=args.batch_size
    )
    report = evaluate(records, results)
    report["model"] = "convaiinnovations/laya"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
