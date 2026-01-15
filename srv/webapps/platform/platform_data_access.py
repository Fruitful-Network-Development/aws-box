from __future__ import annotations

from pathlib import Path
from typing import Any

from data_access import load_json

PLATFORM_ROOT = Path(__file__).resolve().parent
PLATFORM_DATA_DIR = PLATFORM_ROOT / "data"


def load_platform_json(filename: str) -> Any:
    """Load a JSON file from the platform data directory."""

    clean_name = Path(filename).name
    if clean_name != filename:
        raise ValueError("Platform data filenames cannot include directories")

    target = (PLATFORM_DATA_DIR / clean_name).resolve()
    try:
        target.relative_to(PLATFORM_DATA_DIR)
    except ValueError as exc:
        raise ValueError("Resolved platform data path escapes the data directory") from exc

    if not target.exists():
        raise FileNotFoundError(f"Platform data file not found: {clean_name}")

    return load_json(target)
