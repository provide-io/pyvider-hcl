#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Tests for the Terraform type-string constructs beyond list/map/object."""

import pytest

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
)
from pyvider.hcl.factories import HclTypeParsingError, parse_hcl_type_string


class TestSetTypes:
    """``set(type)`` maps onto :class:`CtySet`."""

    def test_set_of_string(self) -> None:
        assert parse_hcl_type_string("set(string)") == CtySet(element_type=CtyString())

    def test_set_of_object(self) -> None:
        parsed = parse_hcl_type_string("set(object({name=string}))")
        assert parsed == CtySet(element_type=CtyObject({"name": CtyString()}))

    def test_nested_set_in_list(self) -> None:
        parsed = parse_hcl_type_string("list(set(number))")
        assert parsed == CtyList(element_type=CtySet(element_type=CtyNumber()))

    def test_empty_set_rejected(self) -> None:
        with pytest.raises(HclTypeParsingError, match="Set type string is empty"):
            parse_hcl_type_string("set()")


class TestTupleTypes:
    """``tuple([...])`` maps onto :class:`CtyTuple`."""

    def test_tuple_of_two(self) -> None:
        parsed = parse_hcl_type_string("tuple([string, number])")
        assert parsed == CtyTuple((CtyString(), CtyNumber()))

    def test_empty_tuple(self) -> None:
        assert parse_hcl_type_string("tuple([])") == CtyTuple(())

    def test_tuple_with_nested_collections(self) -> None:
        parsed = parse_hcl_type_string("tuple([list(string), map(bool)])")
        assert parsed == CtyTuple((CtyList(element_type=CtyString()), CtyMap(element_type=CtyBool())))

    def test_tuple_with_nested_object_containing_comma(self) -> None:
        parsed = parse_hcl_type_string("tuple([object({a=string,b=number}), bool])")
        assert parsed == CtyTuple((CtyObject({"a": CtyString(), "b": CtyNumber()}), CtyBool()))

    def test_tuple_requires_brackets(self) -> None:
        with pytest.raises(HclTypeParsingError, match=r"must be enclosed in \[\]"):
            parse_hcl_type_string("tuple(string)")

    def test_tuple_trailing_comma_rejected(self) -> None:
        with pytest.raises(HclTypeParsingError, match="Trailing comma"):
            parse_hcl_type_string("tuple([string,])")


class TestOptionalAttributes:
    """``optional(type)`` marks an object attribute optional."""

    def test_single_optional_attribute(self) -> None:
        parsed = parse_hcl_type_string("object({name=string, port=optional(number)})")
        assert parsed == CtyObject(
            {"name": CtyString(), "port": CtyNumber()},
            optional_attributes=frozenset({"port"}),
        )

    def test_all_attributes_optional(self) -> None:
        parsed = parse_hcl_type_string("object({a=optional(string), b=optional(bool)})")
        assert isinstance(parsed, CtyObject)
        assert parsed.optional_attributes == frozenset({"a", "b"})

    def test_optional_with_default_ignores_default(self) -> None:
        """Terraform's ``optional(type, default)`` parses; the default is dropped."""
        parsed = parse_hcl_type_string('object({region=optional(string, "us-west-2")})')
        assert parsed == CtyObject(
            {"region": CtyString()},
            optional_attributes=frozenset({"region"}),
        )

    def test_optional_collection_type(self) -> None:
        parsed = parse_hcl_type_string("object({tags=optional(map(string))})")
        assert parsed == CtyObject(
            {"tags": CtyMap(element_type=CtyString())},
            optional_attributes=frozenset({"tags"}),
        )

    def test_optional_nested_object(self) -> None:
        parsed = parse_hcl_type_string("object({cfg=optional(object({a=string,b=number}))})")
        assert isinstance(parsed, CtyObject)
        assert parsed.optional_attributes == frozenset({"cfg"})
        assert parsed.attribute_types["cfg"] == CtyObject({"a": CtyString(), "b": CtyNumber()})

    def test_no_optional_attributes_means_empty_frozenset(self) -> None:
        parsed = parse_hcl_type_string("object({a=string})")
        assert isinstance(parsed, CtyObject)
        assert not parsed.optional_attributes

    def test_empty_optional_rejected(self) -> None:
        with pytest.raises(HclTypeParsingError, match="Optional type string is empty"):
            parse_hcl_type_string("object({a=optional()})")

    def test_optional_outside_object_is_rejected(self) -> None:
        """``optional`` is only meaningful as an object attribute wrapper."""
        with pytest.raises(HclTypeParsingError, match="Unknown or malformed type string"):
            parse_hcl_type_string("optional(string)")


class TestValidationBehaviour:
    """The parsed types behave as expected when validating values."""

    def test_optional_attribute_may_be_omitted(self) -> None:
        schema = parse_hcl_type_string("object({name=string, port=optional(number)})")
        value = schema.validate({"name": "x"})
        assert value.value["name"].value == "x"
        assert value.value["port"].is_null

    def test_set_deduplicates(self) -> None:
        schema = parse_hcl_type_string("set(string)")
        value = schema.validate(["a", "b", "a"])
        assert len(value.value) == 2

    def test_tuple_positional_types(self) -> None:
        schema = parse_hcl_type_string("tuple([string, number])")
        value = schema.validate(["x", 5])
        assert value.value[0].value == "x"
        assert value.value[1].value == 5

    def test_any_is_dynamic(self) -> None:
        assert parse_hcl_type_string("any") == CtyDynamic()


# 📄⚙️🔚
