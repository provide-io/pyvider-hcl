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
   - `normalize_hcl_data(data)`: Strip python-hcl2 8.x serialization artifacts (quoted string
     literals, `__is_block__`/`__comments__` markers, escape sequences left raw). Every parse
     passes `normalize.HCL2_OPTIONS`, which turns off `preserve_heredocs` so hcl2 resolves
     heredoc bodies itself; escape resolution stays here (see `Important Implementation Notes`)
   - `null_required_attributes(value)`: Report null non-optional object attributes (pyvider-cty
     defers required-ness to the schema layer, so this package enforces it)
   - Uses `python-hcl2` for underlying HCL parsing (see the upstream status note: the
     currently required version is unreleased)
   - Modules: `base.py`, `inference.py`, `context.py`, `normalize.py`, `diagnostics.py`, `required.py`

2. **Factory Functions** (`factories/` subpackage)
   - `create_variable_cty(name, type_str, default_py=None, ...)`: Create Terraform variable CTY structures
   - `create_resource_cty(r_type, r_name, attributes_py, ...)`: Create Terraform resource CTY structures.
     Produces `resource[0].<type>.<name>` — the same shape the parser returns for the same resource,
     with one list at the `resource` level only. Do NOT wrap the resource name in a second list;
     that made factory output disagree with parser output, and `tests/factories/
     test_factory_parser_agreement.py` holds the two against each other
   - `parse_hcl_type_string(type_str)`: Parse HCL type strings (e.g., "list(string)", "object({...})")
   - Supports primitive types: string, number, bool, any
   - Supports complex types: list(), set(), map(), tuple([...]), object({...})
   - Supports optional(T) and optional(T, default) inside object() — the default is dropped,
     since CTY object types carry no per-attribute defaults
   - Modules: `types.py`, `variables.py`, `resources.py`

3. **Output Formatting and Emission** (`output/` subpackage)
   - `pretty_print_cty(value)`: Print CTY values in readable format
   - `format_cty(value)`: Same rendering, returned as a string
   - `cty_to_hcl(value)`: Render an object/map CTY value back into HCL text via `hcl2.dumps`
   - `cty_to_hcl_data(value)`: The intermediate python-hcl2-convention structure
   - `cty_to_hcl_block(block_type, labels, body)`: Render one HCL block. A `CtyValue` records no
     block-ness, so the type and labels come from the caller rather than being inferred
   - `cty_to_hcl_block_data(...)`: The same, unrendered, carrying `__is_block__` on the innermost
     body — merge several before calling `hcl2.dumps` to emit them together
   - Recursive formatting for nested structures (objects, lists, maps, sets, tuples), with
     explicit rendering of null, unknown, and marked values
   - Modules: `formatting.py`, `emitter.py`

4. **Terraform Integration** (`terraform/` subpackage)
   - `parse_terraform_config(config_path)`: Parse a `.tf` file into a `TerraformConfig`
   - `parse_terraform_blocks(content, source_file=None)`: Same, from a string
   - `TerraformConfig`: `blocks`, `attributes`, `blocks_of(type)`, `block_at(type, *labels)`,
     `block_types`
   - `TerraformBlock`: `block_type`, `labels`, `body`, `start_line`, `end_line`, `address`
   - Block source lines come from `SerializationOptions(with_meta=True)`, which annotates each
     block with `__start_line__`/`__end_line__`. `config.BLOCK_OPTIONS` adds that to the shared
     `HCL2_OPTIONS`; the keys are read off the block dict before `normalize_hcl_data` drops them
   - Modules: `config.py`

5. **Error Handling** (`exceptions.py`)
   - Every exception the package raises lives here, and every one derives from `HclError`, so
     `except HclError` catches all of them
   - `HclError`: Base exception class (extends `provide.foundation.FoundationError`)
   - `HclParsingError`: Structured exception with source location information (file, line, column),
     populated from the lark error the parser raises, plus a caret-annotated source snippet
   - `HclEmitError`: Raised when a CTY value has no HCL representation
   - `HclFactoryError`, `HclTypeParsingError`: Raised by the factories. Both also derive from
     `ValueError`, which they derived from alone before 0.6.1 -- keep that base, dropping it
     would break a caller catching `ValueError` around a factory call
   - The modules that used to define these still expose them, so a deep import such as
     `from pyvider.hcl.output.emitter import HclEmitError` keeps working

### Public API

Exported in `__init__.py`:
```python
from pyvider.hcl import (
    parse_hcl_to_cty,          # Main parser
    parse_with_context,        # Parser returning raw normalized data
    load_hcl_data,             # Parse + normalize, no CTY conversion
    normalize_hcl_data,        # Strip python-hcl2 8.x serialization artifacts
    auto_infer_cty_type,       # Type inference (delegates to pyvider-cty)
    null_required_attributes,  # Required-attribute checker
    create_variable_cty,       # Variable factory
    create_resource_cty,       # Resource factory
    pretty_print_cty,          # Pretty printer (stdout)
    format_cty,                # Pretty printer (string)
    cty_to_hcl,                # CTY -> HCL text
    cty_to_hcl_data,           # CTY -> python-hcl2 dict conventions
    cty_to_hcl_block,          # CTY -> one HCL block
    cty_to_hcl_block_data,     # CTY -> block dict, for merging
    parse_terraform_config,    # Terraform file parser
    parse_terraform_blocks,    # Terraform string parser
    TerraformConfig,           # Parsed configuration
    TerraformBlock,            # One top-level block, with source lines
    TERRAFORM_BLOCK_TYPES,     # Terraform's own block type names
    HclError,                  # Base exception
    HclParsingError,           # Parsing exception
    HclEmitError,              # Emission exception
    HclFactoryError,           # Factory exception
    HclTypeParsingError,       # Type-string exception
)
```

