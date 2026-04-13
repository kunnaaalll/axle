# AXLE OS — Master Task Tracker

> **Rules**: Tasks are executed strictly in order. No task begins until its predecessor is complete.  
> Every completion is logged in [DEVLOG.md](./DEVLOG.md) with a before/after summary.

**Legend**: `[ ]` Todo · `[/]` In Progress · `[x]` Done · `[!]` Blocked

---

## Sprint 1 — Foundation & Scaffolding

> **Goal**: Project infrastructure, build pipeline, branding. A launchable AMI skeleton.

### 1.1 Project Infrastructure
- [x] **T-001**: Create `docs/` folder and organize all documentation
- [x] **T-002**: Set up change tracking (`CHANGELOG.md`, `DEVLOG.md`, `TASKS.md`)
- [x] **T-003**: Scaffold full directory structure (axle/, web/, build/, templates/, tests/)
- [x] **T-004**: Create `pyproject.toml` with all dependencies
- [x] **T-005**: Create `.gitignore`, `.env.example`, `Makefile`
- [x] **T-006**: Initialize all Python `__init__.py` module files
- [x] **T-007**: Create stub `models.py` with Pydantic models
- [x] **T-008**: Create stub `settings.py` with Pydantic settings
- [x] **T-009**: Create stub `cli.py` with Click command group
- [x] **T-010**: Create `__main__.py` entry point

### 1.2 Packer Build Pipeline
- [x] **T-011**: Create `build/packer/variables.pkr.hcl` (AWS region, instance type, AMI name)
- [x] **T-012**: Create `build/packer/axle-ami.pkr.hcl` (main Packer template)
- [x] **T-013**: Create `build/packer/scripts/01-base-setup.sh` (Ubuntu update, base deps)
- [x] **T-014**: Create `build/packer/scripts/02-server-stack.sh` (Nginx, PostgreSQL, Node.js, Python, Go)
- [x] **T-015**: Create `build/packer/scripts/03-install-axle.sh` (install AXLE Python package)
- [x] **T-016**: Create `build/packer/scripts/04-branding.sh` (copy MOTD, os-release, banners)
- [x] **T-017**: Create `build/packer/scripts/05-first-boot.sh` (install first-boot systemd service)
- [x] **T-018**: Create `build/packer/scripts/06-cleanup.sh` (minimize image size)

### 1.3 Branding & First-Boot
- [x] **T-019**: Create `build/branding/motd/00-axle-banner` (ASCII art logo)
- [x] **T-020**: Create `build/branding/motd/10-system-info` (CPU/RAM/disk script)
- [x] **T-021**: Create `build/branding/motd/20-deployment-status` (current app status)
- [x] **T-022**: Create `build/branding/motd/90-help` (quick command reference)
- [x] **T-023**: Create `build/branding/os-release` (AXLE OS identity)
- [x] **T-024**: Create `build/branding/issue` (pre-login banner)
- [x] **T-025**: Create `build/branding/ssh-banner` (SSH connection banner)
- [x] **T-026**: Create `build/firstboot/axle-firstboot.service` (systemd unit)
- [x] **T-027**: Create `build/firstboot/axle-firstboot.py` (TUI setup wizard)
- [x] **T-028**: Create `build/cloud-init/user-data.yaml` (default cloud-init config)

### 1.4 Sprint 1 Verification
- [x] **T-029**: Validate Packer template with `packer validate`
- [x] **T-030**: Test branding scripts locally
- [x] **T-031**: Update DEVLOG and CHANGELOG with Sprint 1 completion

---

## Sprint 2 — Core Engine

> **Goal**: Build the brain — project scanning, AI engine, and deployment planning.

### 2.1 Data Models (Finalize)
- [x] **T-032**: Expand `models.py` — add `FrameworkType` enum (express, django, fastapi, nextjs, flask, etc.)
- [x] **T-033**: Expand `models.py` — add `ServerProfile` model (CPU, RAM, disk, OS)
- [x] **T-034**: Expand `models.py` — add `DeploymentHistory` model (timestamp, status, plan snapshot)
- [x] **T-035**: Expand `models.py` — add `HealthMetrics` model (cpu_percent, ram_used, disk_used, etc.)
- [x] **T-036**: Write unit tests for all models (`tests/test_models.py`)

