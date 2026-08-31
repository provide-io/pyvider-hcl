#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Emitting HCL blocks, which `cty_to_hcl` cannot do on its own.

Nothing in a `CtyValue` records that it was written as a block rather than as an
object, so block-ness cannot be recovered from one. `cty_to_hcl_block` takes the
block type and labels from the caller instead of guessing, and puts python-hcl2's
`__is_block__` marker on the innermost body -- which is what tells `hcl2.dumps`
where the labels stop and the attributes start.
"""

import pytest

from pyvider.cty import CtyList, CtyString, CtyValue
from pyvider.cty.marks import CtyMark
from pyvider.hcl import (
    HclEmitError,
    create_resource_cty,
    cty_to_hcl_block,
    cty_to_hcl_block_data,
    load_hcl_data,
    parse_hcl_to_cty,
)


class TestBlockEmission:
    """Each label arity renders the shape Terraform writes."""

    def test_two_labels(self) -> None:
        body = parse_hcl_to_cty('ami = "ami-123"\n')
        assert cty_to_hcl_block("resource", ("aws_instance", "web"), body) == (
            'resource "aws_instance" "web" {\n  ami = "ami-123"\n}\n'
        )

    def test_one_label(self) -> None:
        body = parse_hcl_to_cty('default = "us-west-2"\n')
        assert cty_to_hcl_block("variable", ("region",), body) == (
            'variable "region" {\n  default = "us-west-2"\n}\n'
        )

    def test_no_labels(self) -> None:
        body = parse_hcl_to_cty('prefix = "app"\n')
        assert cty_to_hcl_block("locals", (), body) == 'locals {\n  prefix = "app"\n}\n'

    def test_labels_are_quoted(self) -> None:
        """An unquoted label emits as a bare identifier, which Terraform rejects."""
        rendered = cty_to_hcl_block("resource", ("aws_instance", "web"), parse_hcl_to_cty("a = 1"))
        assert '"aws_instance" "web"' in rendered

    def test_nested_values_survive(self) -> None:
        body = parse_hcl_to_cty('tags = { Name = "web" }\nports = [80, 443]\n')
        rendered = cty_to_hcl_block("resource", ("t", "n"), body)
        assert "tags" in rendered
        assert "80" in rendered


class TestRoundTrip:
    """What is emitted parses back to what went in."""

    def test_reparses_as_a_block(self) -> None:
        body = parse_hcl_to_cty('ami = "ami-123"\n')
        rendered = cty_to_hcl_block("resource", ("aws_instance", "web"), body)
        assert load_hcl_data(rendered) == {"resource": [{"aws_instance": {"web": {"ami": "ami-123"}}}]}

    def test_unlabelled_block_reparses(self) -> None:
        rendered = cty_to_hcl_block("locals", (), parse_hcl_to_cty('prefix = "app"\n'))
        assert load_hcl_data(rendered) == {"locals": [{"prefix": "app"}]}

    def test_matches_the_factory_shape(self) -> None:
        """The emitted block reparses to what create_resource_cty produces."""
        built = create_resource_cty("aws_instance", "web", {"ami": "a"}, {"ami": "string"})
        rendered = cty_to_hcl_block("resource", ("aws_instance", "web"), parse_hcl_to_cty('ami = "a"'))
        assert load_hcl_data(rendered) == {"resource": [{"aws_instance": {"web": {"ami": "a"}}}]}
        assert "aws_instance" in built.value["resource"].value[0].value


class TestBlockData:
    """The intermediate structure, for merging several blocks before rendering."""

    def test_carries_the_marker(self) -> None:
        data = cty_to_hcl_block_data("resource", ("t", "n"), parse_hcl_to_cty("a = 1"))
        assert data["resource"][0]['"t"']['"n"']["__is_block__"] is True

    def test_body_values_use_hcl2_conventions(self) -> None:
        data = cty_to_hcl_block_data("resource", ("t", "n"), parse_hcl_to_cty('a = "x"\n'))
        assert data["resource"][0]['"t"']['"n"']["a"] == '"x"'

    def test_merging_two_blocks(self) -> None:
        import hcl2

        one = cty_to_hcl_block_data("locals", (), parse_hcl_to_cty("a = 1"))
        two = cty_to_hcl_block_data("locals", (), parse_hcl_to_cty("b = 2"))
        merged = {"locals": one["locals"] + two["locals"]}
        assert load_hcl_data(hcl2.dumps(merged)) == {"locals": [{"a": 1}, {"b": 2}]}


class TestRefusals:
    """Input that has no valid HCL rendering is refused, not emitted broken."""

    @pytest.mark.parametrize("block_type", ["", "my type", "9lives", "a.b", " ", "resource!"])
    def test_block_type_must_be_an_identifier(self, block_type: str) -> None:
        with pytest.raises(HclEmitError, match="HCL identifier"):
            cty_to_hcl_block(block_type, (), parse_hcl_to_cty("a = 1"))

    def test_labels_must_be_strings(self) -> None:
        with pytest.raises(HclEmitError, match="must be strings"):
            cty_to_hcl_block("resource", (1,), parse_hcl_to_cty("a = 1"))  # type: ignore[arg-type]

    def test_body_must_be_a_body(self) -> None:
        with pytest.raises(HclEmitError, match="object- or map-typed"):
            cty_to_hcl_block("locals", (), CtyString().validate("x"))

    def test_list_body_rejected(self) -> None:
        with pytest.raises(HclEmitError, match="object- or map-typed"):
            cty_to_hcl_block("locals", (), CtyList(element_type=CtyString()).validate(["a"]))

    def test_unknown_body_rejected(self) -> None:
        with pytest.raises(HclEmitError, match="unknown"):
            cty_to_hcl_block("locals", (), CtyValue.unknown(parse_hcl_to_cty("a = 1").type))

    def test_marked_body_rejected(self) -> None:
        marked = parse_hcl_to_cty("a = 1").mark(CtyMark("sensitive"))
        with pytest.raises(HclEmitError, match="marked"):
            cty_to_hcl_block("locals", (), marked)

    def test_body_carrying_the_marker_key_rejected(self) -> None:
        """A body with its own `__is_block__` would silently change the nesting."""
        from pyvider.cty import CtyBool, CtyObject

        body = CtyObject({"__is_block__": CtyBool()}).validate({"__is_block__": True})
        with pytest.raises(HclEmitError, match="__is_block__"):
            cty_to_hcl_block("locals", (), body)


# 📄⚙️🔚
