#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright (c) 2026 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Memray stress test for HCL type parsing hot path."""

import os

os.environ["PLUGIN_LOG_LEVEL"] = "ERROR"

from pyvider.hcl.factories.types import parse_hcl_type_string

PRIMITIVES = ["string", "number", "bool", "any"]
LISTS = ["list(string)", "list(number)", "list(bool)"]
MAPS = ["map(string)", "map(number)", "map(bool)"]
OBJECTS = [
    "object({name=string, age=number})",
    "object({enabled=bool, label=string})",
    "object({host=string, port=number, tls=bool})",
]
NESTED = [
    "list(map(object({a=string,b=number})))",
    "map(list(string))",
    "object({items=list(map(string)),count=number})",
]

ALL_SIMPLE = PRIMITIVES + LISTS + MAPS + OBJECTS


def main() -> None:
    # 10K calls with varied simple inputs
    for i in range(10_000):
        type_str = ALL_SIMPLE[i % len(ALL_SIMPLE)]
        parse_hcl_type_string(type_str)

    # 5K calls with deeply nested types
    for i in range(5_000):
        type_str = NESTED[i % len(NESTED)]
        parse_hcl_type_string(type_str)

    print("type_parsing stress complete: 15K calls")


if __name__ == "__main__":
    main()
