#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Required-attribute enforcement for schema-validated HCL.

``pyvider-cty`` deliberately stopped rejecting null values for non-optional
object attributes: ``CtyObject.validate`` records the null and leaves
required-ness to the schema layer that owns the semantics. For HCL that layer
is this package, so a schema-validated parse re-applies the rule here.

Missing attributes are still rejected by ``pyvider-cty`` itself; only
explicitly-null ones reach this module.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any, cast

from pyvider.cty import CtyList, CtyMap, CtyObject, CtySet, CtyTuple, CtyValue


def _mapping(value: CtyValue[Any]) -> dict[str, Any]:
    """Read an object or map payload as a plain mapping."""
    return dict(cast("dict[str, Any]", value.value))


def _sequence(value: CtyValue[Any]) -> list[Any]:
    """Read a list, tuple, or set payload as a plain sequence."""
    return list(cast("Iterable[Any]", value.value))


def _child_values(value: CtyValue[Any]) -> list[tuple[str, Any]]:
    """Return ``(path_suffix, child)`` pairs for a container value.

    Set payloads are a ``frozenset`` in pyvider-cty 0.4.x and a sorted tuple in
    0.5.x; both are iterable, and sets have no stable index so their elements
    are addressed with ``[*]``.
    """
    vtype = value.type
    if isinstance(vtype, CtyObject):
        return [(f".{name}", child) for name, child in _mapping(value).items()]
    if isinstance(vtype, CtyMap):
        return [(f'["{key}"]', child) for key, child in _mapping(value).items()]
    if isinstance(vtype, CtyList | CtyTuple):
        return [(f"[{index}]", child) for index, child in enumerate(_sequence(value))]
    if isinstance(vtype, CtySet):
        return [("[*]", child) for child in _sequence(value)]
    return []


def _null_required_paths(value: Any, path: str, found: list[str]) -> None:
    """Walk ``value`` collecting paths of null non-optional object attributes."""
    if not isinstance(value, CtyValue) or value.is_null or value.is_unknown:
        return

    vtype = value.type
    if isinstance(vtype, CtyObject):
        optional = vtype.optional_attributes or frozenset()
        for name, child in _mapping(value).items():
            child_path = f"{path}.{name}" if path else name
            if isinstance(child, CtyValue) and child.is_null and name not in optional:
                found.append(child_path)
                continue
            _null_required_paths(child, child_path, found)
        return

    for suffix, child in _child_values(value):
        _null_required_paths(child, f"{path}{suffix}" if path else suffix.lstrip("."), found)


def null_required_attributes(value: CtyValue[Any]) -> list[str]:
    """Find attributes that are null but not declared optional.

    Args:
        value: A CTY value produced by validating against a schema.

    Returns:
        Dotted paths of null non-optional attributes, in document order. Empty
        when every required attribute carries a value.

    Example:
        >>> from pyvider.cty import CtyNumber, CtyObject, CtyString
        >>> schema = CtyObject({"name": CtyString(), "port": CtyNumber()})
        >>> null_required_attributes(schema.validate({"name": "x", "port": None}))
        ['port']
    """
    found: list[str] = []
    _null_required_paths(value, "", found)
    return found


# 📄⚙️🔚
