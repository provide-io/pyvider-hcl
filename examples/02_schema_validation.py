#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Example 02: Schema Validation

This example demonstrates how to validate HCL data against
CTY type schemas for type safety."""

from pyvider.cty import CtyBool, CtyList, CtyNumber, CtyObject, CtyString
from pyvider.hcl import HclParsingError, parse_hcl_to_cty, pretty_print_cty


def example_simple_schema() -> None:
    """Validate HCL against a simple schema."""
    print("=" * 60)
    print("Example 1: Simple Schema Validation")
    print("=" * 60)

    # Define a schema
    schema = CtyObject(
        {
            "name": CtyString(),
            "age": CtyNumber(),
            "active": CtyBool(),
        }
    )

    # Valid HCL that matches the schema
    hcl_content = """
    name = "Alice"
    age = 30
    active = true
    """

    result = parse_hcl_to_cty(hcl_content, schema=schema)

    print("\nParsed value:")
    pretty_print_cty(result)


def example_validation_failure() -> None:
    """Demonstrate schema validation failure."""
    print("\n" + "=" * 60)
    print("Example 2: Schema Validation Failure")
    print("=" * 60)

    schema = CtyObject(
        {
            "name": CtyString(),
            "age": CtyNumber(),
        }
    )

    # Invalid HCL - age is a string instead of number
    invalid_hcl = """
    name = "Bob"
    age = "thirty"
    """

    try:
        parse_hcl_to_cty(invalid_hcl, schema=schema)
    except HclParsingError as e:
        print("\n❌ Validation failed as expected:")
        print(f"Error: {e}")


def example_nested_schema() -> None:
    """Validate nested objects with schema."""
    print("\n" + "=" * 60)
    print("Example 3: Nested Object Schema")
    print("=" * 60)

    schema = CtyObject(
        {
            "service": CtyObject(
                {
                    "name": CtyString(),
                    "port": CtyNumber(),
                    "ssl": CtyBool(),
                }
            )
        }
    )

    hcl_content = """
    service = {
      name = "api"
      port = 8080
      ssl  = true
    }
    """

    result = parse_hcl_to_cty(hcl_content, schema=schema)

    print("\nParsed value:")
    pretty_print_cty(result)


def example_list_schema() -> None:
    """Validate lists with schema."""
    print("\n" + "=" * 60)
    print("Example 4: List Schema Validation")
    print("=" * 60)

    schema = CtyObject(
        {
            "users": CtyList(
                element_type=CtyObject(
                    {
                        "name": CtyString(),
                        "age": CtyNumber(),
                    }
                )
            )
        }
    )

    hcl_content = """
    users = [
      {
        name = "Alice"
        age  = 30
      },
      {
        name = "Bob"
        age  = 25
      }
    ]
    """

    result = parse_hcl_to_cty(hcl_content, schema=schema)

    print("\nParsed value:")
    pretty_print_cty(result)


def main() -> None:
    """Run all schema validation examples."""
    example_simple_schema()
    example_validation_failure()
    example_nested_schema()
    example_list_schema()

    print("\n" + "=" * 60)
    print("All schema validation examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()

# 📄⚙️🔚
