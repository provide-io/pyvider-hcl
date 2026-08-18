#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Tests for rendering CTY values back into HCL text."""

from decimal import Decimal

import pytest

from pyvider.cty import (
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
from pyvider.cty.marks import CtyMark
from pyvider.hcl import cty_to_hcl, parse_hcl_to_cty, parse_with_context
from pyvider.hcl.output.emitter import HclEmitError, cty_to_hcl_data


def _roundtrip(hcl_text: str) -> dict:
    """Parse, emit, and re-parse, returning the re-parsed data."""
    emitted = cty_to_hcl(parse_hcl_to_cty(hcl_text))
    return parse_with_context(emitted)


class TestScalarEmission:
    """Primitive CTY values map onto HCL literals."""

    def test_string(self) -> None:
        assert cty_to_hcl(parse_hcl_to_cty('name = "x"')) == 'name = "x"\n'

    def test_integral_number_stays_integral(self) -> None:
        assert cty_to_hcl(parse_hcl_to_cty("port = 8080")) == "port = 8080\n"

    def test_fractional_number(self) -> None:
        assert cty_to_hcl(parse_hcl_to_cty("ratio = 1.5")) == "ratio = 1.5\n"

    def test_negative_number(self) -> None:
        assert cty_to_hcl(parse_hcl_to_cty("offset = -3")) == "offset = -3\n"

    def test_booleans(self) -> None:
        assert cty_to_hcl(parse_hcl_to_cty("a = true\nb = false")) == "a = true\nb = false\n"

    def test_null(self) -> None:
        assert cty_to_hcl(parse_hcl_to_cty("a = null")) == "a = null\n"

    def test_decimal_scientific_notation_is_integral(self) -> None:
        value = CtyObject({"n": CtyNumber()}).validate({"n": Decimal("1E+3")})
        assert cty_to_hcl(value) == "n = 1000\n"


class TestStringEscaping:
    """String literals are re-quoted and re-escaped on the way out."""

    def test_embedded_quote(self) -> None:
        value = CtyObject({"s": CtyString()}).validate({"s": 'say "hi"'})
        assert cty_to_hcl(value) == 's = "say \\"hi\\""\n'

    def test_newline_and_tab(self) -> None:
        value = CtyObject({"s": CtyString()}).validate({"s": "a\nb\tc"})
        assert cty_to_hcl(value) == 's = "a\\nb\\tc"\n'

    def test_backslash(self) -> None:
        value = CtyObject({"s": CtyString()}).validate({"s": "back\\slash"})
        assert cty_to_hcl(value) == 's = "back\\\\slash"\n'

    def test_quote_roundtrips(self) -> None:
        assert _roundtrip(r'msg = "quote \"in\" here"') == {"msg": 'quote "in" here'}

    def test_escapes_roundtrip(self) -> None:
        assert _roundtrip(r'msg = "a\nb\tc"') == {"msg": "a\nb\tc"}

    def test_unicode_roundtrips(self) -> None:
        assert _roundtrip('msg = "café 日本"') == {"msg": "café 日本"}


class TestExpressionEmission:
    """Whole-interpolation strings are emitted as expressions, not literals."""

    def test_variable_reference(self) -> None:
        value = CtyObject({"v": CtyString()}).validate({"v": "${var.name}"})
        assert cty_to_hcl(value) == "v = var.name\n"

    def test_expression_roundtrips(self) -> None:
        assert _roundtrip("v = var.name") == {"v": "${var.name}"}

    def test_function_call_roundtrips(self) -> None:
        assert _roundtrip('v = upper("x")') == {"v": '${upper("x")}'}

    def test_template_with_literal_text_is_quoted(self) -> None:
        value = CtyObject({"v": CtyString()}).validate({"v": "a${var.x}b"})
        assert cty_to_hcl(value) == 'v = "a${var.x}b"\n'

    def test_template_roundtrips(self) -> None:
        assert _roundtrip('v = "a${var.x}b"') == {"v": "a${var.x}b"}


class TestContainerEmission:
    """Collections and structural types map onto HCL tuples and objects."""

    def test_list(self) -> None:
        assert _roundtrip('l = ["a", "b"]') == {"l": ["a", "b"]}

    def test_empty_list(self) -> None:
        assert _roundtrip("l = []") == {"l": []}

    def test_nested_object(self) -> None:
        assert _roundtrip("o = { a = { b = 1 } }") == {"o": {"a": {"b": 1}}}

    def test_mixed_list(self) -> None:
        assert _roundtrip('l = ["a", 1, true]') == {"l": ["a", 1, True]}

    def test_map_schema(self) -> None:
        value = CtyObject({"m": CtyMap(element_type=CtyString())}).validate({"m": {"k": "v"}})
        assert _roundtrip(cty_to_hcl(value)) == {"m": {"k": "v"}}

    def test_tuple_schema(self) -> None:
        value = CtyObject({"t": CtyTuple((CtyString(), CtyNumber()))}).validate({"t": ["x", 5]})
        assert cty_to_hcl(value) == 't = [\n  "x",\n  5,\n]\n'

    def test_set_is_deterministic(self) -> None:
        schema = CtyObject({"s": CtySet(element_type=CtyString())})
        first = cty_to_hcl(schema.validate({"s": ["b", "a", "c"]}))
        second = cty_to_hcl(schema.validate({"s": ["c", "b", "a"]}))
        assert first == second

    def test_dynamic_unwraps(self) -> None:
        value = CtyObject({"d": CtyDynamic()}).validate({"d": "x"})
        assert cty_to_hcl(value) == 'd = "x"\n'

    def test_heredoc_body_roundtrips_as_escaped_string(self) -> None:
        """A heredoc re-emits as a quoted string with the same content.

        The trailing newline HCL gives every heredoc body survives the round
        trip; only the syntax used to express it changes.
        """
        assert _roundtrip("s = <<EOT\nline1\nline2\nEOT\n") == {"s": "line1\nline2\n"}


class TestEmissionErrors:
    """Values with no HCL representation are rejected explicitly."""

    def test_unknown_rejected(self) -> None:
        with pytest.raises(HclEmitError, match="unknown"):
            cty_to_hcl_data(CtyValue.unknown(CtyString()))

    def test_unknown_nested_in_body_rejected(self) -> None:
        value = CtyObject({"s": CtyString()}).validate({"s": "x"})
        body = CtyValue(
            vtype=value.type,
            value={"s": CtyValue.unknown(CtyString())},
        )
        with pytest.raises(HclEmitError, match="unknown"):
            cty_to_hcl(body)

    def test_marked_value_rejected(self) -> None:
        marked = CtyString().validate("secret").mark(CtyMark("sensitive"))
        with pytest.raises(HclEmitError, match="marked"):
            cty_to_hcl_data(marked)

    def test_non_body_value_rejected(self) -> None:
        with pytest.raises(HclEmitError, match="object- or map-typed"):
            cty_to_hcl(CtyString().validate("x"))

    def test_list_root_rejected(self) -> None:
        value = CtyList(element_type=CtyString()).validate(["a"])
        with pytest.raises(HclEmitError, match="object- or map-typed"):
            cty_to_hcl(value)

    def test_plain_python_passes_through(self) -> None:
        assert cty_to_hcl_data(5) == 5


# 📄⚙️🔚
