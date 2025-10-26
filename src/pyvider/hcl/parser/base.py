#!/usr/bin/env python3
"""Core HCL parsing functionality with CTY integration."""

from __future__ import annotations

from typing import Any

import hcl2
from provide.foundation import logger

from pyvider.cty import CtyType, CtyValue
from pyvider.cty.exceptions import CtyError as CtySchemaError, CtyValidationError
from pyvider.hcl.exceptions import HclParsingError
from pyvider.hcl.parser.inference import auto_infer_cty_type


def parse_hcl_to_cty(hcl_content: str, schema: CtyType[Any] | None = None) -> CtyValue[Any]:
    """Parse HCL directly into validated CtyValues using pyvider.cty types.

    Args:
        hcl_content: HCL string to parse
        schema: Optional CTY type schema for validation

    Returns:
        Parsed and validated CTY value

    Raises:
        HclParsingError: If parsing or validation fails

    Example:
        >>> hcl = 'name = "example"'
        >>> result = parse_hcl_to_cty(hcl)
        >>> result.value["name"].value
        'example'
    """
    logger.debug("📄⏳ Parsing HCL content", schema_provided=bool(schema))

    try:
        raw_data = hcl2.loads(hcl_content)  # type: ignore[attr-defined]
    except Exception as e:
        logger.error("📄❌ HCL parsing failed", error=str(e), exc_info=True)
        raise HclParsingError(message=f"Failed to parse HCL: {e}") from e

    if schema:
        logger.debug("📄⏳ Validating against schema", schema=str(schema))
        try:
            validated_value = schema.validate(raw_data)
            logger.debug("📄✅ Schema validation successful")
            return validated_value
        except (CtySchemaError, CtyValidationError) as e:
            logger.error("📄❌ Schema validation failed", error=str(e), exc_info=True)
            raise HclParsingError(message=f"Schema validation failed after HCL parsing: {e}") from e
    else:
        logger.debug("📄⏳ Auto-inferring CTY types")
        inferred_value = auto_infer_cty_type(raw_data)
        logger.debug("📄✅ Type inference complete")
        return inferred_value
