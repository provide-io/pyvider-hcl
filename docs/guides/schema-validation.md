# Schema Validation Guide

## Why Use Schemas?

Schemas provide:
- Type safety
- Early error detection
- Clear contracts
- Better error messages

## Defining Schemas

```python
from pyvider.cty import CtyObject, CtyString, CtyNumber, CtyBool

schema = CtyObject({
    "name": CtyString(),
    "port": CtyNumber(),
    "enabled": CtyBool(),
})
```

## Complex Schemas

### Lists
```python
from pyvider.cty import CtyList, CtyString

schema = CtyObject({
    "tags": CtyList(element_type=CtyString())
})
```

### Nested Objects
```python
schema = CtyObject({
    "server": CtyObject({
        "host": CtyString(),
        "port": CtyNumber(),
    })
})
```

### Lists of Objects
```python
schema = CtyObject({
    "users": CtyList(
        element_type=CtyObject({
            "name": CtyString(),
            "age": CtyNumber(),
        })
    )
})
```

## Validation Errors

```python
from pyvider.hcl import HclParsingError, parse_hcl_to_cty

try:
    result = parse_hcl_to_cty(hcl, schema=schema)
except HclParsingError as e:
    print(f"Validation failed: {e}")
```

## Schema Best Practices

1. Define schemas for all external configuration
2. Make schemas as specific as possible
3. Document your schemas
4. Test your schemas

## See Also

- [API Reference](../reference/)
- <!-- [Examples](../../examples/02_schema_validation.py) -->
