"""
Tests for axle.cli — Click CLI commands.

Verifies:
  - CLI group is accessible
  - All commands are registered
  - Commands produce expected output
  - Help text works
"""
import pytest
from click.testing import CliRunner
from axle.cli import main


@pytest.fixture
def runner():
    return CliRunner()


class TestCLIGroup:
    """Test the main CLI group."""

    def test_cli_help(self, runner):
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "AXLE OS" in result.output

    def test_cli_has_deploy_command(self, runner):
        result = runner.invoke(main, ["--help"])
        assert "deploy" in result.output

    def test_cli_has_setup_command(self, runner):
        result = runner.invoke(main, ["--help"])
        assert "setup" in result.output

    def test_cli_has_status_command(self, runner):
        result = runner.invoke(main, ["--help"])
        assert "status" in result.output


class TestDeployCommand:
    """Test the deploy command."""

    def test_deploy_requires_url(self, runner):
        result = runner.invoke(main, ["deploy"])
        assert result.exit_code != 0  # Missing required argument

    def test_deploy_with_url(self, runner):
        result = runner.invoke(main, ["deploy", "https://github.com/user/repo"])
        assert result.exit_code == 0
        assert "Starting deployment" in result.output

    def test_deploy_help(self, runner):
        result = runner.invoke(main, ["deploy", "--help"])
        assert result.exit_code == 0
        assert "repo_url" in result.output.lower() or "REPO_URL" in result.output


class TestSetupCommand:
    """Test the setup command."""

    def test_setup_runs(self, runner):
        result = runner.invoke(main, ["setup"])
        assert result.exit_code == 0
        assert "Welcome" in result.output or "Setup" in result.output


class TestStatusCommand:
    """Test the status command."""

    def test_status_runs(self, runner):
        result = runner.invoke(main, ["status"])
        assert result.exit_code == 0
        assert "status" in result.output.lower()
