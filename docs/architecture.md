# pyvider-hcl Architecture

This document provides a visual and detailed overview of the pyvider-hcl architecture.

## System Overview

```
┌──────────────────────────────────────────────────────────────────────┐
│                          User Application                            │
└──────────────────────────────────┬───────────────────────────────────┘
                                   │
                                   ▼
┌──────────────────────────────────────────────────────────────────────┐
│                         pyvider.hcl Package                          │
│                                                                      │
│  ┌────────────────────┐  ┌───────────────────┐  ┌─────────────────┐  │
│  │  parser/           │  │  factories/       │  │  output/        │  │
│  │  ├─ base.py        │  │  ├─ types.py      │  │  ├─ formatting  │  │
│  │  ├─ context.py     │  │  ├─ variables.py  │  │  │    .py       │  │
│  │  ├─ normalize.py   │  │  └─ resources.py  │  │  └─ emitter.py  │  │
│  │  ├─ inference.py   │  │                   │  │                 │  │
│  │  ├─ diagnostics.py │  │ • create_         │  │ • pretty_print  │  │
│  │  └─ required.py    │  │    variable_cty   │  │    _cty()       │  │
│  │                    │  │ • create_         │  │ • format_cty()  │  │
│  │ • parse_hcl_to_cty │  │    resource_cty   │  │ • cty_to_hcl()  │  │
│  │ • parse_with_      │  │ • parse_hcl_      │  │ • cty_to_hcl_   │  │
│  │    context()       │  │    type_string()  │  │    data()       │  │
│  │ • load_hcl_data()  │  │                   │  │                 │  │
│  │ • normalize_hcl_   │  └───────────────────┘  └─────────────────┘  │
│  │    data()          │                                              │
│  │ • auto_infer_      │  ┌───────────────────┐  ┌─────────────────┐  │
│  │    cty_type()      │  │  terraform/       │  │  exceptions.py  │  │
│  │ • null_required_   │  │  └─ config.py     │  │                 │  │
│  │    attributes()    │  │                   │  │ • HclError      │  │
│  └────────────────────┘  │ • parse_terraform │  │ • HclParsing    │  │
│                          │    _config()      │  │    Error        │  │
│                          │ • parse_terraform │  │ • HclEmitError  │  │
│                          │    _blocks()      │  │ • HclFactory    │  │
│                          │ • TerraformConfig │  │    Error        │  │
│                          │ • TerraformBlock  │  │ • HclTypeParsing│  │
│                          └───────────────────┘  │    Error        │  │
│                                                 └─────────────────┘  │
└──────────────────────────────────┬───────────────────────────────────┘
                                   │
                   ┌───────────────┼───────────────┐
                   │               │               │
                   ▼               ▼               ▼
       ┌──────────────────┐ ┌──────────────┐ ┌──────────────────┐
       │  python-hcl2     │ │ pyvider-cty  │ │ provide-         │
       │  (HCL parser +   │ │ (type system)│ │ foundation       │
       │   emitter)       │ │              │ │ (errors/logging) │
       └──────────────────┘ └──────────────┘ └──────────────────┘
```

## Module Breakdown

### 1. Parser Subpackage (`parser/`)

**Modules:**
- **`base.py`**: Core parsing logic - contains `parse_hcl_to_cty()`
- **`context.py`**: Enhanced error context - contains `parse_with_context()`
- **`normalize.py`**: Reverses python-hcl2 8.x serialization artifacts - contains
  `normalize_hcl_data()`
- **`inference.py`**: Type inference - contains `auto_infer_cty_type()`
- **`diagnostics.py`**: Source location extraction - contains `source_location()`
- **`required.py`**: Required-attribute checking - contains
  `null_required_attributes()`

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
hcl2.loads()  ──→  dict, with source syntax preserved
    │              ('"web"', '"<<EOT\nbody\nEOT"', __is_block__ markers)
    ↓
normalize_hcl_data() [normalize.py]  ──→  plain Python dict/list
    │   unquotes literals, resolves escapes, unwraps heredocs,
    │   drops hcl2 metadata keys. Expressions stay as '${...}'.
    ↓
Schema provided?
    ├─ Yes → schema.validate(data)  ──→  CtyValue
    │            ↓
    │        null_required_attributes() [required.py] reports null
    │        non-optional attributes, which cty defers to the schema layer
    └─ No  → auto_infer_cty_type() [inference.py]  ──→  CtyValue

On a parse failure, source_location() [diagnostics.py] pulls line, column and a
caret snippet off the lark error and HclParsingError carries them.
```

**Key Functions:**
- `parse_hcl_to_cty(hcl_content, schema=None) → CtyValue` (base.py)
- `parse_with_context(content, source_file=None) → dict` (context.py)
- `load_hcl_data(hcl_content) → dict` (base.py)
- `normalize_hcl_data(data) → Any` (normalize.py)
- `auto_infer_cty_type(raw_data) → CtyValue` (inference.py)
- `null_required_attributes(value) → list[str]` (required.py)

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
- **`formatting.py`**: CTY value formatting - contains `pretty_print_cty()` and
  `format_cty()`
- **`emitter.py`**: CTY → HCL text - contains `cty_to_hcl()` and
  `cty_to_hcl_data()`

**Responsibilities:**
- Format CTY values for human-readable display
- Handle nested structures (objects, lists, maps, sets, tuples), rendering null,
  unknown and marked values explicitly
- Render an object- or map-typed CTY value back into HCL text

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
    ├─ CtySet     → Format as JSON array, deterministically ordered
    └─ Primitive  → Format as string/number/bool
```

