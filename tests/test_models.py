"""
Tests for axle.core.models — Pydantic data models.

Verifies:
  - All enums have correct values
  - Models validate required fields
  - Models reject invalid data
  - Default values are applied correctly
  - Serialization round-trips work
"""
import pytest
from axle.core.models import (
    StackType,
    DatabaseType,
    ProjectProfile,
    DeploymentStep,
    DeploymentStepStatus,
    DeploymentPlan,
)


class TestStackType:
    """Test StackType enum values."""

    def test_all_stack_types_exist(self):
        assert StackType.NODEJS == "nodejs"
        assert StackType.PYTHON == "python"
        assert StackType.GO == "go"
        assert StackType.JAVA == "java"
        assert StackType.STATIC == "static"

    def test_stack_type_count(self):
        assert len(StackType) == 5


class TestDatabaseType:
    """Test DatabaseType enum values."""

    def test_all_database_types_exist(self):
        assert DatabaseType.POSTGRESQL == "postgresql"
        assert DatabaseType.MYSQL == "mysql"
        assert DatabaseType.MONGODB == "mongodb"
        assert DatabaseType.REDIS == "redis"
        assert DatabaseType.NONE == "none"


class TestProjectProfile:
    """Test ProjectProfile model validation and defaults."""

    def test_minimal_valid_profile(self):
        profile = ProjectProfile(
            name="test-app",
            github_url="https://github.com/user/repo",
            stack=StackType.NODEJS,
            start_command="node server.js",
        )
        assert profile.name == "test-app"
        assert profile.database == DatabaseType.NONE  # default
        assert profile.env_vars == []  # default
        assert profile.build_command is None  # default
        assert profile.version is None  # default

    def test_full_profile(self):
        profile = ProjectProfile(
            name="my-saas",
            github_url="https://github.com/user/saas",
            stack=StackType.PYTHON,
            version="3.12",
            database=DatabaseType.POSTGRESQL,
            env_vars=["DATABASE_URL", "SECRET_KEY"],
            build_command="pip install -r requirements.txt",
            start_command="uvicorn main:app --port 8000",
        )
        assert profile.stack == StackType.PYTHON
        assert profile.database == DatabaseType.POSTGRESQL
        assert len(profile.env_vars) == 2

    def test_missing_required_field_raises(self):
        with pytest.raises(Exception):
            ProjectProfile(
                name="test",
                github_url="https://github.com/user/repo",
                # missing stack and start_command
            )

    def test_serialization_round_trip(self):
        profile = ProjectProfile(
            name="test-app",
            github_url="https://github.com/user/repo",
            stack=StackType.NODEJS,
            start_command="npm start",
        )
        data = profile.model_dump()
        restored = ProjectProfile(**data)
        assert restored == profile

    def test_json_round_trip(self):
        profile = ProjectProfile(
            name="test-app",
            github_url="https://github.com/user/repo",
            stack=StackType.GO,
            start_command="./main",
            database=DatabaseType.MYSQL,
        )
        json_str = profile.model_dump_json()
        restored = ProjectProfile.model_validate_json(json_str)
        assert restored.stack == StackType.GO
        assert restored.database == DatabaseType.MYSQL


class TestDeploymentStep:
    """Test DeploymentStep model."""

    def test_step_defaults(self):
        step = DeploymentStep(
            id="install-deps",
            name="Install dependencies",
            command="npm install",
        )
        assert step.status == DeploymentStepStatus.PENDING
        assert step.output == ""
        assert step.error is None
        assert step.depends_on == []

    def test_step_with_dependency(self):
        step = DeploymentStep(
            id="build",
            name="Build project",
            command="npm run build",
            depends_on=["install-deps"],
        )
        assert step.depends_on == ["install-deps"]

    def test_step_status_transitions(self):
        step = DeploymentStep(
            id="test",
            name="Run tests",
            command="npm test",
        )
        assert step.status == DeploymentStepStatus.PENDING
        step.status = DeploymentStepStatus.RUNNING
        assert step.status == DeploymentStepStatus.RUNNING
        step.status = DeploymentStepStatus.COMPLETED
        assert step.status == DeploymentStepStatus.COMPLETED


class TestDeploymentPlan:
    """Test DeploymentPlan model."""

    def test_empty_plan(self):
        plan = DeploymentPlan(project_name="test", steps=[])
        assert plan.project_name == "test"
        assert len(plan.steps) == 0

    def test_plan_with_steps(self):
        steps = [
            DeploymentStep(id="s1", name="Step 1", command="echo 1"),
            DeploymentStep(id="s2", name="Step 2", command="echo 2", depends_on=["s1"]),
            DeploymentStep(id="s3", name="Step 3", command="echo 3", depends_on=["s1"]),
        ]
        plan = DeploymentPlan(project_name="my-app", steps=steps)
        assert len(plan.steps) == 3
        assert plan.steps[1].depends_on == ["s1"]

    def test_plan_serialization(self):
        steps = [
            DeploymentStep(id="s1", name="Install", command="npm install"),
        ]
        plan = DeploymentPlan(project_name="app", steps=steps)
        data = plan.model_dump()
        restored = DeploymentPlan(**data)
        assert restored.project_name == "app"
        assert len(restored.steps) == 1
        assert restored.steps[0].id == "s1"
