#!/bin/bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "=== Updating code from origin/main ==="
./scripts/update_code.sh

echo "=== Deploying srv and nginx ==="
./scripts/deploy_srv.sh
./scripts/deploy_nginx.sh

echo "=== Running healthcheck ==="
./scripts/healthcheck.sh

echo "=== Deploy + healthcheck complete ==="
