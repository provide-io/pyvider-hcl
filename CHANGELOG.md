# Changelog

All notable changes to the pyvider-hcl project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.6.2] - 2026-08-30

### Changed
- **BREAKING: `create_resource_cty` no longer wraps the resource name in a
  list.** It produced `resource[0].<type>[0].<name>`, where python-hcl2 8.x and
  therefore this package's parser produce `resource[0].<type>.<name>`. A value
  built by the factory could not be compared with, merged into, or substituted
  for one that had been parsed, though both claimed to describe the same
  resource. The two are now byte-identical, types included.

  Code reaching into the factory's output loses one index:

  ```python
  # before
  value.value["resource"].value[0].value[r_type].value[0].value[r_name]
  # after
  value.value["resource"].value[0].value[r_type].value[r_name]
  ```

  `create_variable_cty` is unaffected -- a single label was already a plain key.

## [0.6.1] - 2026-08-30

### Fixed
- **`except HclError` now catches everything this package raises.**
  `HclFactoryError` and `HclTypeParsingError` derived from `ValueError` alone,
  so the one thing a caller would reasonably reach for -- catching the
  package's own base class around a call into it -- silently missed both. Both
  keep `ValueError` in their bases, so code written against the old hierarchy
  still works.

### Changed
- All five exceptions are defined in `exceptions.py` rather than scattered
  across the modules that raise them. The modules that used to define them
  still expose them, so `from pyvider.hcl.output.emitter import HclEmitError`
  and the equivalent factory imports keep working.

## [0.6.0] - 2026-08-30

Requires python-hcl2 >= 8.1.3 and pyvider-cty >= 0.5.0. The exported API in
`pyvider.hcl` is unchanged; two names moved inside `pyvider.hcl.parser.normalize`.

### Changed
- **Dependency floors raised.** `python-hcl2>=8.1.3` (was `>=8.1.2`) and
  `pyvider-cty>=0.5.0` (was `>=0.4.0`). Both are hard requirements, not
  preferences: 8.1.3 exports the parsing primitives this package now builds on,
  and pyvider-cty 0.5.0 defers required-ness to the schema layer, which is the
  behaviour `null_required_attributes` is written against.
- **Heredoc and escape handling now use python-hcl2's own primitives**
  (`HEREDOC_PATTERN`, `HEREDOC_TRIM_PATTERN`, `process_escape_sequences`)
  instead of reimplementing them. The patterns track the library's grammar
  terminals, so delimiter and line-ending support follows it automatically.
- **Terraform blocks are read through `hcl2.query`** (`DocumentView`,
  `BlockView`) rather than by walking the rule tree by hand. Source line ranges
  still come from each rule's own metadata, since `with_meta=True` produces
  nothing upstream (amplify-education/python-hcl2#291).
- `normalize_hcl_string` now always returns `str`. It could previously return a
  number, for the one input that no longer reaches it.

### Fixed
- **Heredocs with a `-` or `.` in the delimiter** (`<<EO-T`) leaked their raw
  markers into the value instead of returning the body.
- **Heredocs in CRLF files** leaked their raw markers the same way.
- **`\uD800` and other lone-surrogate escapes** resolved to a string that
  cannot be encoded to UTF-8. They are now preserved verbatim, as are escapes
  naming a codepoint outside the Unicode range.
- Block labels containing escapes are resolved rather than left spelled as the
  source spelled them.

### Removed
- `pyvider.hcl.parser.normalize.unescape_hcl_string` — use
  `hcl2.utils.process_escape_sequences`, which it duplicated.
- The workaround converting `${-N}` expression strings back into negative
  numbers, fixed upstream in python-hcl2 8.1.3.
- `_normalize_key` is now public as `normalize_hcl_key`.

### Upstream
Three fixes in python-hcl2 8.1.3 were contributed from this work and removed
workarounds here: negative integer literals loading as `${-N}` strings (#307,
PR #311), an empty heredoc failing to parse and silently swallowing the
attributes after it (#309, PR #312), and `strip_string_quotes` stripping quotes
inside expressions while leaving escapes raw (#308/#310, PR #313).

## [0.5.0] - 2026-08-20

### Added
- CTY -> HCL emission (`cty_to_hcl`, `cty_to_hcl_data`, `HclEmitError`).
- Terraform config parsing into typed blocks with source line ranges
  (`TerraformConfig`, `TerraformBlock`, `parse_terraform_blocks`).
- Required-attribute checking (`null_required_attributes`).
- `format_cty`, alongside the existing `pretty_print_cty`.
- Parse errors carry file, line, column and a caret-annotated source snippet.
- Type-string support for `set()`, `tuple([...])` and `optional(T[, default])`.

### Changed
- Adapted to python-hcl2 8.x, whose output preserves source syntax for
  round-tripping; `parser/normalize.py` reverses it into plain Python values.

### Fixed
- A body-less heredoc yields the empty string.
- Escapes in quoted object keys and block labels are resolved.

## Earlier development notes

These entries predate the versioned sections above and were never dated; the
work they describe shipped by v0.3.0.

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

### Security
- Input validation for all HCL parsing operations via python-hcl2
- Schema validation to ensure type safety

## [0.0.1000] - initial release

HCL parsing with pyvider-cty integration: `parse_hcl_to_cty()`,
`parse_with_context()`, automatic type inference, schema validation, the
`create_variable_cty()` / `create_resource_cty()` factories, Terraform type
string parsing, `pretty_print_cty()`, and structured errors carrying a source
location. Built on python-hcl2 7.x.

Expression evaluation, template processing and `parse_terraform_config()` were
not implemented at this point; the last of those arrived in 0.5.0.
