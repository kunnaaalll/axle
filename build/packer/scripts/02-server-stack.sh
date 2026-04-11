#!/usr/bin/env bash
# =============================================================================
# AXLE OS — 02-server-stack.sh (T-014)
#
# Layer 2: Install the full production server stack.
# Everything is installed but NOT initialized — AXLE activates components
# on-demand when a project needs them.
# =============================================================================
set -euo pipefail

echo ">>> [AXLE] Step 2/6 — Installing server stack"

# =========================
# NGINX (latest stable)
# =========================
echo ">>> Installing Nginx..."
apt-get install -y nginx
systemctl enable nginx
# Write a temporary default page (replaced by branding later)
systemctl start nginx

# =========================
# CERTBOT (Let's Encrypt)
# =========================
echo ">>> Installing Certbot..."
apt-get install -y certbot python3-certbot-nginx

# =========================
# POSTGRESQL 16
# =========================
echo ">>> Installing PostgreSQL 16..."
sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -
apt-get update -y
apt-get install -y postgresql-16 postgresql-client-16
# Stop PostgreSQL — AXLE initializes it only when a project needs it
systemctl stop postgresql
systemctl disable postgresql

# =========================
# MYSQL 8
# =========================
echo ">>> Installing MySQL 8..."
apt-get install -y mysql-server-8.0 mysql-client-8.0
# Stop MySQL — AXLE initializes it only when a project needs it
systemctl stop mysql
systemctl disable mysql

# =========================
# NODE.JS (via nvm — multiple versions)
# =========================
echo ">>> Installing Node.js via nvm..."
export NVM_DIR="/usr/local/nvm"
mkdir -p "$NVM_DIR"
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash

# Source nvm and install LTS versions
export NVM_DIR="/usr/local/nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

nvm install 18
nvm install 20
nvm install 22
nvm alias default 20
nvm use 20

# Make nvm available system-wide
cat > /etc/profile.d/nvm.sh << 'NVMEOF'
export NVM_DIR="/usr/local/nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"
NVMEOF
chmod +x /etc/profile.d/nvm.sh

# =========================
# PYTHON (via pyenv — multiple versions)
# =========================
echo ">>> Installing Python via pyenv..."
# Install pyenv dependencies
apt-get install -y \
    libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev \
    libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev \
    libffi-dev liblzma-dev

export PYENV_ROOT="/usr/local/pyenv"
curl https://pyenv.run | bash

# Install Python versions
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
pyenv install 3.10.14
pyenv install 3.11.9
pyenv install 3.12.4
pyenv global 3.12.4

# Make pyenv available system-wide
cat > /etc/profile.d/pyenv.sh << 'PYENVEOF'
export PYENV_ROOT="/usr/local/pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
PYENVEOF
chmod +x /etc/profile.d/pyenv.sh

# =========================
# GO (latest stable)
# =========================
echo ">>> Installing Go..."
GO_VERSION="1.22.2"
wget -q "https://go.dev/dl/go${GO_VERSION}.linux-amd64.tar.gz" -O /tmp/go.tar.gz
tar -C /usr/local -xzf /tmp/go.tar.gz
rm /tmp/go.tar.gz

cat > /etc/profile.d/golang.sh << 'GOEOF'
export PATH=$PATH:/usr/local/go/bin
export GOPATH=$HOME/go
export PATH=$PATH:$GOPATH/bin
GOEOF
chmod +x /etc/profile.d/golang.sh

# =========================
# UFW FIREWALL
# =========================
echo ">>> Configuring UFW firewall..."
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw allow 4000/tcp  # AXLE Dashboard
ufw --force enable

echo ">>> [AXLE] Step 2/6 — Server stack installation complete"
