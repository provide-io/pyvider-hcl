#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Pytest configuration and fixtures for pyvider-hcl tests."""

from pathlib import Path

from provide.testkit import (
    reset_foundation_setup_for_testing,
)
import pytest


@pytest.fixture(autouse=True)
def reset_foundation() -> None:
    """Reset foundation setup for testing.

    This ensures clean state between tests, particularly for logger configuration.
    """
    reset_foundation_setup_for_testing()


@pytest.fixture
def hcl_temp_dir(tmp_path: Path) -> Path:
    """Provides a temporary directory for HCL test files."""
    return tmp_path


@pytest.fixture
def sample_hcl_content() -> str:
    """Provides sample HCL content for testing."""
    return """
variable "name" {
  description = "Resource name"
  type        = string
  default     = "example"
}

resource "example" "test" {
  name = var.name
  port = 8080
}
"""


@pytest.fixture
def multi_file_hcl_structure(tmp_path: Path) -> Path:
    """Creates a multi-file HCL project structure."""
    structure = {
        "main.hcl": """
terraform {
  required_version = ">= 1.0"
}

module "vpc" {
  source = "./modules/vpc"
  vpc_name = var.vpc_name
}
""",
        "variables.hcl": """
variable "vpc_name" {
  description = "VPC name"
  type        = string
  default     = "main-vpc"
}

variable "region" {
  description = "AWS region"
  type        = string
  default     = "us-west-2"
}
""",
        "outputs.hcl": """
output "vpc_id" {
  description = "VPC ID"
  value       = module.vpc.id
}

output "vpc_cidr" {
  description = "VPC CIDR block"
  value       = module.vpc.cidr_block
}
""",
        "modules/vpc/main.hcl": """
resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"

  tags = {
    Name = var.vpc_name
  }
}

output "id" {
  value = aws_vpc.main.id
}

output "cidr_block" {
  value = aws_vpc.main.cidr_block
}
""",
        "modules/vpc/variables.hcl": """
variable "vpc_name" {
  description = "Name tag for VPC"
  type        = string
}
""",
    }

    # Create the file structure
    for file_path, content in structure.items():
        full_path = tmp_path / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content)

    return tmp_path


@pytest.fixture
def hcl_config_file(tmp_path: Path) -> Path:
    """Provides a temporary HCL configuration file."""
    content = """
config {
  name = "test-config"
  version = "1.0.0"

  settings {
    enabled = true
    timeout = 30
    retries = 3
  }
}
"""
    config_file = tmp_path / "config.hcl"
    config_file.write_text(content)
    return config_file


@pytest.fixture
def nested_object_hcl() -> str:
    """HCL content with nested objects for testing."""
    return """
config {
  name = "my-service"

  owner {
    name = "Admin"

    contact {
      email = "admin@example.com"
      phone = "555-0100"
    }
  }

  threshold = 100
  enabled = true
  tags = ["production", "critical"]
}
"""


@pytest.fixture
def list_of_objects_hcl() -> str:
    """HCL content with lists of objects for testing."""
    return """
item_group {
  group_name = "group1"

  items {
    id = "item1"
    value = 100

    spec {
      feature_a = "enabled"
      feature_b = true
    }
  }

  items {
    id = "item2"
    value = 200

    spec {
      feature_a = "disabled"
      feature_b = false
    }
  }
}
"""


# 📄⚙️🔚
