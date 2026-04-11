#!/usr/bin/env bash
# =============================================================================
# AXLE OS — 03-install-axle.sh (T-015)
#
# Layer 3: Install the AXLE Python package, build the React dashboard,
# and set up systemd services for the API and dashboard.
# =============================================================================
set -euo pipefail

echo ">>> [AXLE] Step 3/6 — Installing AXLE appliance"

AXLE_VERSION="${AXLE_VERSION:-1.0.0}"
AXLE_HOME="/opt/axle"
AXLE_DATA="/var/lib/axle"
AXLE_CONF="/etc/axle"
AXLE_LOG="/var/log/axle"

# --- Create directories ---
mkdir -p "$AXLE_HOME"
mkdir -p "$AXLE_DATA"
mkdir -p "$AXLE_CONF"
mkdir -p "$AXLE_LOG"

# --- Copy AXLE source code ---
# During Packer build, the repo is uploaded to /tmp/axle-src
# (We'll add a file provisioner in the Packer template for this)
if [ -d "/tmp/axle-src" ]; then
    cp -r /tmp/axle-src/* "$AXLE_HOME/"
else
    echo "WARNING: /tmp/axle-src not found — AXLE source must be provisioned"
fi

# --- Install AXLE Python package ---
cd "$AXLE_HOME"

# Use system Python 3 to create a dedicated venv
python3 -m venv "${AXLE_HOME}/.venv"
source "${AXLE_HOME}/.venv/bin/activate"

pip install --upgrade pip setuptools wheel
pip install -e .

# --- Create symlink for `axle` CLI in system PATH ---
ln -sf "${AXLE_HOME}/.venv/bin/axle" /usr/local/bin/axle

# --- Build React dashboard ---
if [ -d "${AXLE_HOME}/web/dashboard" ]; then
    echo ">>> Building React dashboard..."
    export NVM_DIR="/usr/local/nvm"
    [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
    nvm use 20

    cd "${AXLE_HOME}/web/dashboard"
    npm install
    npm run build
    cd "$AXLE_HOME"
fi

# --- Create default config ---
cat > "${AXLE_CONF}/axle.conf" << EOF
# AXLE OS Configuration
# Generated during image build — version ${AXLE_VERSION}

[general]
version = ${AXLE_VERSION}
data_dir = ${AXLE_DATA}
log_dir = ${AXLE_LOG}

[dashboard]
port = 4000
host = 0.0.0.0

[ai]
# Provider is configured during first-boot setup
# Options: gemini, openrouter, openai, ollama
provider = none
EOF

# --- Create systemd service for AXLE API ---
cat > /etc/systemd/system/axle-api.service << EOF
[Unit]
Description=AXLE OS API Server
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=${AXLE_HOME}
ExecStart=${AXLE_HOME}/.venv/bin/python -m web.api.app
Restart=always
RestartSec=5
Environment=AXLE_CONF=${AXLE_CONF}/axle.conf

[Install]
WantedBy=multi-user.target
EOF

# --- Create systemd service for AXLE Dashboard ---
cat > /etc/systemd/system/axle-dashboard.service << EOF
[Unit]
Description=AXLE OS Web Dashboard
After=network.target axle-api.service
Requires=axle-api.service

[Service]
Type=simple
User=root
WorkingDirectory=${AXLE_HOME}
ExecStart=${AXLE_HOME}/.venv/bin/python -m flask --app web.api.app run --host=0.0.0.0 --port=4000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable axle-api.service
# Dashboard starts after first-boot setup
systemctl disable axle-dashboard.service

echo ">>> [AXLE] Step 3/6 — AXLE appliance installed"
