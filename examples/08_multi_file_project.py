#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Example 08: Multi-File Project

This example demonstrates parsing multiple HCL files
in a real-world project structure."""

from pathlib import Path
from tempfile import TemporaryDirectory

from pyvider.hcl import parse_with_context


def create_sample_project(base_dir: Path) -> None:
    """Create a sample multi-file Terraform project."""
    # Create main configuration
    (base_dir / "main.hcl").write_text("""
terraform {
  required_version = ">= 1.0"
}

module "vpc" {
  source = "./modules/vpc"
  vpc_name = var.vpc_name
  cidr_block = var.vpc_cidr
}

module "compute" {
  source = "./modules/compute"
  vpc_id = module.vpc.id
  instance_count = var.instance_count
}
""")

    # Create variables file
    (base_dir / "variables.hcl").write_text("""
variable "vpc_name" {
  description = "Name of the VPC"
  type        = string
  default     = "main-vpc"
}

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "instance_count" {
  description = "Number of instances"
  type        = number
  default     = 3
}
""")

    # Create outputs file
    (base_dir / "outputs.hcl").write_text("""
output "vpc_id" {
  description = "ID of the VPC"
  value       = module.vpc.id
}

output "instance_ids" {
  description = "IDs of compute instances"
  value       = module.compute.instance_ids
}
""")

    # Create module directory
    modules_dir = base_dir / "modules" / "vpc"
    modules_dir.mkdir(parents=True)

    (modules_dir / "main.hcl").write_text("""
resource "aws_vpc" "main" {
  cidr_block = var.cidr_block

  tags = {
    Name = var.vpc_name
  }
}

output "id" {
  value = aws_vpc.main.id
}
""")

    (modules_dir / "variables.hcl").write_text("""
variable "vpc_name" {
  type = string
}

variable "cidr_block" {
  type = string
}
""")


def example_parse_all_files() -> None:
    """Parse all HCL files in a project."""
    print("=" * 60)
    print("Example 1: Parsing All Project Files")
    print("=" * 60)

    with TemporaryDirectory() as tmpdir:
        base_dir = Path(tmpdir)
        create_sample_project(base_dir)

        # Find all HCL files
        hcl_files = sorted(base_dir.glob("**/*.hcl"))

        for file in hcl_files:
            rel_path = file.relative_to(base_dir)
            print(f"  - {rel_path}")

        # Parse each file
        for file in hcl_files:
            rel_path = file.relative_to(base_dir)
            try:
                content = file.read_text()
                parse_with_context(content, source_file=file)
            except Exception as e:
                print(f"  ❌ {rel_path}: {e}")


def example_parse_specific_files() -> None:
    """Parse specific files by type (variables, outputs, etc)."""
    print("\n" + "=" * 60)
    print("Example 2: Parsing Specific File Types")
    print("=" * 60)

    with TemporaryDirectory() as tmpdir:
        base_dir = Path(tmpdir)
        create_sample_project(base_dir)

        # Parse variables file
        variables_file = base_dir / "variables.hcl"
        content = variables_file.read_text()
        variables = parse_with_context(content, source_file=variables_file)
        print(f"\n  Found {len(variables.get('variable', []))} variables:")
        for var_block in variables.get("variable", []):
            for var_name in var_block:
                print(f"    - {var_name}")

        # Parse outputs file
        outputs_file = base_dir / "outputs.hcl"
        content = outputs_file.read_text()
        outputs = parse_with_context(content, source_file=outputs_file)
        print(f"\n  Found {len(outputs.get('output', []))} outputs:")
        for output_block in outputs.get("output", []):
            for output_name in output_block:
                print(f"    - {output_name}")


def example_validate_project_structure() -> None:
    """Validate that a project has required files."""
    print("\n" + "=" * 60)
    print("Example 3: Validating Project Structure")
    print("=" * 60)

    with TemporaryDirectory() as tmpdir:
        base_dir = Path(tmpdir)
        create_sample_project(base_dir)

        required_files = [
            "main.hcl",
            "variables.hcl",
            "outputs.hcl",
        ]

        print("\n🔍 Checking for required files:")
        all_present = True
        for filename in required_files:
            file_path = base_dir / filename
            if file_path.exists():
                print(f"  ✅ {filename}")
            else:
                print(f"  ❌ {filename} (missing)")
                all_present = False

        if all_present:
            print("\n✅ Project structure is complete!")
        else:
            print("\n❌ Project structure is incomplete!")


def example_aggregate_configuration() -> None:
    """Aggregate configuration from multiple files."""
    print("\n" + "=" * 60)
    print("Example 4: Aggregating Configuration")
    print("=" * 60)

    with TemporaryDirectory() as tmpdir:
        base_dir = Path(tmpdir)
        create_sample_project(base_dir)

        # Aggregate all configuration
        all_config = {
            "variables": {},
            "outputs": {},
            "modules": [],
            "resources": [],
        }

        for hcl_file in base_dir.glob("*.hcl"):
            content = hcl_file.read_text()
            config = parse_with_context(content, source_file=hcl_file)

            # Extract variables
            if "variable" in config:
                for var_block in config["variable"]:
                    all_config["variables"].update(var_block)

            # Extract outputs
            if "output" in config:
                for output_block in config["output"]:
                    all_config["outputs"].update(output_block)

            # Extract modules
            if "module" in config:
                for module_block in config["module"]:
                    all_config["modules"].extend(module_block.keys())

        print("\n📊 Project Summary:")
        print(f"  Variables: {len(all_config['variables'])}")
        print(f"  Outputs: {len(all_config['outputs'])}")
        print(f"  Modules: {len(all_config['modules'])}")

        print("\n📋 Variable Names:")
        for var_name in all_config["variables"]:
            print(f"    - {var_name}")


def main() -> None:
    """Run all multi-file project examples."""
    example_parse_all_files()
    example_parse_specific_files()
    example_validate_project_structure()
    example_aggregate_configuration()

    print("\n" + "=" * 60)
    print("All multi-file project examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()

# 📄⚙️🔚
