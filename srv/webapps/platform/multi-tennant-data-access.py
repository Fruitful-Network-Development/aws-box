from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

PLATFORM_ROOT = Path(__file__).resolve().parent
WEBAPPS_ROOT = PLATFORM_ROOT.parent
CLIENTS_ROOT = WEBAPPS_ROOT / "clients"
PLATFORM_DATA_DIR = PLATFORM_ROOT / "data"

DEFAULT_CLIENT_SLUG = os.getenv(
    "DEFAULT_CLIENT_SLUG", "fruitfulnetworkdevelopment.com"
)


def load_json(path: Path) -> Any:
    """Load JSON content from disk."""
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def save_json(path: Path, payload: Any) -> None:
    """Persist JSON content, ensuring parent directories exist."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)


def _extract_host(request) -> str:
    forwarded = request.headers.get("X-Forwarded-Host") or ""
    raw_host = forwarded or request.host or ""
    primary_host = raw_host.split(",", maxsplit=1)[0].strip()
    return primary_host.split(":", maxsplit=1)[0].strip()


def get_client_slug(request) -> str:
    """Choose which client directory to serve based on the request host."""
    host = _extract_host(request)
    if host:
        candidate = CLIENTS_ROOT / host
        if candidate.exists():
            return host
    return DEFAULT_CLIENT_SLUG


def get_client_paths(client_slug: str) -> Dict[str, Path]:
    """Return key filesystem roots for a given client."""
    client_root = CLIENTS_ROOT / client_slug
    return {
        "client_root": client_root,
        "frontend_dir": client_root / "frontend",
        "data_dir": client_root / "data",
        "platform_data_dir": PLATFORM_DATA_DIR,
    }


def _find_manifest_file(client_root: Path) -> Optional[Path]:
    matches = sorted(client_root.glob("msn_*.json"))
    return matches[0] if matches else None


def _as_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value if isinstance(item, (str, bytes))]
    return []


def load_client_manifest(paths: Dict[str, Path]) -> Dict[str, Any]:
    """Load the client manifest and normalize key settings."""
    client_root = paths["client_root"]
    manifest_path = _find_manifest_file(client_root)
    manifest = load_json(manifest_path) if manifest_path else {}

    settings = manifest.get("MSS") if isinstance(manifest, dict) else {}
    if not isinstance(settings, dict):
        settings = {}

    frontend_root = settings.get("frontend_root") or "frontend"
    if Path(frontend_root).is_absolute():
        frontend_dir = Path(frontend_root)
    else:
        frontend_dir = (client_root / frontend_root).resolve()

    return {
        "manifest_path": manifest_path,
        "frontend_dir": frontend_dir,
        "default_entry": settings.get("default_entry") or "index.html",
        "backend_data": _as_list(settings.get("backend_data")),
    }
