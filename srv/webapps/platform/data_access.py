from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

# ===============================================================================
#                             Multi-tenant Data Acess
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


def _find_manifest(frontend_dir: Path) -> Optional[Path]:
    matches = sorted(frontend_dir.glob("msn_*.json"))
    if not matches:
        return None

    return matches[0]


def load_client_manifest(paths: Dict[str, Path]) -> Dict[str, Any]:
    """Load msn_<user>.json for a client and expose default + backend data info."""

    frontend_dir = paths["frontend_dir"]
    manifest_path = _find_manifest(frontend_dir)
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


def _normalize_dataset_name(filename: str) -> str:
    clean_name = Path(filename).name
    if clean_name != filename:
        raise ValueError("Dataset filenames cannot include directories")
    return clean_name


def _dataset_id_from_filename(filename: str) -> str:
    return Path(filename).stem


def _list_allowed_dataset_files(
    data_dir: Path, manifest: Dict[str, Any]
) -> List[Path]:
    backend_data = manifest.get("backend_data") or []
    if backend_data:
        return sorted(
            (data_dir / _normalize_dataset_name(name)).resolve()
            for name in backend_data
        )

    return sorted(path.resolve() for path in data_dir.glob("*.json"))


def list_client_dataset_ids(
    paths: Dict[str, Path], manifest: Dict[str, Any]
) -> List[str]:
    """Return dataset IDs available for the client based on manifest/data dir."""

    data_dir = paths["data_dir"].resolve()
    dataset_files = _list_allowed_dataset_files(data_dir, manifest)
    dataset_ids = []
    for path in dataset_files:
        try:
            path.relative_to(data_dir)
        except ValueError:
            continue
        if path.suffix.lower() != ".json":
            continue
        dataset_ids.append(_dataset_id_from_filename(path.name))
    return sorted(set(dataset_ids))


def resolve_client_dataset_path(
    paths: Dict[str, Path], manifest: Dict[str, Any], dataset_id: str
) -> Path:
    """Resolve a dataset ID to a JSON file path within the client data dir."""

    data_dir = paths["data_dir"].resolve()
    dataset_files = _list_allowed_dataset_files(data_dir, manifest)
    lookup = {_dataset_id_from_filename(path.name): path for path in dataset_files}
    target = lookup.get(dataset_id)
    if not target:
        raise ValueError("Requested dataset is not registered for this client")

    try:
        target.relative_to(data_dir)
    except ValueError:
        raise ValueError("Resolved dataset path escapes the data directory")

    return target


def resolve_backend_data_path(
    paths: Dict[str, Path], manifest: Dict[str, Any], filename: str
) -> Path:
    """Validate and resolve a backend data filename declared in the manifest."""

    clean_name = Path(filename).name
    if clean_name != filename:
        raise ValueError("Backend data filenames cannot include directories")

    allowed = {Path(name).name for name in manifest.get("backend_data", [])}
    if clean_name not in allowed:
        raise ValueError("Requested file is not declared in backend_data list")

    data_dir = paths["data_dir"].resolve()
    target = (data_dir / clean_name).resolve()

    try:
        target.relative_to(data_dir)
    except ValueError:
        raise ValueError("Resolved backend data path escapes the data directory")

    return target

# ===============================================================================
#                            Cient-Spesific Data Acess
# ===============================================================================

# HERE
