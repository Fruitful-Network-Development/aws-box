# /srv/webapps/platform/app.py

from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory, abort


MODULE_DIR = Path(__file__).resolve().parent


def _load_data_module(module_name: str, filename: str):
    if module_name in sys.modules:
        return sys.modules[module_name]

    module_path = MODULE_DIR / filename
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load module: {filename}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


multi_access = _load_data_module(
    "multi_tennant_data_access", "multi-tennant-data-access.py"
)
client_access = _load_data_module(
    "client_data_acess", "client-data-acess.py"
)

get_client_paths = multi_access.get_client_paths
get_client_slug = multi_access.get_client_slug
load_client_manifest = multi_access.load_client_manifest
load_json = multi_access.load_json
save_json = multi_access.save_json

get_client_dataset_ids = client_access.get_client_dataset_ids
resolve_client_dataset_for_request = client_access.resolve_client_dataset_for_request
resolve_backend_data_path = client_access.resolve_backend_data_path



def validate_env(
    required: list[str] | None = None, optional: dict[str, str] | None = None
) -> dict[str, str]:
    if required is None:
        required = []
    if optional is None:
        optional = {}

    config = {}
    missing = []

    for var in required:
        value = os.getenv(var)
        if not value:
            missing.append(var)
        else:
            config[var] = value

    if missing:
        raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

    for var, default in optional.items():
        config[var] = os.getenv(var, default)

    return config


# Validate core environment variables
try:
    env_config = validate_env(
        required=['FLASK_SECRET_KEY'],
        optional={
            'FLASK_DEBUG': '0',
            'FLASK_ENABLE_CORS': '0'
        }
    )
except ValueError as e:
    # In development, allow missing FLASK_SECRET_KEY with a clear warning
    if os.getenv('FLASK_ENV') != 'production':
        env_config = {
            'FLASK_SECRET_KEY': 'DEV-ONLY-INSECURE-KEY-DO-NOT-USE-IN-PRODUCTION',
            'FLASK_DEBUG': os.getenv('FLASK_DEBUG', '0'),
            'FLASK_ENABLE_CORS': os.getenv('FLASK_ENABLE_CORS', '0')
        }
        print("⚠️  WARNING: Using development-only SECRET_KEY. Set FLASK_SECRET_KEY in production!")
    else:
        raise


app = Flask(__name__)

app.config['SECRET_KEY'] = env_config['FLASK_SECRET_KEY']

app.config['DEBUG'] = env_config['FLASK_DEBUG'] in ('1', 'true', 'True', 'yes', 'Yes')

app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False  # Disable pretty JSON in production
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 31536000  # Cache static files for 1 year


if env_config['FLASK_ENABLE_CORS'] == '1':
    try:
        from flask_cors import CORS
        allowed_origins = os.getenv('ALLOWED_ORIGINS', '').split(',') if os.getenv('ALLOWED_ORIGINS') else ['*']
        CORS(app, resources={r"/api/*": {"origins": allowed_origins}})
        print("✓ CORS enabled for /api/* routes")
    except ImportError:
        print("⚠️  WARNING: FLASK_ENABLE_CORS is set but flask-cors is not installed.")
        print("   Install with: pip install flask-cors")


