import pytest
import asyncio
from unittest.mock import MagicMock
from axle.core.models import (
    DeploymentPlan,
    DeploymentStep,
    DeploymentStepStatus,
    ProjectProfile,
    StackType,
)
from axle.core.runner import TaskRunner
from axle.plugins.registry import PluginRegistry
from axle.plugins.base import BasePlugin, PluginResult


class MockPlugin(BasePlugin):
    name = "mock"
    
    def __init__(self, should_fail_val=False, should_fail_cfg=False, delay=0.1):
        self.should_fail_val = should_fail_val
        self.should_fail_cfg = should_fail_cfg
        self.delay = delay
        self.rollback_called = False
    
    def validate(self, context) -> PluginResult:
        if self.should_fail_val:
            return PluginResult(success=False, error="validate err")
        return PluginResult(success=True)

    def configure(self, context) -> PluginResult:
        import time
        time.sleep(self.delay)  # simulate work
        if self.should_fail_cfg:
            return PluginResult(success=False, error="cfg err")
        return PluginResult(success=True, output="mock cfg done")

    def verify(self, context) -> PluginResult:
        return PluginResult(success=True)

    def rollback(self, context) -> PluginResult:
        self.rollback_called = True
        return PluginResult(success=True)


@pytest.fixture
def plan():
    return DeploymentPlan(
        project_name="TestApp",
        profile=ProjectProfile(name="TestApp", stack=StackType.NODEJS, start_command="npm run start"),
        steps=[
            DeploymentStep(id="s1", name="Step 1", command="echo 1", plugin="mock", depends_on=[]),
            DeploymentStep(id="s2", name="Step 2", command="echo 2", plugin="mock", depends_on=[]),
            DeploymentStep(id="s3", name="Step 3", command="echo 3", plugin="mock", depends_on=["s1", "s2"]),
        ]
    )

@pytest.fixture
def runner():
    registry = PluginRegistry()
    registry.register(MockPlugin())
    return TaskRunner(registry=registry)


@pytest.mark.asyncio
async def test_runner_executes_plan_successfully(runner, plan):
    await runner.execute_plan(plan, context={})
    
    # All steps should be completed
    for step in plan.steps:
        assert step.status == DeploymentStepStatus.COMPLETED
        assert step.error is None
        assert step.output == "mock cfg done"
        assert step.duration_seconds > 0

    assert len(runner.log_stream) > 0


@pytest.mark.asyncio
async def test_runner_handles_validation_failure():
    # Setup a failing plugin
    registry = PluginRegistry()
    registry.register(MockPlugin(should_fail_val=True))
    runner = TaskRunner(registry=registry)
    
    plan = DeploymentPlan(
        project_name="TestApp",
        steps=[
            DeploymentStep(id="s1", name="Step 1", command="echo 1", plugin="mock")
        ]
    )
    
    await runner.execute_plan(plan, context={})
    
    assert plan.steps[0].status == DeploymentStepStatus.FAILED
    assert "validate err" in plan.steps[0].error


@pytest.mark.asyncio
async def test_runner_rollback_on_failure(plan):
    registry = PluginRegistry()
    # Mock plugin that succeeds
    registry.register(MockPlugin(delay=0.01))
    
    # Another plugin that fails
    fail_plugin = MockPlugin(should_fail_cfg=True, delay=0.01)
    fail_plugin.name = "fail_mock"
    registry.register(fail_plugin)
    
    runner = TaskRunner(registry=registry)
    
    # Step 1 and 2 succeed (using mock)
    # Step 3 fails (using fail_mock)
    plan.steps[2].plugin = "fail_mock"
    
    await runner.execute_plan(plan, context={})
    
    assert plan.steps[0].status == DeploymentStepStatus.COMPLETED
    assert plan.steps[1].status == DeploymentStepStatus.COMPLETED
    assert plan.steps[2].status == DeploymentStepStatus.FAILED
    
    # Verify rollback was called for completed steps (we'd need a mock tracking to assert this easily, 
    # but the runner._log stream should show rollback initiated)
    log_messages = "\n".join(runner.log_stream)
    assert "[ROLLBACK]" in log_messages
