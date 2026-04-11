#!/usr/bin/env python3
"""
AXLE OS First-Boot Setup Wizard (T-027)

Interactive TUI wizard that runs on first SSH login.
Configures:
  1. AI provider (Gemini / OpenRouter / OpenAI / Ollama)
  2. Admin password for the web dashboard
  3. Optional domain name for SSL
  4. Starts the dashboard service
"""

import os
import sys
import getpass
import subprocess
import json
from pathlib import Path

AXLE_CONF = Path("/etc/axle/axle.conf")
AXLE_DATA = Path("/var/lib/axle")
SETUP_MARKER = AXLE_DATA / ".setup-complete"

BANNER = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║       █████╗ ██╗  ██╗██╗     ███████╗     ██████╗ ███████╗  ║
║      ██╔══██╗╚██╗██╔╝██║     ██╔════╝    ██╔═══██╗██╔════╝  ║
║      ███████║ ╚███╔╝ ██║     █████╗      ██║   ██║███████╗  ║
║      ██╔══██║ ██╔██╗ ██║     ██╔══╝      ██║   ██║╚════██║  ║
║      ██║  ██║██╔╝ ██╗███████╗███████╗    ╚██████╔╝███████║  ║
║      ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚══════╝     ╚═════╝ ╚══════╝  ║
║                                                              ║
║      AXLE OS — First-Boot Setup                              ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""

PROVIDERS = {
    "1": ("gemini", "Google Gemini (recommended — free tier available)"),
    "2": ("openrouter", "OpenRouter (access to multiple models)"),
    "3": ("openai", "OpenAI GPT (requires API key)"),
    "4": ("ollama", "Ollama (local — no API key, needs GPU/RAM)"),
}


def print_header(text: str):
    """Print a section header."""
    print(f"\n{'─' * 50}")
    print(f"  {text}")
    print(f"{'─' * 50}\n")


def setup_ai_provider() -> dict:
    """Configure the AI provider."""
    print_header("Step 1/4 — Choose AI Provider")

    for key, (_, desc) in PROVIDERS.items():
        print(f"  [{key}] {desc}")

    print()
    choice = ""
    while choice not in PROVIDERS:
        choice = input("  Select provider (1-4): ").strip()

    provider_id, provider_name = PROVIDERS[choice]

    api_key = ""
    if provider_id != "ollama":
        print(f"\n  Enter your {provider_name.split('(')[0].strip()} API key:")
        api_key = getpass.getpass("  API Key: ").strip()

        if not api_key:
            print("  ⚠  No API key provided. You can set it later with:")
            print(f"     axle config set {provider_id}_api_key <your-key>")
    else:
        print("\n  Ollama selected — checking if Ollama is installed...")
        result = subprocess.run(["which", "ollama"], capture_output=True)
        if result.returncode != 0:
            print("  ⚠  Ollama not found. Installing...")
            subprocess.run(
                ["bash", "-c", "curl -fsSL https://ollama.com/install.sh | sh"],
                check=False,
            )
        else:
            print("  ✓  Ollama is installed")

    print(f"\n  ✓  AI Provider: {provider_name.split('(')[0].strip()}")
    return {"provider": provider_id, "api_key": api_key}


def setup_admin_password() -> str:
    """Set the admin password for the dashboard."""
    print_header("Step 2/4 — Set Dashboard Admin Password")

    while True:
        password = getpass.getpass("  New password: ").strip()
        if len(password) < 8:
            print("  ✗  Password must be at least 8 characters")
            continue
        confirm = getpass.getpass("  Confirm password: ").strip()
        if password != confirm:
            print("  ✗  Passwords do not match")
            continue
        break

    print("  ✓  Admin password set")
    return password


def setup_domain() -> str:
    """Optionally configure a domain name for SSL."""
    print_header("Step 3/4 — Domain Name (Optional)")

    print("  Enter your domain name for automatic SSL (e.g., myapp.example.com)")
    print("  Leave empty to skip — you can configure this later.\n")

    domain = input("  Domain: ").strip()

    if domain:
        print(f"  ✓  Domain: {domain}")
        print("      SSL will be configured during your first deployment.")
    else:
        print("  ℹ  No domain set — skipping SSL configuration")

    return domain


def start_dashboard():
    """Enable and start the AXLE dashboard."""
    print_header("Step 4/4 — Starting Dashboard")

    print("  Starting AXLE dashboard service...")
    subprocess.run(["systemctl", "enable", "axle-dashboard.service"], check=False)
    subprocess.run(["systemctl", "start", "axle-dashboard.service"], check=False)

    # Get local IP
    result = subprocess.run(
        ["hostname", "-I"], capture_output=True, text=True
    )
    local_ip = result.stdout.strip().split()[0] if result.stdout.strip() else "localhost"

    print(f"  ✓  Dashboard running at: http://{local_ip}:4000")


def write_config(ai_config: dict, password: str, domain: str):
    """Write the setup results to AXLE config."""
    import configparser

    config = configparser.ConfigParser()

    if AXLE_CONF.exists():
        config.read(str(AXLE_CONF))

    if "ai" not in config:
        config["ai"] = {}
    config["ai"]["provider"] = ai_config["provider"]

    if domain:
        if "domain" not in config:
            config["domain"] = {}
        config["domain"]["name"] = domain

    with open(str(AXLE_CONF), "w") as f:
        config.write(f)

    # Store API key in the secrets vault (not in plaintext config)
    if ai_config["api_key"]:
        env_key = f"{ai_config['provider'].upper()}_API_KEY"
        # Write to a temporary env file for the AXLE vault to ingest
        env_file = AXLE_DATA / ".env"
        with open(str(env_file), "a") as f:
            f.write(f"{env_key}={ai_config['api_key']}\n")
        os.chmod(str(env_file), 0o600)

    # Store password hash for dashboard auth
    try:
        import bcrypt
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    except ImportError:
        # Fallback: store using hashlib (less secure but functional)
        import hashlib
        hashed = hashlib.sha256(password.encode()).hexdigest()

    auth_file = AXLE_DATA / "admin.auth"
    with open(str(auth_file), "w") as f:
        f.write(hashed)
    os.chmod(str(auth_file), 0o600)


def main():
    """Run the first-boot setup wizard."""
    print(BANNER)

    if SETUP_MARKER.exists():
        print("  ℹ  AXLE OS is already configured.")
        print("     To reconfigure, delete /var/lib/axle/.setup-complete and run again.")
        sys.exit(0)

    print("  Welcome to AXLE OS! Let's get your deployment engine configured.\n")

    # Step 1: AI Provider
    ai_config = setup_ai_provider()

    # Step 2: Admin Password
    password = setup_admin_password()

    # Step 3: Domain (optional)
    domain = setup_domain()

    # Step 4: Write config and start
    write_config(ai_config, password, domain)
    start_dashboard()

    # Mark setup as complete
    SETUP_MARKER.touch()

    print("\n" + "═" * 50)
    print("  ✓  AXLE OS setup complete!")
    print()
    print("  Next steps:")
    print("    1. Open the dashboard in your browser")
    print("    2. Run: axle deploy <github-url>")
    print("    3. Your app will be live in minutes")
    print("═" * 50 + "\n")


if __name__ == "__main__":
    main()
