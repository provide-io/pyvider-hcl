#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Example 01: Basic HCL Parsing

This example demonstrates the basics of parsing HCL strings
and accessing the parsed values."""

from pyvider.hcl import parse_hcl_to_cty, pretty_print_cty


def example_simple_values() -> None:
    """Parse HCL with simple primitive values."""
    print("=" * 60)
    print("Example 1: Simple Primitive Values")
    print("=" * 60)

    hcl_content = """
    name = "example"
    count = 42
    enabled = true
    """

    # Parse the HCL content
    result = parse_hcl_to_cty(hcl_content)

    # Pretty print the result
    print("\nParsed CTY value:")
    pretty_print_cty(result)

    # Access individual values
    print(f"\nName: {result.value['name'].value}")
    print(f"Count: {result.value['count'].value}")
    print(f"Enabled: {result.value['enabled'].value}")


def example_lists() -> None:
    """Parse HCL with lists."""
    print("\n" + "=" * 60)
    print("Example 2: Lists")
    print("=" * 60)

    hcl_content = """
    tags = ["production", "backend", "api"]
    ports = [80, 443, 8080]
    """

    result = parse_hcl_to_cty(hcl_content)

    print("\nParsed CTY value:")
    pretty_print_cty(result)

    # Access list values
    print(f"\nTags: {[tag.value for tag in result.value['tags'].value]}")
    print(f"Ports: {[port.value for port in result.value['ports'].value]}")


def example_objects() -> None:
    """Parse HCL with nested objects."""
    print("\n" + "=" * 60)
    print("Example 3: Nested Objects")
    print("=" * 60)

    hcl_content = """
    server = {
      host = "localhost"
      port = 8080
    }

    database = {
      host = "db.example.com"
      port = 5432
      ssl  = true
    }
    """

    result = parse_hcl_to_cty(hcl_content)

    print("\nParsed CTY value:")
    pretty_print_cty(result)

    # Access nested values
    server = result.value["server"].value
    print(f"\nServer host: {server['host'].value}")
    print(f"Server port: {server['port'].value}")


def example_mixed_types() -> None:
    """Parse HCL with mixed nested types."""
    print("\n" + "=" * 60)
    print("Example 4: Mixed Nested Types")
    print("=" * 60)

    hcl_content = """
    service = {
      name = "api-service"
      replicas = 3
      ports = [8080, 8081]

      config = {
        timeout = 30
        retries = 3
      }
    }
    """

    result = parse_hcl_to_cty(hcl_content)

    print("\nParsed CTY value:")
    pretty_print_cty(result)


def main() -> None:
    """Run all basic parsing examples."""
    example_simple_values()
    example_lists()
    example_objects()
    example_mixed_types()

    print("\n" + "=" * 60)
    print("All basic parsing examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()

# 📄⚙️🔚
