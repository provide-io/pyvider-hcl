#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Source location extraction for HCL parse failures.

``python-hcl2`` parses through ``lark``, whose ``UnexpectedInput`` exceptions
carry the failing line and column plus a ``get_context()`` helper that renders
the offending source line with a caret. Those attributes are read
structurally rather than by importing ``lark``, so this package keeps a single
direct dependency on ``python-hcl2``.
"""

from __future__ import annotations

from typing import Any

import attrs

# Number of source characters lark should show on either side of the caret.
ERROR_CONTEXT_SPAN = 40


@attrs.define(frozen=True, slots=True)
class SourceLocation:
    """Where a parse failure happened, when the parser reported it."""

    line: int | None = attrs.field(default=None)
    column: int | None = attrs.field(default=None)
    context: str | None = attrs.field(default=None)


def _positive_int(value: Any) -> int | None:
    """Return ``value`` as a positive int, or ``None`` if it is not usable."""
    if isinstance(value, bool) or not isinstance(value, int):
        return None
    return value if value > 0 else None


def _extract_context(error: Exception, content: str) -> str | None:
    """Render the source snippet lark associates with ``error``."""
    get_context = getattr(error, "get_context", None)
    if not callable(get_context):
        return None
    try:
        context = get_context(content, ERROR_CONTEXT_SPAN)
    except Exception:  # lark raises on positions outside the given text
        return None
    return context.rstrip("\n") if isinstance(context, str) else None


def source_location(error: Exception, content: str) -> SourceLocation:
    """Extract the source location a parse error points at.

    Args:
        error: Exception raised while parsing.
        content: The HCL text that was being parsed.

    Returns:
        A :class:`SourceLocation`; its fields are ``None`` when the underlying
        error carries no position information.
    """
    line = _positive_int(getattr(error, "line", None))
    column = _positive_int(getattr(error, "column", None))
    context = _extract_context(error, content) if line is not None else None
    return SourceLocation(line=line, column=column, context=context)


# 📄⚙️🔚
