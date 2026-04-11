"""
AXLE OS — Database Plugin (T-078)

Initializes PostgreSQL or MySQL databases using Jinja2 SQL templates.
Creates users, databases, and grants privileges.
"""
from pathlib import Path
from typing import Optional

from jinja2 import Environment, FileSystemLoader

from axle.plugins.base import BasePlugin, PluginResult

TEMPLATES_DIR = Path(__file__).parent.parent.parent / "templates" / "database"


class DatabasePlugin(BasePlugin):
    """Database initialization and management."""

    name = "database"
    required_commands = []  # Depends on which DB type

    def validate(self, context: dict) -> PluginResult:
        """Check the target database server is available."""
        db_type = context.get("database", "none")
        if db_type == "none":
            return PluginResult(success=True, message="No database needed")
        if db_type == "postgresql":
            if not self.check_command_exists("psql"):
                return PluginResult(success=False, error="PostgreSQL is not installed")
        elif db_type == "mysql":
            if not self.check_command_exists("mysql"):
                return PluginResult(success=False, error="MySQL is not installed")
        return PluginResult(success=True, message=f"{db_type} is available")

    def configure(self, context: dict) -> PluginResult:
        """Create database and user from template."""
        db_type = context.get("database", "none")
        if db_type == "none":
            return PluginResult(success=True, message="No database to configure")

        # Render SQL template
        sql = self.render_init_sql(db_type, context)
        if sql is None:
            return PluginResult(success=False, error=f"No template for {db_type}")

        # Execute SQL
        if db_type == "postgresql":
            return self._init_postgresql(sql, context)
        elif db_type == "mysql":
            return self._init_mysql(sql, context)

        return PluginResult(success=False, error=f"Unsupported database: {db_type}")

    def verify(self, context: dict) -> PluginResult:
        """Verify the database exists and is accessible."""
        db_type = context.get("database", "none")
        db_name = context.get("db_name", "app")

        if db_type == "postgresql":
            return self.run_command(f'sudo -u postgres psql -lqt | grep -w {db_name}')
        elif db_type == "mysql":
            return self.run_command(f'mysql -e "SHOW DATABASES LIKE \'{db_name}\';"')

        return PluginResult(success=True, message="No database to verify")

    def render_init_sql(self, db_type: str, context: dict) -> Optional[str]:
        """Render an SQL init script from a Jinja2 template."""
        template_dir = context.get("templates_dir", str(TEMPLATES_DIR))
        template_map = {
            "postgresql": "postgres_init.sql.j2",
            "mysql": "mysql_init.sql.j2",
        }
        template_name = template_map.get(db_type)
        if not template_name:
            return None

        try:
            env = Environment(loader=FileSystemLoader(template_dir))
            template = env.get_template(template_name)
            return template.render(**context)
        except Exception:
            return None

    def _init_postgresql(self, sql: str, context: dict) -> PluginResult:
        """Execute PostgreSQL init SQL."""
        return self.run_command(f'sudo -u postgres psql -c "{sql}"')

    def _init_mysql(self, sql: str, context: dict) -> PluginResult:
        """Execute MySQL init SQL."""
        return self.run_command(f'mysql -u root -e "{sql}"')