### Key Design Patterns

1. **CTY Integration**: All HCL values are converted to CTY types for type safety
2. **Schema Validation**: Optional schema parameter for validating HCL against expected CTY types
3. **Type Inference**: Automatic CTY type inference when no schema is provided
4. **Error Context**: Rich error messages with source location information (file, line, column)
5. **Factory Pattern**: Specialized factories for common Terraform structures

### Important Implementation Notes

1. **HCL Parsing**: Wraps `python-hcl2` for HCL 2.x compatibility. 8.x output preserves source
   syntax for round-tripping, so `parser/normalize.py` reverses it, reusing
   `hcl2.utils.process_escape_sequences`. Every call site passes `normalize.HCL2_OPTIONS`
   (`SerializationOptions(preserve_heredocs=False)`), so hcl2 hands back the string a heredoc
   body spells, with the dedent and trailing newline HCL gives it.
   Do NOT add `strip_string_quotes=True` to those options. It resolves escapes before this
   package sees the value, and the resolved quoted literal `"<<EOT\nbody\nEOT"` is a string
   that must stay distinct from the heredoc it spells — pinned by
   `tests/parser/test_hcl_semantics.py`. Leaving escapes raw until `normalize_hcl_string` keeps
   the two apart, because hcl2 has already turned the real heredoc into its body and whatever
   is still quoted is a literal.
   Likewise do NOT use `hcl2.utils.is_dollar_string` in the emitter: it accepts `"${a} ${b}"`,
   which emitted bare is invalid HCL
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

- **python-hcl2**: Core HCL parsing and emission (wrapped for enhanced functionality). The
  declared floor is `>=8.1.3`, but the code now needs the unreleased fixes described under
  `python-hcl2 upstream status`
- **pyvider-cty**: Type system integration
- **provide-foundation**: Logging and error handling
- **attrs**: Structured exception and config classes
- **regex**: Enhanced regular expression support for parsing

## Current Limitations and Future Enhancements

### Current Implementation Status

**Implemented:**
- HCL string parsing via python-hcl2, with 8.x serialization artifacts normalized away
- CTY type inference and validation, including required-attribute enforcement
- Terraform variable and resource factory functions
- Terraform type-string parsing: primitives, list/set/map/tuple/object, optional attributes
- Terraform config parsing into typed blocks with source line ranges
- CTY -> HCL emission
- Error handling with source location context (line, column, caret snippet)

**Planned/Not Yet Implemented:**
- Full HCL expression evaluation (e.g., `var.name`, function calls) — expressions are preserved
  verbatim as `${...}` strings, never evaluated
- Template processing with variable substitution
- Performance optimizations (lazy parsing, caching, streaming)
- Terraform block-specific *semantic* validation (required arguments per block type, etc.)

**python-hcl2 upstream status:**

> **This package currently requires an unreleased python-hcl2.** The three fixes below are
> committed only on local branches in `../python-hcl2` (merged on `integration/all-three`), not
> filed, not released. Against PyPI 8.1.3 this package fails to import — `hcl2.const` has no
> `START_LINE`/`END_LINE` — and its heredoc values are wrong. Raise the floor in
> `pyproject.toml` when the release carrying them lands.
>
> Until then the checkout has to be installed by hand — `uv pip install
> /Volumes/data/pyv/python-hcl2` — and **`uv sync` / `uv run` put the published 8.1.3 back**,
> because that is what `uv.lock` pins. Export `UV_NO_SYNC=1` in any shell used here: without it
> the `mypy strict` pre-commit hook (`uv run mypy src/`) reverts the environment and then fails
> on the five resulting import errors. Nothing in the repo is configured around this, so there
> is nothing to undo later.
>
> Install it non-editable. `-e` works at runtime but mypy cannot follow an editable install (it
> does not read `.pth` files) and reports `hcl2` as missing; a plain install also avoids the
> stale `site-packages/hcl2/` directory that uv's uninstall leaves behind, which shadows an
> editable install as a namespace package.

Fixed upstream, workarounds removed here:
- Negative integer literals loaded as `${-N}` strings (#307, fixed by PR #311)
- Empty heredoc (`<<EOF\nEOF`) failed to parse, silently swallowing the attributes that
  followed (#309, fixed by PR #312)
- `strip_string_quotes` stripped quotes inside expressions and left escapes unresolved
  (#308/#310, fixed by PR #313) — the option is still unused here, for the reasons in
  `Important Implementation Notes`

Fixed locally, not yet upstream (branches in `../python-hcl2`):
- `SerializationOptions.with_meta` emitted nothing (#291) — now emits `__start_line__` and
  `__end_line__` per block, which is where `config.py` reads them from
- hcl2's heredoc value form dropped the trailing newline, dedented whitespace-only lines, and
  measured `<<-` indentation in spaces only — now matches OpenTofu, so `normalize.py` no longer
  computes the body itself. The same change stopped `strings_to_heredocs` writing a body one
  line longer than the value it came from
- `BodyView.blocks()`/`.attributes()` were annotated `List[NodeView]` — now the concrete view
  classes, so `config.py` no longer narrows with `isinstance`

Still open upstream, still handled here:
- Heredoc markers are retained in the default (round-trippable) value form (#303) — by design
  upstream, avoided here with `preserve_heredocs=False`

### Security Considerations

- **Input Validation**: All HCL input is parsed through python-hcl2 library
- **Schema Validation**: Use CTY schemas to validate expected structure
- **Error Information**: Error messages include source location but avoid exposing sensitive data
- **File Access**: When implementing file loading, restrict to authorized paths only
