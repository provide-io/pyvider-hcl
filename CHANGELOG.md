# Changelog

All notable changes to the pyvider-hcl project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Infrastructure & Build Tooling**
  - Makefile with 25+ development targets (test, lint, format, typecheck, docs, etc.)
  - Build automation following provide ecosystem standards

- **Documentation Suite**
  - Getting started guide (docs/getting-started.md)
  - Comprehensive architecture documentation (docs/architecture.md)
  - Contributing guidelines (CONTRIBUTING.md)
  - 6 topic-specific guides: parsing, schema-validation, terraform-integration, type-inference, error-handling, testing
  - 8 working example scripts demonstrating all major features
  - Enhanced README with FAQ section

### Changed
- **Major Restructuring: Modular Architecture**
  - Migrated from flat module structure to modular subpackages
  - `parser/` subpackage: HCL parsing logic (base.py, inference.py, context.py)
  - `factories/` subpackage: Terraform factories (types.py, variables.py, resources.py)
  - `output/` subpackage: Output formatting (formatting.py)
  - `terraform/` subpackage: Terraform-specific features (config.py)
  - **Backward Compatibility Maintained**: All existing imports continue to work

- **Foundation Integration**
  - Switched from stdlib `logging` to `provide.foundation.logger`
  - Structured logging with key-value pairs throughout codebase
  - Emoji prefixes for visual log parsing (📄 for HCL, 🏭 for factories)

- **Code Quality Improvements**
  - **Zero linting errors** (ruff check)
  - **Zero type checking errors** (mypy)
  - **100% code formatted** (ruff format)
  - Full type annotations across all modules, examples, and tests
  - 97% test coverage (89/89 tests passing)

### Fixed
- Fixed pretty_print_cty handling of nested CtyValue objects
- Fixed integration test fixtures to use pytest's tmp_path

### Deprecated
- N/A (initial release)

### Removed
- N/A (initial release)

### Security
- Input validation for all HCL parsing operations via python-hcl2
- Schema validation to ensure type safety

### Planned for Future Releases
- Full HCL expression evaluation (e.g., `var.name`, function calls, conditionals)
- Template processing with variable substitution and HCL template functions
- Configuration file loading and validation pipeline
- Performance optimizations (lazy parsing, caching, streaming)
- Terraform block-specific validation (provider, data, module, locals, outputs)
- Direct file parsing API (currently requires manual file reading)

## Release Notes

### v0.0.1000 (Initial Release)

This is the first release of pyvider-hcl, providing HCL (HashiCorp Configuration Language) parsing with seamless pyvider.cty type system integration.

**Core Features:**
- **HCL Parsing**: Parse HCL strings using python-hcl2 library
- **CTY Integration**: Automatic conversion of HCL data to CTY type-safe values
- **Type Inference**: Automatic CTY type inference from HCL data structures
- **Schema Validation**: Validate HCL data against CTY type schemas
- **Factory Functions**: Create Terraform variable and resource structures programmatically

**Parser Capabilities:**
- **String Parsing**: Parse HCL content from strings via `parse_hcl_to_cty()`
- **Context Parsing**: Enhanced error reporting with `parse_with_context()`
- **Type String Parsing**: Parse Terraform type syntax (e.g., `"list(string)"`, `"object({name=string})"`)
- **Automatic Inference**: Infer CTY types when no schema is provided

**CTY Type System Integration:**
- **Type Safety**: All HCL values converted to type-safe CTY values
- **Type Validation**: Schema validation using CTY type definitions
- **Value Conversion**: Automatic conversion from HCL/Python to CTY types
- **Supported Types**: string, number, bool, list(), map(), object(), any/dynamic

**Factory Functions:**
- **Variables**: `create_variable_cty()` for Terraform variable structures
- **Resources**: `create_resource_cty()` for Terraform resource structures
- **Type String Support**: Parse and validate Terraform type syntax

**Development Features:**
- **Rich Errors**: Structured exceptions with source location (file, line, column)
- **Pretty Printing**: `pretty_print_cty()` for formatted CTY value output
- **Unicode Support**: Full Unicode support in HCL configuration strings
- **Testing Suite**: Comprehensive tests including property-based testing
- **Logging Integration**: Error handling via provide-foundation

**Integration Points:**
- **pyvider-cty**: Type system for all value handling
- **provide-foundation**: Error handling and logging infrastructure
- **python-hcl2**: Underlying HCL parser

**Dependencies:**
- `python-hcl2>=7.2.1`: Core HCL parsing
- `pyvider-cty>=0.0.113`: CTY type system
- `provide-foundation>=0.0.0`: Foundation services
- `attrs>=25.3.0`: Structured exception classes
- `regex>=2024.11.6`: Enhanced regex support

**Current Limitations:**
- No direct file parsing (use manual `Path.read_text()` + `parse_hcl_to_cty()`)
- No HCL expression evaluation (e.g., `var.name`, function calls)
- No template processing or variable substitution
- `parse_terraform_config()` is a placeholder, not yet implemented

This release establishes pyvider-hcl as a focused HCL-to-CTY parser for the pyvider ecosystem, with plans for expanded Terraform-specific features in future releases.
