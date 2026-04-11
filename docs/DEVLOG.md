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
- **Action**: Established change tracking via `CHANGELOG.md` and `DEVLOG.md`.
- **Action**: Scaffolded complete project directory structure (axle, web, build, templates, tests).
- **Action**: Created core configuration files: `pyproject.toml`, `.gitignore`, `.env.example`, `Makefile`.
- **Action**: Initialized Python package stubs and core models/settings.
- **Status**: Sprint 1 (Foundation) infrastructure complete. Transitioning to core component implementation.

### Feature Change: Added OpenRouter AI Provider
- **What changed**: Added OpenRouter as a 4th AI provider alongside OpenAI, Gemini, and Ollama.
- **Before**: 3 providers (OpenAI, Gemini, Ollama). Fallback: Gemini → OpenAI → Ollama.
- **After**: 4 providers (OpenAI, Gemini, OpenRouter, Ollama). Fallback: Gemini → OpenRouter → OpenAI → Ollama.
- **Files modified**: `axle/config/settings.py`, `.env.example`, `docs/TASKS.md`
- **Files added**: `axle/ai/providers/openrouter_provider.py` (stub)

### Sprint 1 Build — Packer Pipeline (T-011 to T-018)
- **What changed**: Created the complete AMI build pipeline using HashiCorp Packer.
- **Before**: Empty `build/packer/` directory.
- **After**: Full 6-stage provisioning pipeline — base setup, server stack (Nginx, PostgreSQL 16, MySQL 8, Node.js 18/20/22, Python 3.10-3.12, Go 1.22), AXLE appliance install, branding, first-boot wizard, and cleanup/optimization.
- **Files added**: `variables.pkr.hcl`, `axle-ami.pkr.hcl`, `01-base-setup.sh` through `06-cleanup.sh`

### Sprint 1 Build — Branding & First-Boot (T-019 to T-028)
- **What changed**: Created all OS branding assets and the interactive first-boot wizard.
- **Before**: Empty `build/branding/` and `build/firstboot/` directories.
- **After**: MOTD scripts (ASCII banner, system info, deployment status, help), os-release identity, SSH/issue banners, styled Nginx welcome page, systemd first-boot service, Python TUI setup wizard (AI provider, admin password, domain, dashboard start), cloud-init config.
- **Files added**: 12 files across `build/branding/`, `build/firstboot/`, `build/cloud-init/`
