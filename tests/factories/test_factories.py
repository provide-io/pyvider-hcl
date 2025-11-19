#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""TODO: Add module docstring."""

from typing import Any
import unittest

from pyvider.cty import (
    CtyBool,
    CtyDynamic,
    CtyList,
    CtyMap,
    CtyNumber,
    CtyObject,
    CtyString,
    CtyValue,
)
from pyvider.cty.conversion import cty_to_native
from pyvider.hcl.factories import (
    HclFactoryError,
    HclTypeParsingError,
    create_resource_cty,
    create_variable_cty,
    parse_hcl_type_string,
)


class TestParseHclTypeString(unittest.TestCase):
    def test_parse_primitive_types(self) -> None:
        self.assertEqual(parse_hcl_type_string("string"), CtyString())
        self.assertEqual(parse_hcl_type_string(" number "), CtyNumber())
        self.assertEqual(parse_hcl_type_string("bool"), CtyBool())
        self.assertEqual(parse_hcl_type_string("any"), CtyDynamic())

    def test_parse_simple_list_and_map_types(self) -> None:
        self.assertEqual(parse_hcl_type_string("list(string)"), CtyList(element_type=CtyString()))
        self.assertEqual(parse_hcl_type_string("map(number)"), CtyMap(element_type=CtyNumber()))

    def test_parse_nested_types(self) -> None:
        self.assertEqual(
            parse_hcl_type_string("list(map(number))"), CtyList(element_type=CtyMap(element_type=CtyNumber()))
        )
        expected = CtyObject(
            {"data": CtyMap(element_type=CtyObject({"value": CtyString(), "flag": CtyBool()}))}
        )
        self.assertEqual(
            parse_hcl_type_string("object({data=map(object({value=string,flag=bool}))})"), expected
        )

    def test_invalid_type_strings(self) -> None:
        invalid_strings = ["foo", "string()", "list)", "list(", "list(string", "object({name=string,})"]
        for type_str in invalid_strings:
            with self.assertRaises(HclTypeParsingError, msg=f"Expected error for: '{type_str}'"):
                parse_hcl_type_string(type_str)

    def test_malformed_object_attributes(self) -> None:
        # FIX: The test now expects the correct error message from the parser.
        with self.assertRaisesRegex(HclTypeParsingError, "Unknown or malformed type string"):
            parse_hcl_type_string("object({name=string age=number})")

    def test_empty_list_type(self) -> None:
        """Test that empty list type raises error."""
        with self.assertRaisesRegex(HclTypeParsingError, "List type string is empty"):
            parse_hcl_type_string("list()")

    def test_empty_map_type(self) -> None:
        """Test that empty map type raises error."""
        with self.assertRaisesRegex(HclTypeParsingError, "Map type string is empty"):
            parse_hcl_type_string("map()")

    def test_object_without_braces(self) -> None:
        """Test that object type without braces raises error."""
        with self.assertRaisesRegex(HclTypeParsingError, "must be enclosed in"):
            parse_hcl_type_string("object(name=string)")

    def test_object_empty_braces(self) -> None:
        """Test that object with empty braces works."""
        result = parse_hcl_type_string("object({})")
        self.assertEqual(result, CtyObject({}))

    def test_object_whitespace_only(self) -> None:
        """Test that object with whitespace only works."""
        result = parse_hcl_type_string("object({   })")
        self.assertEqual(result, CtyObject({}))

    def test_object_trailing_comma(self) -> None:
        """Test that object with trailing comma raises error."""
        with self.assertRaisesRegex(HclTypeParsingError, "Trailing comma"):
            parse_hcl_type_string("object({name=string,})")

    def test_object_empty_attribute_part(self) -> None:
        """Test that object with empty attribute part raises error."""
        with self.assertRaisesRegex(HclTypeParsingError, "Empty attribute part"):
            parse_hcl_type_string("object({name=string,,other=bool})")

    def test_object_attribute_without_equals(self) -> None:
        """Test that object attribute without = raises error."""
        with self.assertRaisesRegex(HclTypeParsingError, "missing '='"):
            parse_hcl_type_string("object({namestring})")

    def test_object_attribute_empty_name(self) -> None:
        """Test that object attribute with empty name raises error."""
        with self.assertRaisesRegex(HclTypeParsingError, "Invalid attribute name or type"):
            parse_hcl_type_string("object({=string})")

    def test_object_attribute_empty_type(self) -> None:
        """Test that object attribute with empty type raises error."""
        with self.assertRaisesRegex(HclTypeParsingError, "Invalid attribute name or type"):
            parse_hcl_type_string("object({name=})")


