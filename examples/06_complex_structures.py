#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Example 06: Complex Nested Structures

This example demonstrates parsing and working with
complex nested HCL structures."""

from pyvider.cty import CtyList, CtyNumber, CtyObject, CtyString
from pyvider.hcl import parse_hcl_to_cty, pretty_print_cty


def example_nested_objects() -> None:
    """Parse deeply nested objects."""
    print("=" * 60)
    print("Example 1: Deeply Nested Objects")
    print("=" * 60)

    hcl_content = """
    application = {
      name = "myapp"

      config = {
        server = {
          host = "localhost"
          port = 8080

          tls = {
            enabled = true
            cert_path = "/etc/certs/server.crt"
            key_path = "/etc/certs/server.key"
          }
        }

        database = {
          host = "db.example.com"
          port = 5432

          pool = {
            min_size = 5
            max_size = 20
            timeout = 30
          }
        }
      }
    }
    """

    result = parse_hcl_to_cty(hcl_content)

    pretty_print_cty(result)


def example_list_of_objects() -> None:
    """Parse lists containing objects."""
    print("\n" + "=" * 60)
    print("Example 2: Lists of Objects")
    print("=" * 60)

    hcl_content = """
    servers = [
      {
        name = "web-1"
        ip = "10.0.1.10"
        role = "web"
      },
      {
        name = "web-2"
        ip = "10.0.1.11"
        role = "web"
      },
      {
        name = "db-1"
        ip = "10.0.2.10"
        role = "database"
      }
    ]
    """

    result = parse_hcl_to_cty(hcl_content)

    pretty_print_cty(result)


def example_mixed_collections() -> None:
    """Parse mixed collections (lists of lists, objects with lists)."""
    print("\n" + "=" * 60)
    print("Example 3: Mixed Collections")
    print("=" * 60)

    hcl_content = """
    deployment = {
      regions = ["us-west-2", "us-east-1", "eu-west-1"]

      region_configs = [
        {
          region = "us-west-2"
          zones = ["us-west-2a", "us-west-2b", "us-west-2c"]
          instance_types = ["t3.micro", "t3.small"]
        },
        {
          region = "us-east-1"
          zones = ["us-east-1a", "us-east-1b"]
          instance_types = ["t3.micro"]
        }
      ]
    }
    """

    result = parse_hcl_to_cty(hcl_content)

    pretty_print_cty(result)


def example_with_schema_validation() -> None:
    """Parse complex structure with schema validation."""
    print("\n" + "=" * 60)
    print("Example 4: Complex Structure with Schema")
    print("=" * 60)

    schema = CtyObject(
        {
            "services": CtyList(
                element_type=CtyObject(
                    {
                        "name": CtyString(),
                        "port": CtyNumber(),
                        "endpoints": CtyList(element_type=CtyString()),
                    }
                )
            )
        }
    )

    hcl_content = """
    services = [
      {
        name = "api"
        port = 8080
        endpoints = ["/health", "/metrics", "/api/v1"]
      },
      {
        name = "admin"
        port = 8081
        endpoints = ["/admin", "/health"]
      }
    ]
    """

    result = parse_hcl_to_cty(hcl_content, schema=schema)

    pretty_print_cty(result)


def main() -> None:
    """Run all complex structure examples."""
    example_nested_objects()
    example_list_of_objects()
    example_mixed_collections()
    example_with_schema_validation()

    print("\n" + "=" * 60)
    print("All complex structure examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()

# 📄⚙️🔚
