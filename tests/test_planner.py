"""
Tests for axle.core.planner — Deployment planning and ordering. (T-061)

Covers:
  - Plan generation via mocked AI engine
  - Topological sort of step dependencies
  - Parallel wave grouping
  - Cycle detection
  - Plan validation (duplicate IDs, broken dependencies)
  - Formatted preview output
"""
import json
import pytest

from axle.core.planner import Planner
from axle.ai.engine import AIEngine
from axle.core.models import (
    DeploymentPlan,
    DeploymentStep,
    ProjectProfile,
    ServerProfile,
    StackType,
    FrameworkType,
    DatabaseType,
)


# =============================================================================
# Fixtures
# =============================================================================

MOCK_PLAN_RESPONSE = json.dumps([
    {"id": "install-runtime", "name": "Install Node.js", "command": "nvm install 20", "plugin": "runtime", "depends_on": []},
    {"id": "install-deps", "name": "Install deps", "command": "npm install", "plugin": "runtime", "depends_on": ["install-runtime"]},
    {"id": "setup-db", "name": "Setup DB", "command": "createdb app", "plugin": "database", "depends_on": []},
    {"id": "build", "name": "Build", "command": "npm run build", "plugin": "runtime", "depends_on": ["install-deps"]},
    {"id": "create-service", "name": "Create service", "command": "systemctl enable app", "plugin": "systemd", "depends_on": ["build"]},
    {"id": "setup-nginx", "name": "Configure Nginx", "command": "nginx -t", "plugin": "nginx", "depends_on": ["create-service"]},
])


class MockProviderForPlanner:
    name = "mock"
    def is_available(self):
        return True
    def generate(self, system_prompt, user_prompt, temperature=0.3):
        return MOCK_PLAN_RESPONSE
    def diagnose(self, system_prompt, user_prompt):
        return "All good."


@pytest.fixture
def planner():
    engine = AIEngine()
    engine.providers = {"mock": MockProviderForPlanner()}
    return Planner(engine)


@pytest.fixture
def sample_profile():
    return ProjectProfile(
        name="test-app",
        stack=StackType.NODEJS,
        framework=FrameworkType.EXPRESS,
        database=DatabaseType.POSTGRESQL,
        start_command="npm start",
        build_command="npm run build",
    )


# =============================================================================
# Plan Generation Tests
# =============================================================================

class TestPlanGeneration:

    def test_generates_plan(self, planner, sample_profile):
        plan = planner.generate_plan(sample_profile)
        assert isinstance(plan, DeploymentPlan)
        assert plan.project_name == "test-app"
        assert len(plan.steps) == 6

    def test_plan_has_profile(self, planner, sample_profile):
        plan = planner.generate_plan(sample_profile)
        assert plan.profile.stack == StackType.NODEJS

    def test_plan_has_server(self, planner, sample_profile):
        server = ServerProfile(cpu_count=4)
        plan = planner.generate_plan(sample_profile, server=server)
        assert plan.server.cpu_count == 4

    def test_plan_uses_default_server(self, planner, sample_profile):
        plan = planner.generate_plan(sample_profile)
        assert plan.server.cpu_count == 2  # default


# =============================================================================
# Topological Sort Tests
# =============================================================================

class TestOrderResolution:

    def test_linear_chain(self, planner):
        steps = [
            DeploymentStep(id="a", name="A", command="a"),
            DeploymentStep(id="b", name="B", command="b", depends_on=["a"]),
            DeploymentStep(id="c", name="C", command="c", depends_on=["b"]),
        ]
        ordered = planner._resolve_order(steps)
        ids = [s.id for s in ordered]
        assert ids.index("a") < ids.index("b") < ids.index("c")

    def test_parallel_steps_preserved(self, planner):
        steps = [
            DeploymentStep(id="a", name="A", command="a"),
            DeploymentStep(id="b", name="B", command="b"),
            DeploymentStep(id="c", name="C", command="c", depends_on=["a", "b"]),
        ]
        ordered = planner._resolve_order(steps)
        ids = [s.id for s in ordered]
        assert ids.index("a") < ids.index("c")
        assert ids.index("b") < ids.index("c")

    def test_empty_steps(self, planner):
        assert planner._resolve_order([]) == []


