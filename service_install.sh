#!/bin/bash
set -e

# Resolve absolute path to the directory where this script lives
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

SERVICE_NAME="ezFileServe"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"

echo "Installing systemd service with WorkingDirectory: ${SCRIPT_DIR}"

cat <<EOF | tee $SERVICE_FILE >/dev/null
[Unit]
Description=Gunicorn instance to serve EzFileServe Flask app
After=network.target

[Service]
WorkingDirectory=${SCRIPT_DIR}
ExecStart=${SCRIPT_DIR}/start_server.sh

# Security hardening
PrivateTmp=true             # Give the service its own /tmp
ProtectHome=true            # Block access to /home, /root, /run/user
NoNewPrivileges=true        # Prevent privilege escalation
ProtectKernelModules=true   # Block loading/unloading kernel modules

# Restart on failures
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

echo "Reloading systemd daemon..."
systemctl daemon-reload

echo "Enabling service ${SERVICE_NAME}..."
systemctl enable ${SERVICE_NAME}

echo "Starting/restarting service ${SERVICE_NAME}..."
systemctl restart ${SERVICE_NAME}

echo "Done! Service ${SERVICE_NAME} is installed and running."
