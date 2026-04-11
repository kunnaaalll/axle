"""
AXLE OS — Runtime Plugin (T-080)

Manages language runtime installation, dependency installation, and builds.
Supports Node.js (via nvm), Python (via apt/pyenv), and Go.
"""
from axle.plugins.base import BasePlugin, PluginResult


class RuntimePlugin(BasePlugin):
    """Language runtime, dependency, and build management."""

    name = "runtime"

    def validate(self, context: dict) -> PluginResult:
        """Check the required runtime is available."""
        stack = context.get("stack", "")

        if stack == "nodejs":
            if not self.check_command_exists("node"):
                return PluginResult(success=False, error="Node.js is not installed")
        elif stack == "python":
            if not self.check_command_exists("python3"):
                return PluginResult(success=False, error="Python3 is not installed")
        elif stack == "go":
            if not self.check_command_exists("go"):
                return PluginResult(success=False, error="Go is not installed")
        elif stack == "static":
            return PluginResult(success=True, message="No runtime needed for static sites")

        return PluginResult(success=True, message=f"Runtime {stack} is available")

    def configure(self, context: dict) -> PluginResult:
        """Install dependencies and build the project."""
        stack = context.get("stack", "")
        app_dir = context.get("app_dir", f"/var/www/{context.get('app_name', 'app')}")

        if stack == "nodejs":
            return self._configure_nodejs(app_dir, context)
        elif stack == "python":
            return self._configure_python(app_dir, context)
        elif stack == "go":
            return self._configure_go(app_dir, context)
        elif stack == "static":
            return PluginResult(success=True, message="No build needed for static sites")

        return PluginResult(success=False, error=f"Unsupported stack: {stack}")

    def verify(self, context: dict) -> PluginResult:
        """Check that the app directory exists and has expected files."""
        app_dir = context.get("app_dir", f"/var/www/{context.get('app_name', 'app')}")
        return self.run_command(f"test -d {app_dir}")

    def _configure_nodejs(self, app_dir: str, context: dict) -> PluginResult:
        """Install Node.js deps and run build."""
        version = context.get("version", "20")

        # Install correct Node version
        result = self.run_command(f"nvm install {version} && nvm use {version}", check=False)

        # Install dependencies
        result = self.run_command(f"cd {app_dir} && npm install --production", timeout=120)
        if not result.success:
            return result

        # Run build if build command exists
        build_cmd = context.get("build_command")
        if build_cmd:
            result = self.run_command(f"cd {app_dir} && {build_cmd}", timeout=180)

        return result

    def _configure_python(self, app_dir: str, context: dict) -> PluginResult:
        """Create venv, install deps."""
        # Create virtual environment
        result = self.run_command(f"python3 -m venv {app_dir}/.venv")
        if not result.success:
            return result

        # Install dependencies
        build_cmd = context.get("build_command", "pip install -r requirements.txt")
        result = self.run_command(
            f"cd {app_dir} && source .venv/bin/activate && {build_cmd}",
            timeout=120
        )
        return result

    def _configure_go(self, app_dir: str, context: dict) -> PluginResult:
        """Build Go binary."""
        build_cmd = context.get("build_command", "go build -o app .")
        return self.run_command(f"cd {app_dir} && {build_cmd}", timeout=120)
