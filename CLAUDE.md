# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`pyvider-hcl` is a Python library that provides HCL (HashiCorp Configuration Language) parsing capabilities with seamless integration into the pyvider ecosystem, particularly with the CTY type system.

## Development Environment Setup

**IMPORTANT**: Use `uv sync` to set up the development environment. This script provisions a virtual environment in `workenv/` (NOT `.venv`). The environment setup handles:
- Python 3.11+ requirement
- UV package manager for dependency management
- Platform-specific virtual environments (e.g., `workenv/pyvider-hcl_darwin_arm64`)

## Common Development Commands

```bash
# Environment setup (always use this instead of manual venv creation)
uv sync

# Run tests
uv run pytest                           # Run all tests
uv run pytest -n auto                   # Run tests in parallel
uv run pytest -n auto -vvv             # Verbose parallel test run
uv run pytest tests/test_specific.py   # Run specific test file
uv run pytest -k "test_name"           # Run tests matching pattern

# Code quality checks
uv run ruff check .                    # Run linter
uv run ruff format .                   # Format code
uv run mypy src/                       # Type checking

# Build and distribution
uv build                        # Build package
uv publish                      # Publish to PyPI
```

## Architecture & Code Structure

> **📐 For detailed architecture diagrams and data flow documentation, see [docs/architecture.md](docs/architecture.md)**

### Core Modules

The library is organized as a modular package under `src/pyvider/hcl/`:

1. **HCL Parser** (`parser/` subpackage)
   - `parse_hcl_to_cty(hcl_content, schema=None)`: Main parsing function that converts HCL strings to CTY values
   - `parse_with_context(content, source_file=None)`: Parse HCL with enhanced error context
   - `auto_infer_cty_type(raw_data)`: Automatically infer CTY types from Python data structures
   - Uses `python-hcl2` library for underlying HCL parsing
   - Modules: `base.py`, `inference.py`, `context.py`

2. **Factory Functions** (`factories/` subpackage)
   - `create_variable_cty(name, type_str, default_py=None, ...)`: Create Terraform variable CTY structures
   - `create_resource_cty(r_type, r_name, attributes_py, ...)`: Create Terraform resource CTY structures
   - `parse_hcl_type_string(type_str)`: Parse HCL type strings (e.g., "list(string)", "object({...})")
   - Supports primitive types: string, number, bool, any
   - Supports complex types: list(), map(), object()
   - Modules: `types.py`, `variables.py`, `resources.py`

3. **Output Formatting** (`output/` subpackage)
   - `pretty_print_cty(value)`: Format and display CTY values in readable format
   - Recursive formatting for nested structures (objects, lists, maps, tuples)
   - Modules: `formatting.py`

4. **Terraform Integration** (`terraform/` subpackage)
   - `parse_terraform_config(config_path)`: Placeholder for future Terraform-specific config parsing
   - **Note**: Currently not fully implemented, returns placeholder
   - Modules: `config.py`

5. **Error Handling** (`exceptions.py`)
   - `HclError`: Base exception class (extends `provide.foundation.FoundationError`)
   - `HclParsingError`: Structured exception with source location information (file, line, column)

### Public API

Exported in `__init__.py`:
```python
from pyvider.hcl import (
    parse_hcl_to_cty,        # Main parser
    parse_with_context,      # Parser with error context
    create_variable_cty,     # Variable factory
    create_resource_cty,     # Resource factory
    pretty_print_cty,        # Pretty printer
    parse_terraform_config,  # Terraform parser (placeholder)
    HclError,               # Base exception
    HclParsingError,        # Parsing exception
)
```

### Key Design Patterns

1. **CTY Integration**: All HCL values are converted to CTY types for type safety
2. **Schema Validation**: Optional schema parameter for validating HCL against expected CTY types
3. **Type Inference**: Automatic CTY type inference when no schema is provided
4. **Error Context**: Rich error messages with source location information (file, line, column)
5. **Factory Pattern**: Specialized factories for common Terraform structures

### Important Implementation Notes

1. **HCL Parsing**: Wraps `python-hcl2` library for HCL 2.x compatibility
2. **CTY Type Safety**: All values validated using the pyvider-cty type system
3. **Type String Parsing**: Supports Terraform type syntax (e.g., "list(string)", "object({name=string, age=number})")
4. **Unicode Support**: Full Unicode support in configuration files
5. **Structured Errors**: Uses `attrs` for structured exception classes

## Testing Strategy

### Core Testing Requirements

**CRITICAL**: When testing pyvider-hcl, `provide-testkit` MUST be available and used for all testing utilities.

- **provide-testkit dependency**: Required in dev dependencies (already configured)
- **Test files**: Located in `tests/` directory
  - `tests/parser/test_parser.py`: Core parsing functionality tests
  - `tests/factories/test_factories.py`: Factory function tests
  - `tests/output/test_printer.py`: Pretty printing tests
  - `tests/terraform/test_terraform.py`: Terraform-specific functionality tests
  - `tests/test_integration.py`: End-to-end integration tests
  - `tests/test_property_based.py`: Property-based tests using Hypothesis

### Standard Testing Pattern

