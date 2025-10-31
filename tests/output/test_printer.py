#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""TODO: Add module docstring."""

import textwrap
from typing import Any

import pytest

from pyvider.cty import (
    CtyBool,
    CtyDynamic,
    CtyList,
    CtyMap,
    CtyNumber,
    CtyObject,
    CtyString,
    CtyTuple,
    CtyValue,
)
from pyvider.hcl.output import pretty_print_cty


def test_pretty_print_cty_string(capsys: pytest.CaptureFixture[str]) -> None:
    """
    Tests that pretty_print_cty correctly prints a CtyString.
    """
    cty_val = CtyValue(value="hello", vtype=CtyString())
    pretty_print_cty(cty_val)
    captured = capsys.readouterr()
    assert captured.out.strip() == '"hello"'


def test_pretty_print_cty_number(capsys: pytest.CaptureFixture[str]) -> None:
    """
    Tests that pretty_print_cty correctly prints a CtyNumber.
    """
    cty_val = CtyValue(value=123, vtype=CtyNumber())
    pretty_print_cty(cty_val)
    captured = capsys.readouterr()
    assert captured.out.strip() == "123"


def test_pretty_print_cty_bool(capsys: pytest.CaptureFixture[str]) -> None:
    """
    Tests that pretty_print_cty correctly prints a CtyBool.
    """
    cty_val = CtyValue(value=True, vtype=CtyBool())
    pretty_print_cty(cty_val)
    captured = capsys.readouterr()
    assert captured.out.strip() == "true"


def test_pretty_print_cty_list(capsys: pytest.CaptureFixture[str]) -> None:
    """
    Tests that pretty_print_cty correctly prints a CtyList.
    """
    cty_val = CtyValue(value=["a", "b", "c"], vtype=CtyList(element_type=CtyString()))
    pretty_print_cty(cty_val)
    captured = capsys.readouterr()
    expected = textwrap.dedent("""    [
      "a",
      "b",
      "c"
    ]""").strip()
    assert captured.out.strip() == expected


def test_pretty_print_cty_map(capsys: pytest.CaptureFixture[str]) -> None:
    """
    Tests that pretty_print_cty correctly prints a CtyMap.
    """
    cty_val = CtyValue(value={"a": 1, "b": 2}, vtype=CtyMap(element_type=CtyNumber()))
    pretty_print_cty(cty_val)
    captured = capsys.readouterr()
    expected = textwrap.dedent("""    {
      "a": 1,
      "b": 2
    }""").strip()
    assert captured.out.strip() == expected


def test_pretty_print_cty_object(capsys: pytest.CaptureFixture[str]) -> None:
    """
    Tests that pretty_print_cty correctly prints a CtyObject.
    """
    cty_val = CtyValue(
        value={"name": "John", "age": 30}, vtype=CtyObject({"name": CtyString(), "age": CtyNumber()})
    )
    pretty_print_cty(cty_val)
    captured = capsys.readouterr()
    expected = textwrap.dedent("""    {
      "name": "John",
      "age": 30
    }""").strip()
    assert captured.out.strip() == expected


def test_pretty_print_cty_tuple(capsys: pytest.CaptureFixture[str]) -> None:
    """
    Tests that pretty_print_cty correctly prints a CtyTuple.
    """
    cty_val = CtyValue(value=["hello", 123], vtype=CtyTuple(tuple([CtyString(), CtyNumber()])))
    pretty_print_cty(cty_val)
    captured = capsys.readouterr()
    expected = textwrap.dedent("""    [
      "hello",
      123
    ]""").strip()
    assert captured.out.strip() == expected


def test_pretty_print_cty_dynamic(capsys: pytest.CaptureFixture[str]) -> None:
    """
    Tests that pretty_print_cty correctly prints a CtyDynamic.
    """
    cty_val = CtyValue(value="dynamic", vtype=CtyDynamic())
    pretty_print_cty(cty_val)
    captured = capsys.readouterr()
    assert captured.out.strip() == "dynamic"


def test_pretty_print_cty_unknown_type(capsys: pytest.CaptureFixture[str]) -> None:
    """
    Tests that pretty_print_cty handles unknown CtyTypes by falling back to str().
    """
    from pyvider.cty import CtyType

    # Create a custom CtyType for testing the fallback path
    class CustomCtyType(CtyType):
        def validate(self, value: Any) -> CtyValue[Any]:
            return CtyValue(vtype=self, value=value)

        def equal(self, other: "CtyType") -> bool:
            return isinstance(other, CustomCtyType)

        def usable_as(self, other: "CtyType") -> bool:
            return isinstance(other, CustomCtyType)

        def _to_wire_json(self) -> dict[str, str]:
            return {"type": "custom"}

    custom_type = CustomCtyType()
    cty_val = CtyValue(value="custom_value", vtype=custom_type)
    pretty_print_cty(cty_val)
    captured = capsys.readouterr()
    assert captured.out.strip() == "custom_value"


# 📄⚙️🔚
