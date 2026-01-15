Shared Platform Application (Flask)
This document describes the internal structure of the Flask application in srv/webapps/platform and how to customize it. The app is designed to be domain‑agnostic and to serve only a small set of API endpoints. Static content (HTML, CSS, JS) is served by nginx and does not involve Python.
Purpose
The shared platform provides two core capabilities:
    1. Manifest lookup: Determine which client is making a request based on the incoming host header and load that client’s manifest file. The manifest describes the site (titles, logos, etc.) and lists backend data files that may be served via the API.
    2. Dataset registry: Expose read‑only JSON data to the front‑end through stable API routes. Data files must live under a client’s data/ directory and be explicitly whitelisted in the manifest.
By keeping the platform API simple, multiple client domains can be hosted on the same server without risk of data leakage or accidental access to arbitrary files.
Running the app
On the server the app is executed by Gunicorn via a systemd service (platform.service). The unit file starts Gunicorn using the venv’s binary (ExecStart=/srv/webapps/platform/venv/bin/gunicorn). The application factory lives in app.py and is referenced as platform.app:app in the unit file. The backend listens on 127.0.0.1:8000; nginx proxies /api/ requests to this port when configured.
To restart the app after code changes run:
sudo systemctl restart platform.service
sudo systemctl status platform.service --no-pager
Manifest lookup and data access
The heart of the backend is data_access.py, which performs two tasks:
    1. Client detection: It inspects the Host header of the incoming request and derives a client slug (e.g. fruitfulnetworkdevelopment.com). The slug is used to locate the client directory under /srv/webapps/clients.
    2. Manifest loading: It searches for a file matching msn_*.json inside the client directory. In this repository we choose to store the manifest at the root of each client directory (not inside frontend/). If you want to move the manifest elsewhere you must adjust the _find_manifest helper in data_access.py to search the correct location.
When a request targets /api/datasets, data_access.py reads the manifest’s backend_data array and returns the list of file basenames relative to the client’s data/ directory. When a request targets /api/datasets/<dataset_id>, it resolves <dataset_id> against the client’s data/ directory and ensures the file is whitelisted before returning its contents.
Customizing the manifest location
The default implementation of _find_manifest in data_access.py looks for files named msn_*.json under a provided path. Earlier versions of the platform stored the manifest in frontend/; this repository stores the manifest at the root of the client directory. To change where the manifest is found:
    • Open data_access.py and locate the _find_manifest function.
    • Modify the search path from frontend_dir.glob("msn_*.json") to client_root.glob("msn_*.json") or any path you prefer.
    • Ensure that load_client_manifest passes the correct base directory to _find_manifest.
After making changes, restart platform.service.
API endpoints
The Flask app exposes two main routes. All responses are JSON:
    • GET /api/datasets – Returns an array of dataset IDs. Each ID corresponds to a file in the client’s data/ directory that has been whitelisted in the manifest.
    • GET /api/datasets/<dataset_id> – Returns the contents of the specified dataset file. The file must be listed in the manifest and exist under data/. Attempting to access a file that is not in backend_data will result in a 404.
Dataset IDs are derived from filenames (e.g. 3_2_3_17_77_19_10_1_1). They do not include the .json extension in the API path. Clients should persist only the ID portion and rely on the API to resolve it.
Adding new endpoints
If you need additional functionality (for example, returning other types of data, adding POST routes, or integrating third‑party services), you can create Flask Blueprints under a modules/ directory and register them in app.py. Keep the following guidelines in mind:
    1. Avoid exposing arbitrary filesystem paths. Always restrict file reads to a known directory and validate inputs.
    2. Use the manifest to control per‑client behavior. Adding keys to the manifest allows new features to be toggled on/off per client.
    3. Keep the core app minimal. Complex business logic should live in separate services, called asynchronously if necessary.
Refer to Flask’s documentation for blueprint patterns and to the existing data_access.py code for examples of safe file handling.
Changing where manifests live
The design of this repository expects msn_<user>.json to live at the root of each client folder. Moving it elsewhere is possible but requires synchronizing changes across:
    • The manifest itself (so it doesn’t get left behind).
    • The nginx configuration if you want to restrict access to certain subdirectories.
    • The data_access.py lookup logic as described above.
For simplicity we recommend leaving the manifest at the client root. It visually signals that there is special metadata associated with the client and keeps the frontend/ folder dedicated to static assets.
