"""
Tests for axle.plugins — Server plugin system (T-082 to T-086)

Covers:
  - BasePlugin contract and utilities
  - PluginResult dataclass
  - PluginRegistry (register, get, list, has)
  - Nginx plugin: template rendering (reverse_proxy, static, fullstack)
  - SSL plugin: validation logic
  - Database plugin: SQL template rendering (PostgreSQL, MySQL)
  - Systemd plugin: service file rendering
  - Runtime plugin: stack validation
  - Firewall plugin: port calculations
  - Template file existence and content validation
"""
import pytest
from pathlib import Path

from axle.plugins.base import BasePlugin, PluginResult
from axle.plugins.registry import PluginRegistry, create_default_registry
from axle.plugins.nginx import NginxPlugin
from axle.plugins.ssl import SSLPlugin
from axle.plugins.database import DatabasePlugin
from axle.plugins.systemd import SystemdPlugin
from axle.plugins.runtime import RuntimePlugin
from axle.plugins.firewall import FirewallPlugin

PROJECT_ROOT = Path(__file__).parent.parent
NGINX_TEMPLATES = str(PROJECT_ROOT / "templates" / "nginx")
DB_TEMPLATES = str(PROJECT_ROOT / "templates" / "database")
SYSTEMD_TEMPLATES = str(PROJECT_ROOT / "templates" / "systemd")


# =============================================================================
# PluginResult Tests
# =============================================================================

class TestPluginResult:
    def test_default_values(self):
        r = PluginResult(success=True)
        assert r.message == ""
        assert r.output == ""
        assert r.error is None
        assert r.changed is False

    def test_failure_result(self):
        r = PluginResult(success=False, error="Something broke")
        assert r.success is False
        assert r.error == "Something broke"


# =============================================================================
# Registry Tests
# =============================================================================

class TestPluginRegistry:
    def test_register_and_get(self):
        registry = PluginRegistry()
        plugin = NginxPlugin()
        registry.register(plugin)
        assert registry.get("nginx") is plugin

    def test_get_missing_returns_none(self):
        registry = PluginRegistry()
        assert registry.get("nonexistent") is None

    def test_list_plugins(self):
        registry = PluginRegistry()
        registry.register(NginxPlugin())
        registry.register(SSLPlugin())
        assert sorted(registry.list_plugins()) == ["nginx", "ssl"]

    def test_has(self):
        registry = PluginRegistry()
        registry.register(NginxPlugin())
        assert registry.has("nginx") is True
        assert registry.has("unknown") is False

    def test_default_registry_has_all_plugins(self):
        registry = create_default_registry()
        expected = ["nginx", "ssl", "database", "systemd", "runtime", "firewall"]
        for name in expected:
            assert registry.has(name), f"Missing plugin: {name}"


# =============================================================================
# Nginx Plugin Tests (T-083)
# =============================================================================

class TestNginxPlugin:
    def test_name(self):
        assert NginxPlugin().name == "nginx"

    def test_render_reverse_proxy(self):
        plugin = NginxPlugin()
        ctx = {
            "app_name": "my-api",
            "port": 3000,
            "domain": "api.example.com",
            "templates_dir": NGINX_TEMPLATES,
        }
        config = plugin.render_config("reverse_proxy.conf.j2", ctx)
        assert config is not None
        assert "my-api" in config
        assert "3000" in config
        assert "api.example.com" in config
        assert "proxy_pass" in config

    def test_render_static_site(self):
        plugin = NginxPlugin()
        ctx = {
            "app_name": "portfolio",
            "domain": "example.com",
            "static_dir": "dist",
            "templates_dir": NGINX_TEMPLATES,
        }
        config = plugin.render_config("static_site.conf.j2", ctx)
        assert config is not None
        assert "portfolio" in config
        assert "/dist" in config
        assert "try_files" in config

    def test_render_fullstack(self):
        plugin = NginxPlugin()
        ctx = {
            "app_name": "saas",
            "port": 3000,
            "domain": "saas.io",
            "templates_dir": NGINX_TEMPLATES,
        }
        config = plugin.render_config("fullstack.conf.j2", ctx)
        assert config is not None
        assert "/api" in config
        assert "/ws" in config
        assert "proxy_pass" in config

    def test_determine_config_type_static(self):
        plugin = NginxPlugin()
        assert plugin._determine_config_type({"stack": "static"}) == "static_site"

    def test_determine_config_type_fullstack(self):
        plugin = NginxPlugin()
        ctx = {"has_frontend": True, "has_backend": True}
        assert plugin._determine_config_type(ctx) == "fullstack"

    def test_determine_config_type_backend_only(self):
        plugin = NginxPlugin()
        ctx = {"has_frontend": False, "has_backend": True}
        assert plugin._determine_config_type(ctx) == "reverse_proxy"

    def test_render_invalid_template(self):
        plugin = NginxPlugin()
        ctx = {"templates_dir": NGINX_TEMPLATES}
        assert plugin.render_config("nonexistent.j2", ctx) is None


# =============================================================================
# SSL Plugin Tests
# =============================================================================

class TestSSLPlugin:
    def test_name(self):
        assert SSLPlugin().name == "ssl"

    def test_validate_fails_without_domain(self):
        plugin = SSLPlugin()
        result = plugin.validate({"domain": None})
        assert result.success is False

    def test_validate_fails_with_underscore_domain(self):
        plugin = SSLPlugin()
        result = plugin.validate({"domain": "_"})
        assert result.success is False


