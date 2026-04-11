"""
AXLE OS — SSL Plugin (T-077)

Manages SSL certificates via Certbot (Let's Encrypt).
Configures HTTPS redirect and schedules automatic renewal.
"""
from axle.plugins.base import BasePlugin, PluginResult


class SSLPlugin(BasePlugin):
    """SSL certificate management via Certbot."""

    name = "ssl"
    required_commands = ["certbot"]

    def validate(self, context: dict) -> PluginResult:
        """Check Certbot is installed and domain is provided."""
        if not self.check_command_exists("certbot"):
            return PluginResult(success=False, error="Certbot is not installed")
        domain = context.get("domain")
        if not domain or domain == "_":
            return PluginResult(success=False, error="Domain is required for SSL")
        return PluginResult(success=True, message=f"Ready for SSL: {domain}")

    def configure(self, context: dict) -> PluginResult:
        """Request SSL cert and configure Nginx for HTTPS."""
        domain = context.get("domain")
        email = context.get("admin_email", f"admin@{domain}")

        # Request certificate via Certbot
        cmd = (
            f"certbot --nginx -d {domain} "
            f"--email {email} --agree-tos --non-interactive "
            f"--redirect"
        )
        result = self.run_command(cmd, timeout=120)
        if not result.success:
            return result

        # Ensure auto-renewal timer is active
        self.run_command("systemctl enable certbot.timer", check=False)
        self.run_command("systemctl start certbot.timer", check=False)

        return PluginResult(
            success=True,
            message=f"SSL configured for {domain}",
            changed=True,
        )

    def verify(self, context: dict) -> PluginResult:
        """Check SSL certificate status."""
        domain = context.get("domain", "")
        return self.run_command(f"certbot certificates -d {domain}", check=False)

    def rollback(self, context: dict) -> PluginResult:
        """Revoke and delete certificate."""
        domain = context.get("domain", "")
        self.run_command(f"certbot delete --cert-name {domain} --non-interactive", check=False)
        return PluginResult(success=True, message=f"SSL cert removed for {domain}")
