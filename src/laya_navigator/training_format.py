"""Convert normalized workflow records to Laya typed-decision training rows."""

from __future__ import annotations

import json
import re
from typing import Any

OPERATION_CRITERIA = {
    "click_element": "Click an interactive element",
    "type_text": "Type text into a field",
    "select_option": "Select an option",
    "press_key": "Press a keyboard key",
    "scroll": "Scroll the page",
    "hover": "Hover over an element",
}


def _norm(value: str) -> str:
    return re.sub(r"\s+", " ", str(value).strip().lower())


def _one_hot(options: list[str], selected: str) -> dict[str, float]:
    return {option: 1.0 if option == selected else 0.0 for option in options}


def build_training_row(record: dict[str, Any], max_candidates: int = 64) -> dict[str, Any] | None:
    """Move DOM candidates into a typed choice question and create gold targets."""
    state = record.get("state") or {}
    label = record.get("label") or {}
    operation = label.get("operation") or label.get("next_action")
    target = label.get("target_element") or {}
    if operation not in OPERATION_CRITERIA or not target.get("name"):
        return None

    candidates = state.get("visible_elements") or []
    target_role = _norm(target.get("role", ""))
    target_name = _norm(target.get("name", ""))
    target_index = None
    for index, candidate in enumerate(candidates):
        if _norm(candidate.get("role", "")) == target_role and _norm(candidate.get("name", "")) == target_name:
            target_index = index
            break
    if target_index is None:
        name_matches = [
            index
            for index, candidate in enumerate(candidates)
            if _norm(candidate.get("name", "")) == target_name and target_name
        ]
        if len(name_matches) == 1:
            target_index = name_matches[0]
    if target_index is None and target_name:
        fuzzy_matches = [
            index
            for index, candidate in enumerate(candidates)
            if target_name in _norm(candidate.get("name", ""))
            or _norm(candidate.get("name", "")) in target_name
        ]
        if len(fuzzy_matches) == 1:
            target_index = fuzzy_matches[0]
    if target_index is None:
        return None

    selected = list(candidates[:max_candidates])
    if target_index >= max_candidates:
        selected = selected[:-1] + [candidates[target_index]]
        target_index = max_candidates - 1
    options = {
        f"e{index}": f"[{candidate.get('role', 'unknown')}] {candidate.get('name', '')}"
        for index, candidate in enumerate(selected)
    }
    state_for_training = {
        key: value
        for key, value in state.items()
        if key not in {"visible_elements", "form_fields"}
    }
    operation_options = list(OPERATION_CRITERIA)
    target_options = list(options)
    return {
        "id": record.get("id"),
        "app": record.get("app"),
        "workflow": record.get("workflow"),
        "state": state_for_training,
        "questions": {
            "operation": {
                "type": "choice",
                "instructions": "What browser operation should happen next?",
                "criteria": OPERATION_CRITERIA,
            },
            "target_element": {
                "type": "choice",
                "instructions": "Which element is the target of the next operation?",
                "criteria": options,
            },
        },
        "gold": {
            "operation": {
                "choice": operation,
                "probabilities": _one_hot(operation_options, operation),
            },
            "target_element": {
                "choice": f"e{target_index}",
                "probabilities": _one_hot(target_options, f"e{target_index}"),
            },
        },
    }


def to_laya_jsonl(row: dict[str, Any]) -> str:
    """Serialize a training row using the official string-field convention."""
    return json.dumps(
        {
            "id": row.get("id"),
            "app": row.get("app"),
            "workflow": row.get("workflow"),
            "state": json.dumps(row["state"], ensure_ascii=False, separators=(",", ":")),
            "questions": json.dumps(row["questions"], ensure_ascii=False, separators=(",", ":")),
            "gold": json.dumps(row["gold"], ensure_ascii=False, separators=(",", ":")),
        },
        ensure_ascii=False,
        separators=(",", ":"),
    )
