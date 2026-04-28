# Getting Started with AXLE OS

Welcome to AXLE OS — the AI-powered autonomous deployment engine. This guide will take you from zero to a fully running AXLE instance.

---

## Prerequisites

| Requirement | Details |
|-------------|---------|
| **OS** | Ubuntu 24.04 LTS (EC2, Multipass, or bare metal) |
| **Python** | 3.9 or later |
| **Node.js** | 18 or later (for dashboard) |
| **AI Key** | At least one of: Gemini, OpenAI, or OpenRouter API key. Or a local Ollama instance. |

---

## Quick Start (Local Development)

### 1. Clone the Repository
```bash
git clone https://github.com/kunnaaalll/axle.git
cd axle
```

### 2. Set Up Python Environment
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[all,dev]"
```

### 3. Configure API Keys
```bash
cp .env.example .env
# Edit .env and add your AI provider key
```

### 4. Run the Setup Wizard
```bash
axle setup
```
This will walk you through selecting an AI provider, entering your API key, and setting a dashboard password.

### 5. Verify Installation
```bash
axle info
axle status
```

---

## Quick Start (Production Server)

### 1. Launch an EC2 Instance
Use the AXLE AMI from our Packer build, or start with a fresh Ubuntu 24.04 instance.

### 2. Run Provisioning Scripts
```bash
git clone https://github.com/kunnaaalll/axle.git /opt/axle
cd /opt/axle
chmod +x build/packer/scripts/*.sh

# Run base provisioning
sudo ./build/packer/scripts/01-system-base.sh
sudo ./build/packer/scripts/02-docker-setup.sh
sudo ./build/packer/scripts/03-python-env.sh
```

### 3. Install and Configure
```bash
cd /opt/axle
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[all]"
axle setup
```

### 4. Enable Services
```bash
sudo cp build/services/*.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now axle-api axle-dashboard
```

### 5. Access the Dashboard
Open `http://<your-server-ip>:8080` in your browser and log in.

---

## Your First Deployment

### Via Dashboard
1. Navigate to the **Deploy** tab
2. Paste your GitHub repository URL (e.g., `https://github.com/user/my-app`)
3. Select your AI provider
4. Click **START DEPLOYMENT**
5. Watch the AI analyze your code, generate a plan, and execute it in real-time

### Via CLI
```bash
axle deploy https://github.com/user/my-app
```
AXLE will scan the repo, show you the AI-generated plan, and ask for confirmation before executing.

---

## Dry Run (Plan Only)
Preview what AXLE would do without actually deploying:
```bash
axle plan https://github.com/user/my-app
```

---

## Managing Secrets
```bash
axle secrets set DATABASE_URL postgresql://...
axle secrets set STRIPE_KEY sk_live_...
axle secrets list
axle secrets delete STRIPE_KEY
```

---

## Next Steps
- Read the [Architecture Guide](architecture.md) for technical details
- Check the [Building the Image](building-the-image.md) guide for AMI creation
- See [CONTRIBUTING.md](../CONTRIBUTING.md) to contribute
