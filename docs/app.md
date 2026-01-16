# Shared Platform Application (Flask)

This document describes the Flask application under `srv/webapps/platform`. The
platform is intentionally minimal and domain-agnostic: it only provides a
handful of JSON endpoints while Nginx serves all static assets directly from the
client `frontend/` folders.

## Purpose

The shared platform exists for two reasons:

1. **Manifest lookup**: determine which client is making a request based on the
   incoming host header and load that client’s manifest file.
2. **Dataset registry**: expose read-only JSON data to the frontend through
   stable API routes. Data files must live under a client’s `data/` directory
   and be explicitly whitelisted in the manifest.

Keeping the API surface this small allows multiple client domains to be hosted
on the same server without leaking data between tenants.

## Running the app

On the server the app is executed by Gunicorn via `platform.service`. The unit
file starts Gunicorn using the venv binary:

```
ExecStart=/srv/webapps/platform/venv/bin/gunicorn
```

The application entry point lives in `app.py` and is referenced as
`platform.app:app` in the unit file. The backend listens on `127.0.0.1:8000` and
Nginx proxies `/api/` requests to this port.

To restart the app after code changes:

```bash
sudo systemctl restart platform.service
sudo systemctl status platform.service --no-pager
```

## Data-access files (the two main helpers)

The Flask platform relies on two data-access modules, both created from scratch
and intentionally scoped to avoid reusing older data-access code:

- `multi-tennant-data-access.py`
  - Determines the client slug from the request host header.
  - Locates client directories under `/srv/webapps/clients/<domain>`.
  - Loads a client manifest (`msn_*.json`) and normalizes key settings.
- `client-data-acess.py`
  - Lists whitelisted dataset IDs based on the manifest’s `backend_data` list.
  - Resolves dataset IDs and backend data filenames to safe paths under a
    client’s `data/` directory.

Because these filenames contain hyphens, the Flask app loads them via
`importlib` instead of standard Python imports.

## Manifest lookup and data access flow

1. **Client detection**: `multi-tennant-data-access.py` inspects `X-Forwarded-Host`
   or `Host` to determine the client slug. It falls back to
   `DEFAULT_CLIENT_SLUG` when the host doesn’t match a known client directory.
2. **Manifest loading**: the manifest is discovered by searching for
   `msn_*.json` at the root of the client directory. The manifest’s `MSS` section
   can set `frontend_root`, `default_entry`, and `backend_data`.
3. **Dataset registry**:
   - `GET /api/datasets` returns the dataset IDs derived from the manifest’s
     `backend_data` list (filenames without the `.json` extension).
   - `GET /api/datasets/<dataset_id>` resolves the dataset ID to a file under
     the client’s `data/` directory and returns its JSON contents.

## Customizing manifest location

By default, manifests live at the root of each client directory. If you want to
move the manifest elsewhere, update the `_find_manifest_file` helper in
`multi-tennant-data-access.py` and ensure the new location is still under the
client root.

## API endpoints

The Flask app exposes two main routes. All responses are JSON:

- `GET /api/datasets` – Returns an array of dataset IDs. Each ID corresponds to a
  file in the client’s `data/` directory that has been whitelisted in the
  manifest.
- `GET /api/datasets/<dataset_id>` – Returns the contents of the specified
  dataset file. The file must be listed in the manifest and exist under
  `data/`.

Dataset IDs are derived from filenames (e.g. `3_2_3_17_77_19_10_1_1`). They do
not include the `.json` extension in the API path.

## Adding new endpoints

If you need additional functionality (for example, returning other types of
JSON data or adding POST routes), create Flask Blueprints under `modules/` and
register them in `app.py`. Keep these guidelines in mind:

1. Avoid exposing arbitrary filesystem paths. Always restrict file reads to a
   known directory and validate inputs.
2. Use the manifest to control per-client behavior. Adding keys to the manifest
   allows new features to be toggled on/off per client.
3. Keep the core app minimal. Complex business logic should live in separate
   services, called asynchronously if necessary.
