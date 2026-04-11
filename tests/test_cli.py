"""
Tests for axle.cli — Click CLI commands.

Verifies:
  - CLI group is accessible
  - All commands are registered
  - Commands produce expected output
  - Help text works
  - Scan command works with real fixture projects
"""
import json
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

    def test_cli_has_scan_command(self, runner):
        result = runner.invoke(main, ["--help"])
        assert "scan" in result.output

    def test_cli_has_plan_command(self, runner):
        result = runner.invoke(main, ["--help"])
        assert "plan" in result.output

    def test_cli_has_info_command(self, runner):
        result = runner.invoke(main, ["--help"])
        assert "info" in result.output

    def test_version(self, runner):
        result = runner.invoke(main, ["--version"])
        assert result.exit_code == 0
        assert "0.1.0" in result.output


class TestScanCommand:
    """Test the scan command with real fixtures."""

    def test_scan_node_project(self, runner, sample_node_project):
        result = runner.invoke(main, ["scan", str(sample_node_project)])
        assert result.exit_code == 0
        assert "nodejs" in result.output

    def test_scan_python_project(self, runner, sample_python_project):
        result = runner.invoke(main, ["scan", str(sample_python_project)])
        assert result.exit_code == 0
        assert "python" in result.output

    def test_scan_static_project(self, runner, sample_static_project):
        result = runner.invoke(main, ["scan", str(sample_static_project)])
        assert result.exit_code == 0
        assert "static" in result.output

    def test_scan_nonexistent_dir(self, runner):
        result = runner.invoke(main, ["scan", "/nonexistent/path"])
        assert result.exit_code == 1

    def test_scan_unknown_project(self, runner, tmp_dir):
        (tmp_dir / "random.txt").write_text("nothing")
        result = runner.invoke(main, ["scan", str(tmp_dir)])
        assert result.exit_code == 1


class TestDeployCommand:
    """Test the deploy command."""

    def test_deploy_shows_warning(self, runner):
        result = runner.invoke(main, ["deploy", "https://github.com/user/repo"])
        assert result.exit_code == 0

    def test_deploy_help(self, runner):
        result = runner.invoke(main, ["deploy", "--help"])
        assert result.exit_code == 0


class TestStatusCommand:
    """Test the status command."""

    def test_status_runs(self, runner):
        result = runner.invoke(main, ["status"])
        assert result.exit_code == 0
        assert "Ready" in result.output or "Status" in result.output


class TestInfoCommand:
    """Test the info command."""

    def test_info_runs(self, runner):
        result = runner.invoke(main, ["info"])
        assert result.exit_code == 0
        assert "0.1.0" in result.output
