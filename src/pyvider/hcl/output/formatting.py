#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""CTY value formatting and pretty printing."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any, cast

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
    CtyValue,
)

INDENT_STEP = 2

# Rendered stand-ins for values that carry no payload to print.
NULL_REPR = "null"
UNKNOWN_REPR = "(unknown)"


def _as_cty_value(item: Any, vtype: Any) -> CtyValue[Any]:
    """Wrap a raw payload in a CtyValue when it is not one already.

    Container payloads normally hold CtyValues, but some pyvider-cty paths leave
    raw Python values in place, so both shapes are handled.
    """
    if isinstance(item, CtyValue):
        return item
    return CtyValue(vtype=vtype, value=item)


def _format_marks(value: CtyValue[Any]) -> str:
    """Render a value's marks as a trailing annotation, if it carries any."""
    if not value.marks:
        return ""
    marks = ", ".join(sorted(str(mark) for mark in value.marks))
    return f" # marks: {marks}"


def _join_entries(entries: list[str], open_char: str, close_char: str, indent: int) -> str:
    """Assemble rendered entries into a bracketed, indented block."""
    if not entries:
        return f"{open_char}{close_char}"
    pad = " " * (indent + INDENT_STEP)
    body = ",\n".join(f"{pad}{entry}" for entry in entries)
    return f"{open_char}\n{body}\n{' ' * indent}{close_char}"


def _element_type(vtype: Any, index: int) -> Any:
    """Return the declared type of the element at ``index``."""
    if isinstance(vtype, CtyTuple):
        return vtype.element_types[index]
    return vtype.element_type


def _format_mapping(value: CtyValue[Any], indent: int) -> str:
    """Render an object or map value."""
    vtype = value.type
    items = dict(cast("dict[str, Any]", value.value))
    entries = []
    for key, item in items.items():
        if isinstance(vtype, CtyObject):
            item_type = vtype.attribute_types[key]
        else:
            item_type = cast(CtyMap[Any], vtype).element_type
        rendered = _pretty_print_cty_recursive(_as_cty_value(item, item_type), indent + INDENT_STEP)
        entries.append(f'"{key}": {rendered}')
    return _join_entries(entries, "{", "}", indent)


def _format_sequence(value: CtyValue[Any], indent: int) -> str:
    """Render a list, tuple, or set value."""
    vtype = value.type
    items = list(cast("Iterable[Any]", value.value))
    entries = []
    for index, item in enumerate(items):
        item_type = _element_type(vtype, index)
        entries.append(_pretty_print_cty_recursive(_as_cty_value(item, item_type), indent + INDENT_STEP))
    if isinstance(vtype, CtySet):
        entries.sort()
    return _join_entries(entries, "[", "]", indent)


def _format_scalar(value: CtyValue[Any]) -> str:
    """Render a primitive or dynamic value."""
    vtype = value.type
    if isinstance(vtype, CtyString):
        return f'"{value.value}"'
    if isinstance(vtype, CtyBool):
        return str(value.value).lower()
    if isinstance(vtype, CtyNumber):
        return str(value.value)
    if isinstance(vtype, CtyDynamic) and isinstance(value.value, CtyValue):
        return _format_scalar(value.value)
    return str(value.value)


def _pretty_print_cty_recursive(value: CtyValue[Any], indent: int) -> str:
    """Recursive helper for pretty printing CtyValue objects.

    Args:
        value: CTY value to format
        indent: Current indentation level

    Returns:
        Formatted string representation
    """
    suffix = _format_marks(value)

    if value.is_unknown:
        return f"{UNKNOWN_REPR}{suffix}"
    if value.is_null:
        return f"{NULL_REPR}{suffix}"

    vtype = value.type
    if isinstance(vtype, CtyDynamic) and isinstance(value.value, CtyValue):
        return f"{_pretty_print_cty_recursive(value.value, indent)}{suffix}"
    if isinstance(vtype, CtyObject | CtyMap):
        return f"{_format_mapping(value, indent)}{suffix}"
    if isinstance(vtype, CtyList | CtyTuple | CtySet):
        return f"{_format_sequence(value, indent)}{suffix}"
    return f"{_format_scalar(value)}{suffix}"


def format_cty(value: CtyValue[Any]) -> str:
    """Format a CTY value as an indented, human-readable string.

    Args:
        value: CTY value to format.

    Returns:
        The formatted representation, without a trailing newline.

    Example:
        >>> from pyvider.cty import CtyString
        >>> format_cty(CtyString().validate("test"))
        '"test"'
    """
    return _pretty_print_cty_recursive(value, 0)


def pretty_print_cty(value: CtyValue[Any]) -> None:
    """Pretty print a CTY value to stdout.

    Args:
        value: CTY value to print

    Example:
        >>> from pyvider.cty import CtyString
        >>> val = CtyString().validate("test")
        >>> pretty_print_cty(val)
        "test"
    """
    print(format_cty(value))


# 📄⚙️🔚
