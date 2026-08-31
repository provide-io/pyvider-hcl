# Terraform Integration Guide

pyvider-hcl works with Terraform configurations in two directions: it reads a
`.tf` file into typed blocks that keep their source positions, and it builds
Terraform structures programmatically through factory functions.

Neither direction evaluates anything. Expressions are preserved as source text,
never resolved — see [What is not evaluated](#what-is-not-evaluated).

## Reading a configuration

`parse_terraform_config` takes a path; `parse_terraform_blocks` takes the text
directly. Both return a `TerraformConfig`.

```python
from pathlib import Path
from pyvider.hcl import parse_terraform_config

config = parse_terraform_config(Path("main.tf"))

print(config.block_types)
# ('terraform', 'variable', 'resource', 'output')

print([block.address for block in config.blocks])
# ['terraform', 'variable.region', 'resource.aws_instance.web', 'output.instance_id']
```

### TerraformConfig

| Member | Description |
|---|---|
| `blocks` | Every top-level block, in source order |
| `attributes` | Attributes written outside any block, normalized |
| `source_file` | The path parsed, or `None` for string input |
| `blocks_of(type)` | Every block of one type, in source order; `()` if none |
| `block_at(type, *labels)` | The first block matching type and labels, or `None` |
| `block_types` | The distinct block types present, in first-appearance order |

### TerraformBlock

| Member | Description |
|---|---|
| `block_type` | `"resource"`, `"variable"`, `"locals"`, … |
| `labels` | The block's labels, unquoted and unescaped |
| `body` | The block body as plain Python values |
| `start_line` / `end_line` | The source line range the block occupies |
| `address` | Dotted address, e.g. `resource.aws_instance.web` |

### Finding blocks

```python
block = config.block_at("resource", "aws_instance", "web")

print(block.labels)   # ('aws_instance', 'web')
print(block.body)     # {'ami': 'ami-123', 'instance_type': 't2.micro', 'tags': {'Name': 'web'}}

print([b.labels[0] for b in config.blocks_of("variable")])   # ['region']
```

Both lookups are total — nothing raises when a block is absent:

```python
config.block_at("resource", "aws_s3_bucket", "logs")   # None
config.blocks_of("data")                               # ()
```

### Source lines

Every block records where it came from, which is what lets a tool point at the
offending block rather than at the file:

```python
for block in config.blocks_of("resource"):
    print(f"{block.address} at lines {block.start_line}-{block.end_line}")
# resource.aws_instance.web at lines 11-18
```

### Top-level attributes

Attributes outside any block are collected separately from blocks, so a
`.tfvars`-style file parses without producing empty block lists:

```python
from pyvider.hcl import parse_terraform_blocks

config = parse_terraform_blocks('name = "x"\nport = 8080\n')
print(config.attributes)   # {'name': 'x', 'port': 8080}
print(config.blocks)       # ()
```

Numbers arrive as numbers, negatives included:

```python
config = parse_terraform_blocks('resource "t" "n" {\n  port = 8080\n  ratio = -1.5\n}\n')
print(config.blocks[0].body)   # {'port': 8080, 'ratio': -1.5}
```

### Block types beyond Terraform's own

Any top-level block parses, whether or not Terraform defines it.
`TERRAFORM_BLOCK_TYPES` names the ones Terraform itself owns, for callers that
want to tell them apart from provider- or tool-specific blocks:

```python
from pyvider.hcl import TERRAFORM_BLOCK_TYPES, parse_terraform_blocks

config = parse_terraform_blocks('plugin "x" {\n  enabled = true\n}\n')
block = config.blocks[0]

print(block.block_type)                          # 'plugin'
print(block.block_type in TERRAFORM_BLOCK_TYPES) # False
```

### What is not evaluated

This package parses HCL; it does not evaluate it. An expression is preserved as
its source text, wrapped in `${...}`:

```python
output = config.block_at("output", "instance_id")
print(output.body)   # {'value': '${aws_instance.web.id}'}
```

`aws_instance.web.id` is not resolved, `var.name` is not substituted, and
functions are not called. If you need evaluated values, run Terraform or
OpenTofu and read their output; use this package for the configuration as
written.

## Validating what you parsed

A block body is plain Python, so it validates against a CTY schema directly:

```python
from pyvider.cty import CtyObject, CtyString
from pyvider.hcl import null_required_attributes, parse_terraform_blocks

schema = CtyObject({"ami": CtyString(), "instance_type": CtyString()})
config = parse_terraform_config(Path("main.tf"))

for block in config.blocks_of("resource"):
    value = schema.validate(block.body)
    for attribute in null_required_attributes(value):
        print(f"{block.address} line {block.start_line}: {attribute} is null")
```

Note the two distinct failures:

- An **absent** attribute makes `schema.validate` raise
  `CtyAttributeValidationError` — pyvider-cty catches that itself.
- An attribute written as an explicit `null` validates fine, because
  pyvider-cty defers required-ness to the schema layer. That is what
  `null_required_attributes` reports, and why it exists.

Without a schema, infer one from the data:

```python
from pyvider.hcl import auto_infer_cty_type

block = config.block_at("resource", "aws_instance", "web")
print(auto_infer_cty_type(block.body).type)
# CtyObject(attributes=['ami', 'instance_type', 'tags'])
```

### Rendering a body back to HCL

```python
from pyvider.hcl import cty_to_hcl

print(cty_to_hcl(schema.validate(block.body)))
# ami = "ami-123"
# instance_type = "t2.micro"
```

`cty_to_hcl` emits attributes only. A `CtyValue` carries no notion of HCL
blocks, so the surrounding `resource "aws_instance" "web" { … }` cannot be
reconstructed from one.

### Parse errors

`HclParsingError` carries the file, line and column, plus a caret-annotated
snippet in its message:

```python
from pyvider.hcl import HclParsingError, parse_terraform_config

try:
    config = parse_terraform_config(Path("broken.tf"))
except HclParsingError as e:
    print(e.source_file, e.line, e.column)   # broken.tf 2 8
    print(e)                                 # message, then the snippet with a caret
```

An unreadable file raises the same type, with `line` left as `None`:

```
Could not read Terraform config: [Errno 2] No such file or directory: 'absent.tf'
```

## Creating variables

```python
from pyvider.hcl import create_variable_cty

variable = create_variable_cty(
    name="region",
    type_str="string",
    default_py="us-west-2",
    description="AWS region",
)
```

| Argument | Required | Description |
|---|---|---|
| `name` | yes | Variable name; must be a valid identifier |
| `type_str` | yes | HCL type string |
| `default_py` | no | Default value, validated against `type_str` |
| `description` | no | Description |
| `sensitive` | no | Mark as sensitive |
| `nullable` | no | Allow null |

## Creating resources

```python
from pyvider.hcl import create_resource_cty

resource = create_resource_cty(
    r_type="aws_instance",
    r_name="web",
    attributes_py={
        "ami": "ami-12345",
        "instance_type": "t2.micro",
    },
    attributes_schema_py={
        "ami": "string",
        "instance_type": "string",
    },
)
```

Every attribute in `attributes_py` needs an entry in `attributes_schema_py`; an
attribute with no declared type raises `HclFactoryError`.

## Type strings

- Primitives: `string`, `number`, `bool`, `any`
- Collections: `list(string)`, `set(string)`, `map(number)`
- Structural: `tuple([string, number])`, `object({name=string, age=number})`
- Optional attributes: `object({name=string, port=optional(number)})`

`optional(T, default)` parses, but the default is dropped — CTY object types
carry no per-attribute defaults.

### Complex types

```python
# Nested objects
"object({host=string, pool=object({min=number, max=number})})"

# Lists of objects
"list(object({name=string, port=number}))"
```

## Error handling

### Variable creation

Factory functions raise `HclFactoryError` for invalid input:

```python
from pyvider.hcl import HclFactoryError, create_variable_cty

for kwargs in (
    {"name": "port", "type_str": "invalid_type", "default_py": 8080},
    {"name": "enabled", "type_str": "bool", "default_py": "not a boolean"},
    {"name": "", "type_str": "string"},
):
    try:
        create_variable_cty(**kwargs)
    except HclFactoryError as e:
        print(e)
# Invalid type string for variable 'port': Unknown or malformed type string: 'invalid_type'
# Default value for variable 'enabled' is not compatible with type 'bool': ...
# Invalid variable name: ''. Must be a valid identifier.
```

### Resource creation

```python
from pyvider.hcl import HclFactoryError, create_resource_cty

try:
    create_resource_cty(
        r_type="aws_instance",
        r_name="web",
        attributes_py={"ami": "ami-123", "port": "not a number"},
        attributes_schema_py={"ami": "string", "port": "number"},
    )
except HclFactoryError as e:
    print(e)
# One or more attributes for resource 'aws_instance.web' are not compatible
# with the provided schema: At port: Number validation error: Cannot represent
# str value 'not a number' as Decimal
```

An attribute present in `attributes_py` but missing from
`attributes_schema_py` raises the same error, naming the attribute.

### Type string parsing

```python
from pyvider.hcl import HclTypeParsingError
from pyvider.hcl.factories import parse_hcl_type_string

try:
    parse_hcl_type_string("object({name=}")
except HclTypeParsingError as e:
    print(e)   # Unknown or malformed type string: 'object({name=}'
```

## See Also

- [examples/04_terraform_variables.py](https://github.com/provide-io/pyvider-hcl/blob/main/examples/04_terraform_variables.py)
- [examples/05_terraform_resources.py](https://github.com/provide-io/pyvider-hcl/blob/main/examples/05_terraform_resources.py)
- [Parsing guide](parsing.md)
- [Schema validation guide](schema-validation.md)
- [Required attributes guide](required-attributes.md)
- [Emission guide](emission.md)
- [Error handling guide](error-handling.md)
