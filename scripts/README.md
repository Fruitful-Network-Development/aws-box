# Scripts Directory

This directory contains utility scripts for managing and auditing the Flask application deployment on AWS EC2.

## Overview

The scripts are organized into two categories:
- **Deployment Scripts**: Used for deploying and updating the application
- **Audit Scripts**: Used for system administration and security auditing

---

## Deployment Scripts

### `deploy_srv.sh`
Deploys the Flask application to `/srv/webapps/platform` on the EC2 server.

### `deploy_nginx.sh`
Deploys and configures NGINX for the Flask application.

### `update_code.sh`
Updates the application code from the Git repository.

### `deploy_and_check.sh`
Master deployment script that:
1. Updates code from `origin/main`
2. Deploys the application (`deploy_srv.sh`)
3. Deploys NGINX configuration (`deploy_nginx.sh`)
4. Runs health checks (`healthcheck.sh`)

### `healthcheck.sh`
Performs health checks on the deployed application.

---

## Audit Scripts

The audit scripts are designed to help system administrators identify potential issues and misconfigurations related to web server setup and application deployment. **These scripts do NOT modify any system files**; they only collect and report information for analysis.

### Quick Start

Run all audits at once:
```bash
./scripts/audit_all.sh [output_file]
```

Or run individual audits:
```bash
./scripts/audit_permissions.sh
./scripts/audit_nginx_config.sh
./scripts/audit_services.sh
```

### `audit_permissions.sh`

**Purpose**: Audits file and directory ownership and permissions for the Flask application deployment under `/srv/webapps/platform`.

**What it checks**:
- Directory and file ownership (identifies root-owned items)
- World-writable files and directories (security risk)
- Sensitive files (keys, certificates, `.env` files) with incorrect permissions
- SetUID/SetGID bits
- Flask application structure (entry points, dependencies, virtual environment)

**Usage**:
```bash
./scripts/audit_permissions.sh
```

**Exit Codes**:
- `0` - Script completed successfully
- `1` - Critical errors (e.g., `/srv/webapps/platform` does not exist)

**Dependencies**: `find`, `stat`, `ls`, `awk`, `grep`

---

### `audit_nginx_config.sh`

**Purpose**: Audits NGINX configuration files to ensure alignment with the actual application deployment structure.

**What it checks**:
- NGINX configuration syntax validity
- Path alignment between NGINX config and `/srv/webapps/platform`
- Gunicorn socket/port configuration alignment
- Security settings (HTTPS, `server_tokens`, HTTP redirects)
- SSL certificate file existence
- Logging configuration (access_log, error_log)
- Configuration file permissions

**Usage**:
```bash
./scripts/audit_nginx_config.sh
```

**Note**: May require `sudo` privileges to test NGINX configuration syntax.

**Exit Codes**:
- `0` - Script completed successfully
- `1` - NGINX configuration files not found or critical errors

**Dependencies**: `grep`, `awk`, `find`, `test`, `nginx` (for config test)

---

### `audit_services.sh`

**Purpose**: Audits systemd unit files and service configurations for the Flask application and related services (Gunicorn, NGINX).

**What it checks**:
- Gunicorn service status (enabled/active)
- NGINX service status (enabled/active)
- Service `WorkingDirectory` alignment with deployment location
- Service `User` and `Group` settings (security check)
- Socket path consistency between service files and NGINX config
- Service dependencies and ordering
- Service file permissions

**Usage**:
```bash
./scripts/audit_services.sh
```

**Note**: May require `sudo` privileges to check service status.

**Exit Codes**:
- `0` - Script completed successfully
- `1` - Critical errors (e.g., systemd not available)

**Dependencies**: `systemctl`, `grep`, `awk`, `find`, `test`

---

### `audit_all.sh`

**Purpose**: Master script that runs all audit scripts in sequence and generates a comprehensive system audit report.

**Usage**:
```bash
# Output to stdout
./scripts/audit_all.sh

# Save to file
./scripts/audit_all.sh /path/to/audit_report.txt
```

**What it does**:
1. Runs `audit_permissions.sh`
2. Runs `audit_nginx_config.sh`
3. Runs `audit_services.sh`
4. Generates a unified summary report with recommendations

**Exit Codes**:
- `0` - All audits completed successfully
- `1` - One or more audits failed

**Output**: Comprehensive audit report combining results from all individual audit scripts.

---

## General Notes

### Permissions
All scripts should be executable:
```bash
chmod +x scripts/*.sh
```

### Running on EC2
These scripts are designed to be run on the EC2 server where the Flask application is deployed. Some scripts may require `sudo` privileges for certain checks (e.g., NGINX config testing, service status).

### Output Format
All audit scripts use color-coded output:
- **RED**: Errors (critical issues)
- **YELLOW**: Warnings (potential issues)
- **GREEN**: Info (normal/expected conditions)
- **BLUE**: Details (additional information)

### Best Practices
1. Run `audit_all.sh` regularly to maintain system health awareness
2. Review all WARNING and ERROR messages
3. Address security concerns promptly
4. Verify file ownership matches application user (not root)
5. Ensure NGINX configuration paths match actual deployment
6. Confirm Gunicorn socket/port matches NGINX proxy settings
7. Verify systemd services are enabled and running
8. Check that sensitive files have restrictive permissions (600 or 640)

---

## Script Design Principles

All audit scripts follow these principles:

- **Modularity**: One concern per script
- **Documentation**: Heavy documentation in comments
- **Minimal Complexity**: Simple, straightforward logic
- **No External Dependencies**: Standard POSIX/Bash tools only
- **Read-Only**: Scripts collect data only; they do NOT modify system files
- **Error Handling**: Proper exit codes and error messages
- **Portability**: POSIX-compliant for maximum compatibility

---

## Troubleshooting

### Script not executable
```bash
chmod +x scripts/audit_*.sh
```

### Permission denied errors
Some checks may require `sudo`:
```bash
sudo ./scripts/audit_nginx_config.sh
sudo ./scripts/audit_services.sh
```

### Path not found errors
Ensure the scripts are run from the correct directory or use absolute paths. The scripts assume standard paths:
- Web application root: `/srv/webapps/platform`
- NGINX config: `/etc/nginx`
- Systemd services: `/etc/systemd/system`

---

## Contributing

When adding new scripts:
1. Follow the existing script structure and documentation style
2. Include a header comment with purpose, usage, exit codes, and dependencies
3. Use the same color-coding scheme for output
4. Ensure scripts are POSIX-compliant
5. Test scripts on the target EC2 environment
6. Update this README.md with script documentation
