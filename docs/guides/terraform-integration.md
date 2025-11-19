# Terraform Integration Guide

## Overview

pyvider-hcl provides factory functions for creating Terraform structures.

## Creating Variables

```python
from pyvider.hcl import create_variable_cty

variable = create_variable_cty(
    name="region",
    type_str="string",
    default_py="us-west-2",
    description="AWS region"
)
```

### Variable Options

- `name`: Variable name (required)
- `type_str`: HCL type string (required)
- `default_py`: Default value (optional)
- `description`: Description (optional)
- `sensitive`: Mark as sensitive (optional)
- `nullable`: Allow null (optional)

## Creating Resources

```python
from pyvider.hcl import create_resource_cty

resource = create_resource_cty(
    r_type="aws_instance",
    r_name="web",
    attributes_py={
        "ami": "ami-12345",
        "instance_type": "t2.micro",
    },
    attributes_schema_py={
        "ami": "string",
        "instance_type": "string",
    }
)
```

## Type Strings

Supported HCL type strings:

- Primitives: `string`, `number`, `bool`, `any`
- Lists: `list(string)`, `list(number)`
- Maps: `map(string)`, `map(number)`
- Objects: `object({name=string, age=number})`

## Complex Types

### Nested Objects
```python
type_str = "object({host=string, pool=object({min=number, max=number})})"
```

### Lists of Objects
```python
type_str = "list(object({name=string, port=number}))"
```

## Error Handling

### Variable Creation Errors

Factory functions raise `HclFactoryError` for invalid inputs:

```python
from pyvider.hcl import create_variable_cty, HclFactoryError

try:
    # Invalid type string
    variable = create_variable_cty(
        name="port",
        type_str="invalid_type",  # Will raise error
        default_py=8080
    )
except HclFactoryError as e:
    print(f"Variable creation failed: {e}")

try:
    # Type mismatch with default value
    variable = create_variable_cty(
        name="enabled",
        type_str="bool",
        default_py="not a boolean"  # Type mismatch
    )
except HclFactoryError as e:
    print(f"Type validation failed: {e}")

try:
    # Empty variable name
    variable = create_variable_cty(
        name="",  # Empty name not allowed
        type_str="string"
    )
except HclFactoryError as e:
    print(f"Invalid variable name: {e}")
```

### Resource Creation Errors

```python
from pyvider.hcl import create_resource_cty, HclFactoryError

try:
    # Missing required attributes in schema
    resource = create_resource_cty(
        r_type="aws_instance",
        r_name="web",
        attributes_py={
            "ami": "ami-123",
            "instance_type": "t2.micro",
            "extra_field": "value"  # Not in schema
        },
        attributes_schema_py={
            "ami": "string",
            "instance_type": "string"
            # extra_field not defined - will raise error
        }
    )
except HclFactoryError as e:
    print(f"Resource validation failed: {e}")

try:
    # Invalid attribute type
    resource = create_resource_cty(
        r_type="aws_instance",
        r_name="web",
        attributes_py={
            "ami": "ami-123",
            "port": "not a number"  # String instead of number
        },
        attributes_schema_py={
            "ami": "string",
            "port": "number"  # Expects number
        }
    )
except HclFactoryError as e:
    print(f"Attribute type mismatch: {e}")
```

### Type String Parsing Errors

```python
from pyvider.hcl import HclTypeParsingError
from pyvider.hcl.factories import parse_hcl_type_string

try:
    # Malformed object syntax
    cty_type = parse_hcl_type_string("object({name=}")
except HclTypeParsingError as e:
    print(f"Type parsing failed: {e}")

try:
    # Unknown type
    cty_type = parse_hcl_type_string("custom_type")
except HclTypeParsingError as e:
    print(f"Unknown type: {e}")
```

### Best Practices for Error Handling

1. **Always wrap factory calls in try-except blocks** for production code
2. **Log errors** with provide-foundation logger for debugging
3. **Provide meaningful error messages** to users
4. **Validate inputs** before calling factory functions
5. **Test error cases** in your test suite

## Best Practices

1. Always provide schemas for resources
2. Use descriptive variable names
3. Add descriptions to all variables
4. Mark sensitive data as sensitive
5. Handle errors gracefully in production code

## See Also

<!-- - [Examples](../../examples/04_terraform_variables.py) -->
<!-- - [Examples](../../examples/05_terraform_resources.py) -->
