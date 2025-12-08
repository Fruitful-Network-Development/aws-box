## GitHub and Some Structure Initialization
```bash
cd ~
ssh-keygen -t ed25519 -C "ec2-aws-etc-key"    # press Enter through prompts

# Show the public key
cat ~/.ssh/id_ed25519.pub
```
Copy that output → add it to GitHub → Settings → SSH and GPG keys → New SSH key.

Then:
```bash
# If origin already exists, this will replace it
git remote remove origin 2>/dev/null || true
git remote add origin git@github.com:Fruitful-Network-Development/aws-etc.git

# Pull the main branch into GH-etc
git pull origin main
```

## Set up GH-etc as the dedicated system-files repo
```bash
cd ~/GH-etc
git init
git remote add origin git@github.com:Fruitful-Network-Development/aws-etc.git
git pull origin main
```

## Build the aws/etc structure (local mirror of system files)
```bash
cd ~/aws

# Create etc/systemd/system
mkdir -p etc/systemd/system

# Create etc/nginx with basic subdirs
mkdir -p etc/nginx/sites-available etc/nginx/sites-enabled

# Create empty placeholder files for now (you'll sync or copy real ones later)
touch etc/systemd/system/platform.service
touch etc/nginx/nginx.conf
touch etc/nginx/mime.types
```

## Create aws/srv/webapps structure
```bash
cd ~/aws

# Base dirs
mkdir -p srv/webapps
mkdir -p srv/webapps/clients

```

## Set up platform repo under aws/srv/webapps/platform
  - Two options again: clone directly or init + set remote.
  - Recommended: clone directly
```bash
cd ~/aws

git clone git@github.com:Fruitful-Network-Development/flask-app.git srv/webapps/platform
# Or HTTPS:
# git clone https://github.com/Fruitful-Network-Development/flask-app.git srv/webapps/platform
```

## Set up client repos under aws/srv/webapps/clients/...
### Fruitful Network Development
```bash
cd ~/aws

git clone git@github.com:Fruitful-Network-Development/web-dir-fnd.git \
  srv/webapps/clients/fruitfulnetworkdevelopment.com

# Or HTTPS:
# git clone https://github.com/Fruitful-Network-Development/web-dir-fnd.git \
#   srv/webapps/clients/fruitfulnetworkdevelopment.com
```

### Cuyahoga Terra Vita
```bash
cd ~/aws

git clone git@github.com:Fruitful-Network-Development/web-dir-ctv.git \
  srv/webapps/clients/cuyahogaterravita.com

# Or HTTPS:
# git clone https://github.com/Fruitful-Network-Development/web-dir-ctv.git \
#   srv/webapps/clients/cuyahogaterravita.com
```

## Create the aws/etc structure
Now let’s build the supporting files tree you described under ~/aws:
```bash
cd ~/aws

# Create etc/systemd/system
mkdir -p etc/systemd/system

# Create etc/nginx with typical layout
mkdir -p etc/nginx/sites-available etc/nginx/sites-enabled
touch etc/nginx/nginx.conf
touch etc/nginx/mime.types

# Create placeholder platform.service (we can overwrite it from GH-etc later)
touch etc/systemd/system/platform.service

```
### (Optional but probably what you want) Copy real configs from GH-etc
If your aws-etc repo already has real Nginx and systemd files (likely at etc/nginx and etc/systemd/system inside GH-etc), you can mirror them into your aws/etc sandbox instead of leaving placeholders.
```bash
cd ~/

# Copy Nginx configs from GH-etc into aws/etc
if [ -d GH-etc/etc/nginx ]; then
  cp -r GH-etc/etc/nginx/* aws/etc/nginx/
fi

# Copy systemd units from GH-etc into aws/etc
if [ -d GH-etc/etc/systemd/system ]; then
  cp -r GH-etc/etc/systemd/system/* aws/etc/systemd/system/
fi
```

## NEXT SECTION

### Install Missing Tools
```bash
sudo apt-get update

# Install dig (dnsutils) and rsync
sudo apt-get install -y dnsutils rsync
```

