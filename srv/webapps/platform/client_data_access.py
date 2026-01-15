from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from data_access import get_client_paths, get_client_slug, load_client_manifest


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
    return sorted(
        (data_dir / _normalize_dataset_name(name)).resolve()
        for name in backend_data
    )


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


def get_client_dataset_ids(request) -> List[str]:
    """List dataset IDs available for the current client request."""

    client_slug = get_client_slug(request)
    paths = get_client_paths(client_slug)
    manifest = load_client_manifest(paths)
    return list_client_dataset_ids(paths, manifest)


def resolve_client_dataset_for_request(request, dataset_id: str) -> Path:
    """Resolve a dataset path for the current client request."""

    client_slug = get_client_slug(request)
    paths = get_client_paths(client_slug)
    manifest = load_client_manifest(paths)
    return resolve_client_dataset_path(paths, manifest, dataset_id)
