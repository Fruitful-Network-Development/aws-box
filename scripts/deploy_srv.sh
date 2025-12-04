# This script will mirror ~/awsDev/srv/ onto /srv/
#!/bin/bash
set -euo pipefail

# Resolve project root as directory above this script
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

SRC="$PROJECT_ROOT/srv/"
DST="/srv/"

echo "=== Deploying srv → $DST"
echo "Source: $SRC"
echo

# WARNING: --delete removes files in /srv that are not in repo/srv
sudo rsync -az --delete "$SRC" "$DST"

echo
echo "=== Deployment of srv complete."