### 2.2 Project Scanner
- [x] **T-037**: Create `axle/core/scanner.py` — `scan_repository(path)` function
- [x] **T-038**: Implement Node.js detection (package.json → read dependencies → detect framework)
- [x] **T-039**: Implement Python detection (requirements.txt / pyproject.toml → detect framework)
- [x] **T-040**: Implement Go detection (go.mod → detect framework)
- [x] **T-041**: Implement static site detection (index.html only, no backend)
- [x] **T-042**: Implement database detection (scan for DB connection strings, ORM packages)
- [x] **T-043**: Implement build/start command inference (scripts in package.json, Procfile, etc.)
- [x] **T-044**: Add GitHub URL cloning support (clone repo → scan → return ProjectProfile)
- [x] **T-045**: Write unit tests for scanner (`tests/test_scanner.py`) with fixture repos

### 2.3 AI Engine
- [x] **T-046**: Create `axle/ai/engine.py` — `AIEngine` class with provider abstraction
- [x] **T-047**: Define common interface: `generate_plan(profile, server) -> DeploymentPlan`
- [x] **T-048**: Define common interface: `diagnose(metrics, logs) -> str`
- [x] **T-049**: Create `axle/ai/providers/gemini_provider.py` — Google Gemini implementation
- [x] **T-050**: Create `axle/ai/providers/openai_provider.py` — OpenAI GPT implementation
- [x] **T-050B**: Create `axle/ai/providers/openrouter_provider.py` — OpenRouter multi-model implementation
- [x] **T-051**: Create `axle/ai/providers/ollama_provider.py` — Local Ollama implementation
- [x] **T-052**: Create `axle/ai/prompts.py` — system prompts for deployment planning
- [x] **T-053**: Add prompt for diagnosis/monitoring context
- [x] **T-054**: Implement provider fallback (Gemini → OpenRouter → OpenAI → Ollama)
- [x] **T-055**: Write unit tests for AI engine with mocked providers (`tests/test_ai.py`)

### 2.4 Deployment Planner
- [x] **T-056**: Create `axle/core/planner.py` — `Planner` class
- [x] **T-057**: Implement `generate_plan()` — takes ProjectProfile + ServerProfile → calls AI → returns DeploymentPlan
- [x] **T-058**: Implement step dependency resolution (which steps can run in parallel)
- [x] **T-059**: Implement plan validation (check all required steps present)
- [x] **T-060**: Implement plan preview/dry-run output (formatted for CLI)
- [x] **T-061**: Write unit tests for planner (`tests/test_planner.py`)

### 2.5 Core Verification
- [x] **T-062**: End-to-end test: clone real repo → scan → generate plan → print plan
- [x] **T-063**: Test with Node.js + Express + PostgreSQL repo
- [x] **T-064**: Test with Python + FastAPI repo
- [x] **T-065**: Test with static HTML site
- [x] **T-066**: Update DEVLOG and CHANGELOG with Sprint 2 completion

---

## Sprint 3 — Server Plugins

> **Goal**: Build every configuration plugin that touches the EC2 server.

### 3.1 Plugin Architecture
- [x] **T-067**: Create `axle/plugins/base.py` — abstract `BasePlugin` class
- [x] **T-068**: Define plugin lifecycle: `validate() → configure() → verify() → rollback()`
- [x] **T-069**: Define plugin registry (discover and load plugins dynamically)

### 3.2 Jinja2 Templates
- [x] **T-070**: Create `templates/nginx/reverse_proxy.conf.j2` (backend only)
- [x] **T-071**: Create `templates/nginx/static_site.conf.j2` (static files only)
- [x] **T-072**: Create `templates/nginx/fullstack.conf.j2` (frontend + backend + API proxy)
- [x] **T-073**: Create `templates/systemd/app.service.j2` (generic app service file)
- [x] **T-074**: Create `templates/database/postgres_init.sql.j2` (create user, db, grant)
- [x] **T-075**: Create `templates/database/mysql_init.sql.j2` (create user, db, grant)

### 3.3 Individual Plugins
- [x] **T-076**: Create `axle/plugins/nginx.py` — generate config, validate (`nginx -t`), reload
- [x] **T-077**: Create `axle/plugins/ssl.py` — request cert via Certbot, configure HTTPS redirect, schedule renewal
- [x] **T-078**: Create `axle/plugins/database.py` — init PostgreSQL/MySQL, create user/db, run migrations
- [x] **T-079**: Create `axle/plugins/systemd.py` — write service file, enable, start, status, restart
- [x] **T-080**: Create `axle/plugins/runtime.py` — install Node/Python/Go, install deps, run build
- [x] **T-081**: Create `axle/plugins/firewall.py` — manage UFW rules (open/close ports)
- [x] **T-082**: Write unit tests for each plugin (`tests/test_plugins/`)

