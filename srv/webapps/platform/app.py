# /srv/webapps/platform/app.py

from flask import Flask, request, jsonify, send_from_directory, abort
from client_context import get_client_slug, get_client_paths
from data_access import load_json, save_json

# Placeholder module imports
from modules import payments

import json
from pathlib import Path

app = Flask(__name__)


# -------------------------------------------------------------------
# Helper functions for client-specific FRONTEND behavior
# -------------------------------------------------------------------

def load_client_settings(client_slug: str, paths=None) -> dict:
    """
    Load settings.json for a given client and derive useful paths.
    Expects settings at: <client_root>/config/settings.json
    """
    if paths is None:
        paths = get_client_paths(client_slug)

    config_dir: Path = paths["config_dir"]
    client_root: Path = paths["client_root"]

    settings_path = config_dir / "settings.json"
    if not settings_path.exists():
        raise FileNotFoundError(f"settings.json not found for client {client_slug}: {settings_path}")

    with settings_path.open("r") as f:
        settings = json.load(f)

    # Figure out where the frontend root lives
    frontend_dir = paths.get("frontend_dir", client_root / settings.get("frontend_root", "frontend"))
    if not frontend_dir.exists():
        raise FileNotFoundError(f"Frontend dir not found for client {client_slug}: {frontend_dir}")

    # Attach handy derived paths
    settings["_client_root"] = client_root
    settings["_config_dir"] = config_dir
    settings["_frontend_dir"] = frontend_dir

    # Backend data file (if you want to use it)
    backend_name = settings.get("backend_data_file", "backend_data.json")
    settings["_backend_data_path"] = client_root / backend_name

    return settings


def serve_client_file(frontend_root: Path, rel_path: str):
    """
    Serve a file relative to the client's frontend root.
    rel_path examples:
      'mycite.html'
      'webpage/home.html'
      'assets/imgs/logo.jpeg'
    """
    full_path = frontend_root / rel_path
    if not full_path.exists():
        abort(404)

    directory = str(full_path.parent)
    filename = full_path.name
    return send_from_directory(directory, filename)


def get_default_page(settings: dict) -> str:
    """
    Decide which page to serve at "/" based on settings.json.
    Settings keys:
      - default_view_mode: "auto" | "mysite" | "webpage"
      - mysite_page: e.g. "mycite.html"
      - webpage_home: e.g. "webpage/home.html"
      - fallback_index: e.g. "index.html"
    """
    mode = settings.get("default_view_mode", "auto")
    mysite_page = settings.get("mysite_page", "mycite.html")
    webpage_home = settings.get("webpage_home", "webpage/home.html")
    fallback_index = settings.get("fallback_index", "index.html")

    frontend_root: Path = settings["_frontend_dir"]

    home_full = frontend_root / webpage_home
    mysite_full = frontend_root / mysite_page
    fallback_full = frontend_root / fallback_index

    if mode == "mysite":
        # Always mycite.html
        if not mysite_full.exists():
            abort(404)
        return mysite_page

    if mode == "webpage":
        # Always webpage/home.html and 404 if missing
        if not home_full.exists():
            abort(404)
        return webpage_home

    # mode == "auto"
    if home_full.exists():
        return webpage_home
    if mysite_full.exists():
        return mysite_page
    if fallback_full.exists():
        return fallback_index

    abort(404)


# -------------------------------------------------------------------
# FRONTEND routes (client-specific HTML and static assets)
# -------------------------------------------------------------------

@app.route("/")
def client_root():
    """
    Root route for the domain.
    Uses client-specific settings.json to choose the landing page:
      - webpage/home.html (if present)
      - else mycite.html
      - else index.html (fallback)
    """
    client_slug = get_client_slug(request)
    paths = get_client_paths(client_slug)
    settings = load_client_settings(client_slug, paths=paths)

    rel_path = get_default_page(settings)
    return serve_client_file(settings["_frontend_dir"], rel_path)


