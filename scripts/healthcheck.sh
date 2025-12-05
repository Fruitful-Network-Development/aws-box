#!/bin/bash
set -euo pipefail

log() {
  echo "[$(date --iso-8601=seconds)] $*"
}

fail() {
  log "ERROR: $*"
  exit 1
}

# 1) Check core services are active
for svc in nginx platform; do
  if ! systemctl is-active --quiet "$svc"; then
    fail "Service $svc is not active"
  fi
done

# 2) Check key URLs
check_url() {
  local url="$1"
  if ! curl -fsS "$url" > /dev/null; then
    fail "URL check failed: $url"
  else
    log "OK: $url"
  fi
}

# Frontends
check_url "https://fruitfulnetworkdevelopment.com/"
check_url "https://cuyahogaterravita.com/"

# API (you can tweak the params if you want)
check_url "https://cuyahogaterravita.com/api/weather/daily?lat=41.1&lon=-81.5&days=1&past_days=0"

log "ALL CHECKS PASSED"
