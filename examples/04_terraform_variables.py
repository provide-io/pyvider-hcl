#!/usr/bin/env python3
"""Example 04: Terraform Variables

This example demonstrates how to create Terraform variable
structures using the factory functions.
"""

from pyvider.hcl import create_variable_cty, pretty_print_cty


def example_simple_variable() -> None:
    """Create a simple string variable."""
    print("=" * 60)
    print("Example 1: Simple String Variable")
    print("=" * 60)

    variable = create_variable_cty(
        name="region",
        type_str="string",
        default_py="us-west-2",
        description="AWS region for deployment",
    )

    print("\n✅ Created Terraform variable structure:")
    pretty_print_cty(variable)


def example_number_variable() -> None:
    """Create a number variable."""
    print("\n" + "=" * 60)
    print("Example 2: Number Variable")
    print("=" * 60)

    variable = create_variable_cty(
        name="instance_count",
        type_str="number",
        default_py=3,
        description="Number of instances to create",
    )

    print("\n✅ Created number variable:")
    pretty_print_cty(variable)


def example_sensitive_variable() -> None:
    """Create a sensitive variable (for secrets)."""
    print("\n" + "=" * 60)
    print("Example 3: Sensitive Variable")
    print("=" * 60)

    variable = create_variable_cty(
        name="api_key",
        type_str="string",
        description="API key for external service",
        sensitive=True,  # Mark as sensitive
    )

    print("\n✅ Created sensitive variable (no default):")
    pretty_print_cty(variable)


def example_list_variable() -> None:
    """Create a list variable."""
    print("\n" + "=" * 60)
    print("Example 4: List Variable")
    print("=" * 60)

    variable = create_variable_cty(
        name="availability_zones",
        type_str="list(string)",
        default_py=["us-west-2a", "us-west-2b", "us-west-2c"],
        description="List of availability zones",
    )

    print("\n✅ Created list variable:")
    pretty_print_cty(variable)


def example_object_variable() -> None:
    """Create an object variable."""
    print("\n" + "=" * 60)
    print("Example 5: Object Variable")
    print("=" * 60)

    variable = create_variable_cty(
        name="server_config",
        type_str="object({host=string, port=number})",
        default_py={
            "host": "localhost",
            "port": 8080,
        },
        description="Server configuration",
    )

    print("\n✅ Created object variable:")
    pretty_print_cty(variable)


def example_nullable_variable() -> None:
    """Create a nullable variable."""
    print("\n" + "=" * 60)
    print("Example 6: Nullable Variable")
    print("=" * 60)

    variable = create_variable_cty(
        name="optional_tag",
        type_str="string",
        default_py=None,
        nullable=True,
        description="Optional tag for resources",
    )

    print("\n✅ Created nullable variable:")
    pretty_print_cty(variable)


def example_complex_object_variable() -> None:
    """Create a complex nested object variable."""
    print("\n" + "=" * 60)
    print("Example 7: Complex Object Variable")
    print("=" * 60)

    variable = create_variable_cty(
        name="database_config",
        type_str="object({host=string, port=number, ssl=bool, pool=object({min=number, max=number})})",
        default_py={
            "host": "db.example.com",
            "port": 5432,
            "ssl": True,
            "pool": {
                "min": 5,
                "max": 20,
            },
        },
        description="Database configuration with connection pool settings",
    )

    print("\n✅ Created complex object variable:")
    pretty_print_cty(variable)


def main() -> None:
    """Run all Terraform variable examples."""
    example_simple_variable()
    example_number_variable()
    example_sensitive_variable()
    example_list_variable()
    example_object_variable()
    example_nullable_variable()
    example_complex_object_variable()

    print("\n" + "=" * 60)
    print("All Terraform variable examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
