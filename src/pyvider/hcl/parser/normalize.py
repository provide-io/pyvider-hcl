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
:func:`hcl2_options` turns off ``preserve_heredocs``, so a heredoc arrives as
the quoted string its body spells, dedent and trailing newline already applied
the way HCL applies them.

:func:`normalize_hcl_data` expects input serialized with those options. Handed
the output of a bare ``hcl2.loads``, it returns heredoc *markers* rather than
bodies -- silently, since a heredoc and a string that merely looks like one are
indistinguishable by then. Use :func:`loads_normalized` or
:func:`to_dict_normalized` rather than pairing the two by hand.

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

import hcl2
from hcl2.utils import SerializationOptions, process_escape_sequences


def hcl2_options() -> SerializationOptions:
    """Build the serialization options every parse in this package uses.

    A fresh instance per call. ``SerializationOptions`` is a plain mutable
    dataclass, so a module-level singleton is one object shared by every parse
    in the process: anything that assigns to a field -- a caller, a subclass, a
    test that forgets to restore -- silently reconfigures parsing everywhere.

    ``preserve_heredocs`` is off, so a heredoc arrives as the quoted string its
    body spells, dedent and trailing newline already applied the way HCL
    applies them.

    ``with_comments`` and ``explicit_blocks`` are off because this package
    discards both. Asking for them and then filtering them out cost real data:
    the markers are ordinary attribute names as far as HCL is concerned, so a
    configuration with an attribute called ``__is_block__`` or ``__comments__``
    lost it to the filter. Not requesting them means nothing has to be removed,
    and nothing a document actually says can collide with the removal.
    """
    return SerializationOptions(
        preserve_heredocs=False,
        with_comments=False,
        explicit_blocks=False,
    )


def loads_normalized(text: str) -> Any:
    """Parse *text* with this package's options and normalize the result.

    The options and the normalization belong together -- output serialized
    another way normalizes wrongly, silently -- so both entry points go through
    here rather than each remembering to pass the options.
    """
    return normalize_hcl_data(hcl2.loads(text, serialization_options=hcl2_options()))


def to_dict_normalized(node: Any) -> Any:
    """Serialize a python-hcl2 query view with this package's options."""
    return normalize_hcl_data(node.to_dict(options=hcl2_options()))


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
    so it is resolved the same way -- otherwise ``{ "a\\nb" = "a\\nb" }`` yields
    a key and a value that spell the same source text differently. It delegates
    rather than repeating the body: the two were identical once the heredoc
    branch left this module, and two copies drift.
    """
    return normalize_hcl_string(key)


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
        return {normalize_hcl_key(key): normalize_hcl_data(value) for key, value in data.items()}
    if isinstance(data, list):
        return [normalize_hcl_data(item) for item in data]
    if isinstance(data, str):
        return normalize_hcl_string(data)
    return data


# 📄⚙️🔚
