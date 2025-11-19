#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""CTY value formatting and pretty printing."""

from __future__ import annotations

from typing import Any, cast

from pyvider.cty import (
    CtyBool,
    CtyDynamic,
    CtyList,
    CtyMap,
    CtyNumber,
    CtyObject,
    CtyString,
    CtyTuple,
    CtyValue,
)


def _pretty_print_cty_recursive(value: CtyValue[Any], indent: int) -> str:  # noqa: C901
    """Recursive helper for pretty printing CtyValue objects.

    Args:
        value: CTY value to format
        indent: Current indentation level

    Returns:
        Formatted string representation
    """
    if isinstance(value.type, CtyObject):
        s = "{\n"
        obj_value = cast(dict[str, Any], value.value)
        for i, (key, val) in enumerate(obj_value.items()):
            s += " " * (indent + 2) + f'"{key}": '
            # Check if val is already a CtyValue or needs to be wrapped
            if isinstance(val, CtyValue):
                s += _pretty_print_cty_recursive(val, indent + 2)
            else:
                s += _pretty_print_cty_recursive(
                    CtyValue(vtype=value.type.attribute_types[key], value=val), indent + 2
                )
            if i < len(obj_value) - 1:
                s += ",\n"
            else:
                s += "\n"
        s += " " * indent + "}"
        return s

    elif isinstance(value.type, CtyList):
        s = "[\n"
        list_value = cast(list[Any], value.value)
        for i, item in enumerate(list_value):
            s += " " * (indent + 2)
            # Check if item is already a CtyValue or needs to be wrapped
            if isinstance(item, CtyValue):
                s += _pretty_print_cty_recursive(item, indent + 2)
            else:
                s += _pretty_print_cty_recursive(
                    CtyValue(vtype=value.type.element_type, value=item), indent + 2
                )
            if i < len(list_value) - 1:
                s += ",\n"
            else:
                s += "\n"
        s += " " * indent + "]"
        return s

    elif isinstance(value.type, CtyMap):
        s = "{\n"
        map_value = cast(dict[str, Any], value.value)
        for i, (key, val) in enumerate(map_value.items()):
            s += " " * (indent + 2) + f'"{key}": '
            # Check if val is already a CtyValue or needs to be wrapped
            if isinstance(val, CtyValue):
                s += _pretty_print_cty_recursive(val, indent + 2)
            else:
                s += _pretty_print_cty_recursive(
                    CtyValue(vtype=value.type.element_type, value=val), indent + 2
                )
            if i < len(map_value) - 1:
                s += ",\n"
            else:
                s += "\n"
        s += " " * indent + "}"
        return s

    elif isinstance(value.type, CtyTuple):
        s = "[\n"
        tuple_value = cast(list[Any], value.value)
        for i, item in enumerate(tuple_value):
            s += " " * (indent + 2)
            # Check if item is already a CtyValue or needs to be wrapped
            if isinstance(item, CtyValue):
                s += _pretty_print_cty_recursive(item, indent + 2)
            else:
                s += _pretty_print_cty_recursive(
                    CtyValue(vtype=value.type.element_types[i], value=item), indent + 2
                )
            if i < len(tuple_value) - 1:
                s += ",\n"
            else:
                s += "\n"
        s += " " * indent + "]"
        return s

    elif isinstance(value.type, CtyString):
        return f'"{value.value}"'
    elif isinstance(value.type, CtyNumber):
        return str(value.value)
    elif isinstance(value.type, CtyBool):
        return str(value.value).lower()
    elif isinstance(value.type, CtyDynamic):
        return str(value.value)
    else:
        return str(value.value)


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
    print(_pretty_print_cty_recursive(value, 0))


# 📄⚙️🔚
