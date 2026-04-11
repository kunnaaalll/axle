"""
AXLE OS — Systemd Plugin (T-079)

Manages systemd service files — writes .service files from templates,
enables, starts, and monitors application processes.
"""
from pathlib import Path
from typing import Optional

from jinja2 import Environment, FileSystemLoader

from axle.plugins.base import BasePlugin, PluginResult

TEMPLATES_DIR = Path(__file__).parent.parent.parent / "templates" / "systemd"
SYSTEMD_DIR = "/etc/systemd/system"


class SystemdPlugin(BasePlugin):
    """Systemd service file management."""

    name = "systemd"
    required_commands = ["systemctl"]

    def validate(self, context: dict) -> PluginResult:
        """Check systemd is available."""
        if not self.check_command_exists("systemctl"):
            return PluginResult(success=False, error="systemctl not found")
        return PluginResult(success=True, message="systemd is available")

    def configure(self, context: dict) -> PluginResult:
        """Generate and install a systemd service file."""
        app_name = context.get("app_name", "app")
        service_content = self.render_service(context)
        if service_content is None:
            return PluginResult(success=False, error="Failed to render service template")

        # Write service file
        service_path = f"{SYSTEMD_DIR}/{app_name}.service"
        try:
            Path(service_path).write_text(service_content)
        except PermissionError:
            return PluginResult(success=False, error=f"Permission denied: {service_path}")

        # Reload systemd and enable the service
        result = self.run_command("systemctl daemon-reload")
        if not result.success:
            return result

        result = self.run_command(f"systemctl enable {app_name}")
        if not result.success:
            return result

        result = self.run_command(f"systemctl start {app_name}")
        return result

    def verify(self, context: dict) -> PluginResult:
        """Check the service is running."""
        app_name = context.get("app_name", "app")
        return self.run_command(f"systemctl is-active {app_name}")

    def rollback(self, context: dict) -> PluginResult:
        """Stop and remove the service."""
        app_name = context.get("app_name", "app")
        self.run_command(f"systemctl stop {app_name}", check=False)
        self.run_command(f"systemctl disable {app_name}", check=False)
        self.run_command(f"rm -f {SYSTEMD_DIR}/{app_name}.service", check=False)
        self.run_command("systemctl daemon-reload", check=False)
        return PluginResult(success=True, message=f"Service {app_name} removed", changed=True)

    def render_service(self, context: dict) -> Optional[str]:
        """Render a systemd service file from the Jinja2 template."""
        template_dir = context.get("templates_dir", str(TEMPLATES_DIR))
        try:
            env = Environment(loader=FileSystemLoader(template_dir))
            template = env.get_template("app.service.j2")
            return template.render(**context)
        except Exception:
            return None
