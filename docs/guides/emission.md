# Emission Guide

`cty_to_hcl()` renders a CTY value back into HCL text. It is the inverse of
`parse_hcl_to_cty()` for the subset of HCL that survives a round trip.

```python
from pyvider.hcl import cty_to_hcl, parse_hcl_to_cty

value = parse_hcl_to_cty('name = "x"\nport = 8080\nok = true\n')
print(cty_to_hcl(value), end="")
# name = "x"
# port = 8080
# ok = true
```

## What it takes

The root must be an object- or map-typed `CtyValue`, because its attributes
become the top-level HCL body. Anything else is refused:

```python
from pyvider.cty import CtyList, CtyString
from pyvider.hcl import HclEmitError, cty_to_hcl

try:
    cty_to_hcl(CtyList(element_type=CtyString()).validate(["a"]))
except HclEmitError as e:
    print(e)   # cty_to_hcl requires an object- or map-typed CtyValue
```

## Nested structures

Objects, maps, lists, tuples and sets all render:

```python
value = parse_hcl_to_cty('tags = { Name = "web" }\nports = [80, 443]\n')
print(cty_to_hcl(value), end="")
# tags = {
#   Name = "web",
# }
# ports = [
#   80,
#   443,
# ]
```

Set elements are emitted in a stable order, so the same set always renders the
same text regardless of iteration order.

## Literals and expressions

A string that is *nothing but* one interpolation is emitted bare, as an
expression. Anything else is emitted as a quoted literal:

```python
print(cty_to_hcl(parse_hcl_to_cty("v = var.name\n")), end="")
# v = var.name

print(cty_to_hcl(parse_hcl_to_cty('v = "a${var.x}b"\n')), end="")
# v = "a${var.x}b"
```

The second case is a template, not an expression — emitting it bare would
produce invalid HCL. The same applies to a string holding two interpolations
(`"${a} ${b}"`), which stays quoted.

Escapes are re-escaped on the way out, so a round trip is stable:

```python
print(cty_to_hcl(parse_hcl_to_cty(r'v = "say \"hi\""' + "\n")), end="")
# v = "say \"hi\""
```

## What does not round-trip

**Heredocs become quoted strings.** Parsing resolves a heredoc to its body, and
nothing in the resulting `CtyValue` records that it was written as a heredoc:

```python
print(cty_to_hcl(parse_hcl_to_cty("v = <<EOT\nline\nEOT\n")), end="")
# v = "line\n"
```

The value is correct; the syntax is not preserved.

**Comments are not preserved.** They are dropped at parse time.

**A bare identifier comes back quoted.** `type = string` parses to the string
`"string"`, and nothing in the resulting value distinguishes it from a literal,
so it re-emits as `type = "string"`.

## Emitting blocks

`cty_to_hcl` emits attributes, because that is all a `CtyValue` can tell you:
nothing in one records that it was written as a block. `cty_to_hcl_block` takes
that missing piece — the block type and its labels — from you instead:

```python
from pyvider.hcl import cty_to_hcl_block, parse_hcl_to_cty

body = parse_hcl_to_cty('ami = "ami-123"\ninstance_type = "t2.micro"\n')
print(cty_to_hcl_block("resource", ("aws_instance", "web"), body), end="")
# resource "aws_instance" "web" {
#   ami           = "ami-123"
#   instance_type = "t2.micro"
# }
```

Any label arity works, including none:

```python
print(cty_to_hcl_block("locals", (), parse_hcl_to_cty('prefix = "app"\n')), end="")
# locals {
#   prefix = "app"
# }
```

What comes out parses back to what went in:

```python
from pyvider.hcl import load_hcl_data

rendered = cty_to_hcl_block("resource", ("aws_instance", "web"), parse_hcl_to_cty('ami = "a"'))
load_hcl_data(rendered)
# {'resource': [{'aws_instance': {'web': {'ami': 'a'}}}]}
```

That is the same shape `create_resource_cty` produces and the parser returns,
so a block can be built, emitted, and read back without changing shape.

### Refusals

The block type must be an HCL identifier and labels must be strings, because
neither has a valid rendering otherwise:

```python
from pyvider.hcl import HclEmitError

try:
    cty_to_hcl_block("my type", (), body)
except HclEmitError as e:
    print(e)   # Block type must be an HCL identifier, got 'my type'
```

The body must be object- or map-typed, and the unknown and marked rules above
apply to it unchanged.

### Emitting several blocks

`cty_to_hcl_block_data()` returns the structure without rendering it, so several
blocks can be merged and written in one pass:

```python
import hcl2
from pyvider.hcl import cty_to_hcl_block_data, parse_hcl_to_cty

one = cty_to_hcl_block_data("locals", (), parse_hcl_to_cty("a = 1"))
two = cty_to_hcl_block_data("locals", (), parse_hcl_to_cty("b = 2"))
print(hcl2.dumps({"locals": one["locals"] + two["locals"]}), end="")
# locals {
#   a = 1
# }
#
#
# locals {
#   b = 2
# }
```

The marker that makes this work is `__is_block__`, which sits on the innermost
body — that is how `hcl2.dumps` tells where the labels stop and the attributes
start. `cty_to_hcl_block_data` places it for you, and refuses a body that
carries a key by that name.

## Values with no HCL representation

Two kinds of CTY value are refused rather than guessed at:

```python
from pyvider.cty import CtyObject, CtyString, CtyValue
from pyvider.cty.marks import CtyMark
from pyvider.hcl import HclEmitError, cty_to_hcl, cty_to_hcl_data

try:
    cty_to_hcl(CtyValue.unknown(CtyObject({})))
except HclEmitError as e:
    print(e)   # Cannot emit an unknown CTY value as HCL

try:
    cty_to_hcl_data(CtyString().validate("s").mark(CtyMark("sensitive")))
except HclEmitError as e:
    print(e)   # Cannot emit a marked CTY value as HCL; strip marks before emitting ...
```

An unknown value has no text that means "unknown" in HCL, and emitting a marked
value would silently drop the mark — which for a `sensitive` mark means writing
a secret into a file. Strip marks deliberately if that is what you want.

A **null** value is fine, and emits as `null`:

```python
schema = CtyObject({"a": CtyString()}, optional_attributes=frozenset({"a"}))
print(cty_to_hcl(schema.validate({"a": None})), end="")
# a = null
```

## The intermediate form

`cty_to_hcl_data()` returns the structure `cty_to_hcl` hands to
`hcl2.dumps` — python-hcl2's conventions, where a quoted string is a literal
and a bare `${...}` is an expression:

```python
from pyvider.cty import CtyNumber, CtyString
from pyvider.hcl import cty_to_hcl_data
from decimal import Decimal

cty_to_hcl_data(CtyString().validate("web"))          # '"web"'
cty_to_hcl_data(CtyString().validate("${var.x}"))     # '${var.x}'
cty_to_hcl_data(CtyNumber().validate(Decimal("3.0"))) # 3
```

Reach for it when you want to merge emitted values into a larger structure
before rendering, or to drive `hcl2.dumps` yourself with block markers.

Numbers narrow to `int` when integral and `float` otherwise, which is the
precision HCL consumers work with.

## See Also

- [Parsing guide](parsing.md)
- [Terraform integration guide](terraform-integration.md)
- [Error handling guide](error-handling.md)
