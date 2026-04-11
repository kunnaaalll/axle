#!/usr/bin/env bash
# =============================================================================
# AXLE OS — 05-first-boot.sh (T-017)
#
# Install the first-boot wizard as a systemd service.
# On first SSH login, the user sees "Run: axle setup" in MOTD.
# The setup wizard configures AI provider + admin password.
# =============================================================================
set -euo pipefail

echo ">>> [AXLE] Step 5/6 — Setting up first-boot wizard"

AXLE_HOME="/opt/axle"
FIRSTBOOT_SRC="/tmp/axle-src/build/firstboot"

# --- Copy first-boot wizard script ---
if [ -f "${FIRSTBOOT_SRC}/axle-firstboot.py" ]; then
    cp "${FIRSTBOOT_SRC}/axle-firstboot.py" "${AXLE_HOME}/firstboot.py"
    chmod +x "${AXLE_HOME}/firstboot.py"
fi

# --- Install first-boot systemd service ---
cat > /etc/systemd/system/axle-firstboot.service << EOF
[Unit]
Description=AXLE OS First-Boot Setup Wizard
After=network-online.target
Wants=network-online.target
ConditionPathExists=!/var/lib/axle/.setup-complete

[Service]
Type=oneshot
ExecStart=${AXLE_HOME}/.venv/bin/python ${AXLE_HOME}/firstboot.py
RemainAfterExit=yes
StandardInput=tty
StandardOutput=tty
TTYPath=/dev/tty1

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable axle-firstboot.service

# --- Create a marker directory (wizard creates .setup-complete when done) ---
mkdir -p /var/lib/axle

echo ">>> [AXLE] Step 5/6 — First-boot wizard installed"
