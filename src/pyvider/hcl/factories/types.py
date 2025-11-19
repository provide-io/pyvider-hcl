#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""HCL type string parsing for Terraform type syntax."""

from __future__ import annotations

import re
from typing import Any

from pyvider.cty import CtyBool, CtyDynamic, CtyList, CtyMap, CtyNumber, CtyObject, CtyString, CtyType


class HclTypeParsingError(ValueError):
    """Custom exception for errors during HCL type string parsing."""


PRIMITIVE_TYPE_MAP: dict[str, CtyType[Any]] = {
    "string": CtyString(),
    "number": CtyNumber(),
    "bool": CtyBool(),
    "any": CtyDynamic(),
}

COMPLEX_TYPE_REGEX = re.compile(r"^(list|object|map)\((.*)\)$", re.IGNORECASE | re.DOTALL)


def parse_hcl_type_string(type_str: str) -> CtyType[Any]:  # noqa: C901
    """Parse HCL type string into CTY type.

    Supports:
    - Primitives: string, number, bool, any
    - Lists: list(element_type)
    - Maps: map(element_type)
    - Objects: object({attr=type, ...})

    Args:
        type_str: HCL type string (e.g., "list(string)", "object({name=string})")

    Returns:
        Corresponding CTY type

    Raises:
        HclTypeParsingError: If type string is malformed

    Example:
        >>> parse_hcl_type_string("list(string)")
        CtyList(element_type=CtyString())
    """
    type_str = type_str.strip()

    if type_str.lower() in PRIMITIVE_TYPE_MAP:
        return PRIMITIVE_TYPE_MAP[type_str.lower()]

    match = COMPLEX_TYPE_REGEX.match(type_str)
    if not match:
        raise HclTypeParsingError(f"Unknown or malformed type string: '{type_str}'")

    type_keyword = match.group(1).lower()
    inner_content = match.group(2).strip()

    if type_keyword == "list":
        if not inner_content:
            raise HclTypeParsingError("List type string is empty, e.g., 'list()'")
        element_type = parse_hcl_type_string(inner_content)
        return CtyList(element_type=element_type)

    if type_keyword == "map":
        if not inner_content:
            raise HclTypeParsingError("Map type string is empty, e.g., 'map()'")
        element_type = parse_hcl_type_string(inner_content)
        return CtyMap(element_type=element_type)

    if type_keyword == "object":
        if not inner_content.startswith("{") or not inner_content.endswith("}"):
            raise HclTypeParsingError(
                f"Object type string content must be enclosed in {{}}, got: '{inner_content}'"
            )
        if inner_content == "{}":
            return CtyObject({})

        attrs_str = inner_content[1:-1].strip()
        if not attrs_str:
            return CtyObject({})

        attributes = _parse_object_attributes_str(attrs_str)
        return CtyObject(attributes)

    raise HclTypeParsingError(f"Unhandled type keyword: '{type_keyword}'")


def _parse_object_attributes_str(attrs_str: str) -> dict[str, CtyType[Any]]:
    """Parse object attribute definitions from HCL type string."""
    attributes: dict[str, CtyType[Any]] = {}
    balance = 0
    last_break = 0

    for i, char in enumerate(attrs_str):
        if char in "({":
            balance += 1
        elif char in ")}":
            balance -= 1
        elif char == "," and balance == 0:
            part = attrs_str[last_break:i].strip()
            if not part:
                raise HclTypeParsingError(f"Empty attribute part found in '{attrs_str}'")
            name, type_str = _split_attr_part(part)
            attributes[name] = parse_hcl_type_string(type_str)
            last_break = i + 1

    last_part = attrs_str[last_break:].strip()
    if last_part:
        name, type_str = _split_attr_part(last_part)
        attributes[name] = parse_hcl_type_string(type_str)
    elif attrs_str.strip().endswith(","):
        raise HclTypeParsingError(f"Trailing comma found in attribute string: '{attrs_str}'")

    return attributes


def _split_attr_part(part: str) -> tuple[str, str]:
    """Split 'name=type' attribute definition."""
    equal_sign_pos = part.find("=")
    if equal_sign_pos == -1:
        raise HclTypeParsingError(f"Malformed attribute part (missing '='): '{part}'")

    name = part[:equal_sign_pos].strip()
    type_str = part[equal_sign_pos + 1 :].strip()

    if not name or not type_str:
        raise HclTypeParsingError(f"Invalid attribute name or type in part: '{part}'")

    return name, type_str


# 📄⚙️🔚
