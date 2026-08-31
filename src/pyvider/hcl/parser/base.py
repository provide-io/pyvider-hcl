#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Core HCL parsing functionality with CTY integration."""

from __future__ import annotations

from typing import Any

import hcl2

from pyvider.cty import CtyType, CtyValue
from pyvider.cty.exceptions import CtyError as CtySchemaError, CtyValidationError
from pyvider.hcl.exceptions import HclParsingError
from pyvider.hcl.parser.diagnostics import source_location
from pyvider.hcl.parser.inference import auto_infer_cty_type
from pyvider.hcl.parser.normalize import HCL2_OPTIONS, normalize_hcl_data
from pyvider.hcl.parser.required import null_required_attributes


def load_hcl_data(hcl_content: str) -> Any:
    """Parse HCL text into normalized Python data.

    Args:
        hcl_content: HCL string to parse.

    Returns:
        Parsed data with python-hcl2 serialization artifacts removed.

    Raises:
        HclParsingError: If the HCL cannot be parsed, carrying the source line
            and column when the parser reported them.
    """
    try:
        return normalize_hcl_data(hcl2.loads(hcl_content, serialization_options=HCL2_OPTIONS))
    except Exception as e:
        location = source_location(e, hcl_content)
        message = f"Failed to parse HCL: {e}"
        if location.context:
            message = f"{message}\n{location.context}"
        raise HclParsingError(
            message=message,
            line=location.line,
            column=location.column,
        ) from e


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
    raw_data = load_hcl_data(hcl_content)

    if schema is None:
        return auto_infer_cty_type(raw_data)

    try:
        validated_value = schema.validate(raw_data)
    except (CtySchemaError, CtyValidationError) as e:
        raise HclParsingError(message=f"Schema validation failed after HCL parsing: {e}") from e

    missing = null_required_attributes(validated_value)
    if missing:
        raise HclParsingError(
            message=(
                "Schema validation failed after HCL parsing: null value for "
                f"required attribute(s): {', '.join(missing)}"
            )
        )
    return validated_value


# 📄⚙️🔚
