# Error Handling Guide

## Exception Hierarchy

```
HclError (base)
└── HclParsingError (parsing and validation errors)
```

## Catching Errors

```python
from pyvider.hcl import HclParsingError, parse_hcl_to_cty

try:
    result = parse_hcl_to_cty(hcl_content, schema=schema)
except HclParsingError as e:
    print(f"Error: {e.message}")
    if e.source_file:
        print(f"File: {e.source_file}")
    if e.line:
        print(f"Line: {e.line}")
```

## Error Types

### Syntax Errors
```python
invalid_hcl = "name = "  # Missing value
# Raises: HclParsingError
```

### Validation Errors
```python
schema = CtyObject({"port": CtyNumber()})
invalid = 'port = "8080"'  # String instead of number
# Raises: HclParsingError with validation details
```

### Factory Errors
```python
from pyvider.hcl import HclFactoryError, create_variable_cty

try:
    create_variable_cty(name="invalid-name", ...)
except HclFactoryError as e:
    print(f"Factory error: {e}")
```

## Error Context

### Enhanced Error Reporting with parse_with_context

The `parse_with_context` function provides enhanced error reporting with source location information. Unlike `parse_hcl_to_cty`, it captures and includes the source file path in error messages, making debugging significantly easier.

#### Basic Usage
```python
from pathlib import Path
from pyvider.hcl import parse_with_context, HclParsingError

config_file = Path("config.hcl")
try:
    content = config_file.read_text()
    result = parse_with_context(content, source_file=config_file)
except HclParsingError as e:
    print(f"Parse error in {e.source_file}:{e.line}:{e.column}")
    print(f"Message: {e.message}")
```

#### Difference from parse_hcl_to_cty

```python
from pyvider.hcl import parse_hcl_to_cty, parse_with_context, HclParsingError

invalid_hcl = '''
resource "aws_instance" {
    # Missing closing quote
    ami = "ami-123
    instance_type = "t2.micro"
}
'''

# Without context - minimal error info
try:
    result = parse_hcl_to_cty(invalid_hcl)
except HclParsingError as e:
    print(f"Error: {e}")
    # Output: Error: HCL parsing failed: ...
    # No file information available

# With context - full error details
try:
    result = parse_with_context(invalid_hcl, source_file=Path("terraform/main.tf"))
except HclParsingError as e:
    print(f"Error in {e.source_file} at line {e.line}, column {e.column}")
    print(f"Message: {e.message}")
    # Output: Error in terraform/main.tf at line 4, column 15
    # Message: HCL parsing failed: unterminated string literal
```

#### Processing Multiple Files with Context

```python
from pathlib import Path
from pyvider.hcl import parse_with_context, HclParsingError
import logging

logger = logging.getLogger(__name__)

def parse_hcl_directory(directory: Path):
    """Parse all HCL files in a directory with error context."""
    results = {}
    errors = []

    for hcl_file in directory.glob("**/*.hcl"):
        try:
            content = hcl_file.read_text()
            data = parse_with_context(content, source_file=hcl_file)
            results[hcl_file] = data
            logger.info(f"✅ Parsed: {hcl_file}")
        except HclParsingError as e:
            errors.append(e)
            logger.error(
                f"❌ Failed to parse {e.source_file}:{e.line}:{e.column} - {e.message}"
            )

    return results, errors

# Usage
configs, parse_errors = parse_hcl_directory(Path("terraform/"))
if parse_errors:
    print(f"Found {len(parse_errors)} parsing errors:")
    for err in parse_errors:
        print(f"  - {err.source_file}:{err.line} - {err.message}")
```

#### Note on Return Types

- `parse_with_context` returns **raw Python data** (dict/list), not CTY values
- Use it when you need enhanced error reporting but don't need CTY validation
- For CTY validation with error context, combine both approaches:

```python
from pyvider.hcl import parse_with_context, auto_infer_cty_type, HclParsingError

try:
    # Parse with context for better errors
    raw_data = parse_with_context(content, source_file=file_path)
    # Then convert to CTY
    cty_value = auto_infer_cty_type(raw_data)
except HclParsingError as e:
    # Error will have file context
    print(f"Error in {e.source_file}: {e}")
```

## Graceful Degradation

```python
def load_configs(files):
    results = []
    errors = []

    for file in files:
        try:
            content = file.read_text()
            result = parse_hcl_to_cty(content)
            results.append((file, result))
        except HclParsingError as e:
            errors.append((file, e))

    return results, errors
```

## Best Practices

1. Always catch `HclParsingError`
2. Log errors with context
3. Provide helpful error messages to users
4. Don't expose stack traces to end users
5. Use error context for debugging

## See Also

- <!-- [Examples](../../examples/07_error_handling.py) -->
