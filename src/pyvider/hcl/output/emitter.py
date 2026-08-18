#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Emission of CTY values back into HCL text.

``python-hcl2`` 8.x added a write path (``hcl2.dumps``) whose input dicts follow
the same conventions its reader emits: a string literal is wrapped in quotes
(``'"web"'``), a bare ``'${...}'`` is an expression, and any other bare string
is an identifier. This module maps CTY values onto those conventions so a
parsed configuration can be rendered back out.

Everything is emitted as an attribute. A ``CtyValue`` carries no notion of HCL
blocks, so block structure cannot be recovered from one; callers who need
blocks should drive ``hcl2.dumps`` directly with ``__is_block__`` markers.
"""

from __future__ import annotations

from collections.abc import Iterable
from decimal import Decimal
import re
from typing import Any, cast

import hcl2

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
from pyvider.hcl.exceptions import HclError

# A string that is nothing but one interpolation is emitted as an expression, so
# that `${var.x}` survives a parse/emit round trip as HCL rather than becoming a
# quoted literal.
_WHOLE_INTERPOLATION_RE = re.compile(r"^\$\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}$", re.DOTALL)

# Characters that must be escaped inside an HCL quoted string literal. `${` is
# deliberately absent: parsed values keep interpolation markers verbatim, so
# emitting them unchanged is what round trips.
_STRING_ESCAPES = {
    "\\": "\\\\",
    '"': '\\"',
    "\n": "\\n",
    "\r": "\\r",
    "\t": "\\t",
}


class HclEmitError(HclError):
    """Raised when a CTY value cannot be represented as HCL."""


def _quote_string(value: str) -> str:
    """Wrap a string in the quoted-literal form ``hcl2.dumps`` expects."""
    escaped = "".join(_STRING_ESCAPES.get(char, char) for char in value)
    return f'"{escaped}"'


def _emit_string(value: str) -> str:
    """Emit a CTY string as either an expression or a quoted literal."""
    if _WHOLE_INTERPOLATION_RE.match(value):
        return value
    return _quote_string(value)


def _emit_number(value: Any) -> int | float:
    """Emit a CTY number as an ``int`` when integral, otherwise a ``float``.

    Non-integral values are narrowed to IEEE-754 doubles, which is the
    precision HCL consumers work with.
    """
    if isinstance(value, Decimal):
        if value == value.to_integral_value():
            return int(value)
        return float(value)
    if isinstance(value, bool):  # pragma: no cover - bools are CtyBool
        return int(value)
    return value if isinstance(value, int | float) else float(value)


def _sorted_set_items(value: CtyValue[Any]) -> list[Any]:
    """Emit set elements in a stable order.

    Set payloads are a ``frozenset`` in pyvider-cty 0.4.x and an already-sorted
    tuple in 0.5.x; sorting the rendered forms makes output deterministic on
    both.
    """
    items = cast("Iterable[Any]", value.value)
    return sorted((cty_to_hcl_data(item) for item in items), key=repr)


def _emit_container(value: CtyValue[Any]) -> Any:
    """Emit a collection or structural CTY value."""
    vtype = value.type
    if isinstance(vtype, CtyObject | CtyMap):
        mapping = cast("dict[str, Any]", value.value)
        return {key: cty_to_hcl_data(item) for key, item in mapping.items()}
    if isinstance(vtype, CtyList | CtyTuple):
        return [cty_to_hcl_data(item) for item in cast("Iterable[Any]", value.value)]
    return _sorted_set_items(value)


def cty_to_hcl_data(value: Any) -> Any:
    """Convert a CTY value into a ``hcl2.dumps``-compatible Python structure.

    Args:
        value: The CTY value to convert. Plain Python values are passed through,
            which is what nested payloads of a partially-unwrapped value look
            like.

    Returns:
        A structure using python-hcl2's serialization conventions.

    Raises:
        HclEmitError: If the value is unknown or carries marks, neither of which
            has an HCL representation.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.marks:
        raise HclEmitError(
            "Cannot emit a marked CTY value as HCL; strip marks before emitting "
            f"(marks: {sorted(str(mark) for mark in value.marks)})"
        )
    if value.is_unknown:
        raise HclEmitError("Cannot emit an unknown CTY value as HCL")
    if value.is_null:
        return None

    vtype = value.type
    if isinstance(vtype, CtyDynamic):
        return cty_to_hcl_data(value.value)
    if isinstance(vtype, CtyString):
        return _emit_string(str(value.value))
    if isinstance(vtype, CtyBool):
        return bool(value.value)
    if isinstance(vtype, CtyNumber):
        return _emit_number(value.value)
    if isinstance(vtype, CtyObject | CtyMap | CtyList | CtyTuple | CtySet):
        return _emit_container(value)

    raise HclEmitError(f"Cannot emit CTY type {vtype} as HCL")


def cty_to_hcl(value: CtyValue[Any]) -> str:
    """Render a CTY object or map as HCL text.

    Args:
        value: An object- or map-typed CTY value whose attributes become the
            top-level HCL body.

    Returns:
        Formatted HCL text, terminated by a newline.

    Raises:
        HclEmitError: If the value is not a body-shaped value, or holds
            something with no HCL representation.

    Example:
        >>> from pyvider.hcl import parse_hcl_to_cty
        >>> print(cty_to_hcl(parse_hcl_to_cty('name = "x"')), end="")
        name = "x"
    """
    if not isinstance(value, CtyValue) or not isinstance(value.type, CtyObject | CtyMap | CtyDynamic):
        raise HclEmitError("cty_to_hcl requires an object- or map-typed CtyValue")

    data = cty_to_hcl_data(value)
    if not isinstance(data, dict):
        raise HclEmitError("cty_to_hcl requires a CtyValue that renders to an HCL body")

    try:
        rendered: str = hcl2.dumps(data)
    except Exception as e:
        raise HclEmitError(f"Failed to render CTY value as HCL: {e}") from e
    return rendered


# 📄⚙️🔚
