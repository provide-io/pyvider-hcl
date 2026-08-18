#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Tests for formatting CTY values that carry sets, nulls, unknowns, or marks."""

from pyvider.cty import (
    CtyDynamic,
    CtyList,
    CtyMap,
    CtyNumber,
    CtyObject,
    CtySet,
    CtyString,
    CtyValue,
)
from pyvider.cty.marks import CtyMark
from pyvider.hcl import format_cty


class TestSetFormatting:
    """Set payloads render as a bracketed, deterministically ordered block."""

    def test_set_of_strings(self) -> None:
        value = CtySet(element_type=CtyString()).validate(["b", "a"])
        assert format_cty(value) == '[\n  "a",\n  "b"\n]'

    def test_set_order_is_stable(self) -> None:
        schema = CtySet(element_type=CtyString())
        assert format_cty(schema.validate(["b", "a", "c"])) == format_cty(schema.validate(["c", "a", "b"]))

    def test_empty_set(self) -> None:
        assert format_cty(CtySet(element_type=CtyString()).validate([])) == "[]"

    def test_set_inside_object(self) -> None:
        value = CtyObject({"s": CtySet(element_type=CtyNumber())}).validate({"s": [2, 1]})
        assert format_cty(value) == '{\n  "s": [\n    1,\n    2\n  ]\n}'


class TestNullAndUnknown:
    """Values with no payload render as explicit placeholders."""

    def test_null_scalar(self) -> None:
        assert format_cty(CtyValue.null(CtyString())) == "null"

    def test_unknown_scalar(self) -> None:
        assert format_cty(CtyValue.unknown(CtyString())) == "(unknown)"

    def test_null_attribute_in_object(self) -> None:
        value = CtyObject(
            {"a": CtyString(), "b": CtyString()},
            optional_attributes=frozenset({"b"}),
        ).validate({"a": "x", "b": None})
        assert format_cty(value) == '{\n  "a": "x",\n  "b": null\n}'

    def test_unknown_element_in_list(self) -> None:
        value = CtyValue(
            vtype=CtyList(element_type=CtyString()),
            value=(CtyString().validate("x"), CtyValue.unknown(CtyString())),
        )
        assert format_cty(value) == '[\n  "x",\n  (unknown)\n]'

    def test_null_container(self) -> None:
        assert format_cty(CtyValue.null(CtyList(element_type=CtyString()))) == "null"


class TestMarks:
    """Marks are surfaced rather than silently dropped."""

    def test_marked_scalar(self) -> None:
        value = CtyString().validate("secret").mark(CtyMark("sensitive"))
        assert format_cty(value) == '"secret" # marks: sensitive'

    def test_multiple_marks_sorted(self) -> None:
        value = CtyString().validate("s").mark(CtyMark("b")).mark(CtyMark("a"))
        assert format_cty(value).endswith("# marks: a, b")

    def test_marked_attribute_inside_object(self) -> None:
        value = CtyObject({"a": CtyString()}).validate({"a": "x"})
        marked = CtyValue(
            vtype=value.type,
            value={"a": CtyString().validate("x").mark(CtyMark("sensitive"))},
        )
        assert format_cty(marked) == '{\n  "a": "x" # marks: sensitive\n}'

    def test_marked_null(self) -> None:
        value = CtyValue.null(CtyString()).mark(CtyMark("sensitive"))
        assert format_cty(value) == "null # marks: sensitive"


class TestExistingShapes:
    """The shapes already covered elsewhere keep their rendering."""

    def test_object_with_nested_map(self) -> None:
        value = CtyObject({"m": CtyMap(element_type=CtyNumber())}).validate({"m": {"k": 1}})
        assert format_cty(value) == '{\n  "m": {\n    "k": 1\n  }\n}'

    def test_empty_object(self) -> None:
        assert format_cty(CtyObject({}).validate({})) == "{}"

    def test_dynamic_unwraps_to_inner_value(self) -> None:
        value = CtyDynamic().validate("x")
        assert format_cty(value) == '"x"'

    def test_bool_lowercase(self) -> None:
        from pyvider.cty import CtyBool

        assert format_cty(CtyBool().validate(True)) == "true"


# 📄⚙️🔚
