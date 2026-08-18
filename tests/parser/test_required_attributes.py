#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Tests for required-attribute enforcement on schema-validated parses.

pyvider-cty stopped rejecting nulls for non-optional object attributes and left
that rule to the schema layer, so pyvider-hcl applies it when a schema is
supplied to :func:`parse_hcl_to_cty`.
"""

import pytest

from pyvider.cty import (
    CtyBool,
    CtyList,
    CtyMap,
    CtyNumber,
    CtyObject,
    CtySet,
    CtyString,
    CtyTuple,
)
from pyvider.hcl import HclParsingError, parse_hcl_to_cty
from pyvider.hcl.parser.required import null_required_attributes


def _cty_accepts_null_required() -> bool:
    """Whether the installed pyvider-cty leaves required-ness to the caller.

    pyvider-cty 0.4.x rejects a null non-optional attribute inside
    ``CtyObject.validate``; 0.5.x records it and defers to the schema layer.
    Either way a schema-validated parse fails, but only on 0.5.x can a value
    carrying such a null be constructed to hand to the checker directly.
    """
    try:
        CtyObject({"a": CtyString()}).validate({"a": None})
    except Exception:
        return False
    return True


requires_deferred_requiredness = pytest.mark.skipif(
    not _cty_accepts_null_required(),
    reason="installed pyvider-cty rejects null required attributes itself",
)


class TestRequiredAttributeParsing:
    """A null in a required attribute fails a schema-validated parse."""

    def test_null_required_attribute_rejected(self) -> None:
        schema = CtyObject({"name": CtyString(), "port": CtyNumber()})
        with pytest.raises(HclParsingError, match="port"):
            parse_hcl_to_cty('name = "x"\nport = null', schema=schema)

    def test_error_names_the_attribute(self) -> None:
        schema = CtyObject({"name": CtyString(), "port": CtyNumber()})
        with pytest.raises(HclParsingError) as exc_info:
            parse_hcl_to_cty('name = "x"\nport = null', schema=schema)
        assert "port" in str(exc_info.value)

    def test_optional_attribute_may_be_null(self) -> None:
        schema = CtyObject(
            {"name": CtyString(), "port": CtyNumber()},
            optional_attributes=frozenset({"port"}),
        )
        value = parse_hcl_to_cty('name = "x"\nport = null', schema=schema)
        assert value.value["port"].is_null

    def test_all_attributes_present_passes(self) -> None:
        schema = CtyObject({"name": CtyString(), "port": CtyNumber()})
        value = parse_hcl_to_cty('name = "x"\nport = 8080', schema=schema)
        assert value.value["port"].value == 8080

    def test_null_inside_nested_object_rejected(self) -> None:
        schema = CtyObject({"cfg": CtyObject({"host": CtyString()})})
        with pytest.raises(HclParsingError, match=r"cfg\.host"):
            parse_hcl_to_cty("cfg = { host = null }", schema=schema)

    def test_null_inside_list_of_objects_rejected(self) -> None:
        schema = CtyObject({"items": CtyList(element_type=CtyObject({"id": CtyString()}))})
        with pytest.raises(HclParsingError, match=r"items\[0\]\.id"):
            parse_hcl_to_cty("items = [{ id = null }]", schema=schema)

    def test_multiple_nulls_all_reported(self) -> None:
        schema = CtyObject({"a": CtyString(), "b": CtyString()})
        with pytest.raises(HclParsingError) as exc_info:
            parse_hcl_to_cty("a = null\nb = null", schema=schema)
        message = str(exc_info.value)
        assert "a" in message
        assert "b" in message

    def test_inference_path_allows_null(self) -> None:
        """Without a schema there is no requiredness to enforce."""
        value = parse_hcl_to_cty("port = null")
        assert value.value["port"].is_null


@requires_deferred_requiredness
class TestNullRequiredAttributes:
    """Direct tests for the checker itself."""

    def test_empty_for_valid_value(self) -> None:
        schema = CtyObject({"name": CtyString()})
        assert null_required_attributes(schema.validate({"name": "x"})) == []

    def test_reports_top_level_attribute(self) -> None:
        schema = CtyObject({"name": CtyString()})
        assert null_required_attributes(schema.validate({"name": None})) == ["name"]

    def test_reports_map_path(self) -> None:
        schema = CtyObject({"m": CtyMap(element_type=CtyObject({"id": CtyString()}))})
        found = null_required_attributes(schema.validate({"m": {"k": {"id": None}}}))
        assert found == ['m["k"].id']

    def test_reports_tuple_path(self) -> None:
        schema = CtyObject({"t": CtyTuple((CtyObject({"id": CtyString()}),))})
        found = null_required_attributes(schema.validate({"t": [{"id": None}]}))
        assert found == ["t[0].id"]

    def test_reports_set_path(self) -> None:
        schema = CtyObject({"s": CtySet(element_type=CtyObject({"id": CtyString()}))})
        found = null_required_attributes(schema.validate({"s": [{"id": None}]}))
        assert found == ["s[*].id"]

    def test_null_container_is_not_walked(self) -> None:
        schema = CtyObject(
            {"cfg": CtyObject({"host": CtyString()})},
            optional_attributes=frozenset({"cfg"}),
        )
        assert null_required_attributes(schema.validate({"cfg": None})) == []

    def test_non_object_root(self) -> None:
        assert null_required_attributes(CtyBool().validate(True)) == []


# 📄⚙️🔚
