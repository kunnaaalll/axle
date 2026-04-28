# AXLE OS Architecture

This document describes the full technical architecture of AXLE OS v1.0.0.

---

## High-Level Overview

AXLE OS follows a **three-layer appliance architecture**:

```
┌─────────────────────────────────────────────────────────┐
│                   Layer 3: AXLE Appliance               │
│  ┌──────────┐  ┌─────────┐  ┌──────────┐  ┌─────────┐   │
│  │ AI Engine│  │ Planner │  │  Runner  │  │Dashboard│.  │
│  └──────────┘  └─────────┘  └──────────┘  └─────────┘.  │
├─────────────────────────────────────────────────────────┤
│                   Layer 2: Server Stack                 │
│  Nginx • PostgreSQL • Node.js • Python • Docker         │
├─────────────────────────────────────────────────────────┤
│                   Layer 1: Ubuntu 24.04 LTS             │
│  systemd • apt • ufw • certbot • cloud-init             │
└─────────────────────────────────────────────────────────┘
```

---

## Component Flow

```
GitHub URL
    │
    ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Scanner    │────▶│  AI Engine   │────▶│   Planner    │
│ (detect      │     │ (Gemini /    │     │ (generate    │
│  stack)      │     │  OpenAI)     │     │  steps)      │
└──────────────┘     └──────────────┘     └──────┬───────┘
                                                  │
                                                  ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Dashboard  │◀────│  WebSocket   │◀────│ Task Runner  │
│ (React UI)   │     │ (live logs)  │     │ (async exec) │
└──────────────┘     └──────────────┘     └──────┬───────┘
                                                  │
                                          ┌───────┴───────┐
                                          │   Plugins     │
                                          │ nginx│runtime │
                                          │ db   │ssl     │
                                          │ ufw  │systemd │
                                          └───────────────┘
```

---

## Core Components

### 1. Project Scanner (`axle/core/scanner.py`)
Clones and analyzes a Git repository to produce a `ProjectProfile`:
- Detects stack (Node.js, Python, Go, Java, Static)
- Detects framework (Express, Next.js, Django, FastAPI, Flask, etc.)
- Detects database (PostgreSQL, MySQL, MongoDB, Redis)
- Extracts env vars, build/start commands, ports

### 2. AI Engine (`axle/ai/engine.py`)
Multi-provider abstraction supporting hot-swappable LLMs:
- **Providers**: Google Gemini, OpenAI, OpenRouter, Ollama (local)
- Automatic fallback: if preferred provider fails, tries others
- Structured JSON output parsing for deployment plans

### 3. Deployment Planner (`axle/core/planner.py`)
Converts a `ProjectProfile` + AI response into a `DeploymentPlan`:
- Topological dependency sorting
- Groups independent steps into parallel execution waves
- Maps steps to concrete plugins

### 4. Async Task Runner (`axle/core/runner.py`)
Executes plans with production resilience:
- **Parallel wave execution** via `asyncio.gather`
- **3-attempt retry logic** for transient failures
- **Automatic rollback** on critical failures
- **Live log streaming** captured per-step

### 5. Plugin System (`axle/plugins/`)
Each infrastructure concern is encapsulated in a plugin:

| Plugin | Responsibility |
|--------|---------------|
| `nginx` | Reverse proxy, static serving, SSL termination |
| `runtime` | Node.js/Python/Go installation and versioning |
| `database` | PostgreSQL/MySQL setup, user creation, migrations |
| `ssl` | Let's Encrypt certificate provisioning via certbot |
| `firewall` | UFW rules for port management |
| `systemd` | Service file generation and process management |

### 6. Secrets Vault (`axle/secrets/vault.py`)
- AES-256 encryption via Fernet (PBKDF2 key derivation)
- `list_keys()` never exposes values — AI isolation enforced
- Writes directly to systemd `EnvironmentFile` overlays

### 7. Web Dashboard (`web/`)
- **Backend**: Flask + Socket.IO on port 4000
- **Frontend**: React 18 + Vite with glassmorphism design
- **Auth**: Password login → session token → bearer auth
- **Pages**: Dashboard, Deploy Wizard, Deploy History, Secrets Vault, AI Copilot

### 8. CLI (`axle/cli.py`)
Full command suite via Click:
```
axle scan <url>          # Detect project stack
axle plan <url>          # AI dry-run plan
axle deploy <url>        # Full deployment
axle status              # System health
axle logs --tail 100     # View logs
axle secrets list|set|delete
axle rollback [--list]   # Revert deployment
axle setup               # First-boot wizard
axle chat "question"     # AI copilot
axle dashboard start|stop
axle update              # Self-update
axle info                # System info
```

---

## Data Flow

1. **Input**: GitHub URL (or local path)
2. **Scan**: Clone repo → detect `ProjectProfile`
3. **Plan**: Send profile to LLM → receive structured `DeploymentPlan`
4. **Execute**: Run plan through plugin pipeline with retry + rollback
5. **Monitor**: Metrics polling + live WebSocket log streaming to dashboard
6. **Persist**: Deployment history stored for rollback capability

---

## Security Model

- Dashboard password hashed with `werkzeug.security` (scrypt)
- Vault encrypted at rest with AES-256 (Fernet + PBKDF2)
- Secrets never exposed to AI context — only key names visible
- Bearer token authentication for all API endpoints
- UFW firewall configured per deployment
