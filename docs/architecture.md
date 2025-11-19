# pyvider-hcl Architecture

This document provides a visual and detailed overview of the pyvider-hcl architecture.

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Application                         │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      pyvider.hcl Package                         │
│                                                                  │
│  ┌──────────────────┐  ┌──────────────────┐  ┌────────────────┐│
│  │  parser/         │  │  factories/      │  │  output/       ││
│  │  ├─ base.py     │  │  ├─ types.py     │  │  └─ formatting ││
│  │  ├─ inference.py│  │  ├─ variables.py │  │      .py       ││
│  │  └─ context.py  │  │  └─ resources.py │  │                ││
│  │                  │  │                  │  │                ││
│  │ • parse_hcl_    │  │ • create_        │  │ • pretty_print ││
│  │   to_cty()      │  │   variable_cty   │  │   _cty()       ││
│  │ • parse_with_   │  │ • create_        │  │                ││
│  │   context()     │  │   resource_cty   │  │                ││
│  │ • auto_infer_   │  │ • parse_hcl_     │  │                ││
│  │   cty_type()    │  │   type_string()  │  │                ││
│  └─────────────────┘  └──────────────────┘  └────────────────┘│
│                                                                 │
│  ┌──────────────────┐  ┌──────────────────┐                   │
│  │  terraform/      │  │  exceptions.py   │                   │
│  │  └─ config.py    │  │  • HclError      │                   │
│  │                  │  │  • HclParsing    │                   │
│  │ • parse_         │  │    Error         │                   │
│  │   terraform_     │  │                  │                   │
│  │   config()       │  │                  │                   │
│  │   (placeholder)  │  │                  │                   │
│  └──────────────────┘  └──────────────────┘                   │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                ┌───────────────┼───────────────┐
                │               │               │
                ▼               ▼               ▼
    ┌──────────────────┐ ┌──────────────┐ ┌──────────────────┐
    │  python-hcl2     │ │ pyvider-cty  │ │ provide-         │
    │  (HCL parser)    │ │ (type system)│ │ foundation       │
    │                  │ │              │ │ (errors/logging) │
    └──────────────────┘ └──────────────┘ └──────────────────┘
```

## Module Breakdown

### 1. Parser Subpackage (`parser/`)

**Modules:**
- **`base.py`**: Core parsing logic - contains `parse_hcl_to_cty()`
- **`inference.py`**: Type inference - contains `auto_infer_cty_type()`
- **`context.py`**: Enhanced error context - contains `parse_with_context()`

**Responsibilities:**
- Parse HCL strings into Python data structures
- Convert Python data to CTY types
- Automatic type inference
- Schema validation

**Data Flow:**
```
HCL String
    ↓
parse_hcl_to_cty() [base.py]
    ↓
python-hcl2.loads()  ──→  Python dict/list
    ↓
Schema provided?
    ├─ Yes → schema.validate(data)  ──→  CtyValue
    └─ No  → auto_infer_cty_type() [inference.py]  ──→  CtyValue
```

**Key Functions:**
- `parse_hcl_to_cty(hcl_content, schema=None) → CtyValue` (base.py)
- `parse_with_context(content, source_file=None) → dict` (context.py)
- `auto_infer_cty_type(raw_data) → CtyValue` (inference.py)

---

### 2. Factories Subpackage (`factories/`)

**Modules:**
- **`types.py`**: Type string parsing - contains `parse_hcl_type_string()`
- **`variables.py`**: Variable factory - contains `create_variable_cty()`
- **`resources.py`**: Resource factory - contains `create_resource_cty()`

**Responsibilities:**
- Create Terraform variable structures
- Create Terraform resource structures
- Parse HCL type strings into CTY types

**Type String Parsing Flow:**
```
Type String (e.g., "list(string)")
    ↓
parse_hcl_type_string() [types.py]
    ├─ Primitive? → Return CtyString/CtyNumber/CtyBool
    ├─ list(T)?   → Return CtyList(element_type=T)
    ├─ map(T)?    → Return CtyMap(element_type=T)
    └─ object({})?→ Parse attributes → Return CtyObject
```

**Variable Creation Flow:**
```
Python inputs
    ↓
create_variable_cty() [variables.py]
    ↓
Parse type_str → CtyType [types.py]
    ↓
Validate default against type
    ↓
Build Terraform variable structure
    ↓
Validate with schema → CtyValue
```

**Key Functions:**
- `create_variable_cty(name, type_str, default_py=None, ...) → CtyValue` (variables.py)
- `create_resource_cty(r_type, r_name, attributes_py, ...) → CtyValue` (resources.py)
- `parse_hcl_type_string(type_str) → CtyType` (types.py)

---

### 3. Output Subpackage (`output/`)

**Modules:**
- **`formatting.py`**: CTY value formatting - contains `pretty_print_cty()`

**Responsibilities:**
- Format CTY values for human-readable display
- Handle nested structures (objects, lists, maps, tuples)

**Printing Flow:**
```
CtyValue
    ↓
pretty_print_cty() [formatting.py]
    ↓
_pretty_print_cty_recursive()
    ├─ CtyObject  → Format as JSON object
    ├─ CtyList    → Format as JSON array
    ├─ CtyMap     → Format as JSON object
    ├─ CtyTuple   → Format as JSON array
    └─ Primitive  → Format as string/number/bool
```

**Key Functions:**
- `pretty_print_cty(value) → None` (prints to stdout) (formatting.py)

---

### 4. Terraform Subpackage (`terraform/`)

**Modules:**
- **`config.py`**: Terraform configuration parsing - contains `parse_terraform_config()`

**Status:** Placeholder for future implementation

**Planned Responsibilities:**
- Parse Terraform-specific blocks (provider, module, data, etc.)
- Handle Terraform configuration files
- Validate Terraform-specific structures

**Current:**
- `parse_terraform_config(config_path)` returns placeholder (config.py)

---

### 5. Exceptions Module (`exceptions.py`)

**Responsibilities:**
- Define custom exception types
- Provide structured error information
- Integrate with provide-foundation error handling

**Exception Hierarchy:**
```
provide.foundation.FoundationError
    ↓
