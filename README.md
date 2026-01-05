# 📄⚙️ Pyvider HCL

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![uv](https://img.shields.io/badge/uv-package_manager-FF6B35.svg)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![CI](https://github.com/provide-io/pyvider-hcl/actions/workflows/ci.yml/badge.svg)](https://github.com/provide-io/pyvider-hcl/actions)

**Python library for parsing HCL into pyvider.cty types**

pyvider-hcl provides a simple and intuitive way to work with HCL (HashiCorp Configuration Language) data in your Python applications, with seamless integration into the pyvider ecosystem.

## ✨ Key Features

- 🔄 **CTY Integration** - Parses HCL directly into `CtyValue` objects for pyvider compatibility
- 🎯 **Simplified API** - Clean interface for parsing HCL and creating Terraform structures
- 🔍 **Automatic Type Inference** - Infer `CtyType` from HCL data without explicit schemas
- ✅ **Schema Validation** - Validate HCL data against CTY type schemas
- 🏭 **Factory Functions** - Create Terraform variables and resources programmatically
- 🖨️ **Pretty Printing** - Debug-friendly output for CTY values

## Quick Start

> **Note**: pyvider-hcl is in pre-release (v0.x.x). APIs and features may change before 1.0 release.

1. Install: `uv add pyvider-hcl`
2. Read the [Getting Started guide](https://github.com/provide-io/pyvider-hcl/blob/main/docs/getting-started.md).
3. Try the examples in [examples/README.md](https://github.com/provide-io/pyvider-hcl/blob/main/examples/README.md).

## Documentation

- **[User Guide](https://github.com/provide-io/pyvider-hcl/blob/main/docs/guide.md)**: Detailed usage examples and patterns
- **[API Reference](https://github.com/provide-io/pyvider-hcl/blob/main/docs/reference/index.md)**: Complete API documentation
- **[Architecture](https://github.com/provide-io/pyvider-hcl/blob/main/docs/architecture.md)**: System design and data flow diagrams
- **[Contributing](https://github.com/provide-io/pyvider-hcl/blob/main/CONTRIBUTING.md)**: Guidelines for contributors
- **[Changelog](https://github.com/provide-io/pyvider-hcl/blob/main/CHANGELOG.md)**: Version history and release notes

## Development

### Quick Start

```bash
# Set up environment
uv sync

# Run common tasks
we run test       # Run tests
we run lint       # Check code
we run format     # Format code
we tasks          # See all available commands
```

See [CLAUDE.md](https://github.com/provide-io/pyvider-hcl/blob/main/CLAUDE.md) for detailed development instructions and architecture information.

For contribution guidelines, see [CONTRIBUTING.md](https://github.com/provide-io/pyvider-hcl/blob/main/CONTRIBUTING.md).

# Format and lint
uv run ruff format .
uv run ruff check .
```

## Contributing
See [CONTRIBUTING.md](https://github.com/provide-io/pyvider-hcl/blob/main/CONTRIBUTING.md) for contribution guidelines.

## License

Apache-2.0 License - see [LICENSE](https://github.com/provide-io/pyvider-hcl/blob/main/LICENSE) for details.

## Installation

To install `pyvider-hcl`, you can use `uv`:

```bash
uv add pyvider-hcl
```

## Usage

Here's a simple example of how to use `pyvider-hcl` to parse an HCL string:

```python
from pyvider.hcl import parse_hcl_to_cty, pretty_print_cty
from pyvider.cty import CtyString

hcl_string = """
  name = "Jules"
  age = 30
"""

cty_value = parse_hcl_to_cty(hcl_string)

pretty_print_cty(cty_value)
```

You can also parse an HCL file:

```python
from pyvider.hcl import parse_hcl_to_cty, pretty_print_cty

with open("my_config.hcl", "r") as f:
    hcl_content = f.read()
    cty_value = parse_hcl_to_cty(hcl_content)
    pretty_print_cty(cty_value)
```

### Schema Validation

You can validate HCL data against a `CtyType` schema:

```python
from pyvider.hcl import parse_hcl_to_cty, pretty_print_cty
from pyvider.cty import CtyObject, CtyString, CtyNumber

schema = CtyObject({
    "name": CtyString(),
    "age": CtyNumber(),
})

hcl_string = """
  name = "Jules"
  age = "thirty" # Invalid type
"""

try:
    cty_value = parse_hcl_to_cty(hcl_string, schema=schema)
except Exception as e:
    print(e)
```

### Complex Cty Integration Examples

Here are some more complex examples of how to use `pyvider-hcl` with `pyvider.cty`:

#### Parsing a list of objects

```python
from pyvider.hcl import parse_hcl_to_cty, pretty_print_cty
from pyvider.cty import CtyObject, CtyList, CtyString, CtyNumber

hcl_string = """
  users = [
    {
      name = "Jules"
      age  = 30
    },
    {
      name = "Vincent"
      age  = 40
    }
  ]
"""

schema = CtyObject({
    "users": CtyList(
        element_type=CtyObject({
            "name": CtyString(),
            "age": CtyNumber(),
        })
    )
})

cty_value = parse_hcl_to_cty(hcl_string, schema=schema)

pretty_print_cty(cty_value)
```

#### Parsing nested objects

```python
from pyvider.hcl import parse_hcl_to_cty, pretty_print_cty
from pyvider.cty import CtyObject, CtyString, CtyNumber

hcl_string = """
  config = {
    server = {
      host = "localhost"
      port = 8080
    }
    database = {
      host = "localhost"
      port = 5432
    }
  }
"""

schema = CtyObject({
    "config": CtyObject({
        "server": CtyObject({
            "host": CtyString(),
            "port": CtyNumber(),
        }),
        "database": CtyObject({
            "host": CtyString(),
            "port": CtyNumber(),
        }),
    })
})

cty_value = parse_hcl_to_cty(hcl_string, schema=schema)

pretty_print_cty(cty_value)
```

### Creating Terraform Variables and Resources

You can use the factory functions to create `CtyValue` objects for Terraform variables and resources:

```python
from pyvider.hcl import (
    parse_hcl_to_cty,
    pretty_print_cty,
    create_variable_cty,
    create_resource_cty,
)

# Create a variable
variable_cty = create_variable_cty(
    name="my_variable",
    type_str="string",
    default_py="my_default_value",
)

pretty_print_cty(variable_cty)

# Create a resource
resource_cty = create_resource_cty(
    r_type="my_resource",
    r_name="my_instance",
    attributes_py={
        "name": "my_resource_name",
        "value": 123,
    },
)

pretty_print_cty(resource_cty)
```

## FAQ

### How do I parse an HCL file?

Currently, you need to read the file manually and pass the content to `parse_hcl_to_cty()`:

```python
from pathlib import Path
from pyvider.hcl import parse_hcl_to_cty

hcl_content = Path("config.hcl").read_text()
result = parse_hcl_to_cty(hcl_content)
```

### Can this library generate HCL output?

No, `pyvider-hcl` is currently focused on parsing HCL into CTY types. It does not generate HCL output. You can use the `pretty_print_cty()` function to display CTY values in a readable format, but this is not HCL syntax.

### Does this support HCL expressions like `var.name` or `length(list)`?

Not yet. The library currently parses static HCL data. Expression evaluation (variables, functions, conditionals) is exploratory and may change or be removed.

### What's the difference between `parse_hcl_to_cty()` and `parse_with_context()`?

- **`parse_hcl_to_cty()`**: Returns a `CtyValue` object with full type information. Use this for most cases.
- **`parse_with_context()`**: Returns raw Python dict/list from the parser. Use this when you need the raw data structure or want enhanced error context without CTY conversion.

### How do I validate HCL against a specific structure?

Pass a CTY schema to `parse_hcl_to_cty()`:

```python
from pyvider.hcl import parse_hcl_to_cty
from pyvider.cty import CtyObject, CtyString, CtyNumber

schema = CtyObject({
    "name": CtyString(),
    "port": CtyNumber(),
})

result = parse_hcl_to_cty(hcl_content, schema=schema)
# Raises HclParsingError if validation fails
```

### Can I use this with Terraform configurations?

Yes! The library parses HCL syntax used by Terraform. The `create_variable_cty()` and `create_resource_cty()` factory functions help create Terraform-specific structures. Full Terraform-specific validation (provider blocks, module blocks, etc.) is limited.

### What HCL version is supported?

The library uses `python-hcl2` which supports HCL 2.x (the version used by Terraform 0.12+).

### How do I handle parsing errors?

Wrap your parsing calls in a try/except block:

```python
from pyvider.hcl import parse_hcl_to_cty, HclParsingError

try:
    result = parse_hcl_to_cty(hcl_content)
except HclParsingError as e:
    print(f"Parsing failed: {e}")
    # e.source_file, e.line, e.column available if set
```

### Can I parse multiple HCL files at once?

You need to parse each file individually. For multi-file Terraform projects, parse each file separately and combine the results as needed.

### What types can be automatically inferred?

When no schema is provided, the library automatically infers:
- `string` → `CtyString`
- `number` (int/float) → `CtyNumber`
- `bool` → `CtyBool`
- `list` → `CtyList(CtyDynamic())`
- `object` → `CtyObject` with inferred field types

### How do I contribute or report bugs?

See [CONTRIBUTING.md](https://github.com/provide-io/pyvider-hcl/blob/main/CONTRIBUTING.md) for contribution guidelines. For bugs, please open an issue on the GitHub repository with:
- The HCL content that fails
- The error message
- Expected vs. actual behavior

## Related Projects

- [pyvider-cty](https://github.com/provide-io/pyvider-cty): CTY type system for Python
- [pyvider](https://github.com/provide-io/pyvider): Terraform provider framework for Python
- [provide-foundation](https://github.com/provide-io/provide-foundation): Foundation services and utilities

Copyright (c) provide.io LLC.
