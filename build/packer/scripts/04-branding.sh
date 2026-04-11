#!/usr/bin/env bash
# =============================================================================
# AXLE OS — 04-branding.sh (T-016)
#
# Apply AXLE OS branding: MOTD, os-release, SSH banner, issue file,
# and Nginx default welcome page.
# =============================================================================
set -euo pipefail

echo ">>> [AXLE] Step 4/6 — Applying branding"

AXLE_VERSION="${AXLE_VERSION:-1.0.0}"
BRANDING_SRC="/tmp/axle-src/build/branding"

# --- os-release ---
if [ -f "${BRANDING_SRC}/os-release" ]; then
    cp "${BRANDING_SRC}/os-release" /etc/os-release
else
    cat > /etc/os-release << EOF
PRETTY_NAME="AXLE OS ${AXLE_VERSION} (Based on Ubuntu 22.04 LTS)"
NAME="AXLE OS"
VERSION_ID="${AXLE_VERSION}"
VERSION="AXLE OS ${AXLE_VERSION}"
ID=axle
ID_LIKE=ubuntu debian
HOME_URL="https://axle.sh"
SUPPORT_URL="https://github.com/axle-os/axle/issues"
BUG_REPORT_URL="https://github.com/axle-os/axle/issues"
UBUNTU_CODENAME=jammy
EOF
fi

# --- Pre-login issue banner ---
if [ -f "${BRANDING_SRC}/issue" ]; then
    cp "${BRANDING_SRC}/issue" /etc/issue
    cp "${BRANDING_SRC}/issue" /etc/issue.net
fi

# --- SSH banner ---
if [ -f "${BRANDING_SRC}/ssh-banner" ]; then
    cp "${BRANDING_SRC}/ssh-banner" /etc/axle-ssh-banner
    # Enable banner in sshd_config
    if ! grep -q "^Banner" /etc/ssh/sshd_config; then
        echo "Banner /etc/axle-ssh-banner" >> /etc/ssh/sshd_config
    fi
fi

# --- MOTD scripts ---
# Disable default Ubuntu MOTD noise
chmod -x /etc/update-motd.d/* 2>/dev/null || true

MOTD_DIR="/etc/update-motd.d"
if [ -d "${BRANDING_SRC}/motd" ]; then
    cp "${BRANDING_SRC}/motd/"* "${MOTD_DIR}/"
    chmod +x "${MOTD_DIR}/"*
fi

# --- Nginx default welcome page ---
cat > /var/www/html/index.html << 'HTMLEOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AXLE OS — Ready to Deploy</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
            background: linear-gradient(135deg, #0f0f23 0%, #1a1a3e 50%, #0f0f23 100%);
            color: #e0e0ff;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .container {
            text-align: center;
            max-width: 600px;
            padding: 3rem;
        }
        .logo { font-size: 4rem; margin-bottom: 1rem; }
        h1 {
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(90deg, #60a5fa, #a78bfa);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
        }
        .version {
            font-size: 0.9rem;
            color: #888;
            margin-bottom: 2rem;
        }
        p {
            font-size: 1.1rem;
            line-height: 1.7;
            color: #b0b0d0;
            margin-bottom: 1.5rem;
        }
        code {
            background: rgba(255,255,255,0.08);
            padding: 0.3rem 0.7rem;
            border-radius: 6px;
            font-family: 'Fira Code', monospace;
            font-size: 0.95rem;
            color: #60a5fa;
        }
        .status {
            display: inline-block;
            padding: 0.5rem 1.5rem;
            border: 1px solid #22c55e;
            border-radius: 999px;
            color: #22c55e;
            font-size: 0.85rem;
            letter-spacing: 0.05em;
            margin-top: 1rem;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">⚡</div>
        <h1>AXLE OS</h1>
        <p class="version">AI-Powered Linux Deployment Engine</p>
        <p>Your server is ready. SSH in and run <code>axle setup</code> to configure your AI provider, then deploy your first application.</p>
        <p>Dashboard will be available at <code>:4000</code> after setup.</p>
        <div class="status">● System Ready</div>
    </div>
</body>
</html>
HTMLEOF

echo ">>> [AXLE] Step 4/6 — Branding applied"
