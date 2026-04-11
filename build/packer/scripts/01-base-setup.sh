#!/usr/bin/env bash
# =============================================================================
# AXLE OS — 01-base-setup.sh (T-013)
#
# Layer 1 hardening: Update Ubuntu, install essential build tools and libs.
# Runs as root during Packer build.
# =============================================================================
set -euo pipefail

echo ">>> [AXLE] Step 1/6 — Base system setup"

# --- Wait for cloud-init to finish (Packer race condition fix) ---
cloud-init status --wait || true

# --- System update ---
apt-get update -y
apt-get upgrade -y
apt-get dist-upgrade -y

# --- Essential build tools & libraries ---
apt-get install -y \
    build-essential \
    curl \
    wget \
    git \
    unzip \
    zip \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    gnupg \
    lsb-release \
    jq \
    htop \
    tree \
    vim \
    tmux \
    fail2ban \
    logrotate \
    rsync \
    acl

# --- Set timezone ---
timedatectl set-timezone UTC

echo ">>> [AXLE] Step 1/6 — Base setup complete"