@app.errorhandler(404)
def not_found(error):
    """Handle 404 Not Found errors."""
    return 'Not Found', 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 Internal Server Error."""
    return 'Internal Server Error', 500


def load_client_settings(client_slug: str, paths=None) -> dict:
    if paths is None:
        paths = get_client_paths(client_slug)

    manifest = load_client_manifest(paths)

    frontend_dir = manifest["frontend_dir"]
    if not frontend_dir.exists():
        raise FileNotFoundError(
            f"Frontend dir not found for client {client_slug}: {frontend_dir}"
        )

    return manifest


def serve_client_file(frontend_root: Path, rel_path: str):
    """
    Serve a file relative to the client's frontend root.

    rel_path examples:
      'index.html'
      'script.js'
      'msn_<user_id>.json'
      'assets/imgs/logo.jpeg'
      'style.css'
    """
    full_path = frontend_root / rel_path
    if not full_path.exists():
        abort(404)

    return send_from_directory(full_path.parent, full_path.name)


app.register_blueprint(donation_receipts_bp)
app.register_blueprint(catalog_bp)


@app.route("/api/backend-data/<path:data_filename>", methods=["GET", "PUT"])
def backend_data(data_filename: str):
    """Read or write backend data declared in the client's msn_<user>.json."""

    client_slug = get_client_slug(request)
    paths = get_client_paths(client_slug)
    settings = load_client_settings(client_slug, paths=paths)

    try:
        target_path = resolve_backend_data_path(paths, settings, data_filename)
    except ValueError as exc:
        return jsonify({"error": "invalid_backend_data", "message": str(exc)}), 400

    if request.method == "GET":
        if not target_path.exists():
            abort(404)

        return jsonify(load_json(target_path))

    try:
        payload = request.get_json(force=True)
    except Exception:
        return (
            jsonify(
                {
                    "error": "invalid_json",
                    "message": "Request body must be valid JSON",
                }
            ),
            400,
        )

    save_json(target_path, payload)
    return jsonify({"status": "ok"})


@app.route("/api/datasets", methods=["GET"])
def list_datasets():
    client_slug = get_client_slug(request)

    return jsonify(
        {
            "client": client_slug,
            "datasets": get_client_dataset_ids(request),
        }
    )


@app.route("/api/datasets/<string:dataset_id>", methods=["GET"])
def load_dataset(dataset_id: str):
    try:
        dataset_path = resolve_client_dataset_for_request(request, dataset_id)
    except ValueError as exc:
        return jsonify({"error": "invalid_dataset", "message": str(exc)}), 400

    if not dataset_path.exists():
        abort(404)

    return jsonify(load_json(dataset_path))


@app.route("/")
def client_root():
    client_slug = get_client_slug(request)
    paths = get_client_paths(client_slug)
    settings = load_client_settings(client_slug, paths=paths)

    rel_path = settings.get("default_entry", "index.html")
    return serve_client_file(settings["frontend_dir"], rel_path)


@app.route("/assets/<path:asset_path>")
def client_assets(asset_path: str):
    """
    Serve client-specific assets (images, fonts, etc.) under frontend/assets/.
      /assets/imgs/logo.jpeg -> frontend/assets/imgs/logo.jpeg
    
    """
    client_slug = get_client_slug(request)
    paths = get_client_paths(client_slug)
    settings = load_client_settings(client_slug, paths=paths)

    rel_path = f"assets/{asset_path}"
    return serve_client_file(settings["frontend_dir"], rel_path)


@app.route("/frontend/<path:static_path>")
def client_frontend_static(static_path: str):
    """
    Serve files addressed explicitly under /frontend/, like:
      /frontend/style.css
      /frontend/app.js
      /frontend/script.js
      /frontend/msn_<user_id>.json
    
    """
    client_slug = get_client_slug(request)
    paths = get_client_paths(client_slug)
    settings = load_client_settings(client_slug, paths=paths)

    return serve_client_file(settings["frontend_dir"], static_path)


@app.route("/<path:filename>")
def client_catch_all(filename: str):
    """
    Catch-all for other front-end files that live directly under frontend/.

    Examples:
      /style.css
      /app.js
      /script.js
      /msn_<user_id>.json
      /mycite.html
      /demo-design-1  -> demo-design-1.html
    (Note: /api/... is reserved for API endpoints.)
    
    """
    if filename.startswith("api/"):
        abort(404)

    client_slug = get_client_slug(request)
    paths = get_client_paths(client_slug)
    settings = load_client_settings(client_slug, paths=paths)

    # If the filename has no extension, assume it's an .html page
    if "." not in filename:
        filename = f"{filename}.html"

    return serve_client_file(settings["frontend_dir"], filename)


@app.route("/api/health")
def health():
    return jsonify({"status": "ok"})


# -------------------------------------------------------------------
# Development Server (for local testing only)
# -------------------------------------------------------------------
# In production, use Gunicorn or uWSGI behind Nginx.
# The DEBUG flag from environment variables controls whether debug mode is enabled.


if __name__ == "__main__":
    # For development only; in production use gunicorn/uwsgi behind NGINX
    app.run(host="0.0.0.0", port=5000, debug=app.config['DEBUG'])