class TestCreateVariableCty(unittest.TestCase):
    def _assert_variable_structure(
        self, var_cty_val: CtyValue, var_name: str, expected_attrs_values_py: dict[str, Any]
    ) -> None:
        self.assertIsInstance(var_cty_val, CtyValue)
        self.assertIsInstance(var_cty_val.type, CtyObject)
        self.assertIn("variable", var_cty_val.value)
        variable_list_val = var_cty_val.value["variable"]
        self.assertIsInstance(variable_list_val.type, CtyList)
        self.assertEqual(len(variable_list_val.value), 1)
        variable_block_val = variable_list_val.value[0]
        self.assertIn(var_name, variable_block_val.value)
        the_var_actual_attrs_val = variable_block_val.value[var_name]
        # FIX: Convert the CtyValue to a native Python dict before comparison.
        self.assertEqual(cty_to_native(the_var_actual_attrs_val), expected_attrs_values_py)

    def test_create_string_variable(self) -> None:
        var_name = "my_string"
        attrs = {"type": "string", "default": "hello world", "description": "A test string variable"}
        var_cty = create_variable_cty(
            var_name, attrs["type"], default_py=attrs["default"], description=attrs["description"]
        )
        self._assert_variable_structure(var_cty, var_name, attrs)

    def test_create_list_variable(self) -> None:
        var_name = "my_list"
        attrs = {"type": "list(bool)", "default": [True, False], "nullable": True}
        var_cty = create_variable_cty(
            var_name, attrs["type"], default_py=attrs["default"], nullable=attrs["nullable"]
        )
        self._assert_variable_structure(var_cty, var_name, attrs)

    def test_default_value_type_mismatch(self) -> None:
        with self.assertRaisesRegex(HclFactoryError, "Default value .* not compatible"):
            create_variable_cty("test_var", "number", default_py="not-a-number")

    def test_invalid_variable_name_empty(self) -> None:
        """Test that empty variable name raises error."""
        with self.assertRaisesRegex(HclFactoryError, "Invalid variable name"):
            create_variable_cty("", "string")

    def test_invalid_variable_name_not_identifier(self) -> None:
        """Test that invalid variable name raises error."""
        with self.assertRaisesRegex(HclFactoryError, "Invalid variable name"):
            create_variable_cty("my-var-name", "string")

    def test_invalid_type_string_for_variable(self) -> None:
        """Test that invalid type string raises error."""
        with self.assertRaisesRegex(HclFactoryError, "Invalid type string"):
            create_variable_cty("my_var", "invalid_type")

    def test_create_variable_with_sensitive(self) -> None:
        """Test creating a variable with sensitive flag."""
        var_name = "my_secret"
        attrs = {"type": "string", "sensitive": True}
        var_cty = create_variable_cty(var_name, attrs["type"], sensitive=True)
        self._assert_variable_structure(var_cty, var_name, attrs)

    def test_create_variable_with_all_params(self) -> None:
        """Test creating a variable with all optional parameters."""
        var_name = "full_var"
        attrs = {
            "type": "string",
            "default": "test",
            "description": "A full test",
            "sensitive": False,
            "nullable": True,
        }
        var_cty = create_variable_cty(
            var_name,
            attrs["type"],
            default_py=attrs["default"],
            description=attrs["description"],
            sensitive=attrs["sensitive"],
            nullable=attrs["nullable"],
        )
        self._assert_variable_structure(var_cty, var_name, attrs)


