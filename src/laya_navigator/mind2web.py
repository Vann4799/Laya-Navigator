"""Normalize Mind2Web action trajectories into Laya Navigator transitions."""

from __future__ import annotations

import re
from typing import Any, Iterator

_ACTION_RE = re.compile(r"^\[(?P<role>[^\]]+)\]\s*(?P<name>.*?)\s*->\s*(?P<verb>[A-Z]+)(?::\s*(?P<value>.*))?$")
_VERB_MAP = {
    "CLICK": "click_element",
    "TYPE": "type_text",
    "SELECT": "select_option",
    "PRESS": "press_key",
    "SCROLL": "scroll",
    "HOVER": "hover",
}


def parse_action_repr(text: str) -> dict[str, Any]:
    """Parse Mind2Web's human-readable action representation."""
    match = _ACTION_RE.match(text.strip())
    if not match:
        return {
            "role": "unknown",
            "name": text.strip(),
            "action_type": "click_element",
            "value": None,
        }
    verb = match.group("verb")
    return {
        "role": match.group("role").strip(),
        "name": match.group("name").strip(),
        "action_type": _VERB_MAP.get(verb, "click_element"),
        "value": match.group("value"),
    }


def normalize_trajectory(item: dict[str, Any]) -> Iterator[dict[str, Any]]:
    """Yield one state-transition record per annotated action."""
    actions = item.get("action_reprs") or []
    if not actions:
        return
    website = str(item.get("website") or "unknown")
    workflow = str(item.get("subdomain") or item.get("domain") or "web_task")
    task = str(item.get("confirmed_task") or "complete web task")
    parsed = [parse_action_repr(action) for action in actions]
    for index, action in enumerate(parsed):
        history = [entry["action_type"] for entry in parsed[:index]]
        yield {
            "id": f"mind2web-{item.get('annotation_id', 'unknown')}-{index:03d}",
            "app": website,
            "workflow": workflow,
            "source": {
                "name": "mind2web",
                "license": "CC-BY-4.0",
                "annotation_id": item.get("annotation_id"),
            },
            "state": {
                "route": f"trajectory:{index}",
                "page_title": task,
                "auth_state": "unknown",
                "visible_elements": [
                    {
                        "role": action["role"],
                        "name": action["name"],
                        "actionable": True,
                    }
                ],
                "form_fields": [],
                "history": history,
                "event_log": history,
                "last_action": history[-1] if history else None,
                "errors": [],
            },
            "label": {
                "page_state": "workflow_step",
                "goal": "complete_task",
                "next_action": action["action_type"],
                "blocked": False,
                "blocking_reason": None,
                "completion_progress": (index + 1) / len(parsed),
                "confidence": 1.0,
            },
        }
