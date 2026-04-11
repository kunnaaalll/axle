"""
AXLE OS — Firewall Plugin (T-081)

Manages UFW (Uncomplicated Firewall) rules.
Opens/closes ports as needed for the deployed application.
"""
from typing import List
from axle.plugins.base import BasePlugin, PluginResult


DEFAULT_PORTS = [22, 80, 443, 4000]  # SSH, HTTP, HTTPS, Dashboard


class FirewallPlugin(BasePlugin):
    """UFW firewall rule management."""

    name = "firewall"
    required_commands = ["ufw"]

    def validate(self, context: dict) -> PluginResult:
        """Check UFW is installed."""
        if not self.check_command_exists("ufw"):
            return PluginResult(success=False, error="UFW is not installed")
        return PluginResult(success=True, message="UFW is available")

    def configure(self, context: dict) -> PluginResult:
        """Open required ports in the firewall."""
        ports = self._get_required_ports(context)

        for port in ports:
            result = self.run_command(f"ufw allow {port}/tcp")
            if not result.success:
                return result

        # Enable UFW if not already
        self.run_command("ufw --force enable", check=False)

        return PluginResult(
            success=True,
            message=f"Firewall configured: ports {ports} open",
            changed=True,
        )

    def verify(self, context: dict) -> PluginResult:
        """Check firewall status."""
        return self.run_command("ufw status verbose")

    def rollback(self, context: dict) -> PluginResult:
        """Remove app-specific port rules (keep defaults)."""
        app_port = context.get("port", 3000)
        if app_port not in DEFAULT_PORTS:
            self.run_command(f"ufw delete allow {app_port}/tcp", check=False)
        return PluginResult(success=True, message="App firewall rules removed")

    def _get_required_ports(self, context: dict) -> List[int]:
        """Determine which ports need to be open."""
        ports = list(DEFAULT_PORTS)
        app_port = context.get("port", 3000)

        if app_port not in ports:
            ports.append(app_port)

        # Add RDP port if desktop GUI is enabled
        if context.get("desktop_enabled", True):
            if 3389 not in ports:
                ports.append(3389)

        return sorted(set(ports))