```python
import pytest
from pyvider.hcl import parse_hcl_to_cty, pretty_print_cty
from pyvider.cty import CtyObject, CtyString, CtyNumber

def test_hcl_parsing_with_schema():
    """Test HCL parsing with schema validation."""
    hcl_content = '''
    name = "example"
    port = 8080
    '''

    schema = CtyObject({
        "name": CtyString(),
        "port": CtyNumber(),
    })

    cty_value = parse_hcl_to_cty(hcl_content, schema=schema)
    assert cty_value.value["name"].value == "example"
    assert cty_value.value["port"].value == 8080

def test_variable_factory():
    """Test Terraform variable creation."""
    from pyvider.hcl import create_variable_cty

    var_cty = create_variable_cty(
        name="instance_count",
        type_str="number",
        default_py=1,
        description="Number of instances",
    )

    # Verify structure
    assert "variable" in var_cty.value
```

### Testing Infrastructure

- Comprehensive test coverage including unit, integration, and property-based tests
- Tests use `pytest` with async support via `pytest-asyncio`
- Parallel test execution with `pytest-xdist` (use `uv run pytest -n auto`)
- Coverage tracking with `pytest-cov`
- Property-based testing with Hypothesis for edge case discovery

## Common Issues & Solutions

1. **ModuleNotFoundError for dependencies**: Run `uv sync` to ensure proper environment setup
2. **HCL parsing errors**: Check HCL syntax and ensure proper escaping
3. **CTY conversion issues**: Verify type compatibility between HCL and CTY
4. **Import errors**: Ensure PYTHONPATH includes both `src/` and project root

## Development Guidelines

- Always use modern Python 3.11+ type hints (e.g., `list[str]` not `List[str]`)
- Maintain compatibility with HCL 2.x specification
- Follow CTY type system conventions for all values
- Use `attrs` for data classes consistently
- No migration, backward compatibility, or legacy implementation logic
- Only use absolute imports, never relative imports
- Use async in tests where appropriate
- No hardcoded defaults - use configuration constants

## Integration with Ecosystem

### pyvider-cty Integration

```python
from pyvider.hcl import parse_hcl_to_cty, pretty_print_cty
from pyvider.cty import CtyValue, CtyObject, CtyString

# Parse HCL and get CTY values
hcl_content = '''
name = "example"
enabled = true
'''

# Parse with automatic type inference
cty_value = parse_hcl_to_cty(hcl_content)
assert isinstance(cty_value, CtyValue)
assert cty_value.value["name"].value == "example"

# Parse with schema validation
schema = CtyObject({
    "name": CtyString(),
})
validated_value = parse_hcl_to_cty('name = "test"', schema=schema)
```

### provide-foundation Integration

```python
import logging
from pathlib import Path
from pyvider.hcl import parse_with_context, HclParsingError

logger = logging.getLogger(__name__)

# Parse with error context
config_file = Path("config.hcl")
try:
    content = config_file.read_text()
    parsed_data = parse_with_context(content, source_file=config_file)
    logger.info(f"📄✅ HCL parsed successfully: {config_file}")
except HclParsingError as e:
    logger.error(f"📄❌ HCL parse failed: {e}")
    # Error includes file, line, and column information
```

### Terraform Variable and Resource Creation

```python
from pyvider.hcl import create_variable_cty, create_resource_cty, pretty_print_cty

# Create a Terraform variable
variable = create_variable_cty(
    name="region",
    type_str="string",
    default_py="us-west-2",
    description="AWS region",
    sensitive=False,
)
pretty_print_cty(variable)

# Create a Terraform resource
resource = create_resource_cty(
    r_type="aws_instance",
    r_name="web_server",
    attributes_py={
        "ami": "ami-12345678",
        "instance_type": "t2.micro",
        "tags": {"Name": "WebServer"},
    },
    attributes_schema_py={
        "ami": "string",
        "instance_type": "string",
        "tags": "object({Name=string})",
    },
)
pretty_print_cty(resource)
```

## Output Guidelines for CLI and Logging

**IMPORTANT**: Use the correct output method for the context:

- **CLI User-Facing Output**: Use Foundation's output utilities for user messages
- **Application Logging**: Use Foundation logger for internal logging/debugging
- **Parser Errors**: Use structured error reporting with source location

## Third-Party Dependencies

The package has minimal dependencies:

- **python-hcl2**: Core HCL parsing (wrapped for enhanced functionality)
- **pyvider-cty**: Type system integration
- **provide-foundation**: Logging and error handling
- **regex**: Enhanced regular expression support for parsing

## Current Limitations and Future Enhancements

### Current Implementation Status

**Implemented:**
- HCL string parsing via python-hcl2
- CTY type inference and validation
- Terraform variable and resource factory functions
- Error handling with source location context

**Planned/Not Yet Implemented:**
- Full HCL expression evaluation (e.g., `var.name`, function calls)
- Template processing with variable substitution
- Configuration file loading pipeline
- Performance optimizations (lazy parsing, caching, streaming)
- Terraform block-specific validation (provider, data, module, etc.)

### Security Considerations

- **Input Validation**: All HCL input is parsed through python-hcl2 library
- **Schema Validation**: Use CTY schemas to validate expected structure
- **Error Information**: Error messages include source location but avoid exposing sensitive data
- **File Access**: When implementing file loading, restrict to authorized paths only