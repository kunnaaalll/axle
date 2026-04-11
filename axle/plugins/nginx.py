"""
AXLE OS — Nginx Plugin (T-076)

Generates Nginx configurations from Jinja2 templates, validates them,
and manages the Nginx service lifecycle.
"""
from pathlib import Path
from typing import Optional

from jinja2 import Environment, FileSystemLoader

from axle.plugins.base import BasePlugin, PluginResult

TEMPLATES_DIR = Path(__file__).parent.parent.parent / "templates" / "nginx"
NGINX_SITES = "/etc/nginx/sites-available"
NGINX_ENABLED = "/etc/nginx/sites-enabled"


class NginxPlugin(BasePlugin):
    """Nginx reverse proxy and static site configuration."""

    name = "nginx"
    required_commands = ["nginx"]

    def validate(self, context: dict) -> PluginResult:
        """Check Nginx is installed."""
        if not self.check_command_exists("nginx"):
            return PluginResult(success=False, error="Nginx is not installed")
        return PluginResult(success=True, message="Nginx is available")

    def configure(self, context: dict) -> PluginResult:
        """Generate and install Nginx config from templates."""
        app_name = context.get("app_name", "app")
        config_type = self._determine_config_type(context)
        template_file = f"{config_type}.conf.j2"

        # Render the template
        config = self.render_config(template_file, context)
        if config is None:
            return PluginResult(success=False, error=f"Template not found: {template_file}")

        # Write config file
        config_path = f"{NGINX_SITES}/{app_name}"
        try:
            Path(config_path).write_text(config)
        except PermissionError:
            return PluginResult(success=False, error=f"Permission denied writing to {config_path}")

        # Create symlink to enable
        enabled_path = f"{NGINX_ENABLED}/{app_name}"
        result = self.run_command(f"ln -sf {config_path} {enabled_path}")
        if not result.success:
            return result

        # Remove default config if it exists
        self.run_command(f"rm -f {NGINX_ENABLED}/default", check=False)

        # Validate config
        return self.verify(context)

    def verify(self, context: dict) -> PluginResult:
        """Run nginx -t to validate configuration."""
        return self.run_command("nginx -t")

    def rollback(self, context: dict) -> PluginResult:
        """Remove the generated Nginx config."""
        app_name = context.get("app_name", "app")
        self.run_command(f"rm -f {NGINX_SITES}/{app_name}", check=False)
        self.run_command(f"rm -f {NGINX_ENABLED}/{app_name}", check=False)
        self.run_command("systemctl reload nginx", check=False)
        return PluginResult(success=True, message="Nginx config rolled back", changed=True)

    def render_config(self, template_name: str, context: dict) -> Optional[str]:
        """Render an Nginx config from a Jinja2 template."""
        template_dir = context.get("templates_dir", str(TEMPLATES_DIR))
        try:
            env = Environment(loader=FileSystemLoader(template_dir))
            template = env.get_template(template_name)
            return template.render(**context)
        except Exception:
            return None

    def _determine_config_type(self, context: dict) -> str:
        """Choose the right template based on the project profile."""
        has_frontend = context.get("has_frontend", False)
        has_backend = context.get("has_backend", True)
        stack = context.get("stack", "")

        if stack == "static":
            return "static_site"
        if has_frontend and has_backend:
            return "fullstack"
        return "reverse_proxy"
