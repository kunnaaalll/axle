#!/usr/bin/env bash
# =============================================================================
# AXLE OS — 06-cleanup.sh (T-018)
#
# Final cleanup to minimize AMI size:
# - Remove APT cache
# - Remove build artifacts
# - Clear temp files
# - Zero free space (enables better AMI compression)
# =============================================================================
set -euo pipefail

echo ">>> [AXLE] Step 6/6 — Cleanup & image optimization"

# --- Remove APT cache ---
apt-get autoremove -y
apt-get clean
rm -rf /var/lib/apt/lists/*

# --- Remove build source (no longer needed in the image) ---
rm -rf /tmp/axle-src

# --- Clear temp files ---
rm -rf /tmp/*
rm -rf /var/tmp/*

# --- Clear logs (will be fresh on first boot) ---
find /var/log -type f -name "*.log" -exec truncate -s 0 {} \;
truncate -s 0 /var/log/wtmp
truncate -s 0 /var/log/lastlog

# --- Remove SSH host keys (regenerated on first boot via cloud-init) ---
rm -f /etc/ssh/ssh_host_*

# --- Clear shell history ---
unset HISTFILE
rm -f /root/.bash_history
rm -f /home/ubuntu/.bash_history

# --- Zero free space for better AMI compression ---
echo ">>> Zeroing free space (this may take a moment)..."
dd if=/dev/zero of=/EMPTY bs=1M 2>/dev/null || true
rm -f /EMPTY
sync

echo ">>> [AXLE] Step 6/6 — Cleanup complete. Image ready."