class TestCreateResourceCty(unittest.TestCase):
    def _assert_resource_structure(
        self,
        res_cty_val: CtyValue,
        expected_r_type: str,
        expected_r_name: str,
        expected_attrs_values_py: dict[str, Any],
    ) -> None:
        self.assertIsInstance(res_cty_val, CtyValue)
        self.assertIn("resource", res_cty_val.value)
        r_type_block_val = res_cty_val.value["resource"].value[0]
        self.assertIn(expected_r_type, r_type_block_val.value)
        r_name_block_val = r_type_block_val.value[expected_r_type].value[0]
        self.assertIn(expected_r_name, r_name_block_val.value)
        actual_attributes_obj_val = r_name_block_val.value[expected_r_name]
        # FIX: Convert the CtyValue to a native Python dict before comparison.
        self.assertEqual(cty_to_native(actual_attributes_obj_val), expected_attrs_values_py)

    def test_create_resource_with_schema(self) -> None:
        r_type = "local_file"
        r_name = "my_output"
        attrs_py = {"filename": "output.txt", "content": "Test content"}
        attrs_schema_py = {"filename": "string", "content": "string"}
        res_cty = create_resource_cty(r_type, r_name, attrs_py, attrs_schema_py)
        self._assert_resource_structure(res_cty, r_type, r_name, attrs_py)

    def test_create_resource_without_schema_auto_infer(self) -> None:
        r_type = "null_resource"
        r_name = "placeholder"
        attrs_py = {"id": "fake_id", "triggers": {"key": "value", "num": 123.0}}
        res_cty = create_resource_cty(r_type, r_name, attrs_py)
        self._assert_resource_structure(res_cty, r_type, r_name, attrs_py)

    def test_resource_attribute_value_incompatible_with_schema(self) -> None:
        with self.assertRaisesRegex(HclFactoryError, "attributes .* not compatible"):
            create_resource_cty("aws_instance", "my_vm", {"count": "not-a-number"}, {"count": "number"})

    def test_missing_attribute_type_in_schema(self) -> None:
        with self.assertRaisesRegex(HclFactoryError, "Missing type string .* for attribute 'actual_attr'"):
            create_resource_cty(
                "my_resource",
                "test_missing",
                attributes_py={"actual_attr": "some_value"},
                attributes_schema_py={},
            )

    def test_empty_resource_type(self) -> None:
        """Test that empty resource type raises error."""
        with self.assertRaisesRegex(HclFactoryError, "Resource type .* cannot be empty"):
            create_resource_cty("", "my_name", {"attr": "value"})

    def test_whitespace_resource_type(self) -> None:
        """Test that whitespace-only resource type raises error."""
        with self.assertRaisesRegex(HclFactoryError, "Resource type .* cannot be empty"):
            create_resource_cty("   ", "my_name", {"attr": "value"})

    def test_empty_resource_name(self) -> None:
        """Test that empty resource name raises error."""
        with self.assertRaisesRegex(HclFactoryError, "Resource name .* cannot be empty"):
            create_resource_cty("aws_instance", "", {"attr": "value"})

    def test_whitespace_resource_name(self) -> None:
        """Test that whitespace-only resource name raises error."""
        with self.assertRaisesRegex(HclFactoryError, "Resource name .* cannot be empty"):
            create_resource_cty("aws_instance", "   ", {"attr": "value"})

    def test_invalid_type_string_in_schema(self) -> None:
        """Test that invalid type string in schema raises error."""
        with self.assertRaisesRegex(HclFactoryError, "Invalid type string for attribute"):
            create_resource_cty(
                "my_resource", "test_invalid", {"my_attr": "value"}, {"my_attr": "not_a_valid_type"}
            )


# 📄⚙️🔚
