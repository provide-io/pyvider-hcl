#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Normalization of ``python-hcl2`` 8.x serialized output.

``python-hcl2`` 8.x preserves source syntax in the dict it returns so that the
result can be reconstructed back into HCL:

* string literals keep their surrounding quotes (``'"web"'``),
* escape sequences are left raw (``'a\\\\"b'``),
* heredocs keep their markers (``'"<<EOT\\nbody\\nEOT"'``),
* block bodies carry ``__is_block__`` markers and ``__comments__`` entries,
* object keys keep their quotes when the source quoted them,
* negative integer literals are emitted as ``'${-3}'`` expression strings.

None of that is useful for CTY conversion, which wants plain Python values, so
this module reverses it. Expressions (``'${var.x}'``) are deliberately left
alone: this package parses HCL, it does not evaluate it.
"""

from __future__ import annotations

import re
from typing import Any

# hcl2 8.x metadata keys injected into serialized block bodies.
HCL2_METADATA_KEYS = frozenset({"__is_block__", "__comments__", "__inline_comments__"})

# A bare (unquoted) interpolation wrapping nothing but a negative number.
# hcl2 8.x lexes ``-3`` as unary-minus applied to an int literal rather than as
# a negative int literal, so it serializes as an expression string.
_NEGATIVE_NUMBER_RE = re.compile(r"^\$\{-(\d+(?:\.\d+)?)\}$")

# Heredoc as serialized by hcl2 8.x, after the outer quotes are removed:
# ``<<TAG\n<body>\n<indent>TAG``. ``<<-`` requests dedenting of the body.
_HEREDOC_RE = re.compile(r"^<<(?P<dash>-?)(?P<tag>[A-Za-z_][A-Za-z0-9_]*)\n(?P<rest>.*)$", re.DOTALL)

# Escape sequences HCL defines inside quoted templates. ``$${`` and ``%%{``
# (escaped interpolation/directive markers) are intentionally absent, which is a
# deliberate deviation from Terraform: Terraform resolves ``$${x}`` to the
# literal text ``${x}``, but Terraform also evaluates interpolations, so it can
# tell the two apart afterwards. This package preserves expressions verbatim
# instead of evaluating them, so unescaping here would make a literal
# indistinguishable from a live interpolation. The escape is left in place and
# the distinction preserved.
_SIMPLE_ESCAPES = {
    "n": "\n",
    "r": "\r",
    "t": "\t",
    '"': '"',
    "\\": "\\",
}
_UNICODE_ESCAPE_WIDTHS = {"u": 4, "U": 8}


def _decode_unicode_escape(text: str, index: int) -> tuple[str, int] | None:
    """Decode a ``\\uNNNN`` / ``\\UNNNNNNNN`` escape starting at ``index``.

    Args:
        text: The string being scanned.
        index: Offset of the ``u``/``U`` marker (just past the backslash).

    Returns:
        A ``(character, next_index)`` pair, or ``None`` when the escape is
        malformed and should be preserved verbatim.
    """
    width = _UNICODE_ESCAPE_WIDTHS[text[index]]
    digits = text[index + 1 : index + 1 + width]
    if len(digits) != width or any(char not in "0123456789abcdefABCDEF" for char in digits):
        return None
    try:
        return chr(int(digits, 16)), index + 1 + width
    except ValueError:  # pragma: no cover - guarded by the digit check above
        return None


def unescape_hcl_string(value: str) -> str:
    """Process HCL escape sequences in a quoted string literal.

    Unrecognized escapes are preserved verbatim, backslash included. Terraform
    itself rejects them ("The symbol \"q\" is not a valid escape sequence
    selector"), but python-hcl2 accepts them, and a parser is a poor place to
    add a hard error the underlying grammar does not raise.

    Args:
        value: String literal contents, without the surrounding quotes.

    Returns:
        The string with escape sequences resolved.
    """
    if "\\" not in value:
        return value

    parts: list[str] = []
    index = 0
    length = len(value)
    while index < length:
        char = value[index]
        if char != "\\" or index + 1 >= length:
            parts.append(char)
            index += 1
            continue

        marker = value[index + 1]
        if marker in _SIMPLE_ESCAPES:
            parts.append(_SIMPLE_ESCAPES[marker])
            index += 2
            continue
        if marker in _UNICODE_ESCAPE_WIDTHS:
            decoded = _decode_unicode_escape(value, index + 1)
            if decoded is not None:
                parts.append(decoded[0])
                index = decoded[1]
                continue

        # Not an escape we recognize: keep the backslash and the character.
        parts.append(char)
        parts.append(marker)
        index += 2

    return "".join(parts)


def _dedent_heredoc(lines: list[str]) -> list[str]:
    """Strip the common leading whitespace from ``<<-`` heredoc lines."""
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
    match = _HEREDOC_RE.match(value)
    if match is None:
        return None

    rest = match.group("rest")
    tag = match.group("tag")
    body, separator, closing = rest.rpartition("\n")
    if not separator:
        # Nothing follows the opening marker but the closing one, so the
        # heredoc has no body lines at all and holds the empty string. This is
        # distinct from a single empty body line, which holds one newline.
        return "" if rest.strip() == tag else None
    if closing.strip() != tag:
        return None

    lines = body.split("\n")
    if match.group("dash"):
        lines = _dedent_heredoc(lines)
    # HCL heredoc content includes the newline that precedes the closing marker,
    # so `<<EOT\nline\nEOT` is "line\n", not "line". Verified against
    # OpenTofu, which reports the same for the same source.
    return "\n".join(lines) + "\n"


def _coerce_negative_number(value: str) -> int | float | None:
    """Convert a bare ``${-N}`` expression string back into a number."""
    match = _NEGATIVE_NUMBER_RE.match(value)
    if match is None:
        return None
    digits = match.group(1)
    return -float(digits) if "." in digits else -int(digits)


def normalize_hcl_string(value: str) -> Any:
    """Normalize one string as serialized by hcl2 8.x.

    Args:
        value: A string straight out of ``hcl2.loads``.

    Returns:
        A plain Python value: a number for ``${-N}``, the unescaped literal for
        a quoted string, the body for a heredoc, or ``value`` unchanged for a
        bare expression or identifier.
    """
    number = _coerce_negative_number(value)
    if number is not None:
        return number

    if len(value) >= 2 and value.startswith('"') and value.endswith('"'):
        inner = value[1:-1]
        heredoc = _unwrap_heredoc(inner)
        if heredoc is not None:
            return heredoc
        return unescape_hcl_string(inner)

    return value


def _normalize_key(key: str) -> str:
    """Unquote and unescape an object key or block label kept quoted by hcl2 8.x.

    A quoted key is a string literal and carries the same escapes a value does,
    so it has to be resolved the same way -- otherwise ``{ "a\\nb" = "a\\nb" }``
    yields a key and a value that spell the same source text differently.
    """
    if len(key) >= 2 and key.startswith('"') and key.endswith('"'):
        return unescape_hcl_string(key[1:-1])
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
            _normalize_key(key): normalize_hcl_data(value)
            for key, value in data.items()
            if key not in HCL2_METADATA_KEYS
        }
    if isinstance(data, list):
        return [normalize_hcl_data(item) for item in data]
    if isinstance(data, str):
        return normalize_hcl_string(data)
    return data


# 📄⚙️🔚