### 3.4 Sprint 3 Verification
- [x] **T-083**: Test Nginx plugin generates valid configs for all template types
- [x] **T-084**: Test systemd plugin generates valid service files
- [x] **T-085**: Test database plugin generates valid SQL init scripts
- [x] **T-086**: Update DEVLOG and CHANGELOG with Sprint 3 completion

---

## Sprint 4 — Desktop GUI Integration

> **Goal**: Turn the headless OS into a full, branded Linux desktop experience.

### 4.1 Desktop Environment
- [x] **T-GUI-01**: Add `07-desktop-gui.sh` stage to Packer pipeline
- [x] **T-GUI-02**: Install XFCE4, Arc-Dark theme, and Papirus icon set
- [x] **T-GUI-03**: Configure LightDM GTK Greeter with AXLE branding
- [x] **T-GUI-04**: Build Plymouth boot splash animation and custom GRUB theme
- [x] **T-GUI-05**: Configure xRDP and VNC for remote desktop access on EC2
- [x] **T-GUI-06**: Create desktop shortcuts (Terminal, Deploy App, Dashboard)
- [x] **T-GUI-07**: Write 28 unit tests for GUI assets and configs

---

## Sprint 5 — Execution + CLI + Vault

> **Goal**: Wire everything together — execute plans, manage secrets, complete CLI.

### 5.1 Async Task Runner
- [x] **T-087**: Create `axle/core/runner.py` — `TaskRunner` class
- [x] **T-088**: Implement dependency graph execution (topological sort of steps)
- [x] **T-089**: Implement parallel execution of independent steps (asyncio.gather)
- [x] **T-090**: Implement real-time log streaming (stdout/stderr capture per step)
- [x] **T-091**: Implement step status tracking (pending → running → completed/failed)
- [x] **T-092**: Implement failure handling (stop on error, rollback option)
- [x] **T-093**: Write unit tests for runner (`tests/test_runner.py`)

### 5.2 Secrets Vault
- [x] **T-094**: Create `axle/secrets/vault.py` — `Vault` class
- [x] **T-095**: Implement AES-256 encryption/decryption at rest
- [x] **T-096**: Implement PBKDF2 key derivation from admin password
- [x] **T-097**: Implement CRUD: `set(key, value)`, `get(key)`, `delete(key)`, `list_keys()`
- [x] **T-098**: Implement runtime injection — write to systemd `EnvironmentFile`
- [x] **T-099**: Ensure AI isolation — `list_keys()` returns keys only, never values
- [x] **T-100**: Write unit tests for vault (`tests/test_vault.py`)

### 5.3 Complete CLI
- [x] **T-101**: `axle deploy <url>` — full flow: clone → scan → plan → confirm → execute
- [x] **T-102**: `axle deploy --zip <file>` — deploy from ZIP archive
- [x] **T-103**: `axle plan <url>` — dry-run: show plan without executing
- [x] **T-104**: `axle status` — show current deployment status + health
- [x] **T-105**: `axle logs` — stream live application logs
- [x] **T-106**: `axle logs --tail N` — show last N lines
- [x] **T-107**: `axle secrets list` — show all env variable keys (no values)
- [x] **T-108**: `axle secrets set KEY=value` — add/update a secret
- [x] **T-109**: `axle secrets delete KEY` — remove a secret
- [x] **T-110**: `axle rollback` — revert to previous deployment
- [x] **T-111**: `axle rollback --list` — list available snapshots
- [x] **T-112**: `axle setup` — first-boot wizard (TUI via Rich/Textual)
- [x] **T-113**: `axle info` — show AXLE version, system info, AI provider
- [x] **T-114**: `axle chat "question"` — ask AI about the server
- [x] **T-115**: `axle update` — self-update AXLE packages
- [x] **T-116**: `axle dashboard start|stop` — control the web dashboard service

### 5.4 Sprint 5 Verification
- [x] **T-117**: End-to-end CLI test: `axle deploy` with a real GitHub repo
- [x] **T-118**: Test secrets vault encryption round-trip
- [x] **T-119**: Test rollback creates and restores snapshots correctly
- [x] **T-120**: Update DEVLOG and CHANGELOG with Sprint 5 completion

---

## Sprint 6 — Web Dashboard

> **Goal**: Build the browser-based real-time dashboard.

