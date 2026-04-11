import click
from axle.config.settings import settings

@click.group()
def main():
    """AXLE OS - AI-Powered Linux Deployment Engine"""
    pass

@main.command()
@click.argument('repo_url')
def deploy(repo_url):
    """Deploy an application from a GitHub repository URL."""
    click.echo(f"Starting deployment for: {repo_url}")
    # TODO: Implement scanner, planner, and runner
    click.echo("Scanning project... (Not implemented)")

@main.command()
def setup():
    """Run the first-boot setup wizard."""
    click.echo("Welcome to AXLE OS Setup Wizard")
    # TODO: Implement TUI setup wizard

@main.command()
def status():
    """Show the status of the current deployment."""
    click.echo("Current deployment status: Idle")

if __name__ == "__main__":
    main()
