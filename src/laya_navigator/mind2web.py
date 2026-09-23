"""Normalize Mind2Web action trajectories into Laya Navigator transitions."""

from __future__ import annotations

import re
from html.parser import HTMLParser
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
_INTERACTIVE_TAGS = {"a", "button", "input", "select", "textarea", "option"}
_INTERACTIVE_ROLES = {"button", "link", "textbox", "combobox", "checkbox", "radio", "menuitem", "tab"}


class _CandidateParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.candidates: list[dict[str, Any]] = []
        self._stack: list[tuple[str, dict[str, Any]]] = []

    def handle_starttag(self, tag: str, attrs_list: list[tuple[str, str | None]]) -> None:
        attrs = {key: value or "" for key, value in attrs_list}
        role = attrs.get("role") or tag
        is_interactive = (
            tag in _INTERACTIVE_TAGS
            or role in _INTERACTIVE_ROLES
            or attrs.get("is_clickable", "").lower() == "true"
        )
        if not is_interactive:
            return
        name = (
            attrs.get("aria_label")
            or attrs.get("aria-label")
            or attrs.get("placeholder")
            or attrs.get("name")
            or attrs.get("id")
            or ""
        ).strip()
        candidate = {
            "role": role,
            "name": name,
            "actionable": True,
        }
        if attrs.get("value"):
            candidate["value"] = attrs["value"]
        self.candidates.append(candidate)
        self._stack.append((tag, candidate))

    def handle_data(self, data: str) -> None:
        text = " ".join(data.split())
        if not text or not self._stack:
            return
        candidate = self._stack[-1][1]
        if not candidate["name"]:
            candidate["name"] = text[:200]

    def handle_endtag(self, tag: str) -> None:
        for index in range(len(self._stack) - 1, -1, -1):
            if self._stack[index][0] == tag:
                del self._stack[index:]
                return


def extract_candidates(raw_html: str | None, limit: int = 100) -> list[dict[str, Any]]:
    """Extract compact actionable element candidates from a Mind2Web DOM snapshot."""
    if not raw_html:
        return []
    parser = _CandidateParser()
    parser.feed(raw_html)
    seen: set[tuple[str, str]] = set()
    result: list[dict[str, Any]] = []
    for candidate in parser.candidates:
        candidate["name"] = " ".join(candidate["name"].split())[:200]
        key = (candidate["role"], candidate["name"])
        if not candidate["name"] or key in seen:
            continue
        seen.add(key)
        result.append(candidate)
        if len(result) >= limit:
            break
    return result


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
    raw_actions = item.get("actions") or []
    if not actions:
        return
    website = str(item.get("website") or "unknown")
    workflow = str(item.get("subdomain") or item.get("domain") or "web_task")
    task = str(item.get("confirmed_task") or "complete web task")
    parsed = [parse_action_repr(action) for action in actions]
    for index, action in enumerate(parsed):
        history = [entry["action_type"] for entry in parsed[:index]]
        raw_html = raw_actions[index].get("raw_html") if index < len(raw_actions) else None
        candidates = extract_candidates(raw_html)
        if not candidates:
            candidates = [{"role": action["role"], "name": action["name"], "actionable": True}]
        target = {"role": action["role"], "name": action["name"]}
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
                "visible_elements": candidates,
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
                "operation": action["action_type"],
                "target_element": target,
                "blocked": False,
                "blocking_reason": None,
                "completion_progress": (index + 1) / len(parsed),
                "confidence": 1.0,
            },
        }
