# Parsing Guide

## Overview

This guide covers HCL parsing techniques with pyvider-hcl.

## Basic Parsing

```python
from pyvider.hcl import parse_hcl_to_cty

hcl = 'name = "example"'
result = parse_hcl_to_cty(hcl)
```

## Parsing from Files

```python
from pathlib import Path
from pyvider.hcl import parse_hcl_to_cty

content = Path("config.hcl").read_text()
result = parse_hcl_to_cty(content)
```

## Enhanced Error Context

```python
from pyvider.hcl import parse_with_context

content = file.read_text()
result = parse_with_context(content, source_file=file)
```

## Type Inference vs Schemas

### Automatic Inference
Best for: Prototyping, exploration
```python
result = parse_hcl_to_cty(hcl)  # Types inferred automatically
```

### Schema Validation
Best for: Production, type safety
```python
from pyvider.cty import CtyObject, CtyString

schema = CtyObject({"name": CtyString()})
result = parse_hcl_to_cty(hcl, schema=schema)
```

## Handling Complex Structures

### Nested Objects
```python
hcl = """
server = {
  config = {
    host = "localhost"
    port = 8080
  }
}
"""
result = parse_hcl_to_cty(hcl)
```

### Lists
```python
hcl = 'tags = ["prod", "api"]'
result = parse_hcl_to_cty(hcl)
```

## Best Practices

1. Always handle `HclParsingError`
2. Use schemas for production code
3. Use `parse_with_context` for file parsing
4. Validate before processing

## See Also

- [Schema Validation Guide](schema-validation.md)
- [Error Handling Guide](error-handling.md)
- <!-- [Examples](../../examples/01_basic_parsing.py) -->
