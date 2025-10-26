# PyVider HCL Documentation

Welcome to PyVider HCL - HCL (HashiCorp Configuration Language) parsing with seamless pyvider.cty type system integration.

## Features

PyVider HCL provides:

- **HCL Parsing**: Parse HCL strings into Python data structures using python-hcl2
- **CTY Type Integration**: Automatic conversion to pyvider.cty type-safe values
- **Schema Validation**: Validate HCL data against CTY type schemas
- **Type Inference**: Automatic CTY type inference from HCL data
- **Terraform Factories**: Create Terraform variable and resource structures
- **Pretty Printing**: Format and display CTY values in readable format

## Quick Start

```python
from pyvider.hcl import parse_hcl_to_cty, pretty_print_cty
from pyvider.cty import CtyObject, CtyString, CtyNumber

# Parse HCL with automatic type inference
hcl_string = """
  name = "example"
  port = 8080
  enabled = true
"""

cty_value = parse_hcl_to_cty(hcl_string)
pretty_print_cty(cty_value)

# Parse with schema validation
schema = CtyObject({
    "name": CtyString(),
    "port": CtyNumber(),
})

validated_value = parse_hcl_to_cty(hcl_string, schema=schema)
```

## Creating Terraform Structures

```python
from pyvider.hcl import create_variable_cty, create_resource_cty

# Create a Terraform variable
variable = create_variable_cty(
    name="region",
    type_str="string",
    default_py="us-west-2",
    description="AWS region",
)

# Create a Terraform resource
resource = create_resource_cty(
    r_type="aws_instance",
    r_name="web",
    attributes_py={
        "ami": "ami-12345678",
        "instance_type": "t2.micro",
    },
    attributes_schema_py={
        "ami": "string",
        "instance_type": "string",
    },
)
```

## Documentation

### Getting Started
- **[Getting Started Guide](getting-started.md)**: Installation and first steps

### Guides
- **[User Guide](guide.md)**: Detailed usage examples and patterns
- **[HCL Parsing](guides/parsing.md)**: Parsing HCL strings and files
- **[Schema Validation](guides/schema-validation.md)**: Validating with CTY schemas
- **[Type Inference](guides/type-inference.md)**: Automatic type inference
- **[Terraform Integration](guides/terraform-integration.md)**: Creating Terraform structures
- **[Error Handling](guides/error-handling.md)**: Exception handling patterns
- **[Testing](guides/testing.md)**: Testing with pyvider-hcl

### Reference
- **[API Reference](api/index.md)**: Complete API documentation
- **[Architecture](architecture.md)**: System design and data flow diagrams

## Core API

- **`parse_hcl_to_cty(hcl_content, schema=None)`**: Main parsing function
- **`parse_with_context(content, source_file=None)`**: Parse with error context
- **`create_variable_cty(...)`**: Create Terraform variable structures
- **`create_resource_cty(...)`**: Create Terraform resource structures
- **`pretty_print_cty(value)`**: Pretty print CTY values
- **`HclError`, `HclParsingError`**: Exception classes