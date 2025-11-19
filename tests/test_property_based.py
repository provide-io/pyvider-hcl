#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Property-based tests using Hypothesis for HCL parsing and factories."""

from hypothesis import HealthCheck, given, settings, strategies as st
import pytest

from pyvider.cty import CtyBool, CtyList, CtyMap, CtyNumber, CtyObject, CtyString
from pyvider.hcl.factories import (
    HclTypeParsingError,
    create_resource_cty,
    create_variable_cty,
    parse_hcl_type_string,
)
from pyvider.hcl.parser import auto_infer_cty_type, parse_hcl_to_cty

# Strategy for valid HCL primitive type strings
primitive_types = st.sampled_from(["string", "number", "bool", "any"])


# Strategy for valid Python identifiers (for variable/resource names)
valid_identifiers = st.from_regex(r"^[a-zA-Z_][a-zA-Z0-9_]{0,30}$", fullmatch=True)


class TestPropertyBasedTypeStringParsing:
    """Property-based tests for HCL type string parsing."""

    @given(type_str=primitive_types)
    @settings(suppress_health_check=[HealthCheck.differing_executors])
    def test_primitive_types_always_parse(self, type_str: str) -> None:
        """Any valid primitive type string should parse successfully."""

        result = parse_hcl_type_string(type_str)
        assert result is not None
        # Should return one of the known primitive types
        # Note: "any" maps to CtyDynamic
        assert type(result).__name__ in ["CtyString", "CtyNumber", "CtyBool", "CtyDynamic"]

    @given(element_type=primitive_types)
    @settings(suppress_health_check=[HealthCheck.differing_executors])
    def test_list_of_primitive_types_always_parse(self, element_type: str) -> None:
        """List of any primitive type should parse successfully."""
        type_str = f"list({element_type})"
        result = parse_hcl_type_string(type_str)
        assert isinstance(result, CtyList)

    @given(element_type=primitive_types)
    @settings(suppress_health_check=[HealthCheck.differing_executors])
    def test_map_of_primitive_types_always_parse(self, element_type: str) -> None:
        """Map of any primitive type should parse successfully."""
        type_str = f"map({element_type})"
        result = parse_hcl_type_string(type_str)
        assert isinstance(result, CtyMap)

    @given(
        attr_name=valid_identifiers,
        attr_type=primitive_types,
    )
    @settings(suppress_health_check=[HealthCheck.differing_executors])
    def test_object_with_single_attribute_parses(self, attr_name: str, attr_type: str) -> None:
        """Object with a single valid attribute should parse."""
        type_str = f"object({{{attr_name}={attr_type}}})"
        result = parse_hcl_type_string(type_str)
        assert isinstance(result, CtyObject)
        assert attr_name in result.attribute_types

    @given(
        random_str=st.text(min_size=1, max_size=20).filter(
            lambda x: x.strip() not in ["", "string", "number", "bool", "any"]
        )
    )
    @settings(suppress_health_check=[HealthCheck.differing_executors])
    def test_invalid_type_strings_raise_error(self, random_str: str) -> None:
        """Random strings that aren't valid types should raise HclTypeParsingError."""
        # Filter out strings that might accidentally be valid
        if any(
            keyword in random_str.lower()
            for keyword in ["list", "map", "object", "string", "number", "bool", "any"]
        ):
            pytest.skip("String contains valid type keywords")

        with pytest.raises(HclTypeParsingError):
            parse_hcl_type_string(random_str)


class TestPropertyBasedVariableCreation:
    """Property-based tests for variable creation."""

    @given(
        var_name=valid_identifiers,
        type_str=primitive_types,
    )
    @settings(suppress_health_check=[HealthCheck.differing_executors])
    def test_valid_variable_names_and_types_succeed(self, var_name: str, type_str: str) -> None:
        """Any valid identifier and primitive type should create a variable."""
        result = create_variable_cty(var_name, type_str)
        assert result is not None
        assert "variable" in result.value

    @given(
        var_name=valid_identifiers,
        default_value=st.text(min_size=0, max_size=100),
    )
    @settings(suppress_health_check=[HealthCheck.differing_executors])
    def test_string_variables_with_any_default_value(self, var_name: str, default_value: str) -> None:
        """String variables should accept any string as default."""
        result = create_variable_cty(var_name, "string", default_py=default_value)
        assert result is not None

    @given(
        var_name=valid_identifiers,
        default_value=st.integers(min_value=-1000000, max_value=1000000),
    )
    @settings(suppress_health_check=[HealthCheck.differing_executors])
    def test_number_variables_with_integer_defaults(self, var_name: str, default_value: int) -> None:
        """Number variables should accept any integer as default."""
        result = create_variable_cty(var_name, "number", default_py=default_value)
        assert result is not None

    @given(
        var_name=valid_identifiers,
        default_value=st.booleans(),
    )
    @settings(suppress_health_check=[HealthCheck.differing_executors])
    def test_bool_variables_with_boolean_defaults(self, var_name: str, default_value: bool) -> None:
        """Bool variables should accept boolean defaults."""
        result = create_variable_cty(var_name, "bool", default_py=default_value)
        assert result is not None


