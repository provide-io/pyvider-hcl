# API Reference

Complete API reference for Pyvider HCL.

This reference is automatically generated from source code docstrings. Every module, class, and function is documented here.

## Package Organization

The library is organized into these main modules:

- **pyvider.hcl** - Main HCL interface
  - Core parsing and generation functionality
  - Primary entry points for most use cases

- **pyvider.hcl.parser** - Parsing implementation
  - `Parser` - Base parser class
  - `InferenceParser` - Type inference during parsing
  - `ParserContext` - Parsing context management

- **pyvider.hcl.factories** - Object factories
  - `TypeFactory` - HCL type creation
  - `VariableFactory` - Variable declaration handling
  - `ResourceFactory` - Resource block creation

- **pyvider.hcl.output** - Output formatting
  - `Formatter` - HCL output formatting
  - Output serialization and pretty-printing

- **pyvider.hcl.terraform** - Terraform-specific
  - `TerraformConfig` - Terraform configuration handling
  - Terraform-specific HCL features

- **pyvider.hcl.exceptions** - Exception hierarchy
  - Error types for parsing and generation

## Quick Links

**Most commonly used:**

| Import | Purpose | Documentation |
|--------|---------|---------------|
| `from pyvider.hcl import Parser` | Parse HCL content | [pyvider.hcl](pyvider/hcl/index/) |
| `from pyvider.hcl.parser import Parser` | Parser class | [parser](pyvider/hcl/parser/index/) |

**Exceptions:**

| Import | Purpose | Documentation |
|--------|---------|---------------|
| `from pyvider.hcl.exceptions import *` | HCL exceptions | [exceptions](pyvider/hcl/exceptions/) |

## Using the API Reference

Each module page includes:

- Module docstring with overview
- All classes with their methods and attributes
- All functions with signatures and parameters
- Type hints and parameter descriptions
- Usage examples (where available)
- Source code links

Navigate using the tree on the left, or use the search function to find specific classes, functions, or modules.
