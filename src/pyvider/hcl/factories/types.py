#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""HCL type string parsing for Terraform type syntax."""

from __future__ import annotations

from collections.abc import Callable
import re
from typing import Any

from pyvider.cty import (
    CtyBool,
    CtyDynamic,
    CtyList,
    CtyMap,
    CtyNumber,
    CtyObject,
    CtySet,
    CtyString,
    CtyTuple,
    CtyType,
)
from pyvider.hcl.exceptions import HclTypeParsingError

PRIMITIVE_TYPE_MAP: dict[str, CtyType[Any]] = {
    "string": CtyString(),
    "number": CtyNumber(),
    "bool": CtyBool(),
    "any": CtyDynamic(),
}

COMPLEX_TYPE_REGEX = re.compile(r"^(list|set|map|object|tuple)\((.*)\)$", re.IGNORECASE | re.DOTALL)
OPTIONAL_TYPE_REGEX = re.compile(r"^optional\((.*)\)$", re.IGNORECASE | re.DOTALL)

# Bracket pairs that must stay balanced when splitting on top-level commas.
_OPENING_BRACKETS = "({["
_CLOSING_BRACKETS = ")}]"


def _split_top_level(text: str, context: str) -> list[str]:
    """Split ``text`` on commas that are not nested inside brackets.

    Args:
        text: Comma-separated fragment of a type string.
        context: The enclosing fragment, used in error messages.

    Returns:
        The stripped, non-empty parts.

    Raises:
        HclTypeParsingError: If a part is empty or a trailing comma is present.
    """
    parts: list[str] = []
    balance = 0
    start = 0

    for index, char in enumerate(text):
        if char in _OPENING_BRACKETS:
            balance += 1
        elif char in _CLOSING_BRACKETS:
            balance -= 1
        elif char == "," and balance == 0:
            part = text[start:index].strip()
            if not part:
                raise HclTypeParsingError(f"Empty attribute part found in '{context}'")
            parts.append(part)
            start = index + 1

    last_part = text[start:].strip()
    if last_part:
        parts.append(last_part)
    elif parts:
        raise HclTypeParsingError(f"Trailing comma found in attribute string: '{context}'")

    return parts


def _parse_element_type(inner_content: str, keyword: str) -> CtyType[Any]:
    """Parse the single element type of a ``list``/``set``/``map``."""
    if not inner_content:
        raise HclTypeParsingError(f"{keyword.capitalize()} type string is empty, e.g., '{keyword}()'")
    return parse_hcl_type_string(inner_content)


def _parse_list(inner_content: str) -> CtyType[Any]:
    return CtyList(element_type=_parse_element_type(inner_content, "list"))


def _parse_set(inner_content: str) -> CtyType[Any]:
    return CtySet(element_type=_parse_element_type(inner_content, "set"))


def _parse_map(inner_content: str) -> CtyType[Any]:
    return CtyMap(element_type=_parse_element_type(inner_content, "map"))


def _parse_tuple(inner_content: str) -> CtyType[Any]:
    """Parse ``tuple([type, ...])`` into a :class:`CtyTuple`."""
    if not inner_content.startswith("[") or not inner_content.endswith("]"):
        raise HclTypeParsingError(f"Tuple type string content must be enclosed in [], got: '{inner_content}'")
    elements_str = inner_content[1:-1].strip()
    if not elements_str:
        return CtyTuple(())
    element_types = tuple(parse_hcl_type_string(part) for part in _split_top_level(elements_str, elements_str))
    return CtyTuple(element_types)


def _parse_object(inner_content: str) -> CtyType[Any]:
    """Parse ``object({name = type, ...})`` into a :class:`CtyObject`."""
    if not inner_content.startswith("{") or not inner_content.endswith("}"):
        raise HclTypeParsingError(
            f"Object type string content must be enclosed in {{}}, got: '{inner_content}'"
        )

    attrs_str = inner_content[1:-1].strip()
    if not attrs_str:
        return CtyObject({})

    attributes, optional = _parse_object_attributes_str(attrs_str)
    return CtyObject(attributes, optional_attributes=optional)


COMPLEX_TYPE_PARSERS: dict[str, Callable[[str], CtyType[Any]]] = {
    "list": _parse_list,
    "set": _parse_set,
    "map": _parse_map,
    "tuple": _parse_tuple,
    "object": _parse_object,
}


def parse_hcl_type_string(type_str: str) -> CtyType[Any]:
    """Parse HCL type string into CTY type.

    Supports:
    - Primitives: string, number, bool, any
    - Collections: list(element_type), set(element_type), map(element_type)
    - Tuples: tuple([type, ...])
    - Objects: object({attr=type, ...}), including optional(type) attributes

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

    primitive = PRIMITIVE_TYPE_MAP.get(type_str.lower())
    if primitive is not None:
        return primitive

    match = COMPLEX_TYPE_REGEX.match(type_str)
    if not match:
        raise HclTypeParsingError(f"Unknown or malformed type string: '{type_str}'")

    return COMPLEX_TYPE_PARSERS[match.group(1).lower()](match.group(2).strip())


def _unwrap_optional(type_str: str) -> tuple[str, bool]:
    """Strip an ``optional(...)`` wrapper from an object attribute type.

    Terraform's two-argument form, ``optional(type, default)``, is accepted; the
    default is dropped because CTY object types carry no per-attribute defaults.

    Args:
        type_str: Attribute type fragment, possibly ``optional``-wrapped.

    Returns:
        A ``(type_string, is_optional)`` pair.

    Raises:
        HclTypeParsingError: If the wrapper holds no type.
    """
    match = OPTIONAL_TYPE_REGEX.match(type_str)
    if match is None:
        return type_str, False

    inner = match.group(1).strip()
    if not inner:
        raise HclTypeParsingError("Optional type string is empty, e.g., 'optional()'")

    parts = _split_top_level(inner, inner)
    if not parts:
        raise HclTypeParsingError("Optional type string is empty, e.g., 'optional()'")
    return parts[0], True


def _parse_object_attributes_str(attrs_str: str) -> tuple[dict[str, CtyType[Any]], frozenset[str]]:
    """Parse object attribute definitions from an HCL type string.

    Args:
        attrs_str: The contents of an ``object({...})`` declaration.

    Returns:
        A ``(attribute_types, optional_attribute_names)`` pair.
    """
    attributes: dict[str, CtyType[Any]] = {}
    optional: set[str] = set()

    for part in _split_top_level(attrs_str, attrs_str):
        name, type_str = _split_attr_part(part)
        unwrapped, is_optional = _unwrap_optional(type_str)
        attributes[name] = parse_hcl_type_string(unwrapped)
        if is_optional:
            optional.add(name)

    return attributes, frozenset(optional)


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
