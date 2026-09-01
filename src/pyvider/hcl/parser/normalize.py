#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Normalization of ``python-hcl2`` 8.x serialized output.

``python-hcl2`` 8.x preserves source syntax in the dict it returns so that the
result can be reconstructed back into HCL:

* string literals keep their surrounding quotes (``'"web"'``),
* escape sequences are left raw (``'a\\\\tb'``),
* block bodies carry ``__is_block__`` markers and ``__comments__`` entries,
* object keys keep their quotes when the source quoted them.

None of that is useful for CTY conversion, which wants plain Python values, so
this module reverses it. Expressions (``'${var.x}'``) are deliberately left
alone: this package parses HCL, it does not evaluate it.

The pieces python-hcl2 already gets right are asked for rather than rewritten.
``HCL2_OPTIONS`` turns off ``preserve_heredocs``, so a heredoc arrives as the
quoted string its body spells, dedent and trailing newline already applied the
way HCL applies them.

A heredoc and the quoted literal ``"<<EOT\\nbody\\nEOT"`` reach this module in the
same shape -- both quoted, both escaped -- and nothing here tells them apart.
Nothing has to: python-hcl2's grammar already separated them, and by this point
the heredoc has been replaced by its body. Do not add a check that treats a
string *looking* like a heredoc as one; that is what the deleted local unwrapper
did, and it could not distinguish the two either.

``strip_string_quotes`` stays off because escape resolution belongs in one place,
not because it is unsafe: with ``preserve_heredocs`` already off it produces the
same values for every case in ``tests/parser/test_hcl_semantics.py``. Turning it
on would only move the work earlier, so the option buys nothing and splits the
handling in two.
"""

from __future__ import annotations

from typing import Any

from hcl2.const import COMMENTS_KEY, INLINE_COMMENTS_KEY, IS_BLOCK
from hcl2.utils import SerializationOptions, process_escape_sequences

# How this package asks python-hcl2 to serialize: heredocs resolved to their
# bodies, everything else in source form for the normalization below.
HCL2_OPTIONS = SerializationOptions(preserve_heredocs=False)

# hcl2 8.x metadata keys injected into serialized block bodies, named by the
# library rather than spelled out again here.
#
# `__start_line__` and `__end_line__` are deliberately absent. They appear only
# under `with_meta`, which `HCL2_OPTIONS` never sets, so filtering them would
# never drop hcl2 metadata -- it would only delete an attribute a configuration
# happened to name that, since HCL puts no namespace around these.
HCL2_METADATA_KEYS = frozenset({IS_BLOCK, COMMENTS_KEY, INLINE_COMMENTS_KEY})


def normalize_hcl_string(value: str) -> str:
    """Normalize one string as serialized by hcl2 8.x.

    Args:
        value: A string straight out of ``hcl2.loads``.

    Returns:
        A plain Python string: the resolved literal for a quoted string, or
        ``value`` unchanged for a bare expression or identifier.
    """
    if len(value) >= 2 and value.startswith('"') and value.endswith('"'):
        return process_escape_sequences(value[1:-1])

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
