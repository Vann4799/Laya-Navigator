"""Laya typed-decision predictor boundary.

The actual checkpoint loading will be added after the first public-dataset
normalization and baseline notebook are verified.
"""

from __future__ import annotations

from typing import Any


def predict(state: dict[str, Any]) -> dict[str, Any]:
    """Placeholder contract for page_state/goal/next_action inference."""
    raise NotImplementedError("Load the Laya checkpoint before inference")
