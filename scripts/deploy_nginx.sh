# This script will mirror ~/awsDev/etc/nginx/ onto /etc/nginx/, then test and reload nginx.
#!/bin/bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

SRC="$PROJECT_ROOT/etc/nginx/"
DST="/etc/nginx/"

echo "=== Deploying etc/nginx → $DST"
echo "Source: $SRC"
echo

# WARNING: --delete removes files under /etc/nginx that are not in repo/etc/nginx
sudo rsync -az --delete "$SRC" "$DST"

echo
echo "=== Testing nginx configuration..."
sudo nginx -t

echo
echo "=== Reloading nginx..."
sudo systemctl reload nginx

echo
echo "=== Deployment of etc/nginx complete."
