#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Terraform-specific HCL processing module."""

from pyvider.hcl.terraform.config import (
    TERRAFORM_BLOCK_TYPES,
    TerraformBlock,
    TerraformConfig,
    parse_terraform_blocks,
    parse_terraform_config,
)

__all__ = [
    "TERRAFORM_BLOCK_TYPES",
    "TerraformBlock",
    "TerraformConfig",
    "parse_terraform_blocks",
    "parse_terraform_config",
]

# 📄⚙️🔚
