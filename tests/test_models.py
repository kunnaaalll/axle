"""
Tests for axle.core.models — All Pydantic data models. (T-036)

Covers:
  - All enums (StackType, FrameworkType, DatabaseType, DeploymentStepStatus, DeploymentStatus)
  - ProjectProfile (validation, defaults, serialization)
  - ServerProfile (defaults, customization)
  - DeploymentStep / DeploymentPlan (dependency graph, serialization)
  - DeploymentHistory (timestamps, status)
  - HealthMetrics (computed properties)
"""
import pytest
from datetime import datetime
from axle.core.models import (
    StackType,
    FrameworkType,
    DatabaseType,
    DeploymentStepStatus,
    DeploymentStatus,
    ProjectProfile,
    ServerProfile,
    DeploymentStep,
    DeploymentPlan,
    DeploymentHistory,
    HealthMetrics,
)


# =============================================================================
# Enum Tests
# =============================================================================

class TestStackType:
    def test_all_values(self):
        assert StackType.NODEJS == "nodejs"
        assert StackType.PYTHON == "python"
        assert StackType.GO == "go"
        assert StackType.JAVA == "java"
        assert StackType.STATIC == "static"

    def test_count(self):
        assert len(StackType) == 5


class TestFrameworkType:
    def test_node_frameworks(self):
        assert FrameworkType.EXPRESS == "express"
        assert FrameworkType.NEXTJS == "nextjs"
        assert FrameworkType.NESTJS == "nestjs"
        assert FrameworkType.FASTIFY == "fastify"

    def test_python_frameworks(self):
        assert FrameworkType.DJANGO == "django"
        assert FrameworkType.FASTAPI == "fastapi"
        assert FrameworkType.FLASK == "flask"

    def test_go_frameworks(self):
        assert FrameworkType.GIN == "gin"
        assert FrameworkType.FIBER == "fiber"
        assert FrameworkType.ECHO == "echo"

    def test_none_framework(self):
        assert FrameworkType.NONE == "none"

    def test_total_count(self):
        assert len(FrameworkType) == 13


class TestDatabaseType:
    def test_all_values(self):
        assert DatabaseType.POSTGRESQL == "postgresql"
        assert DatabaseType.MYSQL == "mysql"
        assert DatabaseType.MONGODB == "mongodb"
        assert DatabaseType.REDIS == "redis"
        assert DatabaseType.SQLITE == "sqlite"
        assert DatabaseType.NONE == "none"

    def test_count(self):
        assert len(DatabaseType) == 6


class TestDeploymentStepStatus:
    def test_includes_skipped(self):
        assert DeploymentStepStatus.SKIPPED == "skipped"

    def test_count(self):
        assert len(DeploymentStepStatus) == 5


class TestDeploymentStatus:
    def test_all_values(self):
        assert DeploymentStatus.PLANNING == "planning"
        assert DeploymentStatus.ROLLED_BACK == "rolled_back"

    def test_count(self):
        assert len(DeploymentStatus) == 6


# =============================================================================
# ProjectProfile Tests
# =============================================================================

class TestProjectProfile:
    def test_minimal_valid(self):
        p = ProjectProfile(name="app", stack=StackType.NODEJS, start_command="npm start")
        assert p.framework == FrameworkType.NONE
        assert p.database == DatabaseType.NONE
        assert p.port == 3000
        assert p.has_backend is True
        assert p.has_frontend is False

    def test_full_profile(self):
        p = ProjectProfile(
            name="saas",
            github_url="https://github.com/user/saas",
            stack=StackType.PYTHON,
            framework=FrameworkType.FASTAPI,
            version="3.12",
            database=DatabaseType.POSTGRESQL,
            env_vars=["DATABASE_URL", "SECRET_KEY"],
            build_command="pip install -r requirements.txt",
            start_command="uvicorn main:app",
            port=8000,
            has_frontend=False,
            has_backend=True,
        )
        assert p.framework == FrameworkType.FASTAPI
        assert len(p.env_vars) == 2

    def test_missing_required_raises(self):
        with pytest.raises(Exception):
            ProjectProfile(name="test")  # missing stack and start_command

    def test_serialization_round_trip(self):
        p = ProjectProfile(name="app", stack=StackType.NODEJS, start_command="npm start")
        restored = ProjectProfile(**p.model_dump())
        assert restored == p

    def test_json_round_trip(self):
        p = ProjectProfile(
            name="app", stack=StackType.GO, start_command="./main",
            database=DatabaseType.MYSQL, framework=FrameworkType.GIN,
        )
        restored = ProjectProfile.model_validate_json(p.model_dump_json())
        assert restored.stack == StackType.GO
        assert restored.framework == FrameworkType.GIN


