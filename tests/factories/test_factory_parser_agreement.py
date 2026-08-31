#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""A factory and the parser describe the same resource the same way.

`create_resource_cty` wrapped the resource *name* in a list as well as the
resource type -- `resource[0].aws_instance[0].web` -- where python-hcl2 8.x, and
so this package's parser, produce `resource[0].aws_instance.web`. A value built
by the factory therefore could not be compared with, merged into, or substituted
for one that had been parsed, though both claimed to describe the same resource.

These tests hold the two outputs against each other rather than against a
hard-coded shape, so neither can drift without the other.
"""

import hcl2
import pytest

from pyvider.hcl import (
    create_resource_cty,
    create_variable_cty,
    format_cty,
    load_hcl_data,
    parse_hcl_to_cty,
)

RESOURCES = [
    ("aws_instance", "web", {"ami": "ami-123"}, {"ami": "string"}),
    (
        "local_file",
        "out",
        {"filename": "o.txt", "content": "x"},
        {"filename": "string", "content": "string"},
    ),
    ("null_resource", "placeholder", {"id": "fake"}, {"id": "string"}),
]


def _hcl_for(r_type: str, r_name: str, attributes: dict[str, str]) -> str:
    body = "".join(f'  {name} = "{value}"\n' for name, value in attributes.items())
    return f'resource "{r_type}" "{r_name}" {{\n{body}}}\n'


class TestResourceAgreement:
    """The factory's resource shape is the parser's resource shape."""

    @pytest.mark.parametrize(("r_type", "r_name", "attributes", "schema"), RESOURCES)
    def test_rendered_value_matches(
        self, r_type: str, r_name: str, attributes: dict[str, str], schema: dict[str, str]
    ) -> None:
        built = create_resource_cty(r_type, r_name, attributes, schema)
        parsed = parse_hcl_to_cty(_hcl_for(r_type, r_name, attributes))
        assert format_cty(built) == format_cty(parsed)

    @pytest.mark.parametrize(("r_type", "r_name", "attributes", "schema"), RESOURCES)
    def test_type_matches(
        self, r_type: str, r_name: str, attributes: dict[str, str], schema: dict[str, str]
    ) -> None:
        built = create_resource_cty(r_type, r_name, attributes, schema)
        parsed = parse_hcl_to_cty(_hcl_for(r_type, r_name, attributes))
        assert built.type == parsed.type

    def test_the_name_is_not_wrapped_in_a_list(self) -> None:
        """The specific regression: one list, at the `resource` level only."""
        built = create_resource_cty("aws_instance", "web", {"ami": "a"}, {"ami": "string"})
        by_type = built.value["resource"].value[0].value["aws_instance"]
        assert "web" in by_type.value

    def test_shape_matches_python_hcl2(self) -> None:
        """Both agree with the library the parser is built on."""
        raw = load_hcl_data(_hcl_for("aws_instance", "web", {"ami": "ami-123"}))
        assert raw == {"resource": [{"aws_instance": {"web": {"ami": "ami-123"}}}]}

    def test_upstream_still_nests_this_way(self) -> None:
        """Guards the assumption above against a python-hcl2 change."""
        raw = hcl2.loads(_hcl_for("aws_instance", "web", {"ami": "ami-123"}))
        by_type = raw["resource"][0]['"aws_instance"']
        assert isinstance(by_type, dict)
        assert '"web"' in by_type


class TestVariableAgreement:
    """The variable factory already agreed; this keeps it that way."""

    def test_rendered_value_matches(self) -> None:
        built = create_variable_cty(name="region", type_str="string", default_py="us-west-2")
        parsed = parse_hcl_to_cty('variable "region" {\n  type = string\n  default = "us-west-2"\n}\n')
        assert format_cty(built) == format_cty(parsed)

    def test_single_label_is_a_plain_key(self) -> None:
        built = create_variable_cty(name="region", type_str="string")
        assert "region" in built.value["variable"].value[0].value


# 📄⚙️🔚
