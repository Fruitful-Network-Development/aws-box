# Fruitful Network Development — Streamlined Server Setup Guide

This is the **canonical and simplified setup guide** for deploying a fresh FND server on a new EC2 instance.  
It replaces all previous logs and should be followed exactly for every rebuild.

---

## 1. Repositories & Paths

| Repository | Purpose | Deployment Path |
|-----------|---------|-----------------|
| `flask-app` | Shared backend Flask API | `/srv/webapps/platform` |
| `web-dir-fnd` | Frontend for fruitfulnetworkdevelopment.com | `/srv/webapps/clients/fruitfulnetworkdevelopment.com/frontend` |
| `web-dir-ctv` | Frontend for cuyahogaterravita.com | `/srv/webapps/clients/cuyahogaterravita.com/frontend` |
| `aws-etc` | System config sandbox (Nginx, systemd, scripts) | `/home/admin/GH-etc` |

**Important rules:**
- `/etc` and `/srv/webapps` are *not* Git repos.
- Only `GH-etc` is a system configuration repository.
- Agents update GitHub; humans deploy changes via scripts.

---

## 2. EC2 Requirements

Launch a new Ubuntu instance with inbound rules:
- **22** (SSH) — your IP only
- **80** (HTTP)
- **443** (HTTPS)

Login as:
```
admin@<public-ip>
```

Ensure DNS A records point to the instance:
- fruitfulnetworkdevelopment.com
- www.fruitfulnetworkdevelopment.com
- cuyahogaterravita.com
- www.cuyahogaterravita.com

---

## 3. Set Required Environment Variables

### Generate a strong secret:

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### Export environment variables:

```bash
export FND_SECRET_KEY="paste-generated-key-here"
export FND_CONTACT_EMAIL="your-email@fruitfulnetworkdevelopment.com"
```

Run the deployment script using:

```bash
sudo -E bash deploy_platform.sh
```

(`-E` preserves your exported environment variables.)

---

## 4. Deployment Script Behavior

The script:

1. Installs Python, Git, Nginx, Certbot, UFW  
2. Creates:
   - `/srv/webapps/platform`
   - `/srv/webapps/clients/<domain>/frontend`
   - `/home/admin/GH-etc`
3. Clones or updates all four repositories
4. Deploys system configuration from `GH-etc`
5. Sets up Python virtualenv + installs dependencies
6. Creates systemd service `platform.service`
7. Tests + reloads Nginx
8. Obtains HTTPS certificates via Certbot
9. Prints deployment summary

Afterward, visit:

```
https://fruitfulnetworkdevelopment.com
https://cuyahogaterravita.com
```

---

## 5. Updating an Existing Server

To apply changes made in GitHub:

```bash
cd /home/admin/GH-etc
git pull
sudo -E bash deploy_platform.sh
```

This keeps the server synchronized with the configuration repo.

---

## 6. Rules for Agents

Agents may:

- Read and edit `aws-etc` (GitHub version only)
- Write audit logs inside the repo
- Suggest system config changes via PRs

Agents **may not**:

- Edit `/etc` directly
- Edit `/srv/webapps/*` directly
- Modify system services without script-based deployment

---

## 7. Rebuilding a Server

If the EC2 instance becomes corrupted or unreachable:

1. Terminate the instance  
2. Launch a new one  
3. SSH in  
4. Set environment variables  
5. Run the deployment script  
6. Assign Elastic IP (if using)

The server will be fully rebuilt from GitHub + scripts.

---

### This file is your authoritative guide for all future deployments.