@app.route("/mysite")
def mysite_view():
    """
    Explicit route to the MySite framework (e.g. mycite.html).
    """
    client_slug = get_client_slug(request)
    paths = get_client_paths(client_slug)
    settings = load_client_settings(client_slug, paths=paths)

    rel_path = settings.get("mysite_page", "mycite.html")
    return serve_client_file(settings["_frontend_dir"], rel_path)


@app.route("/webpage/<page_slug>")
def webpage_page(page_slug: str):
    """
    Serve pages under frontend/webpage/.
    Uses optional 'routes' mapping from settings.json, else pattern:
      /webpage/home            -> webpage/home.html
      /webpage/csa_browser     -> webpage/csa_browser.html
    """
    client_slug = get_client_slug(request)
    paths = get_client_paths(client_slug)
    settings = load_client_settings(client_slug, paths=paths)

    route_map = settings.get("routes", {})
    if page_slug in route_map:
        rel_path = route_map[page_slug]
    else:
        rel_path = f"webpage/{page_slug}.html"

    return serve_client_file(settings["_frontend_dir"], rel_path)


@app.route("/assets/<path:asset_path>")
def client_assets(asset_path: str):
    """
    Serve client-specific assets (images, etc.).
      /assets/imgs/logo.jpeg -> frontend/assets/imgs/logo.jpeg
    """
    client_slug = get_client_slug(request)
    paths = get_client_paths(client_slug)
    settings = load_client_settings(client_slug, paths=paths)

    rel_path = f"assets/{asset_path}"
    return serve_client_file(settings["_frontend_dir"], rel_path)


@app.route("/frontend/<path:static_path>")
def client_frontend_static(static_path: str):
    """
    Generic mapping for frontend files referenced like:
      /frontend/style.css
      /frontend/app.js
      /frontend/script.js
      /frontend/user_data.js
    which live under frontend/.
    """
    client_slug = get_client_slug(request)
    paths = get_client_paths(client_slug)
    settings = load_client_settings(client_slug, paths=paths)

    return serve_client_file(settings["_frontend_dir"], static_path)


# Catch-all for other front-end files that live directly under frontend/
# Placed AFTER all specific routes and AFTER /api/..., so it won't
# override your API endpoints.
@app.route("/<path:filename>")
def client_catch_all(filename: str):
    """
    For URLs like:
      /style.css
      /app.js
      /script.js
      /user_data.js
      /webpage.html
    that correspond directly to files under frontend/.
    """
    # Let /api/... be handled by API routes, not here.
    if filename.startswith("api/"):
        abort(404)

    client_slug = get_client_slug(request)
    paths = get_client_paths(client_slug)
    settings = load_client_settings(client_slug, paths=paths)

    return serve_client_file(settings["_frontend_dir"], filename)


# -------------------------------------------------------------------
# EXISTING API routes
# -------------------------------------------------------------------

@app.route("/api/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/api/inventory", methods=["GET"])
def get_inventory():
    """
    Example: GET /api/inventory
    Returns this client's inventory.json content.
    """
    client_slug = get_client_slug(request)
    paths = get_client_paths(client_slug)
    inventory_path = paths["data_dir"] / "inventory.json"

    inventory = load_json(inventory_path, default=[])
    return jsonify(inventory)


@app.route("/api/customers", methods=["GET"])
def get_customers():
    """
    Example: GET /api/customers
    Returns this client's customers.json (or donors.json, etc.).
    """
    client_slug = get_client_slug(request)
    paths = get_client_paths(client_slug)
    customers_path = paths["data_dir"] / "customers.json"  # adjust per client

    customers = load_json(customers_path, default=[])
    return jsonify(customers)


# --- Placeholder PayPal route ---
@app.route("/api/paypal/create-order", methods=["POST"])
def paypal_create_order():
    client_slug = get_client_slug(request)
    paths = get_client_paths(client_slug)

    # Delegate to payments module (placeholder)
    order = payments.create_order(request, client_slug, paths)
    return jsonify(order), 201


if __name__ == "__main__":
    # For development only; in production you'll use gunicorn/uwsgi
    app.run(host="0.0.0.0", port=5000, debug=True)

