"""JSON persistence for TinyWorld replays."""

from __future__ import annotations

import json
from os import PathLike
from pathlib import Path
import time
from typing import TYPE_CHECKING

from .recorder import ReplayRecorder

if TYPE_CHECKING:
    from ..state import ApplicationState


def save_replay(recorder: ReplayRecorder, path: str | PathLike[str]) -> Path:
    """Save indented UTF-8 JSON and return its path."""
    destination = Path(path)
    destination.write_text(
        json.dumps(recorder.to_dict(), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return destination


def load_replay(path: str | PathLike[str]) -> ReplayRecorder:
    """Load a replay from a JSON file."""
    source = Path(path)
    data = json.loads(source.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("replay JSON root must be an object")
    return ReplayRecorder.from_dict(data)


def save_application_replay(
    state: "ApplicationState",
    path: str | PathLike[str],
) -> Path:
    """Add save metadata and persist the current application replay."""
    state.recorder.metadata["saved_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    destination = state.recorder.save(path)
    print(f"Replay saved to: {destination}")
    return destination
