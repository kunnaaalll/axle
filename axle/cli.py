"""
AXLE OS — CLI (Command Line Interface)

The main entry point for all AXLE operations.
Wire-up of scanner, AI engine, and planner into real commands.
"""
import click
import json
import sys
import asyncio
from pathlib import Path

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box

console = Console()


@click.group()
@click.version_option(version="0.1.0", prog_name="AXLE OS")
def main():
    """⚡ AXLE OS — AI-Powered Linux Deployment Engine"""
    pass


# =============================================================================
# axle scan <path-or-url>
# =============================================================================

@main.command()
@click.argument("target")
def scan(target):
    """Scan a project directory or GitHub URL and detect its stack."""
    from axle.core.scanner import scan_repository, clone_and_scan

    console.print("\n[bold cyan]⚡ AXLE OS Scanner[/bold cyan]\n")

    try:
        if target.startswith("http") or target.startswith("git@"):
            console.print(f"  Cloning [bold]{target}[/bold]...")
            with console.status("[cyan]Scanning repository...[/cyan]"):
                profile = clone_and_scan(target)
        else:
            console.print(f"  Scanning [bold]{target}[/bold]...")
            profile = scan_repository(target)

        _display_profile(profile)

    except Exception as e:
        console.print(f"  [red]✗ Scan failed:[/red] {e}")
        sys.exit(1)


# =============================================================================
# axle plan <path-or-url>
# =============================================================================

@main.command()
@click.argument("target")
@click.option("--provider", default=None, help="AI provider to use (gemini, openrouter, openai, ollama)")
def plan(target, provider):
    """Generate a deployment plan for a project (dry-run)."""
    from axle.core.scanner import scan_repository, clone_and_scan
    from axle.ai.engine import AIEngine
    from axle.core.planner import Planner
    from axle.config.settings import settings

    console.print("\n[bold cyan]⚡ AXLE OS Planner[/bold cyan]\n")

    try:
        if target.startswith("http") or target.startswith("git@"):
            with console.status("[cyan]Cloning & scanning...[/cyan]"):
                profile = clone_and_scan(target)
        else:
            profile = scan_repository(target)
    except Exception as e:
        console.print(f"  [red]✗ Scan failed:[/red] {e}")
        sys.exit(1)

    _display_profile(profile)
    console.print("\n  [yellow]Generating deployment plan via AI...[/yellow]")

    engine = AIEngine(
        gemini_api_key=settings.gemini_api_key,
        openai_api_key=settings.openai_api_key,
        openrouter_api_key=settings.openrouter_api_key,
        preferred_provider=provider,
    )

    try:
        available = engine.list_available_providers()
        if not available:
            console.print("  [red]✗ No AI provider configured.[/red]")
            return

        planner = Planner(engine)
        with console.status("[cyan]AI is thinking...[/cyan]"):
            deployment_plan = planner.generate_plan(profile)

        _display_plan(deployment_plan, planner)

    except Exception as e:
        console.print(f"  [red]✗ Plan generation failed:[/red] {e}")
        sys.exit(1)


# =============================================================================
# axle deploy <url>
# =============================================================================

@main.command()
@click.argument("repo_url")
@click.option("--provider", default=None, help="AI provider to use")
def deploy(repo_url, provider):
    """Deploy an application from a GitHub repository URL or Path."""
    from axle.core.scanner import scan_repository, clone_and_scan
    from axle.ai.engine import AIEngine
    from axle.core.planner import Planner
    from axle.core.runner import TaskRunner
    from axle.config.settings import settings

    console.print(f"\n[bold cyan]⚡ AXLE OS Deploy[/bold cyan] — {repo_url}\n")

    # 1. Scan
    try:
        if repo_url.startswith("http") or repo_url.startswith("git@"):
            with console.status("[cyan]Cloning & scanning...[/cyan]"):
                profile = clone_and_scan(repo_url)
        else:
            profile = scan_repository(repo_url)
    except Exception as e:
        console.print(f"  [red]✗ Scan failed:[/red] {e}")
        sys.exit(1)

    _display_profile(profile)

    # 2. Plan
    engine = AIEngine(
        gemini_api_key=settings.gemini_api_key,
        openai_api_key=settings.openai_api_key,
        openrouter_api_key=settings.openrouter_api_key,
        preferred_provider=provider,
    )
    if not engine.list_available_providers():
        console.print("  [red]✗ No AI provider configured.[/red]")
        sys.exit(1)

    planner = Planner(engine)
    with console.status("[cyan]AI is generating deployment plan...[/cyan]"):
        try:
            plan = planner.generate_plan(profile)
        except Exception as e:
            console.print(f"  [red]✗ Plan generation failed:[/red] {e}")
            sys.exit(1)

    _display_plan(plan, planner)
    
    if not click.confirm("\n  [bold yellow]? Proceed with deployment?[/bold yellow]", default=True):
        console.print("  [red]Deployment cancelled.[/red]")
        sys.exit(0)

    # 3. Execute
    runner = TaskRunner()
    context = {"app_name": profile.name, "port": profile.port, "stack": profile.stack.value}
    
    console.print("\n  [bold cyan]🚀 Executing Deployment...[/bold cyan]")
    
    # We use asyncio.run to execute the async runner from synchronous click command
    final_plan = asyncio.run(runner.execute_plan(plan, context))
    
    if any(s.status == "failed" for s in final_plan.steps):
        console.print("\n  [bold red]✗ Deployment Failed.[/bold red] Run 'axle logs' for details.")
        sys.exit(1)
    else:
        console.print("\n  [bold green]✓ Deployment completed successfully![/bold green]")


# =============================================================================
# axle secrets (Vault)
# =============================================================================

