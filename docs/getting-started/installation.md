# Installation

Complete installation guide for pyvider-hcl.

## Prerequisites

--8<-- ".provide/foundry/docs/_partials/python-requirements.md"

## Installing UV

--8<-- ".provide/foundry/docs/_partials/uv-installation.md"

## Python Version Setup

--8<-- ".provide/foundry/docs/_partials/python-version-setup.md"

## Virtual Environment

--8<-- ".provide/foundry/docs/_partials/virtual-env-setup.md"

## Installing pyvider-hcl

### Using UV (Recommended)

```bash
uv add pyvider-hcl
```

### Using pip

```bash
pip install pyvider-hcl
```

### From Source

For development or accessing the latest features:

```bash
# Clone the repository
git clone https://github.com/provide-io/pyvider-hcl.git
cd pyvider-hcl

# Set up environment and install
uv sync

# Verify installation
python -c "import pyvider.hcl; print('✅ pyvider-hcl installed')"
```

## Verification

After installation, verify everything works:

```bash
# Check Python version
python --version  # Should show 3.11+

# Verify package installation
python -c "import pyvider.hcl; print(pyvider.hcl.__version__)"

# Run a simple parse test
python -c "from pyvider.hcl import parse_hcl_to_cty; result = parse_hcl_to_cty('name = \"test\"'); print('✅ HCL parsing works')"
```

## Dependencies

pyvider-hcl requires:

- **python-hcl2**: HCL parsing library
- **pyvider-cty**: CTY type system integration
- **provide-foundation**: Logging and error handling
- **regex**: Enhanced regular expression support

These are installed automatically when you install pyvider-hcl.

## Troubleshooting

--8<-- ".provide/foundry/docs/_partials/troubleshooting-common.md"

### HCL-Specific Issues

**Problem**: `ImportError: cannot import name 'parse_hcl_to_cty'`

**Solution**: Ensure you have the latest version installed:
```bash
uv add pyvider-hcl --upgrade
```

**Problem**: HCL parsing errors

**Solution**: Verify your HCL syntax:
- Check for proper quoting of strings
- Ensure proper nesting of blocks
- Validate type expressions (e.g., `list(string)`)

## Next Steps

After installation:

1. **[Getting Started](../getting-started/)** - Learn HCL parsing basics
2. **[User Guide](../guide/)** - Comprehensive usage examples
3. **[API Reference](../reference/)** - Complete API documentation