# =============================================================================
# Database Plugin Tests (T-085)
# =============================================================================

class TestDatabasePlugin:
    def test_name(self):
        assert DatabasePlugin().name == "database"

    def test_render_postgres_sql(self):
        plugin = DatabasePlugin()
        ctx = {
            "db_user": "myapp",
            "db_password": "secret_pass",
            "db_name": "myapp_db",
            "templates_dir": DB_TEMPLATES,
        }
        sql = plugin.render_init_sql("postgresql", ctx)
        assert sql is not None
        assert "myapp" in sql
        assert "myapp_db" in sql
        assert "CREATE" in sql

    def test_render_mysql_sql(self):
        plugin = DatabasePlugin()
        ctx = {
            "db_user": "appuser",
            "db_password": "pass123",
            "db_name": "app_prod",
            "templates_dir": DB_TEMPLATES,
        }
        sql = plugin.render_init_sql("mysql", ctx)
        assert sql is not None
        assert "appuser" in sql
        assert "app_prod" in sql
        assert "utf8mb4" in sql

    def test_render_unsupported_db(self):
        plugin = DatabasePlugin()
        assert plugin.render_init_sql("oracle", {}) is None

    def test_validate_none_db(self):
        plugin = DatabasePlugin()
        result = plugin.validate({"database": "none"})
        assert result.success is True

    def test_configure_none_db(self):
        plugin = DatabasePlugin()
        result = plugin.configure({"database": "none"})
        assert result.success is True


# =============================================================================
# Systemd Plugin Tests (T-084)
# =============================================================================

class TestSystemdPlugin:
    def test_name(self):
        assert SystemdPlugin().name == "systemd"

    def test_render_service_file(self):
        plugin = SystemdPlugin()
        ctx = {
            "app_name": "my-api",
            "start_command": "node server.js",
            "user": "www-data",
            "group": "www-data",
            "env_vars": ["PORT=3000", "NODE_ENV=production"],
            "templates_dir": SYSTEMD_TEMPLATES,
        }
        service = plugin.render_service(ctx)
        assert service is not None
        assert "[Unit]" in service
        assert "[Service]" in service
        assert "[Install]" in service
        assert "my-api" in service
        assert "node server.js" in service
        assert "PORT=3000" in service
        assert "Restart=always" in service

    def test_render_service_with_env_file(self):
        plugin = SystemdPlugin()
        ctx = {
            "app_name": "app",
            "start_command": "python main.py",
            "env_file": "/var/www/app/.env",
            "templates_dir": SYSTEMD_TEMPLATES,
        }
        service = plugin.render_service(ctx)
        assert service is not None
        assert "EnvironmentFile=/var/www/app/.env" in service

    def test_render_service_has_security(self):
        plugin = SystemdPlugin()
        ctx = {
            "app_name": "secure-app",
            "start_command": "npm start",
            "templates_dir": SYSTEMD_TEMPLATES,
        }
        service = plugin.render_service(ctx)
        assert "NoNewPrivileges=true" in service
        assert "PrivateTmp=true" in service


# =============================================================================
# Runtime Plugin Tests
# =============================================================================

class TestRuntimePlugin:
    def test_name(self):
        assert RuntimePlugin().name == "runtime"

    def test_validate_static_always_passes(self):
        plugin = RuntimePlugin()
        result = plugin.validate({"stack": "static"})
        assert result.success is True


# =============================================================================
# Firewall Plugin Tests
# =============================================================================

class TestFirewallPlugin:
    def test_name(self):
        assert FirewallPlugin().name == "firewall"

    def test_default_ports(self):
        plugin = FirewallPlugin()
        ports = plugin._get_required_ports({})
        assert 22 in ports
        assert 80 in ports
        assert 443 in ports
        assert 4000 in ports

    def test_app_port_added(self):
        plugin = FirewallPlugin()
        ports = plugin._get_required_ports({"port": 8080})
        assert 8080 in ports

    def test_rdp_port_added_when_desktop(self):
        plugin = FirewallPlugin()
        ports = plugin._get_required_ports({"desktop_enabled": True})
        assert 3389 in ports

    def test_no_duplicate_ports(self):
        plugin = FirewallPlugin()
        ports = plugin._get_required_ports({"port": 80})  # already in defaults
        assert ports.count(80) == 1

    def test_ports_are_sorted(self):
        plugin = FirewallPlugin()
        ports = plugin._get_required_ports({"port": 5000})
        assert ports == sorted(ports)


# =============================================================================
# Template File Tests
# =============================================================================

class TestTemplateFiles:
    TEMPLATES = [
        "templates/nginx/reverse_proxy.conf.j2",
        "templates/nginx/static_site.conf.j2",
        "templates/nginx/fullstack.conf.j2",
        "templates/systemd/app.service.j2",
        "templates/database/postgres_init.sql.j2",
        "templates/database/mysql_init.sql.j2",
    ]

    @pytest.mark.parametrize("template_path", TEMPLATES)
    def test_template_exists(self, template_path):
        assert (PROJECT_ROOT / template_path).exists(), f"Missing: {template_path}"

    @pytest.mark.parametrize("template_path", TEMPLATES)
    def test_template_has_jinja_syntax(self, template_path):
        content = (PROJECT_ROOT / template_path).read_text()
        assert "{{" in content, f"No Jinja2 variables in {template_path}"
