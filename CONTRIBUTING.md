# Contributing to pyvider-hcl

Thank you for your interest in contributing to pyvider-hcl! This document provides guidelines for contributing to the project.

## Getting Started

### Prerequisites

- Python 3.11 or higher
- `uv` package manager

### Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/provide-io/pyvider-hcl.git
   cd pyvider-hcl
   ```

2. Set up the development environment:
   ```bash
   uv sync
   ```

This will create a virtual environment in `workenv/` with all development dependencies.

## Development Workflow

### Running Tests

```bash
# Run all tests
uv run pytest

# Run tests in parallel
uv run pytest -n auto

# Run with verbose output
uv run pytest -vvv

# Run specific test file
uv run pytest tests/test_parser.py

# Run tests matching a pattern
uv run pytest -k "test_parse"
```

### Code Quality

Before submitting a pull request, ensure your code passes all quality checks:

```bash
# Format code
uv run ruff format .

# Lint code
uv run ruff check .

# Type check
uv run mypy src/
```

### Code Style

- Follow PEP 8 guidelines (enforced by `ruff`)
- Use modern Python 3.11+ type hints (e.g., `list[str]` not `List[str]`)
- Use absolute imports, never relative imports
- Add type hints to all functions and methods
- Write docstrings for public APIs

## Project Structure

```
pyvider-hcl/
├── src/pyvider/hcl/          # Main package
│   ├── __init__.py           # Public API exports
│   ├── _version.py           # Version management
│   ├── exceptions.py         # Error handling
│   ├── parser/               # HCL parsing subpackage
│   │   ├── __init__.py      # Parser exports
│   │   ├── base.py          # Main parse_hcl_to_cty()
│   │   ├── inference.py     # Type inference logic
│   │   └── context.py       # parse_with_context()
│   ├── factories/            # Terraform factories subpackage
│   │   ├── __init__.py      # Factory exports
│   │   ├── types.py         # HCL type string parsing
│   │   ├── variables.py     # create_variable_cty()
│   │   └── resources.py     # create_resource_cty()
│   ├── output/               # Output formatting subpackage
│   │   ├── __init__.py      # Output exports
│   │   └── formatting.py    # pretty_print_cty()
│   └── terraform/            # Terraform-specific subpackage
│       ├── __init__.py      # Terraform exports
│       └── config.py        # parse_terraform_config()
├── tests/                    # Test suite
│   ├── conftest.py          # Pytest fixtures
│   ├── parser/              # Parser tests subpackage
│   │   └── test_parser.py   # Parser tests
│   ├── factories/           # Factory tests subpackage
│   │   └── test_factories.py # Factory tests
│   ├── output/              # Output tests subpackage
│   │   └── test_printer.py  # Output tests
│   ├── terraform/           # Terraform tests subpackage
│   │   └── test_terraform.py # Terraform tests
│   ├── test_integration.py  # Integration tests
│   └── test_property_based.py  # Property-based tests
├── examples/                 # Usage examples
│   ├── README.md            # Examples index
│   └── *.py                 # Example scripts
├── docs/                     # Documentation
│   ├── architecture.md      # Architecture details
│   ├── getting-started.md   # Getting started guide
│   └── guides/              # Topic-specific guides
├── Makefile                  # Build automation
└── pyproject.toml            # Project configuration
```

### Module Responsibilities

| Module | Responsibility | Key Functions |
|--------|---------------|---------------|
| `parser/` | HCL parsing, type inference | `parse_hcl_to_cty()`, `auto_infer_cty_type()` |
| `factories/` | Terraform structure creation | `create_variable_cty()`, `create_resource_cty()` |
| `output/` | CTY value formatting | `pretty_print_cty()` |
| `terraform/` | Terraform-specific features | `parse_terraform_config()` |
| `exceptions.py` | Error handling | `HclError`, `HclParsingError` |

## Testing Guidelines

### Writing Tests

- Place tests in the `tests/` directory
- Name test files with `test_` prefix (e.g., `test_parser.py`)
- Use descriptive test names that explain what is being tested
- Include both positive and negative test cases
- Add edge case tests

### Test Structure

```python
def test_feature_name_scenario():
    """Test description explaining what this test validates."""
    # Arrange
    hcl_content = '''...'''
    schema = CtyObject({...})

    # Act
    result = parse_hcl_to_cty(hcl_content, schema=schema)

    # Assert
    assert result.value["field"].value == expected_value
```

## Documentation

### Docstring Format

Use Google-style docstrings:

```python
def parse_hcl_to_cty(hcl_content: str, schema: CtyType | None = None) -> CtyValue:
    """Parse HCL content into CTY values.

    Args:
        hcl_content: HCL string to parse
        schema: Optional CTY type schema for validation

    Returns:
        Parsed and validated CTY value

    Raises:
        HclParsingError: If parsing or validation fails

    Example:
        >>> hcl = 'name = "example"'
        >>> result = parse_hcl_to_cty(hcl)
        >>> result.value["name"].value
        'example'
    """
```

### Updating Documentation

When adding new features or changing APIs:

1. Update relevant docstrings
2. Update `README.md` if adding user-facing features
3. Update `docs/guide.md` with usage examples
4. Update `CHANGELOG.md` under `[Unreleased]`

## Submitting Changes

### Pull Request Process

1. Create a feature branch from `develop`:
   ```bash
   git checkout -b feature/your-feature-name develop
   ```

2. Make your changes and commit with clear messages:
   ```bash
   git commit -m "Add feature: description of what was added"
   ```

3. Ensure all tests pass and code quality checks pass:
   ```bash
   uv run pytest -n auto
   uv run ruff check .
   uv run mypy src/
   ```

4. Push your branch and create a pull request against `develop`

5. Ensure your PR:
   - Has a clear title and description
   - References any related issues
   - Includes tests for new functionality
   - Updates documentation as needed
   - Passes all CI checks

### Commit Message Guidelines

- Use present tense ("Add feature" not "Added feature")
- Use imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit first line to 72 characters
- Reference issues and pull requests when relevant

Examples:
- `Add support for HCL template functions`
- `Fix parsing error with nested objects`
- `Update documentation for factory functions`

## Code Review Process

All submissions require review. The maintainers will:

- Review code for quality, style, and correctness
- Ensure tests are comprehensive
- Verify documentation is updated
- Check for breaking changes

## Getting Help

- Open an issue for bugs or feature requests
- Tag maintainers for questions on pull requests
- Check existing issues and documentation first

## License

By contributing to pyvider-hcl, you agree that your contributions will be licensed under the Apache-2.0 License.
