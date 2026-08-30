#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Conformance tests against real HCL semantics.

Every expected value here was produced by evaluating the same source with
OpenTofu (``tofu console``, ``jsonencode`` of the resulting locals) rather than
by reading python-hcl2's output. They exist to catch cases where this package
faithfully reproduces python-hcl2's behaviour but python-hcl2 disagrees with
HCL — which is how the heredoc trailing newline and the negative-integer
handling were found.

Two deliberate deviations are recorded as such at the bottom of this file.
"""

import pytest

from pyvider.hcl import parse_with_context

# source -> value OpenTofu evaluates it to
GROUND_TRUTH: list[tuple[str, object]] = [
    (r'x = "quote \"in\" here"', 'quote "in" here'),
    (r'x = "nl\nhere"', "nl\nhere"),
    (r'x = "tab\there"', "tab\there"),
    (r'x = "back\\slash"', "back\\slash"),
    # An escaped backslash followed by "n" is a backslash and a letter, not a
    # newline. python-hcl2 7.x got this wrong by running its replacements in
    # sequence; OpenTofu and this package agree.
    (r'x = "back\\nslash"', "back\\nslash"),
    ("x = -3", -3),
    ("x = -3.5", -3.5),
    ("x = 8080", 8080),
    ("x = true", True),
    ("x = null", None),
    # Heredoc content includes the newline before the closing marker.
    ("x = <<EOT\nline1\nline2\nEOT\n", "line1\nline2\n"),
    ("x = <<-EOF\n    indented\n      more\n    EOF\n", "indented\n  more\n"),
    ('x = <<EOT\nsay "hi"\nEOT\n', 'say "hi"\n'),
    ("x = <<EOT\nliteral\\nbackslash\nEOT\n", "literal\\nbackslash\n"),
    # A trailing blank line and trailing spaces on a content line are content;
    # only the closing marker's own indentation is not.
    ("x = <<EOT\nbody  \n\nEOT\n", "body  \n\n"),
    # `<<-` measures indentation in characters, so a tab-indented heredoc
    # dedents by one tab rather than not at all.
    ("x = <<-EOT\n\ta\n\t\tb\n\tEOT\n", "a\n\tb\n"),
    # A whitespace-only line is neither measured for the dedent nor trimmed
    # by it.
    ("x = <<-EOT\n    a\n      \n    b\n    EOT\n", "a\n      \nb\n"),
    # Any HCL identifier is a valid delimiter, one character included.
    ("x = <<E\nbody\nE\n", "body\n"),
    ("x = <<EO-T\nbody\nEO-T\n", "body\n"),
    # A CRLF file's line endings are content inside a heredoc body.
    ("x = <<EOT\r\na\r\nb\r\nEOT\r\n", "a\r\nb\r\n"),
    # A quoted literal that spells a heredoc is a string, not a heredoc: it has
    # no trailing newline, because it never had a closing marker line.
    ('x = "<<EOT\\nbody\\nEOT"', "<<EOT\nbody\nEOT"),
]


@pytest.mark.parametrize(("source", "expected"), GROUND_TRUTH)
def test_matches_opentofu(source: str, expected: object) -> None:
    """Parsing ``source`` yields what OpenTofu evaluates it to."""
    assert parse_with_context(source)["x"] == expected


class TestDeliberateDeviations:
    """Cases where this package knowingly differs from Terraform/OpenTofu."""

    def test_escaped_interpolation_is_not_unescaped(self) -> None:
        """OpenTofu resolves ``$${x}`` to ``${x}``; we keep the escape.

        Terraform can unescape safely because it evaluates interpolations and
        can therefore still distinguish a literal from a live one afterwards.
        This package preserves expressions verbatim, so unescaping would make
        the two indistinguishable.
        """
        assert parse_with_context('x = "literal $${notinterp}"')["x"] == "literal $${notinterp}"

    def test_invalid_escape_is_not_an_error(self) -> None:
        """OpenTofu rejects ``\\q``; python-hcl2 accepts it, and so do we.

        OpenTofu reports: 'The symbol "q" is not a valid escape sequence
        selector'. Raising here would mean rejecting input the underlying
        grammar parses without complaint.
        """
        assert parse_with_context(r'x = "keep \q intact"')["x"] == r"keep \q intact"

    def test_expressions_are_not_evaluated(self) -> None:
        """OpenTofu resolves expressions; we preserve their source text."""
        assert parse_with_context("x = 1 + 2")["x"] == "${1 + 2}"


# 📄⚙️🔚