### run the DNS check
```bash
dig +short fruitfulnetworkdevelopment.com
dig +short cuyahogaterravita.com
```

### Sync your modeled webapps into the live location
Now that rsync is installed, re-do the sync:
```bash
cd ~

# Ensure live webapps dir exists
sudo mkdir -p /srv/webapps

# Sync modeled webapps into live path
sudo rsync -av ~/aws/srv/webapps/ /srv/webapps/
```


### Make sure Nginx is using your configs (not the default page)
```bash
cd ~

# Make sure Nginx directories exist
sudo mkdir -p /etc/nginx/sites-available /etc/nginx/sites-enabled

# Copy your main config and mime.types
sudo cp ~/aws/etc/nginx/nginx.conf /etc/nginx/nginx.conf
sudo cp ~/aws/etc/nginx/mime.types /etc/nginx/mime.types

# Copy your site configs
sudo cp ~/aws/etc/nginx/sites-available/*.conf /etc/nginx/sites-available/
```

Disable the default Nginx site (this is what’s giving you “Welcome to nginx!”):
```bash
sudo rm -f /etc/nginx/sites-enabled/default
```

Enable your two domains:
```bash
sudo ln -sf /etc/nginx/sites-available/fruitfulnetworkdevelopment.com.conf \
            /etc/nginx/sites-enabled/fruitfulnetworkdevelopment.com.conf

sudo ln -sf /etc/nginx/sites-available/cuyahogaterravita.com.conf \
            /etc/nginx/sites-enabled/cuyahogaterravita.com.conf
```

#### Test and Reload
```bash
sudo nginx -t
```

## FAILS

### Step 1 – Temporarily disable the CTV site
This error comes from the cuyahogaterravita.com.conf file. Easiest move: disable that site for now so we can get FND working:
```bash
sudo rm -f /etc/nginx/sites-enabled/cuyahogaterravita.com.conf

sudo nginx -t
```
## FAILS

So both site configs were written as HTTPS (Certbot-style) configs, but on this fresh box:
    - Certbot hasn’t run yet
    - /etc/letsencrypt/options-ssl-nginx.conf doesn’t exist
    - Nginx refuses to load
Let’s fix this by making fruitfulnetworkdevelopment.com HTTP-only for now with a clean minimal config.```bash
sudo systemctl reload nginx

### Replace the FND site config with a simple HTTP config
```
sudo nano /etc/nginx/sites-available/fruitfulnetworkdevelopment.com.conf
```
In the editor, delete everything in that file and replace it with this:
```bash
server {
    listen 80;
    server_name fruitfulnetworkdevelopment.com www.fruitfulnetworkdevelopment.com;

    root /srv/webapps/clients/fruitfulnetworkdevelopment.com/frontend;
    index index.html;

    location / {
        try_files $uri $uri/ =404;
    }

    # Optional: later, when your backend is running, you can enable this
    # location /api/ {
    #     proxy_pass http://127.0.0.1:8000;
    #     include proxy_params;
    # }
}
```

### Keep CTV disabled for now
We’ll reintroduce CTV later with a similar simple HTTP config (or after Certbot sets up SSL).
```bash
sudo rm -f /etc/nginx/sites-enabled/cuyahogaterravita.com.conf
```
Test and reload Nginx
```bash
sudo nginx -t
```
If you get:
    - nginx: configuration file /etc/nginx/nginx.conf test is successful
then reload:
```bash
sudo systemctl reload nginx
```
## SUCESS!
### Now lets try to:
#### Create a simple HTTP-only config for cuyahogaterravita.com
Since files already exist at `/srv/webapps/clients/cuyahogaterravita.com/frontend`, we’ll mirror the FND config, just pointed at that root.
Edit the site config:
```bash
sudo nano /etc/nginx/sites-available/cuyahogaterravita.com.conf
```
Replace the contents of that file with:
```bash
server {
    listen 80;
    server_name cuyahogaterravita.com www.cuyahogaterravita.com;

    root /srv/webapps/clients/cuyahogaterravita.com/frontend;
    index index.html;

    location / {
        try_files $uri $uri/ =404;
    }

    # Optional backend proxy (commented out for now)
    # location /api/ {
    #     proxy_pass http://127.0.0.1:8000;
    #     include proxy_params;
    # }
}
```
Enable the site
```bash
sudo ln -sf /etc/nginx/sites-available/cuyahogaterravita.com.conf \
            /etc/nginx/sites-enabled/cuyahogaterravita.com.conf
