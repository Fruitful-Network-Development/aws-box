from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any, Dict, List

MODULE_DIR = Path(__file__).resolve().parent


def _load_multi_module():
    module_name = "multi_tennant_data_access"
    if module_name in sys.modules:
        return sys.modules[module_name]

    module_path = MODULE_DIR / "multi-tennant-data-access.py"
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise ImportError("Unable to load multi-tenant data access module")

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


_multi = _load_multi_module()


def _normalize_filename(value: str) -> str:
    clean = Path(value).name
    if clean != value:
        raise ValueError("Dataset filenames cannot include directories")
    return clean


def _dataset_id_from_filename(filename: str) -> str:
    return Path(filename).stem


def _allowed_backend_files(manifest: Dict[str, Any]) -> List[str]:
    allowed = manifest.get("backend_data")
    if not isinstance(allowed, list):
        return []
    return [_normalize_filename(str(name)) for name in allowed if name]


def list_client_dataset_ids(
    paths: Dict[str, Path], manifest: Dict[str, Any]
) -> List[str]:
    """Return dataset IDs for the client based on its manifest."""
    data_dir = paths["data_dir"].resolve()
    dataset_ids = []

    for filename in _allowed_backend_files(manifest):
        if Path(filename).suffix.lower() != ".json":
            continue

        target = (data_dir / filename).resolve()
        try:
            target.relative_to(data_dir)
        except ValueError:
            continue

        if target.exists():
            dataset_ids.append(_dataset_id_from_filename(filename))

    return sorted(set(dataset_ids))


def resolve_client_dataset_path(
    paths: Dict[str, Path], manifest: Dict[str, Any], dataset_id: str
) -> Path:
    """Resolve a dataset ID to a JSON file path inside the client data dir."""
    data_dir = paths["data_dir"].resolve()
    candidates = {}

    for filename in _allowed_backend_files(manifest):
        if Path(filename).suffix.lower() != ".json":
            continue
        candidates[_dataset_id_from_filename(filename)] = filename

    match = candidates.get(dataset_id)
    if not match:
        raise ValueError("Requested dataset is not registered for this client")

    target = (data_dir / match).resolve()
    try:
        target.relative_to(data_dir)
    except ValueError as exc:
        raise ValueError("Resolved dataset path escapes the data directory") from exc

    return target


def resolve_backend_data_path(
    paths: Dict[str, Path], manifest: Dict[str, Any], filename: str
) -> Path:
    """Resolve a manifest-declared backend data filename to a safe path."""
    clean_name = _normalize_filename(filename)

    allowed = set(_allowed_backend_files(manifest))
    if clean_name not in allowed:
        raise ValueError("Requested file is not declared in backend_data list")

    data_dir = paths["data_dir"].resolve()
    target = (data_dir / clean_name).resolve()

    try:
        target.relative_to(data_dir)
    except ValueError as exc:
        raise ValueError("Resolved backend data path escapes the data directory") from exc

    return target


def get_client_dataset_ids(request) -> List[str]:
    """List dataset IDs available for the current request's client."""
    client_slug = _multi.get_client_slug(request)
    paths = _multi.get_client_paths(client_slug)
    manifest = _multi.load_client_manifest(paths)
    return list_client_dataset_ids(paths, manifest)


def resolve_client_dataset_for_request(request, dataset_id: str) -> Path:
    """Resolve a dataset path for the current request's client."""
    client_slug = _multi.get_client_slug(request)
    paths = _multi.get_client_paths(client_slug)
    manifest = _multi.load_client_manifest(paths)
    return resolve_client_dataset_path(paths, manifest, dataset_id)
