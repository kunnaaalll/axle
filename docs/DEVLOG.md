# Development Log (DEVLOG)

This file tracks granular, day-to-day changes, technical decisions, and progress during the development of AXLE OS.

---

## 2026-04-12

### Initial Setup & Planning
- **Task**: Project initialization and strategy.
- **Decision**: Confirmed AXLE OS as a native systemd-based appliance OS (no Docker).
- **Decision**: Default AI provider set to Gemini for Phase 1.
- **Action**: Created detailed Project Blueprint and Competitive Analysis.
- **Action**: Organized documentation into `/docs` folder.
- **Action**: Established change tracking via `CHANGELOG.md`, `DEVLOG.md` and `TASKS.md`.
- **Action**: Scaffolded complete project directory structure (axle, web, build, templates, tests).
- **Action**: Created core configuration files: `pyproject.toml`, `.gitignore`, `.env.example`, `Makefile`.
- **Action**: Initialized Python package stubs and core models/settings.
- **Status**: Sprint 1 (Foundation) infrastructure complete. Transitioning to core component implementation.

### Sprint 1 Build — Packer Pipeline & Branding (T-011 to T-028)
- **What changed**: Created the 6-stage AMI build pipeline using HashiCorp Packer and complete OS branding.
- **Before**: Empty `build/packer/`, `build/branding/`, `build/firstboot/` directories.
- **After**: Full provisioning pipeline — base setup, server stack (Nginx, Postgres, MySQL, Node.js, Python, Go), AXLE package install. Branded MOTD scripts, os-release, SSH banners, TUI first-boot wizard.
- **Files added**: `variables.pkr.hcl`, `axle-ami.pkr.hcl`, `01-base-setup.sh` to `06-cleanup.sh`, MOTD scripts, `axle-firstboot.py`.

### Feature Change: Added OpenRouter AI Provider
- **What changed**: Added OpenRouter as a 4th AI provider alongside OpenAI, Gemini, and Ollama.
- **Before**: 3 providers (OpenAI, Gemini, Ollama). Fallback: Gemini → OpenAI → Ollama.
- **After**: 4 providers (OpenAI, Gemini, OpenRouter, Ollama). Fallback: Gemini → OpenRouter → OpenAI → Ollama.
- **Files modified**: `axle/config/settings.py`, `.env.example`, `docs/TASKS.md`
- **Files added**: `axle/ai/providers/openrouter_provider.py`

### Sprint 2 — Core Engine (Scanner, AI Engine, Planner, CLI)
- **What changed**: Implemented the complete "brain" of the OS.
- **Before**: Project was a headless skeleton.
- **After**: Node/Python/Go/Static/DB project scanner; robust AIEngine with fallback; Deployment Planner using Kahn's topological sort for dependency resolution. Completely functional Click CLI with `scan`, `plan`, `info`, and `status`.
- **Tests**: 181 passing tests (86% overall coverage). API calls heavily mocked.
- **Files added**: `axle/core/scanner.py`, `axle/core/planner.py`, `axle/ai/engine.py`, `axle/cli.py`

### Feature Change: Desktop OS GUI Integration
- **What changed**: Transitioned from a pure headless system to a fully immersive Desktop Linux Distribution.
- **Before**: Headless AWS EC2 image, accessible only via SSH.
- **After**: Packer pipeline expanded to 8 stages to install XFCE4, customized LightDM login screen, Plymouth animated boot splash, GRUB bootloader theme, remote desktop support (xRDP, VNC) and autostart shortcuts (Dashboard auto-launches in Firefox). Added custom dark-circuit wallpapers.
- **Files added**: `07-desktop-gui.sh` (Packer stage), Desktop XML Configs, LightDM Configs, Plymouth theme script, `.desktop` autostart files. Image assets (wallpapers, splash screens) stored natively. Note: 28 CLI-level unit tests for GUI configuration files added.

### Sprint 3 — Server Plugins 
- **What changed**: Complete plugin architecture crafted to execute the AI step directives on the backend Linux servers.
- **Before**: The engine generated abstract JSON plans with no means to execute them on bare metal Linux constructs.
- **After**: A strict base plugin lifecycle with `validate() -> configure() -> verify() -> rollback()`.
- **Implementations**: NginxPlugin (3 configs), SSLPlugin (Certbot), DatabasePlugin (PG/MySQL), SystemdPlugin, RuntimePlugin (nvm/go/py), FirewallPlugin (ufw/xRDP). Added 6 powerful Jinja2 templates covering Node, static, Python architectures.
- **Tests**: Reached 257 passing tests (72% complete test coverage of execution code simulating bare-metal runs).
- **Files added**: `axle/plugins/base.py`, `axle/plugins/registry.py`, 6 concrete plugins (`nginx.py`, `database.py`, etc.), `/templates/*/*.j2`, `tests/test_plugins.py`.
