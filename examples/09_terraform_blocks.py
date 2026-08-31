#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Example 09: Terraform Blocks and Source Lines

`parse_hcl_to_cty` flattens a configuration into nested values, which loses both
the block/attribute distinction and every source position. `parse_terraform_blocks`
keeps them: each top-level block reports its type, its labels, and the line range
it occupies -- which is what a diagnostic needs to point at a specific block."""

from pathlib import Path
from tempfile import TemporaryDirectory

from pyvider.hcl import (
    TERRAFORM_BLOCK_TYPES,
    TerraformConfig,
    parse_terraform_blocks,
    parse_terraform_config,
)

SAMPLE_CONFIG = """terraform {
  required_version = ">= 1.5"
}

variable "region" {
  type    = string
  default = "us-west-2"
}

resource "aws_instance" "web" {
  ami           = "ami-123"
  instance_type = var.instance_type

  tags = {
    Name = "web"
  }
}

resource "aws_instance" "db" {
  ami = "ami-456"
}

locals {
  prefix = "app"
}

output "ip" {
  value = aws_instance.web.public_ip
}
"""


def example_block_inventory() -> None:
    """List every block, with its address and the lines it spans."""
    print("=" * 60)
    print("Example 1: Block Inventory")
    print("=" * 60)

    config = parse_terraform_blocks(SAMPLE_CONFIG)

    print(f"Block types present: {', '.join(config.block_types)}\n")
    for block in config.blocks:
        span = f"lines {block.start_line}-{block.end_line}"
        print(f"  {block.address:<28} {span}")

    # `address` joins the block type and its labels, so it reads the way
    # Terraform itself refers to a block.
    print("\nA block with no labels is addressed by its type alone:")
    print(f"  {config.blocks_of('locals')[0].address}")


def example_finding_blocks() -> None:
    """Select blocks by type, or one block by its exact labels."""
    print("\n" + "=" * 60)
    print("Example 2: Finding Blocks")
    print("=" * 60)

    config = parse_terraform_blocks(SAMPLE_CONFIG)

    resources = config.blocks_of("resource")
    print(f"{len(resources)} resource block(s), in source order:")
    for resource in resources:
        print(f"  {resource.address}")

    web = config.block_at("resource", "aws_instance", "web")
    if web is not None:
        print(f"\nBody of {web.address}:")
        for name, value in web.body.items():
            print(f"  {name} = {value!r}")

    # `block_at` returns None rather than raising, so a lookup for a block that
    # is not there is an ordinary branch.
    missing = config.block_at("resource", "aws_instance", "cache")
    print(f"\nLookup for a block that is not present: {missing}")


def example_expressions_are_preserved() -> None:
    """Expressions survive as `${...}` text; they are never evaluated."""
    print("\n" + "=" * 60)
    print("Example 3: Expressions Are Preserved, Not Evaluated")
    print("=" * 60)

    config = parse_terraform_blocks(SAMPLE_CONFIG)
    web = config.block_at("resource", "aws_instance", "web")
    if web is None:
        return

    print(f"  ami           = {web.body['ami']!r}   <- a literal")
    print(f"  instance_type = {web.body['instance_type']!r}   <- an expression, kept verbatim")
    print("\nResolving `var.instance_type` is the caller's job; this package does not")
    print("evaluate expressions, so nothing is silently guessed at.")


def example_top_level_attributes() -> None:
    """Attributes written outside any block are kept separately."""
    print("\n" + "=" * 60)
    print("Example 4: Top-Level Attributes")
    print("=" * 60)

    config = parse_terraform_blocks(
        'schema_version = 2\nowner = "platform-team"\n\nlocals {\n  prefix = "app"\n}\n'
    )

    print(f"Attributes: {config.attributes}")
    print(f"Blocks:     {[block.address for block in config.blocks]}")


def example_unrecognised_block_types() -> None:
    """`TERRAFORM_BLOCK_TYPES` separates Terraform's own blocks from the rest."""
    print("\n" + "=" * 60)
    print("Example 5: Recognising Terraform's Own Block Types")
    print("=" * 60)

    config = parse_terraform_blocks(
        'resource "aws_instance" "web" {\n  ami = "a"\n}\n\nmy_extension "thing" {\n  enabled = true\n}\n'
    )

    for block in config.blocks:
        known = block.block_type in TERRAFORM_BLOCK_TYPES
        marker = "terraform" if known else "custom"
        print(f"  {block.address:<28} ({marker})")


def example_diagnostics_from_line_numbers() -> None:
    """Line ranges let a caller report a problem against the source."""
    print("\n" + "=" * 60)
    print("Example 6: Reporting Against Source Lines")
    print("=" * 60)

    lines = SAMPLE_CONFIG.splitlines()
    config = parse_terraform_blocks(SAMPLE_CONFIG)

    for resource in config.blocks_of("resource"):
        if "instance_type" not in resource.body:
            print(f"  warning: {resource.address} has no instance_type")
            if resource.start_line is not None:
                print(f"    at line {resource.start_line}: {lines[resource.start_line - 1]}")


def example_parsing_a_file() -> None:
    """`parse_terraform_config` reads a path and records it on the result."""
    print("\n" + "=" * 60)
    print("Example 7: Parsing a File")
    print("=" * 60)

    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "main.tf"
        path.write_text(SAMPLE_CONFIG, encoding="utf-8")

        config: TerraformConfig = parse_terraform_config(path)

        print(f"Source file: {Path(config.source_file).name if config.source_file else None}")
        print(f"Blocks:      {len(config.blocks)}")
        print(f"Addresses:   {[block.address for block in config.blocks][:3]} ...")


def main() -> None:
    """Run all Terraform block examples."""
    example_block_inventory()
    example_finding_blocks()
    example_expressions_are_preserved()
    example_top_level_attributes()
    example_unrecognised_block_types()
    example_diagnostics_from_line_numbers()
    example_parsing_a_file()

    print("\n" + "=" * 60)
    print("All Terraform block examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()

# 📄⚙️🔚
