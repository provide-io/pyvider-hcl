# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`pyvider-hcl` is a Python library for parsing HCL (HashiCorp Configuration Language) into `pyvider.cty` types. It wraps `python-hcl2` to provide seamless integration with the pyvider type system.

## Development Commands

### Environment Setup
```bash
# Install dependencies
uv sync

# Activate environment
source .venv/bin/activate
```

### Testing
```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=pyvider.hcl --cov-report=term-missing

# Run specific test
uv run pytest tests/test_parser.py -v

# Run in parallel
uv run pytest -n auto
```

### Code Quality
```bash
# Format code
uv run ruff format src/ tests/

# Lint code
uv run ruff check src/ tests/

# Auto-fix lint issues
uv run ruff check --fix --unsafe-fixes src/ tests/

# Type checking
uv run mypy src/
```

After editing Python files, run:
```bash
ruff format <file>
ruff check --fix --unsafe-fixes <file>
mypy <file>
ruff format <file>
```

## Architecture

### Core Components

1. **Parser** (`src/pyvider/hcl/parser.py`)
   - `parse_hcl_to_cty()` - Main parsing function
   - Schema validation support
   - Automatic type inference

2. **Type Inference** (`src/pyvider/hcl/inference.py`)
   - Converts HCL values to CtyType
   - Handles nested structures
   - List and object inference

3. **Factory Functions** (`src/pyvider/hcl/factory.py`)
   - `create_variable_cty()` - Create Terraform variables
   - `create_resource_cty()` - Create Terraform resources

4. **Pretty Printing** (`src/pyvider/hcl/display.py`)
   - `pretty_print_cty()` - Human-readable CtyValue output

### Key Dependencies

- **python-hcl2**: Core HCL parsing
- **pyvider-cty**: CtyValue and CtyType system
- **pyvider-telemetry**: Logging infrastructure
- **attrs**: Data class definitions
- **regex**: Advanced pattern matching

### Package Structure

```
src/pyvider/hcl/
├── __init__.py      # Public API exports
├── parser.py        # HCL to Cty parsing
├── inference.py     # Type inference
├── factory.py       # Terraform object factories
└── display.py       # Pretty printing
```

## API Usage

### Basic Parsing
```python
from pyvider.hcl import parse_hcl_to_cty, pretty_print_cty

hcl_string = '''
  name = "Jules"
  age = 30
'''

cty_value = parse_hcl_to_cty(hcl_string)
pretty_print_cty(cty_value)
```

### Schema Validation
```python
from pyvider.hcl import parse_hcl_to_cty
from pyvider.cty import CtyObject, CtyString, CtyNumber

schema = CtyObject({
    "name": CtyString(),
    "age": CtyNumber(),
})

cty_value = parse_hcl_to_cty(hcl_string, schema=schema)
```

### Creating Terraform Objects
```python
from pyvider.hcl import create_variable_cty, create_resource_cty

variable = create_variable_cty(
    name="my_var",
    type_str="string",
    default_py="default_value"
)

resource = create_resource_cty(
    r_type="aws_instance",
    r_name="example",
    attributes_py={"ami": "ami-12345"}
)
```

## Testing Strategy

- **pytest** with asyncio auto mode
- **Comprehensive filterwarnings** for clean output
- **Hypothesis** for property-based testing
- **Benchmark** support via pytest-benchmark
- **Coverage** tracking with branch coverage

## Important Notes

- Namespace package: `pyvider.hcl` under pyvider namespace
- Uses pyvider-telemetry for logging (not direct structlog)
- Modern Python 3.11+ type hints
- Absolute imports only (no relative imports)
- Strict mypy type checking enabled

## Code Style

- Line length: 111 characters
- Comprehensive ruff rules (E, F, W, I, UP, ANN, B, C90, SIM, PTH, RUF)
- No inline defaults - use constants modules
- No backward compatibility or migration logic
- `from __future__ import annotations` is encouraged for unquoted types
