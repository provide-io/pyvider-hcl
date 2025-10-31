#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Example 05: Terraform Resources

This example demonstrates how to create Terraform resource
structures using the factory functions."""

from pyvider.hcl import create_resource_cty, pretty_print_cty


def example_simple_resource() -> None:
    """Create a simple resource with explicit schema."""
    print("=" * 60)
    print("Example 1: Simple Resource with Schema")
    print("=" * 60)

    resource = create_resource_cty(
        r_type="aws_instance",
        r_name="web_server",
        attributes_py={
            "ami": "ami-12345678",
            "instance_type": "t2.micro",
        },
        attributes_schema_py={
            "ami": "string",
            "instance_type": "string",
        },
    )

    pretty_print_cty(resource)


def example_resource_with_inference() -> None:
    """Create a resource with automatic type inference."""
    print("\n" + "=" * 60)
    print("Example 2: Resource with Type Inference")
    print("=" * 60)

    resource = create_resource_cty(
        r_type="aws_s3_bucket",
        r_name="data_bucket",
        attributes_py={
            "bucket": "my-data-bucket",
            "versioning": True,
        },
        # No schema - types will be inferred
    )

    pretty_print_cty(resource)


def example_resource_with_numbers() -> None:
    """Create a resource with number attributes."""
    print("\n" + "=" * 60)
    print("Example 3: Resource with Numbers")
    print("=" * 60)

    resource = create_resource_cty(
        r_type="aws_db_instance",
        r_name="main",
        attributes_py={
            "engine": "postgres",
            "engine_version": "14.7",
            "instance_class": "db.t3.micro",
            "allocated_storage": 20,
            "port": 5432,
        },
        attributes_schema_py={
            "engine": "string",
            "engine_version": "string",
            "instance_class": "string",
            "allocated_storage": "number",
            "port": "number",
        },
    )

    pretty_print_cty(resource)


def example_resource_with_complex_types() -> None:
    """Create a resource with complex nested types."""
    print("\n" + "=" * 60)
    print("Example 4: Resource with Complex Types")
    print("=" * 60)

    resource = create_resource_cty(
        r_type="aws_security_group",
        r_name="web_sg",
        attributes_py={
            "name": "web-security-group",
            "description": "Security group for web servers",
            "vpc_id": "vpc-12345",
            "ingress": [
                {
                    "from_port": 80,
                    "to_port": 80,
                    "protocol": "tcp",
                    "cidr_blocks": ["0.0.0.0/0"],
                },
                {
                    "from_port": 443,
                    "to_port": 443,
                    "protocol": "tcp",
                    "cidr_blocks": ["0.0.0.0/0"],
                },
            ],
        },
        attributes_schema_py={
            "name": "string",
            "description": "string",
            "vpc_id": "string",
            "ingress": "list(object({from_port=number, to_port=number, protocol=string, cidr_blocks=list(string)}))",
        },
    )

    pretty_print_cty(resource)


def main() -> None:
    """Run all Terraform resource examples."""
    example_simple_resource()
    example_resource_with_inference()
    example_resource_with_numbers()
    example_resource_with_complex_types()

    print("\n" + "=" * 60)
    print("All Terraform resource examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()

# 📄⚙️🔚
