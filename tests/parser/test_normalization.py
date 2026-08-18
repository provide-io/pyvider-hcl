#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Tests for normalization of python-hcl2 8.x output artifacts.

python-hcl2 8.x preserves source syntax in its serialized output: string
literals keep their quotes, escape sequences are left raw, heredocs keep their
markers, and negative integer literals are emitted as ``${-N}`` expression
strings. These tests pin the normalization that turns that back into plain
Python values before CTY inference runs.
"""

from decimal import Decimal

from pyvider.cty import CtyNumber, CtyString
from pyvider.hcl import parse_hcl_to_cty, parse_with_context
from pyvider.hcl.parser.normalize import normalize_hcl_data


class TestNegativeNumbers:
    """python-hcl2 8.x emits ``-3`` as the expression string ``${-3}``."""

    def test_negative_int_attribute_is_a_number(self) -> None:
        value = parse_hcl_to_cty("port = -3")
        assert isinstance(value.value["port"].type, CtyNumber)
        assert value.value["port"].value == Decimal("-3")

    def test_negative_int_in_list(self) -> None:
        data = parse_with_context("ports = [-1, 2, -30]")
        assert data["ports"] == [-1, 2, -30]

    def test_negative_int_in_object(self) -> None:
        data = parse_with_context("obj = { a = -1, b = 2 }")
        assert data["obj"] == {"a": -1, "b": 2}

    def test_negative_float_still_a_number(self) -> None:
        value = parse_hcl_to_cty("ratio = -3.5")
        assert value.value["ratio"].value == Decimal("-3.5")

    def test_positive_int_unaffected(self) -> None:
        data = parse_with_context("port = 8080")
        assert data["port"] == 8080

    def test_quoted_interpolation_of_negative_stays_a_string(self) -> None:
        """``"${-3}"`` is a template, not a number literal."""
        data = parse_with_context('label = "${-3}"')
        assert data["label"] == "${-3}"

    def test_negative_expression_stays_an_expression(self) -> None:
        data = parse_with_context("v = -var.count")
        assert data["v"] == "${-var.count}"

    def test_arithmetic_stays_an_expression(self) -> None:
        data = parse_with_context("v = 1 - 3")
        assert data["v"] == "${1 - 3}"


class TestHeredocs:
    """python-hcl2 8.x keeps heredoc markers in the serialized string.

    The expected values below were taken from OpenTofu evaluating the same
    source, so they are HCL's semantics rather than python-hcl2 7.x's (which
    dropped the trailing newline every heredoc body carries).
    """

    def test_heredoc_body_only(self) -> None:
        data = parse_with_context("script = <<EOT\nline1\nline2\nEOT\n")
        assert data["script"] == "line1\nline2\n"

    def test_heredoc_indented_form_is_dedented(self) -> None:
        content = "script = <<-EOF\n    indented\n      more\n    EOF\n"
        data = parse_with_context(content)
        assert data["script"] == "indented\n  more\n"

    def test_heredoc_preserves_inner_quotes(self) -> None:
        data = parse_with_context('script = <<EOT\nsay "hi"\nEOT\n')
        assert data["script"] == 'say "hi"\n'

    def test_heredoc_does_not_process_escapes(self) -> None:
        """Heredoc bodies are literal: a backslash-n stays two characters."""
        data = parse_with_context("script = <<EOT\nliteral\\nbackslash\nEOT\n")
        assert data["script"] == "literal\\nbackslash\n"

    def test_heredoc_keeps_interpolations(self) -> None:
        data = parse_with_context("script = <<EOT\nhello ${var.name}\nEOT\n")
        assert data["script"] == "hello ${var.name}\n"

    def test_heredoc_single_line_keeps_trailing_newline(self) -> None:
        data = parse_with_context("script = <<EOT\nonly\nEOT\n")
        assert data["script"] == "only\n"

    def test_heredoc_blank_body_line(self) -> None:
        data = parse_with_context("script = <<EOT\n\nEOT\n")
        assert data["script"] == "\n"

    def test_empty_heredoc_is_an_empty_string(self) -> None:
        """A heredoc with no body lines holds no content.

        python-hcl2 8.1.2 cannot parse this form, so the normalizer is
        exercised directly; the shape is what a fixed parser emits.
        """
        assert normalize_hcl_data('"<<EOF\nEOF"') == ""

    def test_empty_indented_heredoc_is_an_empty_string(self) -> None:
        assert normalize_hcl_data('"<<-EOF\n  EOF"') == ""

    def test_blank_line_heredoc_is_a_newline(self) -> None:
        """One empty body line is a newline, distinct from no body at all."""
        assert normalize_hcl_data('"<<EOF\n\nEOF"') == "\n"

    def test_unterminated_heredoc_is_left_alone(self) -> None:
        assert normalize_hcl_data('"<<EOF\nbody"') == "<<EOF\nbody"

    def test_mismatched_closing_marker_is_left_alone(self) -> None:
        assert normalize_hcl_data('"<<EOF\nbody\nOTHER"') == "<<EOF\nbody\nOTHER"

    def test_heredoc_through_cty(self) -> None:
        value = parse_hcl_to_cty("script = <<EOT\nbody\nEOT\n")
        assert isinstance(value.value["script"].type, CtyString)
        assert value.value["script"].value == "body\n"


class TestEscapeSequences:
    """python-hcl2 8.x leaves escape sequences raw in string literals."""

    def test_escaped_quote(self) -> None:
        data = parse_with_context(r'msg = "quote \"in\" here"')
        assert data["msg"] == 'quote "in" here'

    def test_escaped_newline_tab_return(self) -> None:
        data = parse_with_context(r'msg = "a\nb\tc\rd"')
        assert data["msg"] == "a\nb\tc\rd"

    def test_escaped_backslash(self) -> None:
        data = parse_with_context(r'msg = "back\\slash"')
        assert data["msg"] == "back\\slash"

    def test_escaped_backslash_before_n_is_literal(self) -> None:
        r"""``\\n`` is an escaped backslash followed by ``n``, not a newline."""
        data = parse_with_context(r'msg = "back\\nslash"')
        assert data["msg"] == "back\\nslash"

    def test_unicode_escape(self) -> None:
        data = parse_with_context(r'msg = "café"')
        assert data["msg"] == "café"

    def test_long_unicode_escape(self) -> None:
        data = parse_with_context(r'msg = "\U0001F600"')
        assert data["msg"] == "\U0001f600"

    def test_literal_unicode_preserved(self) -> None:
        data = parse_with_context('msg = "café ünïcödé 日本"')
        assert data["msg"] == "café ünïcödé 日本"

    def test_escaped_interpolation_marker_preserved(self) -> None:
        """``$${x}`` escapes interpolation in HCL; keep it distinguishable.

        Terraform resolves this to the literal ``${x}``, but Terraform also
        evaluates interpolations and so can still tell a literal from a live
        one. This package preserves expressions verbatim, so unescaping here
        would erase that distinction.
        """
        data = parse_with_context('msg = "literal $${x}"')
        assert data["msg"] == "literal $${x}"

    def test_unknown_escape_is_preserved(self) -> None:
        """Terraform rejects an unknown escape; python-hcl2 accepts it.

        Rather than add an error the grammar does not raise, an unrecognized
        escape is passed through with its backslash intact.
        """
        data = parse_with_context(r'msg = "keep \q intact"')
        assert data["msg"] == r"keep \q intact"

    def test_trailing_backslash_is_preserved(self) -> None:
        assert normalize_hcl_data('"trailing\\"') == "trailing\\"


class TestBlockArtifacts:
    """Quoted labels, ``__is_block__`` and ``__comments__`` are stripped."""

    def test_block_labels_unquoted_and_markers_removed(self) -> None:
        content = 'resource "aws_instance" "web" {\n  ami = "ami-1"\n}\n'
        data = parse_with_context(content)
        body = data["resource"][0]["aws_instance"]["web"]
        assert body == {"ami": "ami-1"}

    def test_quoted_object_keys_unquoted(self) -> None:
        data = parse_with_context('tags = { "Name" = "web", env = "prod" }')
        assert data["tags"] == {"Name": "web", "env": "prod"}

    def test_comments_removed(self) -> None:
        data = parse_with_context('# leading comment\nname = "x"\n')
        assert data == {"name": "x"}

    def test_nested_block_markers_removed(self) -> None:
        content = 'resource "t" "n" {\n  nested {\n    a = 1\n  }\n}\n'
        data = parse_with_context(content)
        body = data["resource"][0]["t"]["n"]
        assert body == {"nested": [{"a": 1}]}


class TestExpressionPassthrough:
    """Expressions are not evaluated; they stay ``${...}`` strings."""

    def test_variable_reference(self) -> None:
        data = parse_with_context("v = var.name")
        assert data["v"] == "${var.name}"

    def test_function_call_keeps_inner_quotes(self) -> None:
        data = parse_with_context('v = upper("x")')
        assert data["v"] == '${upper("x")}'

    def test_conditional_keeps_inner_quotes(self) -> None:
        data = parse_with_context('v = var.x ? "a" : "b"')
        assert data["v"] == '${var.x ? "a" : "b"}'

    def test_for_expression(self) -> None:
        data = parse_with_context("v = [for i in var.xs : i]")
        assert data["v"] == "${[for i in var.xs : i]}"

    def test_type_keyword_is_bare(self) -> None:
        data = parse_with_context("type = string")
        assert data["type"] == "string"

    def test_booleans_and_null(self) -> None:
        data = parse_with_context("a = true\nb = false\nc = null")
        assert data == {"a": True, "b": False, "c": None}


# 📄⚙️🔚
