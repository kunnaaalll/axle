"""
AXLE OS — Plugin Base Class (T-067, T-068)

Defines the abstract interface and lifecycle for all server plugins:
  validate()  → Check prerequisites on the server
  configure() → Apply the configuration (write files, run commands)
  verify()    → Confirm the configuration is working
  rollback()  → Undo changes if something failed

Each plugin also declares:
  - name: unique identifier (e.g., "nginx", "systemd")
  - required_commands: list of CLI tools that must exist
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional, Dict
import logging
import subprocess
import shlex

logger = logging.getLogger("axle.plugins")


@dataclass
class PluginResult:
    """Result of a plugin operation."""
    success: bool
    message: str = ""
    output: str = ""
    error: Optional[str] = None
    changed: bool = False  # True if the plugin actually changed something


class BasePlugin(ABC):
    """
    Abstract base class for all AXLE server plugins.

    Lifecycle:
        1. validate()   — Can we proceed? (deps installed, permissions OK)
        2. configure()  — Do the work (write configs, run commands)
        3. verify()     — Is it working? (test configs, check services)
        4. rollback()   — Undo on failure (restore backups, stop services)
    """

    name: str = "base"
    required_commands: List[str] = []

    @abstractmethod
    def validate(self, context: dict) -> PluginResult:
        """Check that all prerequisites are met."""
        ...

    @abstractmethod
    def configure(self, context: dict) -> PluginResult:
        """Apply the configuration."""
        ...

    @abstractmethod
    def verify(self, context: dict) -> PluginResult:
        """Verify the configuration is working correctly."""
        ...

    def rollback(self, context: dict) -> PluginResult:
        """Undo changes (optional — not all plugins support rollback)."""
        return PluginResult(success=True, message=f"No rollback available for {self.name}")

    def run_command(self, cmd: str, check: bool = True, timeout: int = 60) -> PluginResult:
        """Execute a shell command and return the result."""
        try:
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, timeout=timeout
            )
            if check and result.returncode != 0:
                return PluginResult(
                    success=False,
                    output=result.stdout,
                    error=result.stderr,
                    message=f"Command failed: {cmd}",
                )
            return PluginResult(
                success=True,
                output=result.stdout,
                message=f"Command succeeded: {cmd}",
                changed=True,
            )
        except subprocess.TimeoutExpired:
            return PluginResult(success=False, error=f"Command timed out after {timeout}s: {cmd}")
        except Exception as e:
            return PluginResult(success=False, error=str(e))

    def check_command_exists(self, cmd: str) -> bool:
        """Check if a CLI command is available on the system."""
        try:
            subprocess.run(["which", cmd], capture_output=True, text=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
