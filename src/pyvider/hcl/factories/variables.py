#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Terraform variable factory functions."""

from __future__ import annotations

from typing import Any

from provide.foundation import logger

from pyvider.cty import CtyBool, CtyList, CtyObject, CtyString, CtyType, CtyValue
from pyvider.cty.exceptions import CtyError, CtyValidationError
from pyvider.hcl.factories.types import HclTypeParsingError, parse_hcl_type_string


class HclFactoryError(ValueError):
    """Custom exception for errors during HCL factory operations."""


def create_variable_cty(  # noqa: C901
    name: str,
    type_str: str,
    default_py: Any | None = None,
    description: str | None = None,
    sensitive: bool | None = None,
    nullable: bool | None = None,
) -> CtyValue[Any]:
    """Create a Terraform variable CTY structure.

    Args:
        name: Variable name (must be valid identifier)
        type_str: HCL type string (e.g., "string", "list(number)")
        default_py: Optional default value
        description: Optional description
        sensitive: Optional sensitive flag
        nullable: Optional nullable flag

    Returns:
        CTY value representing Terraform variable structure

    Raises:
        HclFactoryError: If validation fails

    Example:
        >>> var = create_variable_cty(
        ...     name="region",
        ...     type_str="string",
        ...     default_py="us-west-2"
        ... )
    """
    logger.debug("🏭⏳ Creating variable", name=name, type_str=type_str)

    if not name or not name.isidentifier():
        logger.error("🏭❌ Invalid variable name", name=name)
        raise HclFactoryError(f"Invalid variable name: '{name}'. Must be a valid identifier.")

    try:
        parsed_variable_type = parse_hcl_type_string(type_str)
    except HclTypeParsingError as e:
        logger.error("🏭❌ Type string parsing failed", name=name, type_str=type_str, error=str(e))
        raise HclFactoryError(f"Invalid type string for variable '{name}': {e}") from e

    variable_attrs_py: dict[str, Any] = {"type": type_str}

    if description is not None:
        variable_attrs_py["description"] = description
    if sensitive is not None:
        variable_attrs_py["sensitive"] = sensitive
    if nullable is not None:
        variable_attrs_py["nullable"] = nullable

    if default_py is not None:
        try:
            parsed_variable_type.validate(default_py)
        except CtyValidationError as e:
            logger.error(
                "🏭❌ Default value validation failed",
                name=name,
                type_str=type_str,
                error=str(e),
            )
            raise HclFactoryError(
                f"Default value for variable '{name}' is not compatible with type '{type_str}': {e}"
            ) from e
        variable_attrs_py["default"] = default_py

    variable_attrs_schema: dict[str, CtyType[Any]] = {"type": CtyString()}
    if "description" in variable_attrs_py:
        variable_attrs_schema["description"] = CtyString()
    if "sensitive" in variable_attrs_py:
        variable_attrs_schema["sensitive"] = CtyBool()
    if "nullable" in variable_attrs_py:
        variable_attrs_schema["nullable"] = CtyBool()
    if "default" in variable_attrs_py:
        variable_attrs_schema["default"] = parsed_variable_type

    root_py_struct = {"variable": [{name: variable_attrs_py}]}
    root_schema = CtyObject(
        {"variable": CtyList(element_type=CtyObject({name: CtyObject(variable_attrs_schema)}))}
    )

    try:
        result = root_schema.validate(root_py_struct)
        return result  # type: ignore[no-any-return]
    except CtyError as e:
        logger.error("🏭❌ Variable creation failed", name=name, error=str(e))
        raise HclFactoryError(f"Internal error creating variable CtyValue: {e}") from e


# 📄⚙️🔚
