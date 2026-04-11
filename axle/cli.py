"""
AXLE OS — CLI (Command Line Interface)

The main entry point for all AXLE operations.
Wire-up of scanner, AI engine, and planner into real commands.
"""
import click
import json
import sys
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
        # Check if it's a URL or local path
        if target.startswith("http") or target.startswith("git@"):
            console.print(f"  Cloning [bold]{target}[/bold]...")
            with console.status("[cyan]Scanning repository...[/cyan]"):
                profile = clone_and_scan(target)
        else:
            console.print(f"  Scanning [bold]{target}[/bold]...")
            profile = scan_repository(target)

        # Display results
        _display_profile(profile)

    except FileNotFoundError as e:
        console.print(f"  [red]✗ Error:[/red] {e}")
        sys.exit(1)
    except ValueError as e:
        console.print(f"  [red]✗ Error:[/red] {e}")
        sys.exit(1)
    except Exception as e:
        console.print(f"  [red]✗ Unexpected error:[/red] {e}")
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

    # Step 1: Scan
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

    # Step 2: Generate plan via AI
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
            console.print("    Set one of: GEMINI_API_KEY, OPENROUTER_API_KEY, OPENAI_API_KEY")
            console.print("    Or install Ollama for local inference.")
            console.print("\n  [dim]Showing scan result only (no AI plan).[/dim]")
            return

        console.print(f"  [dim]Using provider: {available[0]}[/dim]")

        planner = Planner(engine)
        with console.status("[cyan]AI is thinking...[/cyan]"):
            deployment_plan = planner.generate_plan(profile)

        # Display plan
        _display_plan(deployment_plan, planner)

    except Exception as e:
        console.print(f"  [red]✗ Plan generation failed:[/red] {e}")
        sys.exit(1)


# =============================================================================
# axle deploy <url>
# =============================================================================

@main.command()
@click.argument("repo_url")
def deploy(repo_url):
    """Deploy an application from a GitHub repository URL."""
    console.print("\n[bold cyan]⚡ AXLE OS Deploy[/bold cyan]\n")
    console.print(f"  Target: [bold]{repo_url}[/bold]")
    console.print("  [yellow]⚠  Full deployment requires running on an AXLE OS instance.[/yellow]")
    console.print("  [dim]Use 'axle plan' to preview the deployment locally.[/dim]\n")


# =============================================================================
# axle setup
# =============================================================================

@main.command()
def setup():
    """Run the first-boot setup wizard."""
    console.print("\n[bold cyan]⚡ AXLE OS Setup[/bold cyan]\n")
    console.print("  [yellow]⚠  Setup wizard runs on AXLE OS instances only.[/yellow]")
    console.print("  [dim]For local development, configure .env file instead.[/dim]\n")


# =============================================================================
# axle status
# =============================================================================

@main.command()
def status():
    """Show the current deployment status."""
    console.print("\n[bold cyan]⚡ AXLE OS Status[/bold cyan]\n")

    table = Table(box=box.ROUNDED, show_header=False, padding=(0, 2))
    table.add_column("Key", style="dim")
    table.add_column("Value")

    table.add_row("Version", "0.1.0")
    table.add_row("Status", "[green]Ready[/green]")
    table.add_row("Deployment", "[dim]No active deployment[/dim]")
    table.add_row("Dashboard", "[dim]Not running[/dim]")

    # Check AI providers
    from axle.config.settings import settings
    providers = []
    if settings.gemini_api_key:
        providers.append("Gemini ✓")
    if settings.openrouter_api_key:
        providers.append("OpenRouter ✓")
    if settings.openai_api_key:
        providers.append("OpenAI ✓")
    if not providers:
        providers.append("[dim]None configured[/dim]")

    table.add_row("AI Providers", ", ".join(providers))

    console.print(table)
    console.print()


# =============================================================================
# axle info
# =============================================================================

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
        title="📦 Project Profile",
        box=box.ROUNDED,
        show_header=False,
        padding=(0, 2),
        title_style="bold white",
    )
    table.add_column("Key", style="cyan", min_width=16)
    table.add_column("Value", style="white")

    table.add_row("Name", profile.name)
    table.add_row("Stack", f"[bold green]{profile.stack.value}[/bold green]")
    table.add_row("Framework", profile.framework.value if profile.framework.value != "none" else "[dim]none[/dim]")
    table.add_row("Version", profile.version or "[dim]auto-detect[/dim]")
    table.add_row("Database", profile.database.value if profile.database.value != "none" else "[dim]none[/dim]")
    table.add_row("Build Command", profile.build_command or "[dim]none[/dim]")
    table.add_row("Start Command", f"[yellow]{profile.start_command}[/yellow]")
    table.add_row("Port", str(profile.port))
    table.add_row("Has Frontend", "✓" if profile.has_frontend else "✗")
    table.add_row("Has Backend", "✓" if profile.has_backend else "✗")

    if profile.env_vars:
        table.add_row("Env Vars", ", ".join(profile.env_vars))

    if profile.github_url:
        table.add_row("GitHub", profile.github_url)

    console.print(table)


def _display_plan(plan, planner):
    """Display a deployment plan with wave grouping."""
    groups = planner.get_parallel_groups(plan.steps)

    console.print(f"\n[bold white]📋 Deployment Plan[/bold white] — {len(plan.steps)} steps\n")

    for i, group in enumerate(groups):
        if len(group) > 1:
            header = f"Wave {i+1} [dim](parallel: {len(group)} steps)[/dim]"
        else:
            header = f"Wave {i+1}"

        console.print(f"  [bold cyan]{header}[/bold cyan]")

        for step in group:
            plugin_badge = f" [dim]({step.plugin})[/dim]" if step.plugin else ""
            console.print(f"    [green]○[/green] {step.name}{plugin_badge}")
            console.print(f"      [dim]$ {step.command}[/dim]")
            if step.depends_on:
                console.print(f"      [dim]→ after: {', '.join(step.depends_on)}[/dim]")

        console.print()

    console.print("[bold green]  ✓ Plan ready for execution[/bold green]\n")


if __name__ == "__main__":
    main()