# =============================================================================
# ServerProfile Tests
# =============================================================================

class TestServerProfile:
    def test_defaults(self):
        s = ServerProfile()
        assert s.hostname == "axle-os"
        assert s.cpu_count == 2
        assert s.ram_total_mb == 4096
        assert s.disk_total_gb == 30
        assert s.architecture == "x86_64"

    def test_custom_values(self):
        s = ServerProfile(hostname="prod-1", cpu_count=8, ram_total_mb=16384, ip_address="10.0.1.5")
        assert s.hostname == "prod-1"
        assert s.cpu_count == 8
        assert s.ip_address == "10.0.1.5"


# =============================================================================
# DeploymentStep / Plan Tests
# =============================================================================

class TestDeploymentStep:
    def test_defaults(self):
        step = DeploymentStep(id="s1", name="Install", command="npm install")
        assert step.status == DeploymentStepStatus.PENDING
        assert step.plugin is None
        assert step.duration_seconds is None
        assert step.depends_on == []

    def test_with_plugin(self):
        step = DeploymentStep(id="s1", name="Nginx", command="nginx -t", plugin="nginx")
        assert step.plugin == "nginx"


class TestDeploymentPlan:
    def test_with_profile_and_server(self):
        profile = ProjectProfile(name="app", stack=StackType.NODEJS, start_command="npm start")
        server = ServerProfile(cpu_count=4)
        plan = DeploymentPlan(project_name="app", profile=profile, server=server, steps=[])
        assert plan.profile.stack == StackType.NODEJS
        assert plan.server.cpu_count == 4
        assert plan.created_at is not None

    def test_plan_serialization(self):
        steps = [DeploymentStep(id="s1", name="Test", command="echo ok")]
        plan = DeploymentPlan(project_name="app", steps=steps)
        data = plan.model_dump()
        restored = DeploymentPlan(**data)
        assert len(restored.steps) == 1


# =============================================================================
# DeploymentHistory Tests
# =============================================================================

class TestDeploymentHistory:
    def test_defaults(self):
        h = DeploymentHistory(id="d-001", project_name="app")
        assert h.status == DeploymentStatus.COMPLETED
        assert h.started_at is not None
        assert h.finished_at is None
        assert h.rollback_available is False

    def test_failed_deployment(self):
        h = DeploymentHistory(
            id="d-002", project_name="app",
            status=DeploymentStatus.FAILED,
            error_message="npm install failed with exit code 1",
        )
        assert h.status == DeploymentStatus.FAILED
        assert "npm install" in h.error_message


# =============================================================================
# HealthMetrics Tests
# =============================================================================

class TestHealthMetrics:
    def test_defaults(self):
        m = HealthMetrics()
        assert m.cpu_percent == 0.0
        assert m.process_running is True

    def test_ram_percent_computed(self):
        m = HealthMetrics(ram_used_mb=2048, ram_total_mb=4096)
        assert m.ram_percent == 50.0

    def test_disk_percent_computed(self):
        m = HealthMetrics(disk_used_gb=15, disk_total_gb=30)
        assert m.disk_percent == 50.0

    def test_ram_percent_zero_total(self):
        m = HealthMetrics(ram_used_mb=100, ram_total_mb=0)
        assert m.ram_percent == 0.0

    def test_disk_percent_zero_total(self):
        m = HealthMetrics(disk_used_gb=10, disk_total_gb=0)
        assert m.disk_percent == 0.0

    def test_full_metrics(self):
        m = HealthMetrics(
            cpu_percent=72.5,
            ram_used_mb=6144,
            ram_total_mb=8192,
            disk_used_gb=22,
            disk_total_gb=30,
            http_status_code=200,
            http_response_time_ms=45.2,
            db_connections_active=12,
            ssl_days_remaining=60,
        )
        assert m.cpu_percent == 72.5
        assert m.ram_percent == 75.0
        assert m.ssl_days_remaining == 60
