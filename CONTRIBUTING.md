# Contributing to AXLE OS

Thank you for your interest in contributing to AXLE OS! This guide will help you get set up.

---

## Development Setup

```bash
git clone https://github.com/kunnaaalll/axle.git
cd axle
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[all,dev]"
```

---

## Running Tests

```bash
# Run the full test suite
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=axle --cov-report=term-missing

# Run a specific test file
pytest tests/test_runner.py -v
```

---

## Project Structure

```
axle/
├── ai/           # AI engine + LLM providers
├── cli.py        # Click CLI commands
├── config/       # Pydantic settings
├── core/         # Scanner, planner, runner, models
├── monitor/      # System monitoring (future)
├── plugins/      # Infrastructure plugins (nginx, db, etc.)
└── secrets/      # AES-256 encrypted vault

web/
├── api/          # Flask + Socket.IO backend
└── dashboard/    # React 18 + Vite frontend

build/
├── branding/     # AXLE OS desktop assets
├── cloud-init/   # Cloud-init configuration
├── packer/       # HashiCorp Packer AMI build
└── services/     # systemd unit files

tests/            # pytest test suite
docs/             # Documentation
```

---

## Code Style

- **Python**: Follow PEP 8. Use type hints where practical.
- **JavaScript/React**: Use functional components and hooks.
- **Commits**: Use conventional commit messages:
  - `feat: add deploy --zip support`
  - `fix: resolve vault password derivation bug`
  - `docs: update architecture diagram`
  - `test: add E2E deployment tests`

---

## Adding a New Plugin

1. Create `axle/plugins/your_plugin.py`
2. Extend `BasePlugin` and implement: `validate()`, `configure()`, `verify()`, `rollback()`
3. Register it in `axle/plugins/registry.py` → `create_default_registry()`
4. Write tests in `tests/test_plugins/test_your_plugin.py`

---

## Adding a New CLI Command

1. Add a new `@main.command()` function in `axle/cli.py`
2. Use Rich for console output (never raw `print()`)
3. Add input validation with Click options/arguments
4. Update `docs/TASKS.md` if tracking

---

## Adding a Dashboard Page

1. Create component in `web/dashboard/src/components/YourPage.jsx`
2. Use `useAuth()` from `context/AuthContext.jsx` for API calls
3. Add route in `App.jsx`
4. Add sidebar nav item

---

## Submitting a Pull Request

1. Fork the repository
2. Create a feature branch: `git checkout -b feat/my-feature`
3. Make your changes and add tests
4. Run `pytest tests/ -v` to ensure all tests pass
5. Commit with a descriptive message
6. Push to your fork and open a PR

---

## Questions?

Open an issue on GitHub or use `axle chat "your question"` to ask the AI copilot directly.