**Emission Flow:**
```
CtyValue (object or map at the root)
    ↓
cty_to_hcl() [emitter.py]
    ↓
cty_to_hcl_data()  ──→  dict in python-hcl2's conventions
    │   a literal is quoted ('"web"'), a whole interpolation stays bare
    │   ('${var.x}'); unknown and marked values raise HclEmitError
    ↓
hcl2.dumps()  ──→  HCL text
```

Emission is attribute-only. A `CtyValue` carries no notion of HCL blocks, so
`resource "x" "y" { … }` cannot be reconstructed from one.

**Key Functions:**
- `pretty_print_cty(value) → None` (prints to stdout) (formatting.py)
- `format_cty(value) → str` (same rendering, returned) (formatting.py)
- `cty_to_hcl(value) → str` (emitter.py)
- `cty_to_hcl_data(value) → Any` (emitter.py)

---

### 4. Exceptions Module (`exceptions.py`)

**Responsibilities:**
- Define custom exception types
- Provide structured error information
- Integrate with provide-foundation error handling

**Exception Hierarchy:**
```
provide.foundation.FoundationError
    ↓
HclError (base class)
    ├─ HclParsingError        raised by the parser and the Terraform reader
    │     ├─ message: str
    │     ├─ source_file: str | None
    │     ├─ line: int | None
    │     └─ column: int | None
    └─ HclEmitError           raised when a CTY value has no HCL form
                              (output/emitter.py)

ValueError
    ├─ HclFactoryError        raised by the variable and resource factories
    └─ HclTypeParsingError    raised by parse_hcl_type_string()
```

Note that the two factory exceptions derive from `ValueError` rather than
`HclError`, so `except HclError` does not catch them.

---

### 5. Terraform Subpackage (`terraform/`)

**Modules:**
- **`config.py`**: Terraform configuration reading - contains
  `parse_terraform_config()`, `parse_terraform_blocks()`, `TerraformConfig`,
  `TerraformBlock` and `TERRAFORM_BLOCK_TYPES`

**Responsibilities:**
- Read a configuration into top-level blocks that keep their type, labels and
  source line range
- Collect attributes written outside any block separately from blocks

**Block Reading Flow:**
```
Terraform config text
    ↓
hcl2.query.DocumentView.parse()  ──→  typed rule tree
    │   `hcl2.loads` flattens a config into nested dicts, losing both the
    │   block/attribute distinction and every source position
    ↓
    ├─ .blocks()      → BlockView  ──→  TerraformBlock
    │      block_type, name_labels, body.to_dict(), and the line range
    │      from the rule's own _meta
    └─ .attributes()  → AttributeView  ──→  TerraformConfig.attributes
    ↓
normalize_hcl_data() on each body  ──→  plain Python values
```

Source lines come from each rule's `_meta` rather than from
`SerializationOptions(with_meta=True)`, which emits nothing as of python-hcl2
8.1.3 (amplify-education/python-hcl2#291).

**Key Functions:**
- `parse_terraform_config(config_path) → TerraformConfig` (config.py)
- `parse_terraform_blocks(content, source_file=None) → TerraformConfig` (config.py)

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
HCL Type String           →    CTY Type
──────────────────────────────────────────────────────────
"string"                  →    CtyString()
"number"                  →    CtyNumber()
"bool"                    →    CtyBool()
"any"                     →    CtyDynamic()
"list(string)"            →    CtyList(element_type=CtyString())
"set(string)"             →    CtySet(element_type=CtyString())
"map(number)"             →    CtyMap(element_type=CtyNumber())
"tuple([string, number])" →    CtyTuple(element_types=(...))
"object({...})"           →    CtyObject(attribute_types={...})
"object({a=optional(T)})" →    CtyObject(..., optional_attributes={"a"})
```

`optional(T, default)` parses, but the default is dropped: CTY object types
carry no per-attribute defaults.

### Python to CTY Inference

```
Python Value       →    CTY Type
──────────────────────────────────────────────────────
str                →    CtyString()
int/float/Decimal  →    CtyNumber()
bool               →    CtyBool()
None               →    CtyDynamic()
list               →    CtyList, element type inferred from the elements
                        (["a"] → list(string); [] → list(dynamic))
dict               →    CtyObject, one attribute per key
```

Inference delegates to pyvider-cty's `infer_cty_type_from_raw`.

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
5. **Extensibility:** Clear extension points for potential features
6. **Testability:** All functions are pure and easily testable