### 6.1 Flask API Backend
- [x] **T-121**: Create `web/api/app.py` — Flask app factory + Socket.IO + CORS
- [x] **T-122**: Create `web/api/auth.py` — password login (bcrypt hash, session token)
- [x] **T-123**: Create `web/api/routes/deploy.py` — POST /deploy, GET /deploy/status
- [x] **T-124**: Create `web/api/routes/projects.py` — GET /projects, GET /projects/:id
- [x] **T-125**: Create `web/api/routes/secrets.py` — CRUD for secrets (keys only in response)
- [x] **T-126**: Create `web/api/routes/monitor.py` — GET /metrics, GET /health
- [x] **T-127**: Create `web/api/routes/chatbot.py` — POST /chat (AI query)
- [x] **T-128**: Create `web/api/websocket.py` — Socket.IO events for live logs
- [x] **T-129**: Write API tests (`tests/test_api/`)

### 6.2 React Frontend Setup
- [x] **T-130**: Initialize Vite + React 18 project in `web/dashboard/`
- [x] **T-131**: Create design system: dark theme, color tokens, typography (`index.css`)
- [x] **T-132**: Create layout: sidebar navigation + main content area
- [x] **T-133**: Install and configure Socket.IO client, React Router

### 6.3 Dashboard Components
- [x] **T-134**: Build `DeployWizard` — URL input → scan progress → plan review → deploy → live logs
- [x] **T-135**: Build `LogViewer` — real-time terminal output with ANSI color support
- [x] **T-136**: Build `Dashboard` (home) — system metrics cards (CPU, RAM, disk), deployment status
- [x] **T-137**: Build `SecretsVault` — table of keys, add/edit/delete, values masked
- [x] **T-138**: Build `DeployHistory` — list of past deploys with rollback button
- [x] **T-139**: Build `Chatbot` — AI chat panel with message history
- [x] **T-140**: Build login page — password-based authentication

### 6.4 systemd Services
- [x] **T-141**: Create `axle-api.service` (runs Flask API on boot)
- [x] **T-142**: Create `axle-dashboard.service` (serves React build on :4000)

### 6.5 Sprint 6 Verification
- [x] **T-143**: Test dashboard login flow
- [x] **T-144**: Test deploy wizard end-to-end from browser
- [x] **T-145**: Test live log streaming via WebSocket
- [x] **T-146**: Test secrets management from UI
- [x] **T-147**: Update DEVLOG and CHANGELOG with Sprint 6 completion

---

## Sprint 7 — Polish & Ship

> **Goal**: End-to-end testing, error handling, documentation, publish.

### 7.1 Error Handling & Resilience
- [x] **T-148**: Add graceful failure handling to task runner (rollback on error)
- [x] **T-149**: Add retry logic for transient failures (network, apt installs)
- [x] **T-150**: Add input validation for all CLI commands
- [x] **T-151**: Add input validation for all API endpoints

### 7.2 End-to-End Testing
- [x] **T-152**: Deploy test: React + Express + PostgreSQL (full-stack)
- [x] **T-153**: Deploy test: Next.js (SSR application)
- [x] **T-154**: Deploy test: Django + PostgreSQL (Python stack)
- [x] **T-155**: Deploy test: FastAPI (Python API)
- [x] **T-156**: Deploy test: Static HTML site (simplest case)

### 7.3 Documentation
- [x] **T-157**: Write final `README.md` with badges, screenshots, quick start
- [x] **T-158**: Finalize `docs/getting-started.md`
- [x] **T-159**: Finalize `docs/architecture.md` with final diagrams
- [x] **T-160**: Create `docs/building-the-image.md` (how to build AXLE AMI)
- [x] **T-161**: Create contributor guide (`CONTRIBUTING.md`)

### 7.4 Release
- [x] **T-162**: Build final AXLE OS AMI
- [x] **T-163**: Test cold launch on fresh EC2 instance
- [x] **T-164**: Verify first-boot wizard works end-to-end
- [x] **T-165**: Verify MOTD displays correctly on SSH
- [x] **T-166**: Verify secrets never appear in logs
- [x] **T-167**: Final CHANGELOG entry for v1.0.0
- [x] **T-168**: Tag release in Git

---

## Progress Summary

| Sprint | Total Tasks | Done | Remaining |
|--------|:-----------:|:----:|:---------:|
| **1 — Foundation** | 31 | 31 | 0 |
| **2 — Core Engine** | 35 | 35 | 0 |
| **3 — Plugins** | 20 | 20 | 0 |
| **4 — Desktop GUI** | 7 | 7 | 0 |
| **5 — Execution** | 34 | 34 | 0 |
| **6 — Dashboard** | 27 | 27 | 0 |
| **7 — Polish** | 21 | 21 | 0 |
| **TOTAL** | **175** | **175** | **0** |

---

> **Status**: COMPLETED. (v1.0.0 Output Finalized)
