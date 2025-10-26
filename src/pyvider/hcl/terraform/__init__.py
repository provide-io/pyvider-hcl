"""Terraform-specific HCL processing module."""

from pyvider.hcl.terraform.config import parse_terraform_config

__all__ = [
    "parse_terraform_config",
]
