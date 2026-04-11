"""
AXLE OS — Plugin Registry (T-069)

Discovers and loads all available plugins.
Provides a single access point for the executor to find plugins by name.
"""
from typing import Dict, Optional
from axle.plugins.base import BasePlugin


class PluginRegistry:
    """Registry of all available server plugins."""

    def __init__(self):
        self._plugins: Dict[str, BasePlugin] = {}

    def register(self, plugin: BasePlugin):
        """Register a plugin instance."""
        self._plugins[plugin.name] = plugin

    def get(self, name: str) -> Optional[BasePlugin]:
        """Get a plugin by name."""
        return self._plugins.get(name)

    def list_plugins(self) -> list:
        """List all registered plugin names."""
        return list(self._plugins.keys())

    def has(self, name: str) -> bool:
        """Check if a plugin is registered."""
        return name in self._plugins


def create_default_registry() -> PluginRegistry:
    """Create a registry with all built-in plugins."""
    from axle.plugins.nginx import NginxPlugin
    from axle.plugins.ssl import SSLPlugin
    from axle.plugins.database import DatabasePlugin
    from axle.plugins.systemd import SystemdPlugin
    from axle.plugins.runtime import RuntimePlugin
    from axle.plugins.firewall import FirewallPlugin

    registry = PluginRegistry()
    registry.register(NginxPlugin())
    registry.register(SSLPlugin())
    registry.register(DatabasePlugin())
    registry.register(SystemdPlugin())
    registry.register(RuntimePlugin())
    registry.register(FirewallPlugin())
    return registry
