# ⚡ AXLE OS

**AI-Powered Linux Deployment Engine**

> Deploy any full-stack application to AWS EC2 with zero manual configuration.
> AI handles Nginx, SSL, databases, dependencies, monitoring — everything.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-green.svg)](https://python.org)
[![Phase](https://img.shields.io/badge/Phase-1%20Foundation-orange.svg)](#roadmap)

---

## What is AXLE OS?

AXLE OS is a **custom Ubuntu-based Linux distribution** purpose-built for AI-powered application deployment — like Proxmox is for virtualization. You launch an EC2 instance with the AXLE AMI, paste a GitHub URL, and the AI deploys everything automatically.

```
1. Launch AXLE OS AMI on EC2
2. SSH in → Run: axle setup
3. Open dashboard → Paste GitHub URL
4. AI detects stack → Generates deployment plan → Executes it
5. App is live on HTTPS. Monitoring active. Done.
```

**Zero installation. Zero configuration. Just launch and deploy.**

## Key Features

- 🧠 **AI-Powered Deployment** — AI scans your repo, detects the stack, and generates a complete deployment plan
- 📦 **Appliance OS** — Everything pre-installed from first boot (Nginx, PostgreSQL, Node.js, Python, Go)
- ⚙️ **Native systemd** — No Docker overhead. Apps run natively with auto-restart
- 🔒 **Encrypted Secrets Vault** — AES-256 encryption, architecturally isolated from the AI engine
- 🩺 **AI Self-Healing Monitor** — 60-second health checks with AI-powered diagnosis
- 💬 **AI Chatbot** — Ask questions about your server using real metrics and logs
- 🌐 **Web Dashboard** — Real-time deploy wizard, log viewer, metrics, and management

## Supported Stacks

| Language | Frameworks | Databases |
|----------|-----------|-----------|
| **Node.js** | Express, Next.js, React, Vue | PostgreSQL |
| **Python** | Django, FastAPI, Flask | MySQL |
| **Go** | Gin, Fiber, net/http | MongoDB *(v2)* |
| **Static** | HTML/CSS/JS, SPAs | Redis *(v2)* |

## Architecture

```
┌─────────────────────────────────────────────┐
│  Layer 3: AXLE Appliance                    │
│  AI Engine · Scanner · Planner · Runner     │
│  Secrets Vault · Monitor · Dashboard · CLI  │
├─────────────────────────────────────────────┤
│  Layer 2: Server Stack (Pre-installed)      │
│  Nginx · Certbot · PostgreSQL · MySQL       │
│  Node.js · Python · Go · UFW               │
├─────────────────────────────────────────────┤
│  Layer 1: Ubuntu 22.04 LTS                  │
│  Kernel · APT · systemd · Cloud-Init · SSH  │
└─────────────────────────────────────────────┘
```

## Quick Start

```bash
# On your EC2 instance running AXLE OS:
axle setup                              # Configure AI provider + admin password
axle deploy https://github.com/user/app # Deploy from GitHub
axle status                             # Check deployment status
axle logs                               # Stream live logs
axle chat "why is my app slow?"         # Ask AI about your server
```

## Project Structure

```
axle/
├── axle/           # Core Python package (scanner, planner, AI, plugins, vault)
├── web/            # Web dashboard (Flask API + React frontend)
├── build/          # Packer AMI build pipeline + branding + first-boot wizard
├── templates/      # Jinja2 templates (Nginx, systemd, database configs)
├── tests/          # Unit and integration tests
└── docs/           # Documentation, whitepaper, competitive analysis
```

## Roadmap

| Phase | Version | Features |
|-------|---------|----------|
| **1 — Core** | v1.0 | AI deployment, scanner, planner, plugins, vault, CLI, dashboard |
| **2 — Monitor** | v1.5 | Health monitor, AI anomaly detection, rollback, chatbot |
| **3 — Scale** | v2.0 | MongoDB/Redis, CI/CD webhooks, multi-cloud, blue-green deploys |
| **4 — Enterprise** | v3.0 | RBAC, audit logging, multi-domain, Slack/email alerts |

## License

MIT License — see [LICENSE](LICENSE) for details.
