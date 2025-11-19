#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Example 03: Automatic Type Inference

This example demonstrates how pyvider-hcl automatically infers
CTY types from HCL data when no schema is provided."""

from pyvider.hcl import parse_hcl_to_cty, pretty_print_cty


def example_primitive_inference() -> None:
    """Demonstrate inference of primitive types."""
    print("=" * 60)
    print("Example 1: Primitive Type Inference")
    print("=" * 60)

    hcl_content = """
    string_value = "hello"
    number_value = 42
    bool_value = true
    """

    result = parse_hcl_to_cty(hcl_content)

    print("\n📊 Types automatically inferred:")
    print(f"string_value → {result.value['string_value'].type}")
    print(f"number_value → {result.value['number_value'].type}")
    print(f"bool_value → {result.value['bool_value'].type}")

    pretty_print_cty(result)


def example_list_inference() -> None:
    """Demonstrate inference of list types."""
    print("\n" + "=" * 60)
    print("Example 2: List Type Inference")
    print("=" * 60)

    hcl_content = """
    string_list = ["a", "b", "c"]
    number_list = [1, 2, 3]
    mixed_list  = ["text", 123, true]
    """

    result = parse_hcl_to_cty(hcl_content)

    print("\n📊 List types inferred:")
    print(f"string_list → {result.value['string_list'].type}")
    print(f"number_list → {result.value['number_list'].type}")
    print(f"mixed_list → {result.value['mixed_list'].type}")

    pretty_print_cty(result)


def example_object_inference() -> None:
    """Demonstrate inference of object types."""
    print("\n" + "=" * 60)
    print("Example 3: Object Type Inference")
    print("=" * 60)

    hcl_content = """
    user = {
      name  = "Alice"
      age   = 30
      admin = true
    }

    config = {
      timeout = 30
      retries = 3
    }
    """

    result = parse_hcl_to_cty(hcl_content)

    print("\n📊 Object types inferred:")
    user_obj = result.value["user"]
    print(f"user → {user_obj.type}")
    print(f"  name: {user_obj.value['name'].type}")
    print(f"  age: {user_obj.value['age'].type}")
    print(f"  admin: {user_obj.value['admin'].type}")

    pretty_print_cty(result)


def example_complex_inference() -> None:
    """Demonstrate inference of complex nested structures."""
    print("\n" + "=" * 60)
    print("Example 4: Complex Structure Inference")
    print("=" * 60)

    hcl_content = """
    application = {
      name = "myapp"
      version = "1.0.0"

      servers = [
        {
          host = "server1"
          port = 8080
        },
        {
          host = "server2"
          port = 8081
        }
      ]

      features = {
        caching = true
        logging = true
      }
    }
    """

    result = parse_hcl_to_cty(hcl_content)

    print("\n📊 Complex structure - all types inferred automatically!")
    pretty_print_cty(result)


def example_when_to_use_schemas() -> None:
    """Explain when to use schemas vs inference."""
    print("\n" + "=" * 60)
    print("Guide: When to Use Schemas vs Inference")
    print("=" * 60)

    print("""
Use INFERENCE when:
  ✓ Exploring HCL data
  ✓ Prototyping
  ✓ Data structure is flexible
  ✓ Quick scripts and tools

Use SCHEMAS when:
  ✓ Production code
  ✓ Type safety is critical
  ✓ Clear validation requirements
  ✓ Need specific error messages
  ✓ API contracts and interfaces

Example: Schema provides type safety
""")

    from pyvider.cty import CtyNumber, CtyObject

    # With schema - catches type errors
    schema = CtyObject(
        {
            "port": CtyNumber(),  # Must be number
        }
    )

    try:
        hcl = 'port = "8080"'  # String instead of number
        parse_hcl_to_cty(hcl, schema=schema)
    except Exception as e:
        print(f"Schema caught error: {e}")

    # Without schema - accepts anything
    hcl = 'port = "8080"'
    result = parse_hcl_to_cty(hcl)
    print(f"\nInference accepted: port = {result.value['port'].value} (type: {result.value['port'].type})")


def main() -> None:
    """Run all type inference examples."""
    example_primitive_inference()
    example_list_inference()
    example_object_inference()
    example_complex_inference()
    example_when_to_use_schemas()

    print("\n" + "=" * 60)
    print("All type inference examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()

# 📄⚙️🔚
