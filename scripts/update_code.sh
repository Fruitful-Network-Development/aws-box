# pull latest from GitHub
#!/bin/bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "=== Updating git repository in $PROJECT_ROOT ..."
git pull --ff-only
echo "=== Git update complete."
