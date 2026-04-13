<div align="center">
  <img src="https://via.placeholder.com/150/8b5cf6/ffffff?text=AXLE" alt="AXLE OS Logo" width="150"/>
  <h1>AXLE OS Framework</h1>
  <p>The Advanced, AI-Powered Autonomous Deployment Engine.</p>
  
  <p>
    <img src="https://img.shields.io/badge/version-1.0.0-blue.svg?style=for-the-badge" alt="Version"/>
    <img src="https://img.shields.io/badge/Python-3.9+-yellow.svg?style=for-the-badge" alt="Python Version"/>
    <img src="https://img.shields.io/badge/status-active-success.svg?style=for-the-badge" alt="Status"/>
  </p>
</div>

---

## ⚡ What is AXLE?
The **Autonomous eXecution & Linux Engine (AXLE)** is an intelligent proxy layer built for Ubuntu architectures. Using Large Language Models (Gemini, OpenAI, Groq), AXLE autonomously scans inbound GitHub codebases, maps their required server architecture (Nginx, Node.js, Python, PostgreSQL), and generates parallel deployment execution waves. 

AXLE takes raw code and boots it straight onto your EC2 server in seconds, completely removing DevOps bottlenecks.

### Core Features
- **AI-Driven Infrastructure Scanning:** Generates customized dependency manifests from foreign repositories.
- **Topological Async Execution:** Maps deployment tasks into acyclic dependency graphs and runs independent waves in parallel via `asyncio`.
- **Secrets Vault:** AES-256 military-grade encryption injects keys directly into `systemd` daemon `EnvironmentFile` overlays.
- **Glassmorphism React Dashboard:** Real-time web panel offering VNC metrics, live ANSI log streaming over WebSockets, and AI Chatbot coping.

---

## 🔧 Getting Started

### 1. Requirements
- Canonical Ubuntu 24.04 (Multipass / EC2)
- Python 3.9+ 
- Node.js 18+

### 2. Rapid Installation
```bash
git clone https://github.com/kunnaaalll/axle.git
cd axle 
chmod +x build/packer/scripts/*.sh

# Run the base provisioning scripts
./build/packer/scripts/01-system-base.sh
./build/packer/scripts/02-docker-setup.sh
./build/packer/scripts/03-python-env.sh
./build/packer/scripts/07-desktop-gui.sh
```

### 3. Launching the Web Engine
```bash
# Initialize Engine
source /opt/axle/venv/bin/activate
export FLASK_APP=web.api.app
flask run --host=0.0.0.0 --port=4000

# Launch Dashboard
cd web/dashboard
npm install
npm run dev
```

---

## 🏗️ Architecture Design (T-159)
AXLE is deeply integrated at the host level:
1. **Host Orchestration (`TaskRunner`)**: Maps generic steps into strictly controlled Shell bindings using polymorphic Plugin classes (`BasePlugin`).
2. **WebSockets Bridge**: The execution engine pipes stdout logs directly through Flask into `lucide-react` terminals.
3. **Rollback Resilience**: In the event of a fatal sequence crash during an `apt install`, AXLE reverses wave execution automatically. 

---

## 💡 Contributing (T-161)
We welcome patches targeting SRE workflows, Node runtime logic, or Web Dashboard UI enhancements. Please run `pytest tests/` before submitting Pull Requests.

---
*Developed proudly by the Antigravity Team for the AXLE Engine Roadmap.*
