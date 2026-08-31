# pyvider-hcl Examples

This directory contains comprehensive examples demonstrating how to use pyvider-hcl for HCL parsing and Terraform structure creation.

## Running Examples

All examples can be run directly:

```bash
uv run python examples/01_basic_parsing.py
```

## Example Index

1. **[01_basic_parsing.py](01_basic_parsing.py)** - Simple HCL parsing
   - Parse HCL strings
   - Access parsed values
   - Basic HCL syntax examples

2. **[02_schema_validation.py](02_schema_validation.py)** - Schema validation
   - Define CTY schemas
   - Validate HCL data
   - Handle validation errors

3. **[03_type_inference.py](03_type_inference.py)** - Automatic type inference
   - Let pyvider-hcl infer types
   - Understand inferred types
   - When to use inference vs schemas

4. **[04_terraform_variables.py](04_terraform_variables.py)** - Terraform variables
   - Create variable structures
   - Set defaults and descriptions
   - Handle sensitive variables

5. **[05_terraform_resources.py](05_terraform_resources.py)** - Terraform resources
   - Create resource structures
   - Define resource attributes
   - Type validation for resources

6. **[06_complex_structures.py](06_complex_structures.py)** - Complex nested structures
   - Parse nested objects
   - Handle lists of objects
   - Complex type definitions

7. **[07_error_handling.py](07_error_handling.py)** - Error handling
   - Catch parsing errors
   - Handle validation failures
   - Error context and debugging

8. **[08_multi_file_project.py](08_multi_file_project.py)** - Multi-file projects
   - Parse multiple HCL files
   - Organize Terraform configurations
   - Real-world project structure

9. **[09_terraform_blocks.py](09_terraform_blocks.py)** - Terraform blocks and source lines
   - Parse into typed blocks rather than nested dicts
   - Find blocks by type or by exact labels
   - Report diagnostics against a block's line range

10. **[10_emitting_hcl.py](10_emitting_hcl.py)** - Emitting HCL
    - Render CTY values back into HCL text
    - Emit blocks, and merge several into one file
    - What round-trips, what does not, and what is refused

11. **[11_required_attributes.py](11_required_attributes.py)** - Required attributes
    - Explicit null on a required attribute is rejected
    - Collect every offender instead of raising on the first
    - Dotted paths for nested attributes

## Quick Start

The simplest way to get started:

```python
from pyvider.hcl import parse_hcl_to_cty, pretty_print_cty

hcl = '''
name = "example"
count = 5
'''

result = parse_hcl_to_cty(hcl)
pretty_print_cty(result)
```

## Need Help?

- [User Guide](../docs/guide.md) - Detailed usage documentation
- [Terraform integration](../docs/guides/terraform-integration.md) - Blocks, labels, source lines
- [Emission guide](../docs/guides/emission.md) - Rendering CTY values back to HCL
- [Required attributes](../docs/guides/required-attributes.md) - Null vs missing
- [API Reference](../docs/reference/index.md) - Complete API documentation
- [Architecture](../docs/architecture.md) - System design and internals
