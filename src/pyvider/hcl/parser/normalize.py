#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Normalization of ``python-hcl2`` 8.x serialized output.

``python-hcl2`` 8.x preserves source syntax in the dict it returns so that the
result can be reconstructed back into HCL:

* string literals keep their surrounding quotes (``'"web"'``),
* escape sequences are left raw (``'a\\\\tb'``),
* heredocs keep their markers (``'"<<EOT\\nbody\\nEOT"'``),
* block bodies carry ``__is_block__`` markers and ``__comments__`` entries,
* object keys keep their quotes when the source quoted them.

None of that is useful for CTY conversion, which wants plain Python values, so
this module reverses it. Expressions (``'${var.x}'``) are deliberately left
alone: this package parses HCL, it does not evaluate it.

The pieces python-hcl2 already gets right are imported rather than rewritten:
``HEREDOC_PATTERN`` and ``HEREDOC_TRIM_PATTERN``, which the library documents as
tracking its own grammar terminals (so delimiters containing ``.`` or ``-``,
single-character delimiters, and CRLF line endings all follow automatically),
and ``process_escape_sequences``, which resolves escapes in a single pass.

What stays here is the heredoc body, because python-hcl2's own value form —
``SerializationOptions(preserve_heredocs=False, strip_string_quotes=True)`` —
disagrees with HCL on every case ``tests/parser/test_hcl_semantics.py`` checks
against OpenTofu: it drops the newline before the closing marker, dedents
whitespace-only lines, and measures ``<<-`` indentation in spaces only, so a
tab-indented heredoc is not dedented at all.

``strip_string_quotes`` is unusable here for a second reason. It resolves
escapes before this module sees the value, and a quoted literal spelling
``"<<EOT\\nbody\\nEOT"`` then becomes byte-identical to a real heredoc — two
different values by OpenTofu's reckoning. Unwrapping the heredoc first, while
its escapes are still raw, is what keeps them apart.
"""

from __future__ import annotations

import re
from typing import Any

from hcl2.const import COMMENTS_KEY, INLINE_COMMENTS_KEY, IS_BLOCK
from hcl2.utils import (
    HEREDOC_PATTERN,
    HEREDOC_TRIM_PATTERN,
    process_escape_sequences,
)

# hcl2 8.x metadata keys injected into serialized block bodies, named by the
# library rather than spelled out again here.
HCL2_METADATA_KEYS = frozenset({IS_BLOCK, COMMENTS_KEY, INLINE_COMMENTS_KEY})

# The indentation of the closing heredoc marker, which sits on its own line and
# is not part of the value. Nothing else trailing is removed: a blank final line
# and spaces at the end of a content line are both content, and a content line
# always ends with its own newline, so this can never reach past one.
_CLOSING_MARKER_INDENT_RE = re.compile(r"[ \t]*\Z")


def _dedent_heredoc(lines: list[str]) -> list[str]:
    """Strip the common leading whitespace from ``<<-`` heredoc lines.

    The spec measures "any literal string at the start of each line", so a
    whitespace-only line offers no measurement and is left exactly as it was:
    OpenTofu reports ``"a\\n      \\nb\\n"`` for a heredoc indented by four
    spaces whose middle line is six, neither measuring that line nor trimming
    it. Indentation is counted in characters, not spaces, so a tab-indented
    heredoc dedents like a space-indented one.
    """
    indents = [len(line) - len(line.lstrip()) for line in lines if line.strip()]
    if not indents:
        return lines
    margin = min(indents)
    return [line[margin:] if line.strip() else line for line in lines]


def _unwrap_heredoc(value: str) -> str | None:
    """Extract the body of a heredoc serialized by hcl2 8.x.

    Args:
        value: Candidate string with the outer quotes already removed.

    Returns:
        The heredoc body, or ``None`` when ``value`` is not a heredoc.
    """
    match = HEREDOC_TRIM_PATTERN.match(value)
    dedent = match is not None
    if match is None:
        match = HEREDOC_PATTERN.match(value)
    # Both patterns close on the last occurrence of the delimiter rather than
    # anchoring at the end, so a match that stops short is text that merely
    # begins like a heredoc.
    if match is None or match.end() != len(value):
        return None

    # Everything between the opening marker's newline and the closing one: the
    # content lines with the newlines that terminate them, then the closing
    # marker's indentation. HCL counts the newline before the closing marker as
    # content, so `<<EOT\nline\nEOT` is "line\n", not "line" -- verified against
    # OpenTofu, which reports the same for the same source.
    body = _CLOSING_MARKER_INDENT_RE.sub("", match.group(2))
    if not dedent:
        return body
    return "\n".join(_dedent_heredoc(body.split("\n")))


def normalize_hcl_string(value: str) -> str:
    """Normalize one string as serialized by hcl2 8.x.

    Args:
        value: A string straight out of ``hcl2.loads``.

    Returns:
        A plain Python string: the body for a heredoc, the resolved literal for
        a quoted string, or ``value`` unchanged for a bare expression or
        identifier.
    """
    if len(value) >= 2 and value.startswith('"') and value.endswith('"'):
        inner = value[1:-1]
        heredoc = _unwrap_heredoc(inner)
        if heredoc is not None:
            return heredoc
        return process_escape_sequences(inner)

    return value


def normalize_hcl_key(key: str) -> str:
    """Unquote and unescape an object key or block label kept quoted by hcl2 8.x.

    A quoted key is a string literal and carries the same escapes a value does,
    so it has to be resolved the same way -- otherwise ``{ "a\\nb" = "a\\nb" }``
    yields a key and a value that spell the same source text differently.
    """
    if len(key) >= 2 and key.startswith('"') and key.endswith('"'):
        return process_escape_sequences(key[1:-1])
    return key


def normalize_hcl_data(data: Any) -> Any:
    """Recursively normalize a structure returned by ``hcl2.loads``.

    Drops hcl2 metadata keys, unquotes object keys and block labels, and
    normalizes every string via :func:`normalize_hcl_string`.

    Args:
        data: Parsed hcl2 output (dict, list, or scalar).

    Returns:
        The same structure with hcl2 serialization artifacts removed.
    """
    if isinstance(data, dict):
        return {
            normalize_hcl_key(key): normalize_hcl_data(value)
            for key, value in data.items()
            if key not in HCL2_METADATA_KEYS
        }
    if isinstance(data, list):
        return [normalize_hcl_data(item) for item in data]
    if isinstance(data, str):
        return normalize_hcl_string(data)
    return data


# 📄⚙️🔚