@main.group()
def secrets():
    """Manage encrypted API keys and environment variables."""
    pass

@secrets.command("list")
def list_secrets():
    """List all secret keys."""
    from axle.secrets.vault import Vault
    import getpass
    pwd = getpass.getpass("Vault Password: ")
    try:
        v = Vault(pwd)
        keys = v.list_keys()
        console.print("\n[bold cyan]Stored Secrets:[/bold cyan]")
        for k in keys:
             console.print(f"  [green]✓[/green] {k}")
    except ValueError:
        console.print("  [red]✗ Invalid password[/red]")

@secrets.command("set")
@click.argument("key")
@click.argument("value")
def set_secret(key, value):
    """Store or update a secret."""
    from axle.secrets.vault import Vault
    import getpass
    pwd = getpass.getpass("Vault Password: ")
    try:
        v = Vault(pwd)
        v.set(key, value)
        console.print(f"  [green]✓[/green] Set secret: {key}")
    except ValueError:
        console.print("  [red]✗ Invalid password[/red]")

@secrets.command("delete")
@click.argument("key")
def del_secret(key):
    """Delete a secret."""
    from axle.secrets.vault import Vault
    import getpass
    pwd = getpass.getpass("Vault Password: ")
    try:
        v = Vault(pwd)
        if v.delete(key):
            console.print(f"  [green]✓[/green] Deleted secret: {key}")
        else:
            console.print(f"  [red]✗[/red] Secret not found: {key}")
    except ValueError:
        console.print("  [red]✗ Invalid password[/red]")


# =============================================================================
# Sub-Commands (Status, Logs, Shell)
# =============================================================================

@main.command()
@click.option("--tail", default=50, help="Number of lines to show")
def logs(tail):
    """Stream or show application logs."""
    import subprocess
    console.print(f"  [cyan]Showing last {tail} lines of syslog...[/cyan]")
    try:
        subprocess.run(f"journalctl -n {tail} --no-pager", shell=True)
    except:
        console.print("[red]Command failed. Ensure you are on AXLE OS.[/red]")


@main.command()
def rollback():
    """Revert to a previous deployment state."""
    console.print("  [yellow]Rollback not fully implemented yet.[/yellow]")


@main.command()
def setup():
    """Run the first-boot setup wizard."""
    console.print("  [yellow]⚠  Setup wizard runs automatically on AXLE OS instances.[/yellow]")


@main.command()
def status():
    """Show the current deployment status."""
    console.print("\n[bold cyan]⚡ AXLE OS Status[/bold cyan]\n")

    table = Table(box=box.ROUNDED, show_header=False, padding=(0, 2))
    table.add_column("Key", style="dim")
    table.add_column("Value")

    table.add_row("Version", "0.1.0")
    table.add_row("Status", "[green]Ready[/green]")

    from axle.config.settings import settings
    providers = []
    if settings.gemini_api_key: providers.append("Gemini ✓")
    if settings.openrouter_api_key: providers.append("OpenRouter ✓")
    if settings.openai_api_key: providers.append("OpenAI ✓")
    
    table.add_row("AI Providers", ", ".join(providers) if providers else "[dim]None[/dim]")

    console.print(table)
    console.print()


@main.command()
def info():
    """Show AXLE OS version and system information."""
    import platform
    console.print("\n[bold cyan]⚡ AXLE OS Info[/bold cyan]\n")
    table = Table(box=box.ROUNDED, show_header=False, padding=(0, 2))
    table.add_column("Key", style="dim")
    table.add_column("Value")
    table.add_row("AXLE Version", "0.1.0")
    table.add_row("Python", platform.python_version())
    table.add_row("OS", f"{platform.system()} {platform.release()}")
    table.add_row("Architecture", platform.machine())
    console.print(table)
    console.print()


# =============================================================================
# Display Helpers
# =============================================================================

def _display_profile(profile):
    """Display a scanned ProjectProfile."""
    table = Table(
        title="📦 Project Profile", box=box.ROUNDED, show_header=False,
        padding=(0, 2), title_style="bold white",
    )
    table.add_column("Key", style="cyan", min_width=16)
    table.add_column("Value", style="white")

    table.add_row("Name", profile.name)
    table.add_row("Stack", f"[bold green]{profile.stack.value}[/bold green]")
    table.add_row("Framework", profile.framework.value if profile.framework.value != "none" else "[dim]none[/dim]")
    table.add_row("Version", profile.version or "[dim]auto-detect[/dim]")
    table.add_row("Database", profile.database.value if profile.database.value != "none" else "[dim]none[/dim]")
    table.add_row("Start Command", f"[yellow]{profile.start_command}[/yellow]")
    table.add_row("Port", str(profile.port))

    if profile.env_vars:
        table.add_row("Env Vars", ", ".join(profile.env_vars))
    
    console.print(table)

def _display_plan(plan, planner):
    """Display a deployment plan with wave grouping."""
    groups = planner.get_parallel_groups(plan.steps)
    console.print(f"\n[bold white]📋 Deployment Plan[/bold white] — {len(plan.steps)} steps\n")
    
    for i, group in enumerate(groups):
        header = f"Wave {i+1}" + (f" [dim](parallel: {len(group)} steps)[/dim]" if len(group)>1 else "")
        console.print(f"  [bold cyan]{header}[/bold cyan]")
        for step in group:
            badge = f" [dim]({step.plugin})[/dim]" if step.plugin else ""
            console.print(f"    [green]○[/green] {step.name}{badge}")
            if step.depends_on:
                console.print(f"      [dim]→ after: {', '.join(step.depends_on)}[/dim]")
        console.print()

if __name__ == "__main__":
    main()
