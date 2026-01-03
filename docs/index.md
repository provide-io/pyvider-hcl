# Pyvider HCL Documentation

Welcome to Pyvider HCL - HCL (HashiCorp Configuration Language) parsing with seamless pyvider.cty type system integration.

!!! warning "Pre-release"
    pyvider-hcl is in its pre-release series.
    Some documented or roadmap items are exploratory and may change or be removed.

    - **Current version:** v0.3.0
    - **Status:** Pre-release
    - **Production use:** Use with caution

    Part of the [pyvider framework](https://github.com/provide-io/pyvider) ecosystem.

---

## Part of the provide.io Ecosystem

This project is part of a larger ecosystem of tools for Python and Terraform development.

**[View Ecosystem Overview →](https://docs.provide.io/provide-foundation/ecosystem/)**

Understand how provide-foundation, pyvider, flavorpack, and other projects work together.

---

## When to Use Pyvider HCL

### ✅ Use pyvider-hcl when:

- **Parsing HCL/HCL2 files in Python** - You need to read HashiCorp Configuration Language
- **Building tools for Terraform** - You're creating linters, validators, or analyzers
- **Python-native HCL parsing** - You want pure Python without Go dependencies
- **Validating HCL syntax** - You need to check HCL file correctness
- **Converting HCL to Python** - You need HCL data as Python dictionaries/objects
- **Schema validation** - You want to validate HCL against type schemas
- **Terraform configuration tools** - You're building custom Terraform tooling

### ❌ Don't use pyvider-hcl when:

- **Just need YAML/TOML** → Use standard libraries (`pyyaml`, `tomli`)
- **Need full Terraform evaluation** → Use Terraform CLI directly
- **Building Terraform providers** → Use [pyvider](../pyvider/) (includes HCL support automatically)
- **Simple config files** → Consider JSON/YAML for simpler use cases
- **No HCL involvement** → The library is specifically for HCL parsing

### Typical Users

**1. DevOps Tool Developers**
- Building HCL-aware command-line tools
- Creating Terraform configuration validators
- Developing infrastructure automation scripts
- Building custom HCL linters

**2. Infrastructure Automation Engineers**
- Reading Terraform configurations programmatically
- Extracting data from `.tf` files
- Validating Terraform syntax before apply
- Building Terraform workflow tools

**3. Configuration Validators**
- Linting HCL files for best practices
- Checking Terraform configurations for compliance
- Validating provider configurations
- Building security scanning tools

**4. Migration Tool Authors**
- Converting between configuration formats
- Migrating from other IaC tools to Terraform
- Generating Terraform from other sources
- Building configuration transformation pipelines

### Common Use Cases

**Parse Terraform variables:**
```python
from pyvider.hcl import parse_hcl_to_cty

hcl_string = """
variable "region" {
  type    = string
  default = "us-west-2"
}
"""

config = parse_hcl_to_cty(hcl_string)
```

**Validate against schema:**
```python
from pyvider.hcl import parse_hcl_to_cty
from pyvider.cty import CtyObject, CtyString

schema = CtyObject({"region": CtyString()})
validated = parse_hcl_to_cty(hcl_string, schema=schema)
```

### Related Projects

- **Using pyvider?** → pyvider-hcl is automatically included, no separate installation needed
- **Need type handling?** → See [pyvider-cty](../pyvider-cty/) for working with cty types
- **Building providers?** → See [pyvider](../pyvider/) for the full provider framework
- **View ecosystem?** → See [Ecosystem Overview](https://docs.provide.io/provide-foundation/ecosystem/) for how all projects relate

---

## Features

Pyvider HCL provides:

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
- **[Getting Started Guide](getting-started/)**: Installation and first steps

### Guides
- **[User Guide](guide/)**: Detailed usage examples and patterns
- **[HCL Parsing](guides/parsing/)**: Parsing HCL strings and files
- **[Schema Validation](guides/schema-validation/)**: Validating with CTY schemas
- **[Type Inference](guides/type-inference/)**: Automatic type inference
- **[Terraform Integration](guides/terraform-integration/)**: Creating Terraform structures
- **[Error Handling](guides/error-handling/)**: Exception handling patterns
- **[Testing](guides/testing/)**: Testing with pyvider-hcl

### Reference
- **[API Reference](reference/)**: Complete API documentation
- **[Architecture](architecture/)**: System design and data flow diagrams

## Core API

- **`parse_hcl_to_cty(hcl_content, schema=None)`**: Main parsing function
- **`parse_with_context(content, source_file=None)`**: Parse with error context
- **`create_variable_cty(...)`**: Create Terraform variable structures
- **`create_resource_cty(...)`**: Create Terraform resource structures
- **`pretty_print_cty(value)`**: Pretty print CTY values
- **`HclError`, `HclParsingError`**: Exception classes
