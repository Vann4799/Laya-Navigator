"""Convert noisy DOM/accessibility observations into compact workflow state.

Implementation is intentionally separate from the Laya predictor so the same
state contract can be used for training, evaluation, and production inference.
"""

from __future__ import annotations

from typing import Any


def compact_state(observation: dict[str, Any]) -> dict[str, Any]:
    """Return the stable v0.1 state fields from a browser observation."""
    return {
        "app": observation.get("app", "unknown"),
        "workflow": observation.get("workflow"),
        "route": observation.get("route", ""),
        "page_title": observation.get("page_title", ""),
        "auth_state": observation.get("auth_state", "unknown"),
        "visible_elements": observation.get("visible_elements", []),
        "form_fields": observation.get("form_fields", []),
        "history": observation.get("history", []),
        "event_log": observation.get("event_log", []),
        "last_action": observation.get("last_action"),
        "errors": observation.get("errors", []),
    }
