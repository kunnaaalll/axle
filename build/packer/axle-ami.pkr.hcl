// =============================================================================
// AXLE OS — Main Packer Template
// T-012
//
// Builds the AXLE OS AMI by layering:
//   1. Ubuntu 22.04 LTS base
//   2. Server stack (Nginx, PostgreSQL, Node.js, Python, Go, Certbot)
//   3. AXLE appliance (Python package, dashboard, CLI)
//   4. Branding (MOTD, os-release, banners)
//   5. First-boot wizard service
//   6. Cleanup (minimize image size)
// =============================================================================

packer {
  required_plugins {
    amazon = {
      version = ">= 1.2.0"
      source  = "github.com/hashicorp/amazon"
    }
  }
}

// ---------------------------------------------------------------------------
// Source: Find latest Ubuntu 22.04 AMI and launch a temporary build instance
// ---------------------------------------------------------------------------

source "amazon-ebs" "axle" {
  region        = var.aws_region
  instance_type = var.instance_type
  ssh_username  = var.ssh_username

  source_ami_filter {
    filters = {
      name                = var.ubuntu_ami_filter
      root-device-type    = "ebs"
      virtualization-type = "hvm"
    }
    owners      = ["099720109477"] # Canonical (Ubuntu)
    most_recent = true
  }

  ami_name        = "${var.ami_name}-v${var.axle_version}-{{timestamp}}"
  ami_description = "AXLE OS v${var.axle_version} — AI-Powered Linux Deployment Engine"

  tags = {
    Name    = "AXLE OS"
    Version = var.axle_version
    Builder = "packer"
  }

  launch_block_device_mappings {
    device_name           = "/dev/sda1"
    volume_size           = var.volume_size
    volume_type           = "gp3"
    delete_on_termination = true
  }
}

// ---------------------------------------------------------------------------
// Build: Run provisioning scripts in order (Layer 1 → 2 → 3 → branding)
// ---------------------------------------------------------------------------

build {
  name    = "axle-os"
  sources = ["source.amazon-ebs.axle"]

  // --- Layer 2: Base system update + essential packages ---
  provisioner "shell" {
    script = "scripts/01-base-setup.sh"
    environment_vars = [
      "DEBIAN_FRONTEND=noninteractive"
    ]
  }

  // --- Layer 2: Install full server stack ---
  provisioner "shell" {
    script = "scripts/02-server-stack.sh"
    environment_vars = [
      "DEBIAN_FRONTEND=noninteractive"
    ]
  }

  // --- Layer 3: Install AXLE Python package + dashboard ---
  provisioner "shell" {
    script = "scripts/03-install-axle.sh"
    environment_vars = [
      "AXLE_VERSION=${var.axle_version}"
    ]
  }

  // --- Branding: MOTD, os-release, SSH banner ---
  provisioner "shell" {
    script = "scripts/04-branding.sh"
    environment_vars = [
      "AXLE_VERSION=${var.axle_version}"
    ]
  }

  // --- First-boot wizard systemd service ---
  provisioner "shell" {
    script = "scripts/05-first-boot.sh"
  }

  // --- Cleanup: Remove build artifacts, minimize image ---
  provisioner "shell" {
    script = "scripts/06-cleanup.sh"
  }
}
