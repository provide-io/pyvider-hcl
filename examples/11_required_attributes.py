#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Example 11: Required Attributes

pyvider-cty deliberately stops short of rejecting a null value for a non-optional
object attribute -- it records the null and leaves required-ness to the schema
layer that owns the semantics. For HCL that layer is this package, so a
schema-validated parse re-applies the rule, and `null_required_attributes`
exposes the same check for values you validate yourself."""

from pyvider.cty import CtyList, CtyNumber, CtyObject, CtyString
from pyvider.hcl import (
    HclParsingError,
    load_hcl_data,
    null_required_attributes,
    parse_hcl_to_cty,
)

SERVER_SCHEMA = CtyObject(
    {
        "name": CtyString(),
        "port": CtyNumber(),
        "region": CtyString(),
    },
    optional_attributes=frozenset({"region"}),
)


def example_the_parser_enforces_it() -> None:
    """A schema-validated parse rejects an explicit null on a required attribute."""
    print("=" * 60)
    print("Example 1: The Parser Enforces It")
    print("=" * 60)

    ok = parse_hcl_to_cty('name = "web"\nport = 8080\nregion = "us-west-2"\n', schema=SERVER_SCHEMA)
    print(f"Valid config parses: name = {ok['name'].value!r}")

    try:
        parse_hcl_to_cty('name = "web"\nport = null\nregion = "us-west-2"\n', schema=SERVER_SCHEMA)
    except HclParsingError as e:
        print(f"Explicit null rejected: {e}")


def example_optional_attributes_may_be_null() -> None:
    """An attribute named in `optional_attributes` is allowed to be null."""
    print("\n" + "=" * 60)
    print("Example 2: Optional Attributes May Be Null")
    print("=" * 60)

    value = parse_hcl_to_cty('name = "web"\nport = 8080\nregion = null\n', schema=SERVER_SCHEMA)
    print(f"region is null: {value['region'].is_null}")
    print(f"Offending attributes: {null_required_attributes(value)}")
    print("\n`region` is declared optional, so its null is a value, not an omission.")


def example_null_is_not_missing() -> None:
    """Two different failures, reported differently."""
    print("\n" + "=" * 60)
    print("Example 3: Null Is Not the Same as Missing")
    print("=" * 60)

    # A *missing* attribute never reaches this package's check -- pyvider-cty
    # rejects it during validation.
    try:
        parse_hcl_to_cty('name = "web"\nregion = "us-west-2"\n', schema=SERVER_SCHEMA)
    except HclParsingError as e:
        print(f"  port omitted:      {e}")

    # An *explicit null* validates cleanly in cty, then fails this check.
    try:
        parse_hcl_to_cty('name = "web"\nport = null\nregion = "us-west-2"\n', schema=SERVER_SCHEMA)
    except HclParsingError as e:
        print(f"  port set to null:  {e}")


def example_collecting_every_offender() -> None:
    """Validate yourself when you want the full list instead of an exception."""
    print("\n" + "=" * 60)
    print("Example 4: Collecting Every Offender")
    print("=" * 60)

    source = "name = null\nport = null\nregion = null\n"

    # `parse_hcl_to_cty` raises on the first check, reporting all offenders in one
    # message. Validating the raw data yourself gives you the list to work with.
    value = SERVER_SCHEMA.validate(load_hcl_data(source))
    offenders = null_required_attributes(value)

    print(f"Null required attributes: {offenders}")
    for path in offenders:
        print(f"  {path} must be set")
    print("\n`region` is absent from the list because it is declared optional.")


def example_nested_paths() -> None:
    """Offenders are reported by dotted path, wherever they are nested."""
    print("\n" + "=" * 60)
    print("Example 5: Nested Paths")
    print("=" * 60)

    schema = CtyObject(
        {
            "servers": CtyList(
                element_type=CtyObject({"host": CtyString(), "port": CtyNumber()}),
            ),
            "defaults": CtyObject({"region": CtyString()}),
        }
    )
    source = """servers = [{ host = "a", port = 1 }, { host = null, port = null }]
defaults = { region = null }
"""

    value = schema.validate(load_hcl_data(source))
    for path in null_required_attributes(value):
        print(f"  {path}")

    print("\nList and tuple elements are indexed, map entries are keyed, and set")
    print("elements use `[*]` because a set has no stable index.")


def main() -> None:
    """Run all required-attribute examples."""
    example_the_parser_enforces_it()
    example_optional_attributes_may_be_null()
    example_null_is_not_missing()
    example_collecting_every_offender()
    example_nested_paths()

    print("\n" + "=" * 60)
    print("All required-attribute examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()

# 📄⚙️🔚
