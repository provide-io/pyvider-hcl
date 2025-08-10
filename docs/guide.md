# `pyvider-hcl` Guide

This guide provides a more in-depth look at how to use `pyvider-hcl` to work with HCL and `pyvider.cty`.

## Parsing HCL

The `parse_hcl_to_cty` function is the main entry point for parsing HCL. It takes an HCL string and an optional `CtyType` schema.

### Automatic Type Inference

If you don't provide a schema, `pyvider-hcl` will automatically infer the `CtyType` from the HCL data.

```python
from pyvider.hcl import parse_hcl_to_cty, pretty_print_cty

hcl_string = """
  name = "Jules"
  age = 30
  is_developer = true
  skills = ["python", "go", "rust"]
"""

cty_value = parse_hcl_to_cty(hcl_string)

pretty_print_cty(cty_value)
# Output:
# CtyObject({'name': CtyString, 'age': CtyNumber, 'is_developer': CtyBool, 'skills': CtyList(CtyString)})
```

### Schema Validation

You can provide a `CtyType` schema to validate the HCL data. This is useful for ensuring that the HCL data has the correct structure and types.

```python
from pyvider.hcl import parse_hcl_to_cty
from pyvider.cty import CtyObject, CtyString, CtyNumber

schema = CtyObject({
    "name": CtyString(),
    "age": CtyNumber(),
})

hcl_string = """
  name = "Jules"
  age = "thirty" # Invalid type
"""

try:
    cty_value = parse_hcl_to_cty(hcl_string, schema=schema)
except Exception as e:
    print(e)
# Output:
# Schema validation failed after HCL parsing: At age: Number validation error: Cannot convert str to Number.
```

## Creating Terraform Variables and Resources

The `create_variable_cty` and `create_resource_cty` functions allow you to create `CtyValue` objects for Terraform variables and resources.

### `create_variable_cty`

This function creates a `CtyValue` for a Terraform variable.

```python
from pyvider.hcl import create_variable_cty, pretty_print_cty

variable_cty = create_variable_cty(
    name="my_variable",
    type_str="string",
    description="This is my variable.",
    default_py="my_default_value",
    sensitive=True,
)

pretty_print_cty(variable_cty)
```

### `create_resource_cty`

This function creates a `CtyValue` for a Terraform resource.

```python
from pyvider.hcl import create_resource_cty, pretty_print_cty

resource_cty = create_resource_cty(
    r_type="my_resource",
    r_name="my_instance",
    attributes_py={
        "name": "my_resource_name",
        "value": 123,
    },
    attributes_schema_py={
        "name": "string",
        "value": "number",
    },
)

pretty_print_cty(resource_cty)
```
