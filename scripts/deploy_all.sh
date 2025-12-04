# update + deploy both srv and nginx
#!/bin/bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

./scripts/update_code.sh
./scripts/deploy_srv.sh
./scripts/deploy_nginx.sh

echo
echo "=== Full deploy (srv + nginx) complete."

