# Changelog

All notable changes to the AXLE OS project will be documented in this file.

## [1.0.0] - 2026-04-28

### Added
- **Core Engine**: Project scanner with auto-detection for Node.js, Python, Go, Java, and static sites
- **AI Engine**: Multi-provider support (Gemini, OpenAI, OpenRouter, Ollama) with automatic fallback
- **Deployment Planner**: AI-generated deployment plans with topological dependency sorting
- **Async Task Runner**: Parallel wave execution with 3-attempt retry logic and automatic rollback
- **Secrets Vault**: AES-256 encrypted environment variable storage with PBKDF2 key derivation
- **Plugin System**: Nginx, runtime, database, SSL, firewall, and systemd plugins
- **CLI**: Full command suite — deploy, plan, scan, secrets, rollback, setup, chat, dashboard, update, info, status, logs
- **Web Dashboard**: React 18 + Vite frontend with glassmorphism design
  - Login page with password authentication
  - System metrics dashboard (CPU, RAM, Disk)
  - Deployment wizard with live WebSocket log streaming
  - Deployment history with rollback capability
  - Secrets vault management UI
  - AI Copilot chat interface
- **Flask API**: RESTful backend with Socket.IO, CORS, and bearer token auth
- **systemd Services**: Auto-start daemons for API and dashboard
- **Build Pipeline**: Packer scripts for AMI creation, cloud-init, branding
- **Documentation**: Architecture guide, getting started, AMI build guide, contributing guide
- **Test Suite**: 13 test files covering scanner, planner, runner, plugins, vault, CLI, API endpoints, and E2E deployments

### Security
- Password-based dashboard authentication with scrypt hashing
- Bearer token session management
- Vault encryption isolated from AI context
- UFW firewall plugin for port management

## [0.1.0] - 2026-04-13
### Added
- Initial Sprint 1-4 foundation: scanner, AI engine, planner, plugins, desktop GUI
