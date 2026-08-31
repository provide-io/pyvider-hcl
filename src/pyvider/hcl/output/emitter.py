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

``cty_to_hcl`` emits attributes, because that is all a ``CtyValue`` can tell us:
nothing in one records that it was written as a block rather than as an object.
``cty_to_hcl_block`` takes that missing piece -- the block type and its labels --
from the caller instead of guessing at it.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from decimal import Decimal
import re
from typing import Any, cast

import hcl2
from hcl2.const import IS_BLOCK

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
from pyvider.hcl.exceptions import HclEmitError

# A string that is nothing but one interpolation is emitted as an expression, so
# that `${var.x}` survives a parse/emit round trip as HCL rather than becoming a
# quoted literal. `hcl2.utils.is_dollar_string` tests only that the string starts
# with `${` and ends with `}`, which also accepts `"${a} ${b}"` -- two
# interpolations, which is a template. Emitting that bare produces `x = ${a}
# ${b}`, which is not valid HCL, so the whole string has to be one interpolation.
_WHOLE_INTERPOLATION_RE = re.compile(r"^\$\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}$", re.DOTALL)

# An HCL identifier, which is what a block type and an unquoted label must be.
# Emitting anything else would produce text this package could not parse back.
_IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_-]*$")

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


def cty_to_hcl_block_data(
    block_type: str,
    labels: Sequence[str],
    body: CtyValue[Any],
) -> dict[str, Any]:
    """Build the ``hcl2.dumps`` structure for one HCL block.

    Args:
        block_type: The block's type, e.g. ``"resource"``. Must be an HCL
            identifier.
        labels: The block's labels, e.g. ``("aws_instance", "web")``. Empty for
            a block that takes none, such as ``locals``.
        body: An object- or map-typed CTY value holding the block's attributes.

    Returns:
        A structure using python-hcl2's conventions, carrying the
        ``__is_block__`` marker that makes ``hcl2.dumps`` render a block rather
        than an attribute. Merge several before rendering to emit them together.

    Raises:
        HclEmitError: If the block type is not an identifier, a label is not a
            string, or the body has no HCL representation.

    Example:
        >>> from pyvider.hcl import parse_hcl_to_cty
        >>> data = cty_to_hcl_block_data(
        ...     "resource", ("aws_instance", "web"), parse_hcl_to_cty('ami = "a"')
        ... )
        >>> data["resource"][0]['"aws_instance"']['"web"']["ami"]
        '"a"'
    """
    if not _IDENTIFIER_RE.match(block_type):
        raise HclEmitError(f"Block type must be an HCL identifier, got {block_type!r}")

    for label in labels:
        if not isinstance(label, str):
            raise HclEmitError(f"Block labels must be strings, got {label!r}")

    rendered = cty_to_hcl_data(body)
    if not isinstance(rendered, dict):
        raise HclEmitError("A block body must be an object- or map-typed CtyValue")
    if IS_BLOCK in rendered:
        raise HclEmitError(f"A block body cannot carry its own {IS_BLOCK!r} key")

    # The marker sits on the innermost body, which is how hcl2.dumps tells the
    # label levels apart from an attribute that happens to hold an object.
    nested: dict[str, Any] = {**rendered, IS_BLOCK: True}
    for label in reversed(list(labels)):
        # Quoted, because an unquoted label emits as a bare identifier, which
        # Terraform rejects.
        nested = {_quote_string(label): nested}
    return {block_type: [nested]}


def cty_to_hcl_block(
    block_type: str,
    labels: Sequence[str],
    body: CtyValue[Any],
) -> str:
    """Render one HCL block as text.

    Args:
        block_type: The block's type, e.g. ``"resource"``.
        labels: The block's labels, e.g. ``("aws_instance", "web")``.
        body: An object- or map-typed CTY value holding the block's attributes.

    Returns:
        Formatted HCL text, terminated by a newline.

    Raises:
        HclEmitError: If the block cannot be represented as HCL.

    Example:
        >>> from pyvider.hcl import parse_hcl_to_cty
        >>> print(cty_to_hcl_block("locals", (), parse_hcl_to_cty('a = 1')), end="")
        locals {
          a = 1
        }
    """
    data = cty_to_hcl_block_data(block_type, labels, body)
    try:
        rendered: str = hcl2.dumps(data)
    except Exception as e:
        raise HclEmitError(f"Failed to render CTY value as HCL: {e}") from e
    return rendered


# 📄⚙️🔚
