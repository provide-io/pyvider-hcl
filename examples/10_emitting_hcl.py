#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Example 10: Emitting HCL

Parsing runs one way; `cty_to_hcl` and `cty_to_hcl_block` run the other, turning
CTY values back into HCL text. Together with the factories that closes the loop:
build a resource, emit it, read it back, and get the same shape you started with."""

from collections.abc import Callable

import hcl2

from pyvider.cty import CtyList, CtyNumber, CtyObject, CtyString, CtyValue
from pyvider.cty.marks import CtyMark
from pyvider.hcl import (
    HclEmitError,
    cty_to_hcl,
    cty_to_hcl_block,
    cty_to_hcl_block_data,
    cty_to_hcl_data,
    load_hcl_data,
    parse_hcl_to_cty,
)


def example_emit_attributes() -> None:
    """`cty_to_hcl` renders an object- or map-typed value as an HCL body."""
    print("=" * 60)
    print("Example 1: Emitting Attributes")
    print("=" * 60)

    value = parse_hcl_to_cty(
        'name = "web"\nport = 8080\nenabled = true\ntags = { Name = "web" }\nports = [80, 443]\n'
    )
    print(cty_to_hcl(value), end="")

    # Set elements are emitted in a stable order, so the same set always renders
    # the same text regardless of iteration order.


def example_emit_a_block() -> None:
    """Block type and labels come from the caller, because a CtyValue has none."""
    print("\n" + "=" * 60)
    print("Example 2: Emitting a Block")
    print("=" * 60)

    body = parse_hcl_to_cty('ami = "ami-123"\ninstance_type = "t2.micro"\n')
    print(cty_to_hcl_block("resource", ("aws_instance", "web"), body), end="")

    # Any label arity works, including none.
    print(cty_to_hcl_block("locals", (), parse_hcl_to_cty('prefix = "app"\n')), end="")


def example_round_trip() -> None:
    """What is emitted parses back to the shape the factories produce."""
    print("\n" + "=" * 60)
    print("Example 3: Round Trip")
    print("=" * 60)

    rendered = cty_to_hcl_block("resource", ("aws_instance", "web"), parse_hcl_to_cty('ami = "a"\n'))
    print(rendered, end="")
    print(f"Reparsed: {load_hcl_data(rendered)}")
    print("\nThat is the shape `create_resource_cty` produces and the parser returns,")
    print("so a block can be built, emitted, and read back without changing shape.")


def example_emit_several_blocks() -> None:
    """`cty_to_hcl_block_data` defers rendering, so blocks can be merged first."""
    print("\n" + "=" * 60)
    print("Example 4: Emitting a Whole File")
    print("=" * 60)

    parts = [
        cty_to_hcl_block_data("variable", ("region",), parse_hcl_to_cty('default = "us-west-2"\n')),
        cty_to_hcl_block_data("resource", ("aws_instance", "web"), parse_hcl_to_cty('ami = "a"\n')),
        cty_to_hcl_block_data("resource", ("aws_instance", "db"), parse_hcl_to_cty('ami = "b"\n')),
    ]

    merged: dict[str, list[dict[str, object]]] = {}
    for part in parts:
        for block_type, blocks in part.items():
            merged.setdefault(block_type, []).extend(blocks)

    print(hcl2.dumps(merged), end="")

    # The marker that makes this work is `__is_block__`, placed on the innermost
    # body -- that is how `hcl2.dumps` tells where the labels stop and the
    # attributes start.


def example_intermediate_form() -> None:
    """`cty_to_hcl_data` returns python-hcl2's conventions, before rendering."""
    print("\n" + "=" * 60)
    print("Example 5: The Intermediate Form")
    print("=" * 60)

    value = parse_hcl_to_cty('literal = "web"\nexpression = var.x\ncount = 3.0\ntemplate = "a${var.x}b"\n')
    for name, rendered in cty_to_hcl_data(value).items():
        print(f"  {name:<12} -> {rendered!r}")

    print("\nA quoted string is a literal and a bare `${...}` is an expression. A")
    print("template holding an interpolation stays quoted, because emitting it bare")
    print("would produce invalid HCL. Numbers narrow to int when integral.")


def example_what_does_not_round_trip() -> None:
    """Value survives, syntax does not."""
    print("\n" + "=" * 60)
    print("Example 6: What Does Not Round-Trip")
    print("=" * 60)

    heredoc = cty_to_hcl(parse_hcl_to_cty("body = <<EOT\nline\nEOT\n"))
    print(f"  A heredoc becomes a quoted string:  {heredoc.strip()}")

    identifier = cty_to_hcl(parse_hcl_to_cty("type = string\n"))
    print(f"  A bare identifier comes back quoted: {identifier.strip()}")

    print("\nComments are dropped at parse time and cannot be re-emitted. In every")
    print("case the value is right; only the original syntax is lost.")


def example_refusals() -> None:
    """Values with no HCL representation are refused, not guessed at."""
    print("\n" + "=" * 60)
    print("Example 7: Refusals")
    print("=" * 60)

    body = parse_hcl_to_cty("a = 1\n")
    attempts: list[tuple[str, Callable[[], object]]] = [
        ("a non-body root", lambda: cty_to_hcl(CtyList(element_type=CtyString()).validate(["a"]))),
        ("an unknown value", lambda: cty_to_hcl(CtyValue.unknown(CtyObject({})))),
        ("a marked value", lambda: cty_to_hcl(body.mark(CtyMark("sensitive")))),
        ("a block type that is not an identifier", lambda: cty_to_hcl_block("my type", (), body)),
        ("a non-string label", lambda: cty_to_hcl_block("resource", (1,), body)),  # type: ignore[arg-type]
    ]

    for description, attempt in attempts:
        try:
            attempt()
        except HclEmitError as e:
            print(f"  {description}:\n    {e}")

    print("\nEmitting a marked value would silently drop the mark -- which for a")
    print("`sensitive` mark means writing a secret to a file. Strip marks on purpose.")


def example_null_is_fine() -> None:
    """Null has a spelling in HCL, so it emits rather than being refused."""
    print("\n" + "=" * 60)
    print("Example 8: Null Emits")
    print("=" * 60)

    schema = CtyObject(
        {"name": CtyString(), "port": CtyNumber()},
        optional_attributes=frozenset({"port"}),
    )
    print(cty_to_hcl(schema.validate({"name": "web", "port": None})), end="")


def main() -> None:
    """Run all emission examples."""
    example_emit_attributes()
    example_emit_a_block()
    example_round_trip()
    example_emit_several_blocks()
    example_intermediate_form()
    example_what_does_not_round_trip()
    example_refusals()
    example_null_is_fine()

    print("\n" + "=" * 60)
    print("All emission examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()

# 📄⚙️🔚
