# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`pyvider-hcl` is a Python library that provides HCL (HashiCorp Configuration Language) parsing and generation capabilities with seamless integration into the pyvider ecosystem, particularly with the CTY type system.

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

### Core Components

1. **HCL Parser** (`src/pyvider/hcl/parser/`)
   - `base.py`: Core HCL parsing functionality
   - `expressions.py`: HCL expression evaluation
   - `functions.py`: HCL function implementations
   - `variables.py`: Variable resolution and scoping

2. **CTY Integration** (`src/pyvider/hcl/cty/`)
   - `conversion.py`: Convert HCL values to CTY types
   - `types.py`: Type mapping between HCL and CTY
   - `values.py`: Value conversion utilities

3. **Configuration Processing** (`src/pyvider/hcl/config/`)
   - `loader.py`: Configuration file loading
   - `processor.py`: Configuration processing pipeline
   - `validation.py`: Configuration validation

4. **Template System** (`src/pyvider/hcl/templates/`)
   - `engine.py`: Template processing engine
   - `functions.py`: Template function library
   - `context.py`: Template context management

### Key Design Patterns

1. **CTY Integration**: All HCL values are converted to CTY types for type safety
2. **Parser Composition**: Modular parser design with composable components
3. **Template Processing**: Support for HCL templating with variable substitution
4. **Error Context**: Rich error messages with source location information

### Important Implementation Notes

1. **HCL Compatibility**: Full compatibility with HCL 2.x specification
2. **CTY Type Safety**: All values are type-checked using the CTY type system
3. **Performance**: Optimized parsing for large configuration files
4. **Unicode Support**: Full Unicode support in configuration files

## Testing Strategy

### Core Testing Requirements

**CRITICAL**: When testing pyvider-hcl, `provide-testkit` MUST be available and used for all testing utilities.

- **provide-testkit dependency**: Required in dev dependencies (already configured)
- **HCL test fixtures**: Use testkit fixtures for HCL file creation and validation
- **CTY integration tests**: Test conversion between HCL and CTY types
- **Parser validation**: Comprehensive testing of HCL parsing edge cases

### Standard Testing Pattern

```python
import pytest
from provide.testkit import temp_directory, test_files_structure
from pyvider.hcl import parse_hcl_file, parse_hcl_string

def test_hcl_parsing(temp_directory):
    """Test HCL file parsing."""
    hcl_content = '''
    variable "name" {
      description = "Resource name"
      type        = string
      default     = "example"
    }

    resource "example" "test" {
      name = var.name
      port = 8080
    }
    '''

    hcl_file = temp_directory / "test.hcl"
    hcl_file.write_text(hcl_content)

    config = parse_hcl_file(hcl_file)
    assert config.variables["name"].default == "example"
    assert config.resources["example"]["test"].name == "var.name"
```

### Testing Infrastructure

- Comprehensive test coverage including unit, integration, and property-based tests
- Tests use `pytest` with async support via `pytest-asyncio`
- Parallel test execution with `pytest-xdist`
- Coverage tracking with `pytest-cov`
- **HCL-specific fixtures**: All provided by provide-testkit integration

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
from pyvider.hcl import parse_hcl_string
from pyvider.cty import CtyValue

# Parse HCL and get CTY values
hcl_content = 'name = "example"'
parsed = parse_hcl_string(hcl_content)
cty_value = parsed.attributes["name"]  # Returns CtyString

assert isinstance(cty_value, CtyValue)
assert cty_value.as_python() == "example"
```

### provide-foundation Integration

```python
from provide.foundation import logger
from pyvider.hcl import HCLParser

log = logger.get_logger(__name__)

parser = HCLParser()
try:
    config = parser.parse_file("config.hcl")
    log.info("📄✅ HCL parsed successfully", file="config.hcl")
except HCLParseError as e:
    log.error("📄❌ HCL parse failed",
              file="config.hcl",
              error=str(e),
              line=e.line_number)
```

### pyvider Integration

```python
from pyvider import resource
from pyvider.hcl import hcl_attribute
from pyvider.schema import Attribute

@resource
class ConfiguredResource:
    """Resource with HCL configuration support."""

    name: str = Attribute(required=True)

    @hcl_attribute
    def configuration(self) -> dict:
        """Load configuration from HCL."""
        return self.load_hcl_config()
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

## Performance Considerations

- **Lazy Parsing**: Parse HCL files on-demand to reduce memory usage
- **Caching**: Cache parsed configurations for repeated access
- **Streaming**: Support streaming for large HCL files
- **Parallel Processing**: Parse multiple files in parallel where possible

## Security Considerations

- **Input Validation**: Validate all HCL input for security issues
- **Template Security**: Secure template processing to prevent injection
- **File Access**: Restrict file access to authorized paths only
- **Error Information**: Avoid exposing sensitive information in error messages