class TestPropertyBasedResourceCreation:
    """Property-based tests for resource creation."""

    @given(
        r_type=valid_identifiers,
        r_name=valid_identifiers,
        attr_value=st.text(min_size=0, max_size=100),
    )
    @settings(suppress_health_check=[HealthCheck.differing_executors])
    def test_resource_with_string_attributes(self, r_type: str, r_name: str, attr_value: str) -> None:
        """Resources should handle string attributes correctly."""
        result = create_resource_cty(r_type, r_name, {"attr": attr_value}, {"attr": "string"})
        assert result is not None
        assert "resource" in result.value

    @given(
        r_type=valid_identifiers.filter(lambda x: x.strip() != ""),
        r_name=valid_identifiers.filter(lambda x: x.strip() != ""),
    )
    @settings(suppress_health_check=[HealthCheck.differing_executors])
    def test_resource_with_empty_attributes(self, r_type: str, r_name: str) -> None:
        """Resources can be created with no attributes."""
        result = create_resource_cty(r_type, r_name, {})
        assert result is not None


class TestPropertyBasedAutoInference:
    """Property-based tests for auto type inference."""

    @given(value=st.text())
    @settings(suppress_health_check=[HealthCheck.differing_executors])
    def test_string_inference(self, value: str) -> None:
        """Any string should be inferred as CtyString."""
        result = auto_infer_cty_type({"key": value})
        assert result.value["key"].type == CtyString()

    @given(value=st.integers())
    @settings(suppress_health_check=[HealthCheck.differing_executors])
    def test_integer_inference(self, value: int) -> None:
        """Any integer should be inferred as CtyNumber."""
        result = auto_infer_cty_type({"key": value})
        assert result.value["key"].type == CtyNumber()

    @given(value=st.booleans())
    @settings(suppress_health_check=[HealthCheck.differing_executors])
    def test_boolean_inference(self, value: bool) -> None:
        """Any boolean should be inferred as CtyBool."""
        result = auto_infer_cty_type({"key": value})
        assert result.value["key"].type == CtyBool()

    @given(values=st.lists(st.text(), min_size=0, max_size=10))
    @settings(suppress_health_check=[HealthCheck.differing_executors])
    def test_list_inference(self, values: list[str]) -> None:
        """Any list should be inferred as CtyList."""
        result = auto_infer_cty_type({"key": values})
        assert isinstance(result.value["key"].type, CtyList)

    @given(
        data=st.dictionaries(
            keys=valid_identifiers,
            values=st.one_of(st.text(), st.integers(), st.booleans()),
            min_size=0,
            max_size=5,
        )
    )
    @settings(suppress_health_check=[HealthCheck.differing_executors])
    def test_dict_inference(self, data: dict) -> None:
        """Any dict should be inferred as CtyObject."""
        result = auto_infer_cty_type(data)
        assert isinstance(result.type, CtyObject)


class TestPropertyBasedHclParsing:
    """Property-based tests for HCL parsing."""

    @settings(deadline=None)
    @given(
        value=st.text(
            alphabet=st.characters(blacklist_categories=("Cs", "Cc"), blacklist_characters='"\\\n\r\t'),
            min_size=0,
            max_size=50,
        )
    )
    def test_simple_key_value_parsing(self, value: str) -> None:
        """Simple key=value HCL should always parse."""
        # Use safe characters to avoid HCL parsing issues
        hcl_content = f'test_key = "{value}"'
        result = parse_hcl_to_cty(hcl_content)
        assert result is not None
        assert "test_key" in result.value

    @given(number=st.integers(min_value=-1000000, max_value=1000000))
    def test_numeric_value_parsing(self, number: int) -> None:
        """HCL with numeric values should parse correctly."""
        hcl_content = f"test_number = {number}"
        result = parse_hcl_to_cty(hcl_content)
        assert result is not None
        assert "test_number" in result.value

    @given(bool_value=st.booleans())
    def test_boolean_value_parsing(self, bool_value: bool) -> None:
        """HCL with boolean values should parse correctly."""
        hcl_content = f"test_bool = {str(bool_value).lower()}"
        result = parse_hcl_to_cty(hcl_content)
        assert result is not None
        assert "test_bool" in result.value


# 📄⚙️🔚
