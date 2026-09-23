"""Streaming public-dataset I/O helpers."""

from __future__ import annotations

import json
import urllib.request
from collections.abc import Iterator
from pathlib import Path
from typing import Any


def iter_json_array(path: Path, chunk_size: int = 1024 * 1024) -> Iterator[dict[str, Any]]:
    """Yield objects from a top-level JSON array without loading the array at once."""
    decoder = json.JSONDecoder()
    buffer = ""
    started = False
    finished = False
    with path.open("r", encoding="utf-8") as handle:
        while not finished:
            chunk = handle.read(chunk_size)
            if chunk:
                buffer += chunk
            else:
                finished = True
            while True:
                buffer = buffer.lstrip()
                if not started:
                    if not buffer:
                        break
                    if buffer[0] != "[":
                        raise ValueError("expected a top-level JSON array")
                    started = True
                    buffer = buffer[1:]
                    continue
                buffer = buffer.lstrip()
                if not buffer:
                    break
                if buffer[0] == "]":
                    return
                try:
                    value, end = decoder.raw_decode(buffer)
                except json.JSONDecodeError:
                    if finished:
                        raise ValueError("truncated JSON array")
                    break
                if not isinstance(value, dict):
                    raise ValueError("expected JSON objects inside the array")
                yield value
                buffer = buffer[end:].lstrip()
                if buffer.startswith(","):
                    buffer = buffer[1:]
                elif buffer.startswith("]"):
                    return
                elif buffer and finished:
                    raise ValueError("expected comma or closing bracket")


def download_url(url: str, destination: Path) -> None:
    """Download a public source file with streaming writes."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(url, headers={"User-Agent": "laya-navigator/0.1"})
    with urllib.request.urlopen(request, timeout=120) as response, destination.open("wb") as output:
        while chunk := response.read(1024 * 1024):
            output.write(chunk)
