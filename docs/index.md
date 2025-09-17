# PyVider HCL Documentation

Welcome to PyVider HCL - HCL (HashiCorp Configuration Language) parsing and manipulation for Terraform configurations in Python.

## Features

PyVider HCL provides:

- **HCL Parsing**: Native Python parsing of HCL and HCL2 files
- **AST Manipulation**: Programmatic modification of Terraform configurations
- **Type Safety**: Full type hints and validation for HCL structures
- **Terraform Integration**: Seamless integration with Terraform provider development
- **Configuration Generation**: Programmatic generation of Terraform configurations

## Quick Start

```python
from pyvider.hcl import parse_file, HCLDocument

# Parse an HCL file
doc = parse_file("main.tf")

# Access and modify configuration
for resource in doc.resources:
    print(f"Resource: {resource.type}.{resource.name}")

# Generate HCL output
hcl_content = doc.to_hcl()
```

## API Reference

For complete API documentation, see the [API Reference](api/index.md).

## Core Modules

- **Parser**: HCL file parsing and tokenization
- **AST**: Abstract syntax tree representation
- **Generator**: HCL configuration generation
- **Validation**: Configuration validation and type checking