# =============================================================================
# Parallel Grouping Tests
# =============================================================================

class TestParallelGroups:

    def test_independent_steps_in_one_group(self, planner):
        steps = [
            DeploymentStep(id="a", name="A", command="a"),
            DeploymentStep(id="b", name="B", command="b"),
            DeploymentStep(id="c", name="C", command="c"),
        ]
        groups = planner.get_parallel_groups(steps)
        assert len(groups) == 1
        assert len(groups[0]) == 3

    def test_linear_chain_creates_separate_groups(self, planner):
        steps = [
            DeploymentStep(id="a", name="A", command="a"),
            DeploymentStep(id="b", name="B", command="b", depends_on=["a"]),
            DeploymentStep(id="c", name="C", command="c", depends_on=["b"]),
        ]
        groups = planner.get_parallel_groups(steps)
        assert len(groups) == 3
        assert len(groups[0]) == 1  # only "a"
        assert len(groups[1]) == 1  # only "b"
        assert len(groups[2]) == 1  # only "c"

    def test_diamond_dependency(self, planner):
        steps = [
            DeploymentStep(id="a", name="A", command="a"),
            DeploymentStep(id="b", name="B", command="b", depends_on=["a"]),
            DeploymentStep(id="c", name="C", command="c", depends_on=["a"]),
            DeploymentStep(id="d", name="D", command="d", depends_on=["b", "c"]),
        ]
        groups = planner.get_parallel_groups(steps)
        assert len(groups) == 3  # [a], [b, c], [d]
        assert len(groups[1]) == 2  # b and c run in parallel

    def test_empty_steps(self, planner):
        assert planner.get_parallel_groups([]) == []


# =============================================================================
# Validation Tests
# =============================================================================

class TestPlanValidation:

    def test_valid_plan_no_warnings(self, planner):
        plan = DeploymentPlan(
            project_name="app",
            steps=[
                DeploymentStep(id="a", name="A", command="a"),
                DeploymentStep(id="b", name="B", command="b", depends_on=["a"]),
            ],
        )
        warnings = planner.validate_plan(plan)
        assert len(warnings) == 0

    def test_broken_dependency_warning(self, planner):
        plan = DeploymentPlan(
            project_name="app",
            steps=[
                DeploymentStep(id="a", name="A", command="a", depends_on=["nonexistent"]),
            ],
        )
        warnings = planner.validate_plan(plan)
        assert any("nonexistent" in w for w in warnings)

    def test_cycle_detection(self, planner):
        plan = DeploymentPlan(
            project_name="app",
            steps=[
                DeploymentStep(id="a", name="A", command="a", depends_on=["b"]),
                DeploymentStep(id="b", name="B", command="b", depends_on=["a"]),
            ],
        )
        warnings = planner.validate_plan(plan)
        assert any("circular" in w.lower() for w in warnings)


# =============================================================================
# Preview Formatting Tests
# =============================================================================

class TestFormatPreview:

    def test_preview_contains_project_name(self, planner, sample_profile):
        plan = planner.generate_plan(sample_profile)
        preview = planner.format_preview(plan)
        assert "test-app" in preview

    def test_preview_contains_step_names(self, planner, sample_profile):
        plan = planner.generate_plan(sample_profile)
        preview = planner.format_preview(plan)
        assert "Install Node.js" in preview
        assert "Configure Nginx" in preview

    def test_preview_contains_wave_info(self, planner, sample_profile):
        plan = planner.generate_plan(sample_profile)
        preview = planner.format_preview(plan)
        assert "Wave" in preview