HclError (base class)
    ↓
HclParsingError
    ├─ message: str
    ├─ source_file: str | None
    ├─ line: int | None
    └─ column: int | None
```

---

## Data Flow Examples

### Example 1: Parse HCL with Schema

```
User Code:
  hcl_string = 'name = "test"'
  schema = CtyObject({"name": CtyString()})
  result = parse_hcl_to_cty(hcl_string, schema)

Flow:
  1. parse_hcl_to_cty() receives string and schema
  2. python-hcl2.loads() parses HCL → {"name": "test"}
  3. schema.validate({"name": "test"}) validates
  4. Returns CtyValue with type=CtyObject, value={"name": CtyString("test")}
```

### Example 2: Create Terraform Variable

```
User Code:
  var = create_variable_cty(
      name="region",
      type_str="string",
      default_py="us-west-2"
  )

Flow:
  1. create_variable_cty() receives params
  2. _parse_hcl_type_string("string") → CtyString()
  3. CtyString().validate("us-west-2") → validates
  4. Build structure: {"variable": [{"region": {...}}]}
  5. Create schema for validation
  6. Return validated CtyValue
```

### Example 3: Automatic Type Inference

```
User Code:
  hcl = '''
    name = "example"
    count = 5
    enabled = true
  '''
  result = parse_hcl_to_cty(hcl)

Flow:
  1. parse_hcl_to_cty() with no schema
  2. python-hcl2.loads() → {"name": "example", "count": 5, "enabled": true}
  3. auto_infer_cty_type() walks the data:
     - "example" → CtyString
     - 5 → CtyNumber
     - true → CtyBool
  4. Build CtyObject with inferred types
  5. Return CtyValue
```

---

## Type System Integration

### CTY Type Mapping

```
HCL Type String    →    CTY Type
─────────────────────────────────────
"string"           →    CtyString()
"number"           →    CtyNumber()
"bool"             →    CtyBool()
"any"              →    CtyDynamic()
"list(string)"     →    CtyList(element_type=CtyString())
"map(number)"      →    CtyMap(element_type=CtyNumber())
"object({...})"    →    CtyObject(attributes={...})
```

### Python to CTY Inference

```
Python Value       →    CTY Type
─────────────────────────────────────
str                →    CtyString()
int/float/Decimal  →    CtyNumber()
bool               →    CtyBool()
None               →    CtyDynamic()
list               →    CtyList(CtyDynamic())
dict               →    CtyObject({...})
```

---

## Error Handling Flow

```
Error Occurs
    ↓
Which layer?
    ├─ HCL Parsing → python-hcl2 exception
    │                    ↓
    │               Caught by parse_hcl_to_cty()
    │                    ↓
    │               Wrapped in HclParsingError
    │
    ├─ Schema Validation → CtyValidationError
    │                          ↓
    │                     Caught by parse_hcl_to_cty()
    │                          ↓
    │                     Wrapped in HclParsingError
    │
    └─ Factory → HclFactoryError
                     ↓
                Raised directly
                     ↓
User catches exception with:
    - Descriptive message
    - Source location (if available)
    - Original error context
```

---

## Performance Characteristics

**Current Implementation:**
- **Parsing:** O(n) where n = HCL content size (via python-hcl2)
- **Type Inference:** O(m) where m = number of fields in data structure
- **Schema Validation:** O(m) for field validation
- **No caching:** Each parse is independent
- **No lazy evaluation:** All parsing happens immediately

**Memory Usage:**
- HCL string kept in memory
- Full parse tree created in memory
- CTY objects created for all values
- Typical: ~2-5x HCL string size

---

## Extension Points

### To Add New Features:

1. **New Parser Functions:**
   - Add to appropriate module in `parser/` subpackage
   - Export in `__init__.py`
   - Add tests in `tests/parser/test_parser.py`

2. **New Factory Types:**
   - Add factory function to appropriate module in `factories/` subpackage
   - Export in `__init__.py`
   - Add tests in `tests/factories/test_factories.py`

3. **New Type Support:**
   - Extend `parse_hcl_type_string()` in `factories/types.py`
   - Update `PRIMITIVE_TYPE_MAP` or `COMPLEX_TYPE_REGEX`
   - Add corresponding CTY types from pyvider-cty

4. **Terraform Features:**
   - Implement in appropriate module in `terraform/` subpackage
   - May need new parsing logic
   - Will integrate with existing parser/factory modules

---

## Dependencies

**Runtime Dependencies:**
- `python-hcl2>=7.2.1` - Core HCL parsing
- `pyvider-cty>=0.0.113` - Type system
- `provide-foundation>=0.0.0` - Error handling/logging
- `attrs>=25.3.0` - Structured exceptions
- `regex>=2024.11.6` - Enhanced regex

**Development Dependencies:**
- `pytest` - Testing framework
- `pytest-xdist` - Parallel test execution
- `ruff` - Linting and formatting
- `mypy` - Type checking
- `provide-testkit[standard,advanced-testing,typecheck,build]` - Test utilities

---

## Design Principles

1. **Simplicity:** Focused API with minimal abstractions
2. **Type Safety:** All values go through CTY type system
3. **Error Context:** Rich error messages with source locations
4. **Composability:** Small, focused modules that work together
5. **Extensibility:** Clear extension points for future features
6. **Testability:** All functions are pure and easily testable
