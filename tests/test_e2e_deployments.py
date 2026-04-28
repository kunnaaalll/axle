"""
End-to-End deployment simulation tests.

These tests verify the TaskRunner handles various stack configurations correctly,
including graceful failure when plugins are missing.
"""
import pytest
from unittest.mock import MagicMock
from axle.core.runner import TaskRunner
from axle.core.models import (
    DeploymentPlan,
    DeploymentStep,
    DeploymentStepStatus,
    ProjectProfile,
    StackType,
    FrameworkType,
    DatabaseType,
)
from axle.plugins.registry import PluginRegistry
from axle.plugins.base import BasePlugin, PluginResult


class PassPlugin(BasePlugin):
    """A plugin that always succeeds."""
    name = "pass"
    def validate(self, ctx): return PluginResult(success=True)
    def configure(self, ctx): return PluginResult(success=True, output="ok")
    def verify(self, ctx): return PluginResult(success=True)
    def rollback(self, ctx): return PluginResult(success=True)


class FailPlugin(BasePlugin):
    """A plugin that always fails at configure."""
    name = "fail"
    def validate(self, ctx): return PluginResult(success=True)
    def configure(self, ctx): return PluginResult(success=False, error="simulated failure")
    def verify(self, ctx): return PluginResult(success=True)
    def rollback(self, ctx): return PluginResult(success=True)


def _make_plan(project_name, steps):
    return DeploymentPlan(
        project_name=project_name,
        profile=ProjectProfile(
            name=project_name,
            stack=StackType.NODEJS,
            start_command="npm start",
        ),
        steps=steps,
    )


@pytest.fixture
def registry():
    reg = PluginRegistry()
    reg.register(PassPlugin())
    reg.register(FailPlugin())
    return reg


@pytest.mark.asyncio
async def test_react_express_pg_full_stack(registry):
    """T-152: Simulates a React + Express + PostgreSQL deployment with multi-wave execution."""
    plan = _make_plan("react-express-pg", [
        DeploymentStep(id="s1", name="Install Node 20", command="apt install nodejs", plugin="pass"),
        DeploymentStep(id="s2", name="Install PostgreSQL", command="apt install postgresql", plugin="pass"),
        DeploymentStep(id="s3", name="npm install", command="npm ci", plugin="pass", depends_on=["s1"]),
        DeploymentStep(id="s4", name="DB migrate", command="npx prisma migrate", plugin="pass", depends_on=["s2", "s3"]),
        DeploymentStep(id="s5", name="Start server", command="pm2 start", plugin="pass", depends_on=["s4"]),
    ])
    runner = TaskRunner(registry=registry)
    result = await runner.execute_plan(plan, {"app_name": "test", "port": 3000, "stack": "nodejs"})

    for step in result.steps:
        assert step.status == DeploymentStepStatus.COMPLETED, f"Step '{step.name}' should be COMPLETED but was {step.status}"
        assert step.duration_seconds is not None


@pytest.mark.asyncio
async def test_nextjs_ssr_deployment(registry):
    """T-153: Simulates a Next.js SSR deployment with build + start steps."""
    plan = _make_plan("nextjs-app", [
        DeploymentStep(id="s1", name="Install Node", command="apt install nodejs", plugin="pass"),
        DeploymentStep(id="s2", name="npm install", command="npm ci", plugin="pass", depends_on=["s1"]),
        DeploymentStep(id="s3", name="Build Next.js", command="npm run build", plugin="pass", depends_on=["s2"]),
        DeploymentStep(id="s4", name="Start PM2", command="pm2 start npm -- start", plugin="pass", depends_on=["s3"]),
    ])
    runner = TaskRunner(registry=registry)
    result = await runner.execute_plan(plan, {"app_name": "nextjs-app", "port": 3000, "stack": "nodejs"})

    assert all(s.status == DeploymentStepStatus.COMPLETED for s in result.steps)


@pytest.mark.asyncio
async def test_django_postgres_deployment(registry):
    """T-154: Simulates a Django + PostgreSQL deployment."""
    plan = _make_plan("django-app", [
        DeploymentStep(id="s1", name="Install Python 3.11", command="apt install python3", plugin="pass"),
        DeploymentStep(id="s2", name="Install PostgreSQL", command="apt install postgresql", plugin="pass"),
        DeploymentStep(id="s3", name="pip install", command="pip install -r requirements.txt", plugin="pass", depends_on=["s1"]),
        DeploymentStep(id="s4", name="Migrate DB", command="python manage.py migrate", plugin="pass", depends_on=["s2", "s3"]),
        DeploymentStep(id="s5", name="Collect static", command="python manage.py collectstatic", plugin="pass", depends_on=["s4"]),
        DeploymentStep(id="s6", name="Start Gunicorn", command="gunicorn myapp.wsgi", plugin="pass", depends_on=["s5"]),
    ])
    runner = TaskRunner(registry=registry)
    result = await runner.execute_plan(plan, {"app_name": "django-app", "port": 8000, "stack": "python"})

    assert all(s.status == DeploymentStepStatus.COMPLETED for s in result.steps)


@pytest.mark.asyncio
async def test_fastapi_deployment(registry):
    """T-155: Simulates a FastAPI uvicorn deployment."""
    plan = _make_plan("fastapi-app", [
        DeploymentStep(id="s1", name="Install Python", command="apt install python3", plugin="pass"),
        DeploymentStep(id="s2", name="pip install", command="pip install -r requirements.txt", plugin="pass", depends_on=["s1"]),
        DeploymentStep(id="s3", name="Start uvicorn", command="uvicorn main:app --host 0.0.0.0", plugin="pass", depends_on=["s2"]),
    ])
    runner = TaskRunner(registry=registry)
    result = await runner.execute_plan(plan, {"app_name": "fastapi-app", "port": 8000, "stack": "python"})

    assert all(s.status == DeploymentStepStatus.COMPLETED for s in result.steps)


@pytest.mark.asyncio
async def test_static_html_deployment(registry):
    """T-156: Simulates a basic nginx static site deployment."""
    plan = _make_plan("static-site", [
        DeploymentStep(id="s1", name="Install nginx", command="apt install nginx", plugin="pass"),
        DeploymentStep(id="s2", name="Copy files to /var/www", command="cp -r . /var/www/html", plugin="pass", depends_on=["s1"]),
        DeploymentStep(id="s3", name="Reload nginx", command="systemctl reload nginx", plugin="pass", depends_on=["s2"]),
    ])
    runner = TaskRunner(registry=registry)
    result = await runner.execute_plan(plan, {"app_name": "static-site", "port": 80, "stack": "static"})

    assert all(s.status == DeploymentStepStatus.COMPLETED for s in result.steps)


@pytest.mark.asyncio
async def test_deployment_failure_triggers_rollback(registry):
    """Verify that a failing step triggers rollback of previously completed steps."""
    plan = _make_plan("failing-deploy", [
        DeploymentStep(id="s1", name="Setup runtime", command="apt install", plugin="pass"),
        DeploymentStep(id="s2", name="Broken step", command="fail", plugin="fail", depends_on=["s1"]),
    ])
    runner = TaskRunner(registry=registry)
    result = await runner.execute_plan(plan, {"app_name": "test", "port": 3000, "stack": "nodejs"})

    assert result.steps[0].status == DeploymentStepStatus.COMPLETED
    assert result.steps[1].status == DeploymentStepStatus.FAILED

    log_text = "\n".join(runner.log_stream)
    assert "[ROLLBACK]" in log_text
