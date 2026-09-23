"""Synthetic workflow records and lightweight validation for Laya Navigator."""

from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Any

PAGE_STATES = {
    "landing",
    "login",
    "dashboard",
    "job_list",
    "job_detail",
    "application_form",
    "cv_uploaded",
    "success",
    "error",
    "workflow_step",
}
GOALS = {"login_user", "apply_job", "upload_cv", "submit_application", "complete_task"}
ACTIONS = {
    "click_login",
    "submit_login",
    "open_job",
    "start_application",
    "upload_cv",
    "submit_application",
    "retry_action",
    "click_element",
    "type_text",
    "select_option",
    "press_key",
    "scroll",
    "hover",
}

_TEMPLATES = [
    {
        "route": "/",
        "title": "CareerOS",
        "page_state": "landing",
        "goal": "login_user",
        "next_action": "click_login",
        "progress": 0.0,
        "elements": [{"role": "link", "name": "Sign in", "actionable": True}],
    },
    {
        "route": "/login",
        "title": "Sign in",
        "page_state": "login",
        "goal": "login_user",
        "next_action": "submit_login",
        "progress": 0.2,
        "elements": [
            {"role": "textbox", "name": "Email", "actionable": True, "required": True},
            {"role": "textbox", "name": "Password", "actionable": True, "required": True},
            {"role": "button", "name": "Sign in", "actionable": True},
        ],
    },
    {
        "route": "/jobs",
        "title": "Jobs",
        "page_state": "job_list",
        "goal": "apply_job",
        "next_action": "open_job",
        "progress": 0.35,
        "elements": [{"role": "link", "name": "Frontend Engineer", "actionable": True}],
    },
    {
        "route": "/jobs/123",
        "title": "Frontend Engineer",
        "page_state": "job_detail",
        "goal": "apply_job",
        "next_action": "start_application",
        "progress": 0.48,
        "elements": [{"role": "button", "name": "Apply now", "actionable": True}],
    },
    {
        "route": "/jobs/123/apply",
        "title": "Apply for Frontend Engineer",
        "page_state": "application_form",
        "goal": "upload_cv",
        "next_action": "upload_cv",
        "progress": 0.65,
        "elements": [
            {"role": "textbox", "name": "Name", "actionable": True, "required": True},
            {"role": "button", "name": "Upload CV", "actionable": True},
            {"role": "button", "name": "Submit application", "actionable": True},
        ],
    },
    {
        "route": "/jobs/123/apply",
        "title": "CV uploaded",
        "page_state": "cv_uploaded",
        "goal": "submit_application",
        "next_action": "submit_application",
        "progress": 0.86,
        "elements": [{"role": "button", "name": "Submit application", "actionable": True}],
    },
    {
        "route": "/jobs/123/success",
        "title": "Application submitted",
        "page_state": "success",
        "goal": "submit_application",
        "next_action": "retry_action",
        "progress": 1.0,
        "elements": [{"role": "heading", "name": "Application submitted"}],
    },
]


def generate_records(count: int, seed: int = 0) -> list[dict[str, Any]]:
    """Generate deterministic synthetic workflow states for baseline training."""
    if count < 0:
        raise ValueError("count must be non-negative")
    rng = random.Random(seed)
    records: list[dict[str, Any]] = []
    for index in range(count):
        template = dict(rng.choice(_TEMPLATES))
        position = _TEMPLATES.index(template)
        history = [item["route"] for item in _TEMPLATES[:position]]
        record = {
            "id": f"synthetic-career-{index:06d}",
            "app": "synthetic_careeros",
            "workflow": "job_application",
            "source": {
                "name": "synthetic",
                "license": "Apache-2.0",
                "generator_version": "0.1.0",
            },
            "state": {
                "route": template["route"],
                "page_title": template["title"],
                "auth_state": "authenticated" if position >= 2 else "anonymous",
                "visible_elements": template["elements"],
                "form_fields": [
                    element["name"]
                    for element in template["elements"]
                    if element["role"] == "textbox"
                ],
                "history": history,
                "event_log": [],
                "last_action": None,
                "errors": [],
            },
            "label": {
                "page_state": template["page_state"],
                "goal": template["goal"],
                "next_action": template["next_action"],
                "blocked": False,
                "blocking_reason": None,
                "completion_progress": template["progress"],
                "confidence": 1.0,
            },
        }
        records.append(record)
    return records


def validate_record(record: dict[str, Any]) -> list[str]:
    """Return human-readable validation errors for one normalized record."""
    errors: list[str] = []
    for key in ("id", "app", "workflow", "source", "state", "label"):
        if key not in record:
            errors.append(f"missing top-level field: {key}")
    if errors:
        return errors

    label = record["label"]
    for key in ("page_state", "goal", "next_action", "blocked", "completion_progress", "confidence"):
        if key not in label:
            errors.append(f"missing label field: {key}")
    if label.get("page_state") not in PAGE_STATES:
        errors.append(f"unknown page_state: {label.get('page_state')}")
    if label.get("goal") not in GOALS:
        errors.append(f"unknown goal: {label.get('goal')}")
    if label.get("next_action") not in ACTIONS:
        errors.append(f"unknown next_action: {label.get('next_action')}")
    for field in ("completion_progress", "confidence"):
        value = label.get(field)
        if not isinstance(value, (int, float)) or not 0 <= value <= 1:
            errors.append(f"{field} must be between 0 and 1")
    if not isinstance(label.get("blocked"), bool):
        errors.append("blocked must be boolean")
    if not label.get("blocked") and label.get("blocking_reason") is not None:
        errors.append("blocking_reason must be null when blocked is false")
    return errors


def write_jsonl(records: list[dict[str, Any]], path: Path) -> None:
    """Write validated records as UTF-8 JSONL."""
    errors = [error for record in records for error in validate_record(record)]
    if errors:
        raise ValueError("invalid records: " + "; ".join(errors[:5]))
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")
