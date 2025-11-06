# Testing with pyvider-hcl

## Test Setup

```python
import pytest
from pyvider.hcl import parse_hcl_to_cty
from pyvider.cty import CtyObject, CtyString

def test_parse_config():
    hcl = 'name = "test"'
    result = parse_hcl_to_cty(hcl)
    assert result.value['name'].value == "test"
```

## Using Fixtures

```python
@pytest.fixture
def sample_hcl():
    return 'name = "test"\nport = 8080'

def test_with_fixture(sample_hcl):
    result = parse_hcl_to_cty(sample_hcl)
    assert 'name' in result.value
```

## Testing with Schemas

```python
def test_schema_validation():
    schema = CtyObject({"port": CtyNumber()})
    hcl = 'port = 8080'
    result = parse_hcl_to_cty(hcl, schema=schema)
    assert result.value['port'].value == 8080
```

## Testing Errors

```python
from pyvider.hcl import HclParsingError

def test_invalid_hcl():
    with pytest.raises(HclParsingError):
        parse_hcl_to_cty('invalid = ')
```

## Property-Based Testing

```python
from hypothesis import given
from hypothesis import strategies as st

@given(st.text())
def test_parse_strings(value):
    hcl = f'key = "{value}"'
    result = parse_hcl_to_cty(hcl)
    assert result.value['key'].value == value
```

## See Also

<!-- - [Examples](../../examples/) -->
- [Test Suite](../../tests/)
