"""Deterministic app-held-out dataset splitting."""

from __future__ import annotations

import random
from collections import defaultdict
from typing import Any


def split_rows_by_app(
    rows: list[dict[str, Any]],
    seed: int = 42,
    train_ratio: float = 0.8,
    val_ratio: float = 0.1,
) -> dict[str, list[dict[str, Any]]]:
    """Split rows by app so no app appears in more than one split."""
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[str(row.get("app", "unknown"))].append(row)
    apps = list(groups)
    random.Random(seed).shuffle(apps)
    n = len(apps)
    if n < 3:
        raise ValueError("at least 3 unique apps are required for app-held-out splitting")
    n_val = max(1, round(n * val_ratio))
    n_test = max(1, round(n * (1 - train_ratio - val_ratio)))
    n_train = n - n_val - n_test
    if n_train < 1:
        n_train, n_val, n_test = n - 2, 1, 1
    assignments = {
        "train": apps[:n_train],
        "val": apps[n_train : n_train + n_val],
        "test": apps[n_train + n_val :],
    }
    return {
        split: [row for app in split_apps for row in groups[app]]
        for split, split_apps in assignments.items()
    }
