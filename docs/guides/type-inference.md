# Type Inference Guide

## How Type Inference Works

pyvider-hcl automatically infers CTY types from Python/HCL data structures. The inference algorithm examines the actual values in your data to determine appropriate CTY types.

### Basic Type Mappings

- `str` → `CtyString()`
- `int`, `float` → `CtyNumber()`
- `bool` → `CtyBool()`
- `list` → `CtyList(element_type)` (element type inferred from list contents)
- `dict` → `CtyObject({...})`
- `None` → `CtyDynamic()`
- `Decimal` → `CtyNumber()` (preserves precision)

### Complex Type Inference

#### Nested Objects
When a dictionary is encountered, type inference creates a `CtyObject` with attribute types inferred from each value:

```python
from pyvider.hcl import auto_infer_cty_type

data = {
    "name": "webapp",
    "port": 8080,
    "enabled": True,
    "config": {
        "timeout": 30,
        "retry": True
    }
}

result = auto_infer_cty_type(data)
# Creates CtyObject with:
# - name: CtyString
# - port: CtyNumber
# - enabled: CtyBool
# - config: CtyObject with timeout (CtyNumber) and retry (CtyBool)
```

#### List Type Inference
Lists are analyzed to infer their element types. Homogeneous lists get specific element types, while mixed lists use `CtyDynamic()`:

```python
# Homogeneous list - infers specific element type
data_numbers = {"values": [1, 2, 3, 4]}
result = auto_infer_cty_type(data_numbers)
# values becomes CtyList(CtyNumber())

# Heterogeneous list - falls back to dynamic
data_mixed = {"values": [1, "two", True, 3.14]}
result = auto_infer_cty_type(data_mixed)
# values becomes CtyList(CtyDynamic())
```

#### Deeply Nested Structures
The inference algorithm recursively processes nested structures:

```python
from pyvider.hcl import parse_hcl_to_cty

hcl_content = """
servers = [
  {
    name = "web-1"
    ip = "10.0.1.1"
    tags = {
      environment = "prod"
      team = "platform"
    }
  },
  {
    name = "web-2"
    ip = "10.0.1.2"
    tags = {
      environment = "prod"
      team = "platform"
    }
  }
]
"""

result = parse_hcl_to_cty(hcl_content)
# Infers nested structure with appropriate types at each level
```

## When to Use Inference

**Use inference for:**
- Prototyping and exploration
- Scripts and tools
- Flexible data structures
- Quick parsing without validation

**Use schemas for:**
- Production code
- API contracts
- Type safety requirements
- Clear validation rules

## Examples

<!-- See [examples/03_type_inference.py](../../examples/03_type_inference.py) -->

## Inference Limitations and Edge Cases

### Current Limitations

1. **No Union Types**: Cannot infer union or variant types
   ```python
   # Mixed types fall back to CtyDynamic
   mixed = {"value": some_complex_object}  # → value: CtyDynamic()
   ```

2. **No Validation**: Inference accepts any valid structure without constraints
   ```python
   # No way to enforce required fields or value ranges
   data = {"port": 99999}  # Accepted even if invalid port number
   ```

3. **Type Ambiguity**: Some values could map to multiple types
   ```python
   # String "123" vs number 123
   value = "123"  # Always inferred as CtyString, not CtyNumber
   ```

### Best Practices

- Use schemas when type precision is important
- Combine inference with validation for production code
- Document expected types even when using inference
- Test edge cases with your specific data structures

## See Also

- [Schema Validation Guide](schema-validation.md)
- [Parsing Guide](parsing.md)
