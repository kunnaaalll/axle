// =============================================================================
// AXLE OS — Packer Build Variables
// T-011
// =============================================================================

variable "aws_region" {
  type        = string
  default     = "us-east-1"
  description = "AWS region to build the AMI in"
}

variable "instance_type" {
  type        = string
  default     = "t3.medium"
  description = "EC2 instance type used during the build process"
}

variable "ami_name" {
  type        = string
  default     = "axle-os"
  description = "Base name for the output AMI"
}

variable "axle_version" {
  type        = string
  default     = "1.0.0"
  description = "AXLE OS version number baked into the image"
}

variable "ubuntu_ami_filter" {
  type        = string
  default     = "ubuntu/images/*ubuntu-jammy-22.04-amd64-server-*"
  description = "AMI name filter to find the latest Ubuntu 22.04 base image"
}

variable "ssh_username" {
  type        = string
  default     = "ubuntu"
  description = "SSH username for the base Ubuntu AMI"
}

variable "volume_size" {
  type        = number
  default     = 30
  description = "Root EBS volume size in GB"
}
