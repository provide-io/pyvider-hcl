#!/usr/bin/env python3
"""Memray stress test for pretty printing hot path."""

import os

os.environ["PLUGIN_LOG_LEVEL"] = "ERROR"

import io
import sys

from pyvider.cty import CtyBool, CtyList, CtyMap, CtyNumber, CtyObject, CtyString, CtyValue
from pyvider.hcl.output.formatting import _pretty_print_cty_recursive


def build_nested_value() -> CtyValue:
    """Build a complex nested CtyValue for stress testing."""
    inner_obj_type = CtyObject(
        {
            "name": CtyString(),
            "age": CtyNumber(),
            "active": CtyBool(),
        }
    )
    list_type = CtyList(element_type=inner_obj_type)
    outer_type = CtyObject(
        {
            "users": list_type,
            "count": CtyNumber(),
            "metadata": CtyMap(element_type=CtyString()),
        }
    )
    outer_value = {
        "users": [
            {"name": "alice", "age": 30, "active": True},
            {"name": "bob", "age": 25, "active": False},
            {"name": "charlie", "age": 40, "active": True},
        ],
        "count": 3,
        "metadata": {"env": "production", "region": "us-west-2", "version": "1.2.3"},
    }
    return CtyValue(vtype=outer_type, value=outer_value)


def build_simple_values() -> list[CtyValue]:
    """Build simple CtyValues for variety."""
    return [
        CtyValue(vtype=CtyString(), value="hello world"),
        CtyValue(vtype=CtyNumber(), value=42),
        CtyValue(vtype=CtyBool(), value=True),
        CtyValue(vtype=CtyList(element_type=CtyString()), value=["a", "b", "c"]),
        CtyValue(vtype=CtyMap(element_type=CtyNumber()), value={"x": 1, "y": 2, "z": 3}),
    ]


def main() -> None:
    nested = build_nested_value()
    simples = build_simple_values()

    # Redirect stdout to suppress output during stress test
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()

    try:
        # 5K calls with complex nested objects (exercises recursive path)
        for _ in range(5_000):
            _pretty_print_cty_recursive(nested, 0)

        # 5K calls with simple values for variety
        for i in range(5_000):
            val = simples[i % len(simples)]
            _pretty_print_cty_recursive(val, 0)
    finally:
        sys.stdout = old_stdout

    print("pretty_print stress complete: 10K calls")


if __name__ == "__main__":
    main()
