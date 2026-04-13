# Changelog

All notable changes to the AXLE OS project will be documented in this file.

## [0.1.0] - 2026-04-13
### Added
- **Sprint 6 Complete:** Built out the Web Dashboard infrastructure.
- Configured Flask API with Socket.IO over port `4000`.
- Scaffodled React 18 frontend with Vite in `web/dashboard`.
- Glassmorphism UI styling applied for high-tech premium aesthetic.
- Deployed React Routes for: Dashboard, Secrets Vault, Deploy Wizard, AI Copilot Chat.
- Native Systemd Daemons: `axle-api.service` and `axle-dashboard.service`.
- WebSockets configured to stream execution engine `stdout` to frontend UI.
- Python test suite expansion covering API endpoints `tests/test_api_endpoints.py`.

### Changed
- UX Base overhaul replacing default layout with Plank dock, Orchis GTK Theme, and Zsh Powerlevel10k shell directly into the core system.
