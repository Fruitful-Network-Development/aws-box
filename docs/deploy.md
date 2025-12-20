# Debian EC2 Rebuild Guide (aws-box)

> **Scope:** Manual, step-by-step rebuild instructions for a new Debian EC2 instance using the **single** repository `Fruitful-Network-Development/aws-box`.

### 0) Provision the EC2 instance
1. Launch a **Debian** EC2 instance.
2. Open inbound security group ports: **22**, **80**, **443**.
3. Confirm DNS A records point to the new instance IP:
   - fruitfulnetworkdevelopment.com
   - www.fruitfulnetworkdevelopment.com
   - cuyahogaterravita.com
   - www.cuyahogaterravita.com

### 1) One-time base packages and permissions (Debian)
```bash
ssh admin@<public-ip>

sudo apt-get update
sudo apt-get install -y git rsync nginx python3 python3-venv python3-pip certbot python3-certbot-nginx
```
Enable nginx:
```bash
sudo systemctl enable --now nginx
```
Create live app directories:
```
sudo mkdir -p /srv/webapps/platform /srv/webapps/clients
sudo chown -R admin:admin /srv/webapps
```

### 2) Set up GitHub access from the server

#### 2.A) Generate an SSH key on the server
```bash
ssh-keygen -t ed25519 -C "admin@$(hostname)-aws-box"
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
cat ~/.ssh/id_ed25519.pub
```
The program will prompted  for a "file in which to save the key."
      Pressed Enter (leaving it blank), defaulting it to: /home/admin/.ssh/id_ed25519
Copy the printed public key into GitHub:
      GitHub → Settings → SSH and GPG keys → New SSH key

Test auth
```bash
ssh -T git@github.com
```

#### 2.B) Clone your aws-box repo to become the only source-of-truth
```bash
cd /home/admin
git clone git@github.com:Fruitful-Network-Development/aws-box.git
cd /home/admin/aws-box
git status
```

### 3) Install the repo’s system configs into live `/etc` safely

#### 3.A) Deploy nginx from repo → live
```bash
sudo rsync -a --delete /home/admin/aws-box/etc/nginx/ /etc/nginx/
```
Remove the default site (prevents wrong site being served):
```bash
sudo rm -f /etc/nginx/sites-enabled/default
```
Validate and reload:
```bash
sudo nginx -t
sudo systemctl reload nginx
```

#### 3.B) Deploy systemd units from repo → live
```bash
sudo rsync -a /home/admin/aws-box/etc/systemd/system/ /etc/systemd/system/
sudo systemctl daemon-reload
```
Do not start services yet unless platform code exists.

### 4) Deploy client frontends (repo → live)
If your repo contains client skeletons under `srv/webapps/clients/...`:
```bash
sudo rsync -a /home/admin/aws-box/srv/webapps/clients/ /srv/webapps/clients/
sudo chown -R admin:admin /srv/webapps/clients
```

### 5) Deploy platform backend code (separately)
Platform skeleton comes from aws-box
If `/home/admin/aws-box/srv/webapps/platform/... exists`:
```bash
sudo rsync -a --delete /home/admin/aws-box/srv/webapps/platform/ /srv/webapps/platform/
```

### 6) Create the platform venv and install requirements
Platform skeleton comes from aws-box
If `/home/admin/aws-box/srv/webapps/platform/... exists`:
```bash
cd /srv/webapps/platform
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt || true
deactivate
```
If you don’t have `requirements.txt`, you must add one. As a stopgap you can install minimums:
```bash
source /srv/webapps/platform/venv/bin/activate
pip install flask gunicorn requests
deactivate
```

### 7) Start systemd services (platform + nginx)
If you have `platform.service` deployed already and `ExecStart` points to `/srv/webapps/platform/venv/bin/gunicorn`:
```bash
sudo systemctl enable --now platform.service
sudo systemctl status platform.service --no-pager
```
Verify local backend:
```bash
curl -sS -I http://127.0.0.1:8000/ | head
```

### 8) TLS (certbot) after DNS and port 80 are correct
Confirm DNS points at this instance:
```bash
sudo apt install -y dnsutils
dig +short fruitfulnetworkdevelopment.com
curl -s https://checkip.amazonaws.com
```
Confirm port 80 reachable (from your laptop too). Then:
```bash
sudo certbot --nginx -d fruitfulnetworkdevelopment.com -d www.fruitfulnetworkdevelopment.com \
  -d cuyahogaterravita.com -d www.cuyahogaterravita.com
```
Test renewal:
```bash
sudo certbot renew --dry-run
```

### 9) Add the deploy scripts (prevention)
Create a scripts folder in your repo and add:
 - scripts/deploy_nginx.sh (rsync → nginx -t → reload)
   - scripts/deploy_systemd.sh (rsync → daemon-reload → restart platform)
If you want, I will give you the exact scripts again but with your final chosen paths.


## Historical Note (Deprecated)
Earlier versions of this document described a monolithic deployment
workflow using GH-etc, per-file sync scripts, and a single deploy_platform.sh.
That approach has been retired.

The current and supported model is:
- Single source-of-truth repo: /home/admin/aws-box
- Explicit deploy scripts for nginx and systemd
- No direct editing of /etc or partial syncs

Refer only to the steps above for new instance setup and updates.
