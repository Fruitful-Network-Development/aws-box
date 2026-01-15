from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

# ===============================================================================
#                             Multi-tenant Data Access
# ===============================================================================

# Base directories for locating client sites and data
PLATFORM_ROOT = Path(__file__).resolve().parent
WEBAPPS_ROOT = PLATFORM_ROOT.parent
CLIENTS_ROOT = WEBAPPS_ROOT / "clients"

# Default client fallback when the host header doesn't match a known site.
DEFAULT_CLIENT_SLUG = os.getenv(
    "DEFAULT_CLIENT_SLUG", "fruitfulnetworkdevelopment.com"
)


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def get_client_slug(request) -> str:
    """Determine which client to serve based on the Host header."""

    host = (request.headers.get("X-Forwarded-Host") or request.host or "").split(":")[0]
    candidate_root = CLIENTS_ROOT / host
    if candidate_root.exists():
        return host

    return DEFAULT_CLIENT_SLUG


def get_client_paths(client_slug: str) -> Dict[str, Path]:
    """Return key filesystem locations for a client."""

    client_root = CLIENTS_ROOT / client_slug
    frontend_dir = client_root / "frontend"
    data_dir = client_root / "data"

    return {
        "client_root": client_root,
        "frontend_dir": frontend_dir,
        "data_dir": data_dir,
    }


def _find_manifest(client_root: Path) -> Optional[Path]:
    matches = sorted(client_root.glob("msn_*.json"))
    return matches[0] if matches else None


def load_client_manifest(paths: Dict[str, Path]) -> Dict[str, Any]:
    client_root = paths["client_root"]
    manifest_path = _find_manifest(client_root)
    if manifest_path:
        manifest = load_json(manifest_path)
    else:
        manifest = {}

    mss = manifest.get("MSS") or {}
    backend_data = mss.get("backend_data") or []
    if not isinstance(backend_data, list):
        backend_data = []

    frontend_root_setting = mss.get("frontend_root", "frontend")
    if Path(frontend_root_setting).is_absolute():
        resolved_frontend_dir = Path(frontend_root_setting)
    else:
        resolved_frontend_dir = (paths["client_root"] / frontend_root_setting).resolve()

    return {
        "manifest_path": manifest_path,
        "frontend_dir": resolved_frontend_dir,
        "default_entry": mss.get("default_entry", "index.html"),
        "backend_data": backend_data,
    }
