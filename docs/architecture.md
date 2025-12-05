# Platform architecture and MSN standard

## Server topology
- **Nginx** provides virtual hosts per domain, serves static client frontends, and proxies `/api/` to the shared Flask backend.
- **Flask (srv/webapps/platform/app.py)** is a single multi-tenant app that discovers client manifests, serves the correct frontend entry, and exposes JSON APIs.
- **Clients** live under `/srv/webapps/clients/<domain>/` with `frontend/` assets and optional `data/` files that may be whitelisted for backend access.

## Directory layout
```
etc/
  nginx/                 # Nginx config and vhost definitions
srv/webapps/
  platform/
    app.py               # Flask app and manifest-driven routing
    data_access.py       # Manifest loading + backend data path validation
    modules/
      weather.py         # Weather Blueprint (Open-Meteo daily forecast)
  clients/
    <domain>/
      frontend/          # Universal index + msn_<userId>.json + assets
      data/              # Optional backend_data files referenced by manifest
scripts/                 # Deployment helpers (update_code, deploy_srv, deploy_nginx, deploy_all)
```

## MSN standardization flow
- Each client has exactly one manifest named `msn_<userId>.json`; it is the single source of truth for site config and the `backend_data` whitelist.
- The universal `index.html` embeds MSN metadata:
  ```html
  <meta name="msn-id" content="<userId>">
  <meta name="msn-config" content="msn_<userId>.json">
  ```
- On startup, Flask scans client frontends for the manifest, extracts the `userId`, and builds an in-memory map of domains to manifest metadata (user id, manifest filename, frontend path).
- Routes can use the Host header or provided user id to resolve which manifest to serve or which data files are allowed.

## Discovery and APIs
- Example endpoints aligned with the manifest scan:
  - `/api/site/<user_id>.json` → returns the manifest for that user id.
  - `/api/sites` → optional directory of discovered sites with their user ids and manifest names.
- Manifest-driven routing ensures each request serves the correct frontend entry (`default_entry` from the manifest) and enforces backend file access to the manifest-declared `backend_data` list.

## Universal index template expectations
- A single template should generate every client `index.html`, injecting the MSN meta tags and loading a shared `build.js`.
- Frontend code reads the MSN metadata (or `window.MSN_CONFIG`), fetches `/api/msn/<userId>.json` or the same-origin manifest file, and renders dynamically based on the manifest contents.

## Error handling expectations
- Startup should flag missing or multiple manifests per client directory.
- API routes must validate query parameters and user ids and return clear 4xx errors for invalid input or 5xx/502 when upstream dependencies fail.