```
Test and reload Nginx:
```bash
sudo systemctl reload nginx
```

#### Run Certbot to create SSL config + certs
Since Certbot was already installed earlier; now we’ll have it:
  - validate both domains,
  - obtain certificates,
  - create /etc/letsencrypt/options-ssl-nginx.conf,
  - and adjust your Nginx configs.
Run:
```bash
sudo certbot --nginx \
  -d fruitfulnetworkdevelopment.com \
  -d www.fruitfulnetworkdevelopment.com \
  -d cuyahogaterravita.com \
  -d www.cuyahogaterravita.com
```
Certbot will ask:
  - For an email address → use the one you want for renewal/expiry notices
  - To agree to the ToS → say yes
  - Whether to redirect HTTP to HTTPS → I recommend yes (redirect all HTTP to HTTPS)
If everything succeeds, Certbot will:
  - Create /etc/letsencrypt/options-ssl-nginx.conf
  - Create cert+key under /etc/letsencrypt/live/...
  - Add server blocks with listen 443 ssl; and ssl_certificate lines into your FND and CTV configs, or add extra HTTPS blocks alongside your HTTP ones.

Test and reload Nginx:
```bash
sudo nginx -t
```
If OK:
```bash
sudo systemctl reload nginx
```

Quick “sanity” commands you can run
```bash
# Show what HTTPS ports nginx is listening on
sudo ss -tlnp | grep nginx

# See if the options-ssl file exists
ls -l /etc/letsencrypt/options-ssl-nginx.conf

# Check the cert paths in your site configs
grep -n "ssl_certificate" /etc/nginx/sites-available/*.conf
```

### Configure your Git identity on this server:
Do this once and you won’t be asked again on this machine:
```bash
git config --global user.name "dylcmonty"
git config --global user.email "gleam.regents_67@icloud.com"
```
Confirm it:
```bash
git config --global user.name
git config --global user.email
```

Re-run what failed last time:
```bash
cd ~/GH-etc
git status   # you should still see the two modified .conf files

# Either:
git add etc/nginx/sites-available/fruitfulnetworkdevelopment.com.conf \
        etc/nginx/sites-available/cuyahogaterravita.com.conf

git commit -m "Update nginx vhost configs after HTTPS setup for FND and CTV"
```

### Fix the branch name + push
Right now you’re on master.
But earlier you pulled from origin main, so the remote default branch is main. There is no local branch called main, which is why Git said:
    `error: src refspec main does not match any`
Let’s rename your local branch to main and push it:
```bash
cd ~/GH-etc

# Rename local branch "master" → "main"
git branch -M main

# Push and set upstream tracking
git push -u origin main
```

## Typical workflow from now on:

When you or an agent (via PR) change nginx configs in aws-etc → GH-etc:

#### Pull latest repo on the server:
```bash
cd ~/GH-etc
git pull
```

#### Sync from GH-etc → aws (staging):
```bash
bash ~/GH-etc/scripts/01_sync_nginx_gh_to_aws.sh
```

#### (Optional) Inspect staged files:
```bash
diff -u ~/aws/etc/nginx/sites-available/fruitfulnetworkdevelopment.com.conf \
        /etc/nginx/sites-available/fruitfulnetworkdevelopment.com.conf || true
```

#### Deploy aws → /etc/nginx:
```bash
bash ~/GH-etc/scripts/02_deploy_nginx_from_aws.sh
```

#### (Optional) Log an audit:
```bash
bash ~/GH-etc/scripts/03_audit_nginx.sh
```
