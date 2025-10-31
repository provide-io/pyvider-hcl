#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Example 07: Error Handling

This example demonstrates proper error handling when
parsing HCL and using factory functions."""

from pyvider.cty import CtyNumber, CtyObject
from pyvider.hcl import HclParsingError, parse_hcl_to_cty
from pyvider.hcl.factories import HclFactoryError


def example_syntax_error() -> None:
    """Handle HCL syntax errors."""
    print("=" * 60)
    print("Example 1: Handling Syntax Errors")
    print("=" * 60)

    invalid_hcl = """
    name = "test"
    count =
    """  # Missing value

    try:
        parse_hcl_to_cty(invalid_hcl)
    except HclParsingError as e:
        print("\n❌ Caught HCL parsing error:")
        print(f"Error message: {e.message}")


def example_schema_validation_error() -> None:
    """Handle schema validation errors."""
    print("\n" + "=" * 60)
    print("Example 2: Handling Schema Validation Errors")
    print("=" * 60)

    schema = CtyObject(
        {
            "port": CtyNumber(),  # Expecting number
        }
    )

    invalid_hcl = 'port = "8080"'  # String instead of number

    try:
        parse_hcl_to_cty(invalid_hcl, schema=schema)
    except HclParsingError as e:
        print("\n❌ Caught validation error:")
        print(f"Error: {e}")
        print("\n💡 Tip: Check that your HCL types match the schema!")


def example_factory_error() -> None:
    """Handle factory function errors."""
    print("\n" + "=" * 60)
    print("Example 3: Handling Factory Errors")
    print("=" * 60)

    from pyvider.hcl import create_variable_cty

    try:
        # Invalid: variable name must be a valid identifier
        create_variable_cty(
            name="invalid-name-with-dashes",  # Dashes not allowed
            type_str="string",
        )
    except HclFactoryError as e:
        print("\n❌ Caught factory error:")
        print(f"Error: {e}")
        print("\n💡 Tip: Variable names must be valid Python identifiers!")


def example_type_mismatch_error() -> None:
    """Handle type mismatch in factory defaults."""
    print("\n" + "=" * 60)
    print("Example 4: Handling Type Mismatch Errors")
    print("=" * 60)

    from pyvider.hcl import create_variable_cty

    try:
        # Type mismatch: default is string but type is number
        create_variable_cty(
            name="port",
            type_str="number",
            default_py="8080",  # String instead of number
        )
    except HclFactoryError as e:
        print("\n❌ Caught type mismatch error:")
        print(f"Error: {e}")
        print("\n💡 Tip: Ensure default values match the declared type!")


def example_graceful_recovery() -> None:
    """Demonstrate graceful error recovery."""
    print("\n" + "=" * 60)
    print("Example 5: Graceful Error Recovery")
    print("=" * 60)

    configs = [
        'valid = "config"',
        "invalid = ",  # Syntax error
        "another_valid = 42",
    ]

    results = []
    errors = []

    for i, config in enumerate(configs, 1):
        try:
            result = parse_hcl_to_cty(config)
            results.append(result)
        except HclParsingError as e:
            errors.append((i, str(e)))
            print(f"❌ Config {i}: Failed to parse")

    print("\n📊 Summary:")
    print(f"  Successful: {len(results)}")
    print(f"  Failed: {len(errors)}")

    if errors:
        print("\n❌ Errors:")
        for idx, error in errors:
            print(f"  Config {idx}: {error}")


def example_with_context() -> None:
    """Handle errors with context information."""
    print("\n" + "=" * 60)
    print("Example 6: Errors with Context")
    print("=" * 60)

    from pathlib import Path

    from pyvider.hcl import parse_with_context

    content = """
    name = "test"
    value =
    """  # Syntax error

    try:
        parse_with_context(content, source_file=Path("config.hcl"))
    except HclParsingError as e:
        print("\n❌ Caught parsing error with context:")
        print(f"Message: {e.message}")
        if e.source_file:
            print(f"File: {e.source_file}")
        print("\n💡 Context helps locate errors in multi-file projects!")


def main() -> None:
    """Run all error handling examples."""
    example_syntax_error()
    example_schema_validation_error()
    example_factory_error()
    example_type_mismatch_error()
    example_graceful_recovery()
    example_with_context()

    print("\n" + "=" * 60)
    print("All error handling examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()

# 📄⚙️🔚
