#!/usr/bin/env bash
# deploy_systemd.sh
#
# Deploy systemd unit files from GH-etc into /etc/systemd/system,
# then daemon-reload and restart affected services.
#
set -euo pipefail

GH_ROOT="${GH_ROOT:-/home/admin/GH-etc}"
SRC="${GH_ROOT}/etc/systemd/system"
DEST="/etc/systemd/system"

log(){ echo "[deploy_systemd] $*"; }

if [ ! -d "$SRC" ]; then
  echo "[deploy_systemd] ERROR: source not found: $SRC" >&2
  exit 1
fi

log "Deploying systemd units from $SRC -> $DEST"
sudo rsync -a \
  --exclude='*.bak' \
  --exclude='*.swp' \
  "$SRC/" "$DEST/"

log "Reloading systemd daemon"
sudo systemctl daemon-reload

# Restart common services if present
for svc in platform.service nginx; do
  if systemctl list-unit-files | grep -q "^${svc}"; then
    log "Restarting $svc"
    sudo systemctl restart "$svc" || true
  fi
done

log "Done."
