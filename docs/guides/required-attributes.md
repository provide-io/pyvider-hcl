# Required Attributes Guide

An attribute written as an explicit `null` is not the same as an attribute left
out, and CTY treats them differently:

```hcl
# absent -- CtyObject.validate rejects this itself
note = "x"

# present and null -- validates, and is what this guide is about
name = null
note = "x"
```

`pyvider-cty` deliberately stopped rejecting a null value for a non-optional
attribute: `CtyObject.validate` records the null and leaves required-ness to
the schema layer that owns the semantics. For HCL, that layer is this package.

## It is already applied when you parse with a schema

`parse_hcl_to_cty()` runs the check for you. Nothing extra to call:

```python
from pyvider.cty import CtyObject, CtyString
from pyvider.hcl import HclParsingError, parse_hcl_to_cty

schema = CtyObject(
    {"name": CtyString(), "note": CtyString()},
    optional_attributes=frozenset({"note"}),
)

try:
    parse_hcl_to_cty("name = null\n", schema=schema)
except HclParsingError as e:
    print(e)
    # Schema validation failed after HCL parsing: null value for required
    # attribute(s): name
```

An attribute marked `optional` may be null, and passes:

```python
parse_hcl_to_cty('name = "x"\nnote = null\n', schema=schema)   # fine
```

## When to call it yourself

Call `null_required_attributes()` when you validate a value yourself rather
than going through `parse_hcl_to_cty` — most commonly when checking the body of
a Terraform block, where you want to report every problem with its source line
rather than stop at the first:

```python
from pyvider.cty import CtyObject, CtyString
from pyvider.hcl import null_required_attributes, parse_terraform_blocks

TF = '''resource "aws_instance" "web" {
  ami           = "ami-123"
  instance_type = "t2.micro"
}

resource "aws_instance" "bad" {
  ami           = "ami-456"
  instance_type = null
}
'''

schema = CtyObject({"ami": CtyString(), "instance_type": CtyString()})

for block in parse_terraform_blocks(TF).blocks_of("resource"):
    for attribute in null_required_attributes(schema.validate(block.body)):
        print(f"{block.address} line {block.start_line}: {attribute} is null")
# resource.aws_instance.bad line 6: instance_type is null
```

It returns a list, so an empty list means the value is clean. It never raises.

## Paths it reports

Nulls nested inside collections are reported by path, so you can point at the
exact attribute:

```python
from pyvider.cty import CtyList, CtyMap, CtyObject, CtySet, CtyString
from pyvider.hcl import null_required_attributes

item = CtyObject(
    {"id": CtyString(), "note": CtyString()},
    optional_attributes=frozenset({"note"}),
)

null_required_attributes(
    CtyObject({"items": CtyList(element_type=item)}).validate({"items": [{"id": None, "note": None}]})
)
# ['items[0].id']          -- note is optional, so it is not reported

null_required_attributes(
    CtyObject({"m": CtyMap(element_type=item)}).validate({"m": {"k": {"id": None}}})
)
# ['m["k"].id']

null_required_attributes(
    CtyObject({"s": CtySet(element_type=item)}).validate({"s": [{"id": None}]})
)
# ['s[*].id']
```

| Container | Path syntax | Why |
|---|---|---|
| object | `.name` | attribute name |
| map | `["key"]` | key, quoted |
| list, tuple | `[0]` | positional index |
| set | `[*]` | sets have no stable index |

## What it does not report

- **Absent attributes.** `CtyObject.validate` raises
  `CtyAttributeValidationError` before this ever runs.
- **Optional attributes**, whether null or not.
- **Anything under a null or unknown container.** A null list is one null
  value, not a list of null-attributed elements, so the walk stops there.
- **Non-object roots.** A bare string or list has no attributes to check and
  returns `[]`.

## See Also

- [Schema validation guide](schema-validation.md)
- [Terraform integration guide](terraform-integration.md)
- [Error handling guide](error-handling.md)
