# Deployment scripts

These helpers keep code and nginx config on the server in sync with the repo. All scripts resolve the project root relative to their own location.

## update_code.sh
- Pulls the latest git commits into the repo with `git pull --ff-only`.

## deploy_srv.sh
- Mirrors `srv/` from the repo to `/srv/` using `rsync -az --delete`.
- **Warning:** `--delete` removes files in `/srv` that are not present in `srv/` in the repo.

## deploy_nginx.sh
- Mirrors `etc/nginx/` to `/etc/nginx/` with `rsync -az --delete`.
- Runs `nginx -t` before reload, then issues `systemctl reload nginx`.
- **Warning:** `--delete` removes files under `/etc/nginx` that are not tracked in the repo.

## deploy_all.sh
- Runs `update_code.sh`, then deploys `srv/` and `etc/nginx/`.
- Use when you want a full update plus service reload in one step.
