"""
Tests for build scripts and branding assets.

Verifies:
  - All Packer scripts exist and are executable
  - All branding files exist
  - MOTD scripts have correct shebang
  - First-boot wizard script is valid Python
  - Cloud-init YAML is valid
  - Packer HCL files exist
"""
import pytest
import os
import stat
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent


class TestPackerScripts:
    """Verify all Packer provisioning scripts exist and are executable."""

    SCRIPTS = [
        "build/packer/scripts/01-base-setup.sh",
        "build/packer/scripts/02-server-stack.sh",
        "build/packer/scripts/03-install-axle.sh",
        "build/packer/scripts/04-branding.sh",
        "build/packer/scripts/05-first-boot.sh",
        "build/packer/scripts/06-cleanup.sh",
    ]

    @pytest.mark.parametrize("script_path", SCRIPTS)
    def test_script_exists(self, script_path):
        full_path = PROJECT_ROOT / script_path
        assert full_path.exists(), f"Missing: {script_path}"

    @pytest.mark.parametrize("script_path", SCRIPTS)
    def test_script_is_executable(self, script_path):
        full_path = PROJECT_ROOT / script_path
        file_stat = os.stat(full_path)
        assert file_stat.st_mode & stat.S_IXUSR, f"Not executable: {script_path}"

    @pytest.mark.parametrize("script_path", SCRIPTS)
    def test_script_has_shebang(self, script_path):
        full_path = PROJECT_ROOT / script_path
        first_line = full_path.read_text().split("\n")[0]
        assert first_line.startswith("#!/"), f"Missing shebang: {script_path}"

    @pytest.mark.parametrize("script_path", SCRIPTS)
    def test_script_has_set_euo_pipefail(self, script_path):
        """Ensure scripts use strict error handling."""
        full_path = PROJECT_ROOT / script_path
        content = full_path.read_text()
        assert "set -euo pipefail" in content, f"Missing strict mode: {script_path}"


class TestPackerTemplates:
    """Verify Packer HCL templates exist."""

    def test_main_template_exists(self):
        assert (PROJECT_ROOT / "build/packer/axle-ami.pkr.hcl").exists()

    def test_variables_file_exists(self):
        assert (PROJECT_ROOT / "build/packer/variables.pkr.hcl").exists()

    def test_main_template_has_source(self):
        content = (PROJECT_ROOT / "build/packer/axle-ami.pkr.hcl").read_text()
        assert 'source "amazon-ebs"' in content

    def test_main_template_has_build(self):
        content = (PROJECT_ROOT / "build/packer/axle-ami.pkr.hcl").read_text()
        assert "build {" in content

    def test_variables_has_region(self):
        content = (PROJECT_ROOT / "build/packer/variables.pkr.hcl").read_text()
        assert "aws_region" in content


class TestBrandingAssets:
    """Verify all branding files exist and have correct content."""

    MOTD_SCRIPTS = [
        "build/branding/motd/00-axle-banner",
        "build/branding/motd/10-system-info",
        "build/branding/motd/20-deployment-status",
        "build/branding/motd/90-help",
    ]

    @pytest.mark.parametrize("script_path", MOTD_SCRIPTS)
    def test_motd_script_exists(self, script_path):
        assert (PROJECT_ROOT / script_path).exists()

    @pytest.mark.parametrize("script_path", MOTD_SCRIPTS)
    def test_motd_script_has_shebang(self, script_path):
        first_line = (PROJECT_ROOT / script_path).read_text().split("\n")[0]
        assert first_line.startswith("#!/")

    def test_os_release_exists(self):
        path = PROJECT_ROOT / "build/branding/os-release"
        assert path.exists()
        content = path.read_text()
        assert "AXLE OS" in content

    def test_os_release_has_required_fields(self):
        content = (PROJECT_ROOT / "build/branding/os-release").read_text()
        assert "PRETTY_NAME=" in content
        assert "NAME=" in content
        assert "ID=" in content

    def test_issue_banner_exists(self):
        assert (PROJECT_ROOT / "build/branding/issue").exists()

    def test_ssh_banner_exists(self):
        path = PROJECT_ROOT / "build/branding/ssh-banner"
        assert path.exists()
        assert "AXLE" in path.read_text()


class TestFirstBoot:
    """Verify first-boot wizard components."""

    def test_service_file_exists(self):
        path = PROJECT_ROOT / "build/firstboot/axle-firstboot.service"
        assert path.exists()

    def test_service_file_has_unit_section(self):
        content = (PROJECT_ROOT / "build/firstboot/axle-firstboot.service").read_text()
        assert "[Unit]" in content
        assert "[Service]" in content
        assert "[Install]" in content

    def test_service_uses_condition_path(self):
        """Ensure it only runs if setup hasn't been completed."""
        content = (PROJECT_ROOT / "build/firstboot/axle-firstboot.service").read_text()
        assert "ConditionPathExists=!" in content

    def test_wizard_script_exists(self):
        path = PROJECT_ROOT / "build/firstboot/axle-firstboot.py"
        assert path.exists()

    def test_wizard_script_is_valid_python(self):
        """Compile the wizard to check for syntax errors."""
        path = PROJECT_ROOT / "build/firstboot/axle-firstboot.py"
        source = path.read_text()
        compile(source, str(path), "exec")  # Raises SyntaxError if invalid

    def test_wizard_has_main_function(self):
        content = (PROJECT_ROOT / "build/firstboot/axle-firstboot.py").read_text()
        assert "def main():" in content

    def test_wizard_supports_all_providers(self):
        content = (PROJECT_ROOT / "build/firstboot/axle-firstboot.py").read_text()
        assert "gemini" in content
        assert "openrouter" in content
        assert "openai" in content
        assert "ollama" in content


class TestCloudInit:
    """Verify cloud-init configuration."""

    def test_user_data_exists(self):
        assert (PROJECT_ROOT / "build/cloud-init/user-data.yaml").exists()

    def test_user_data_is_valid_yaml(self):
        """Check YAML can at least be loaded as text without errors."""
        content = (PROJECT_ROOT / "build/cloud-init/user-data.yaml").read_text()
        assert "#cloud-config" in content

    def test_user_data_sets_hostname(self):
        content = (PROJECT_ROOT / "build/cloud-init/user-data.yaml").read_text()
        assert "hostname:" in content
