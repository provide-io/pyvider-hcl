# Getting Started with pyvider-hcl

Welcome to pyvider-hcl! This guide will help you get started with parsing HCL (HashiCorp Configuration Language) and integrating it with the pyvider ecosystem.

!!! tip "Installation"
    If you haven't installed pyvider-hcl yet, see the [Installation Guide](getting-started/installation.md).

## Your First HCL Parse

Let's start with a simple example:

```python
from pyvider.hcl import parse_hcl_to_cty, pretty_print_cty

# Define some HCL content
hcl_content = """
name = "my-app"
port = 8080
enabled = true
"""

# Parse it into CTY values
result = parse_hcl_to_cty(hcl_content)

# Print the result
pretty_print_cty(result)
```

This will output:

```
{
  "name": "my-app",
  "port": 8080,
  "enabled": true
}
```

## Accessing Values

Once parsed, you can access the values:

```python
# Access the CTY values
name = result.value['name'].value          # "my-app"
port = result.value['port'].value          # 8080
enabled = result.value['enabled'].value    # True

print(f"Starting {name} on port {port}")
```

## Using Schemas for Validation

For production code, it's recommended to use schemas:

```python
from pyvider.hcl import parse_hcl_to_cty
from pyvider.cty import CtyObject, CtyString, CtyNumber, CtyBool

# Define a schema
schema = CtyObject({
    "name": CtyString(),
    "port": CtyNumber(),
    "enabled": CtyBool(),
})

# Parse with validation
hcl_content = """
name = "my-app"
port = 8080
enabled = true
"""

result = parse_hcl_to_cty(hcl_content, schema=schema)
```

If the HCL doesn't match the schema, you'll get a clear error:

```python
from pyvider.hcl import HclParsingError

try:
    invalid_hcl = 'port = "8080"'  # String instead of number
    result = parse_hcl_to_cty(invalid_hcl, schema=schema)
except HclParsingError as e:
    print(f"Validation failed: {e}")
```

## Parsing HCL Files

To parse HCL from a file:

```python
from pathlib import Path
from pyvider.hcl import parse_hcl_to_cty

# Read the file
hcl_file = Path("config.hcl")
content = hcl_file.read_text()

# Parse it
result = parse_hcl_to_cty(content)
```

For better error messages, use `parse_with_context`:

```python
from pyvider.hcl import parse_with_context

content = hcl_file.read_text()
result = parse_with_context(content, source_file=hcl_file)
```

## Creating Terraform Structures

pyvider-hcl provides factory functions for creating Terraform variables and resources:

### Creating a Variable

```python
from pyvider.hcl import create_variable_cty

variable = create_variable_cty(
    name="region",
    type_str="string",
    default_py="us-west-2",
    description="AWS region for deployment"
)
```

### Creating a Resource

```python
from pyvider.hcl import create_resource_cty

resource = create_resource_cty(
    r_type="aws_instance",
    r_name="web_server",
    attributes_py={
        "ami": "ami-12345678",
        "instance_type": "t2.micro",
    },
    attributes_schema_py={
        "ami": "string",
        "instance_type": "string",
    }
)
```

## Complex Types

pyvider-hcl supports all HCL types:

```python
from pyvider.hcl import create_variable_cty

# List type
list_var = create_variable_cty(
    name="availability_zones",
    type_str="list(string)",
    default_py=["us-west-2a", "us-west-2b"]
)

# Object type
object_var = create_variable_cty(
    name="server_config",
    type_str="object({host=string, port=number})",
    default_py={
        "host": "localhost",
        "port": 8080
    }
)

# Nested object type
nested_var = create_variable_cty(
    name="database",
    type_str="object({host=string, pool=object({min=number, max=number})})",
    default_py={
        "host": "db.example.com",
        "pool": {
            "min": 5,
            "max": 20
        }
    }
)
```

## Error Handling

Always handle errors when parsing untrusted HCL:

```python
from pyvider.hcl import HclParsingError, parse_hcl_to_cty

try:
    result = parse_hcl_to_cty(hcl_content, schema=schema)
except HclParsingError as e:
    print(f"Failed to parse HCL: {e.message}")
    if e.source_file:
        print(f"File: {e.source_file}")
```

## Next Steps

Now that you've learned the basics, explore more advanced topics:

- **[User Guide](guide.md)** - Comprehensive usage examples
- **[API Reference](reference/index.md)** - Complete API documentation
- **[Architecture](architecture.md)** - Understand how pyvider-hcl works
<!-- - **[Examples](../examples/README.md)** - Working code examples -->

### Guides

- [Parsing Guide](guides/parsing.md) - Advanced parsing techniques
- [Schema Validation](guides/schema-validation.md) - Schema best practices
- [Terraform Integration](guides/terraform-integration.md) - Working with Terraform
- [Error Handling](guides/error-handling.md) - Robust error handling
- [Testing](guides/testing.md) - Testing with pyvider-hcl

## Common Patterns

### Pattern 1: Configuration Loading

```python
def load_config(config_file: Path):
    """Load and validate configuration from HCL file."""
    from pyvider.hcl import parse_hcl_to_cty, HclParsingError
    from pyvider.cty import CtyObject, CtyString, CtyNumber

    schema = CtyObject({
        "app_name": CtyString(),
        "port": CtyNumber(),
    })

    try:
        content = config_file.read_text()
        config = parse_hcl_to_cty(content, schema=schema)
        return config
    except HclParsingError as e:
        print(f"Failed to load config: {e}")
        return None
```

### Pattern 2: Multi-File Projects

```python
def load_terraform_project(project_dir: Path):
    """Load all HCL files in a Terraform project."""
    from pyvider.hcl import parse_with_context

    configs = {}
    for hcl_file in project_dir.glob("**/*.hcl"):
        content = hcl_file.read_text()
        config = parse_with_context(content, source_file=hcl_file)
        configs[hcl_file.name] = config

    return configs
```

## Getting Help

<!-- - **Examples**: Check the [examples/](../examples/) directory for working code -->
- **Issues**: Report bugs at [GitHub Issues](https://github.com/provide-io/pyvider-hcl/issues)
<!-- - **Contributing**: See [CONTRIBUTING.md](../CONTRIBUTING.md) for contribution guidelines -->

Happy parsing! 🚀
