#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Terraform resource factory functions."""

from __future__ import annotations

from typing import Any

from provide.foundation import logger

from pyvider.cty import CtyList, CtyObject, CtyType, CtyValue
from pyvider.cty.exceptions import CtyError, CtyValidationError
from pyvider.hcl.factories.types import HclTypeParsingError, parse_hcl_type_string
from pyvider.hcl.factories.variables import HclFactoryError
from pyvider.hcl.parser import auto_infer_cty_type


def create_resource_cty(  # noqa: C901
    r_type: str,
    r_name: str,
    attributes_py: dict[str, Any],
    attributes_schema_py: dict[str, str] | None = None,
) -> CtyValue[Any]:
    """Create a Terraform resource CTY structure.

    Args:
        r_type: Resource type (e.g., "aws_instance")
        r_name: Resource name
        attributes_py: Resource attributes as Python dict
        attributes_schema_py: Optional type strings for attributes

    Returns:
        CTY value representing Terraform resource structure

    Raises:
        HclFactoryError: If validation fails

    Example:
        >>> resource = create_resource_cty(
        ...     r_type="aws_instance",
        ...     r_name="web",
        ...     attributes_py={"ami": "ami-123", "instance_type": "t2.micro"},
        ...     attributes_schema_py={"ami": "string", "instance_type": "string"}
        ... )
    """
    logger.debug("🏭⏳ Creating resource", r_type=r_type, r_name=r_name)

    if not r_type or not r_type.strip():
        logger.error("🏭❌ Empty resource type")
        raise HclFactoryError("Resource type 'r_type' cannot be empty.")

    if not r_name or not r_name.strip():
        logger.error("🏭❌ Empty resource name")
        raise HclFactoryError("Resource name 'r_name' cannot be empty.")

    attributes_cty_schema: dict[str, CtyType[Any]] = {}

    if attributes_schema_py is not None:
        for attr_name, attr_type_str in attributes_schema_py.items():
            try:
                attributes_cty_schema[attr_name] = parse_hcl_type_string(attr_type_str)
            except HclTypeParsingError as e:
                logger.error(
                    "🏭❌ Attribute type parsing failed",
                    r_type=r_type,
                    r_name=r_name,
                    attr_name=attr_name,
                    type_str=attr_type_str,
                    error=str(e),
                )
                raise HclFactoryError(
                    f"Invalid type string for attribute '{attr_name}' ('{attr_type_str}') "
                    f"in resource '{r_type}.{r_name}': {e}"
                ) from e

        for attr_name in attributes_py:
            if attr_name not in attributes_cty_schema:
                logger.error(
                    "🏭❌ Missing type for attribute",
                    r_type=r_type,
                    r_name=r_name,
                    attr_name=attr_name,
                )
                raise HclFactoryError(
                    f"Missing type string in attributes_schema_py for attribute '{attr_name}' "
                    f"of resource '{r_type}.{r_name}'."
                )

        resource_attributes_obj_type = CtyObject(attributes_cty_schema)
        try:
            resource_attributes_obj_type.validate(attributes_py)
        except CtyValidationError as e:
            logger.error(
                "🏭❌ Attribute validation failed",
                r_type=r_type,
                r_name=r_name,
                error=str(e),
            )
            raise HclFactoryError(
                f"One or more attributes for resource '{r_type}.{r_name}' are not compatible "
                f"with the provided schema: {e}"
            ) from e
    else:
        logger.debug("🏭⏳ Inferring attribute types", r_type=r_type, r_name=r_name)
        inferred_attributes_cty = auto_infer_cty_type(attributes_py)
        if isinstance(inferred_attributes_cty.type, CtyObject):
            attributes_cty_schema = inferred_attributes_cty.type.attribute_types
        else:
            logger.error("🏭❌ Type inference failed", r_type=r_type, r_name=r_name)
            raise HclFactoryError("Could not infer object type from attributes.")

    root_py_struct = {"resource": [{r_type: [{r_name: attributes_py}]}]}
    root_schema = CtyObject(
        {
            "resource": CtyList(
                element_type=CtyObject(
                    {r_type: CtyList(element_type=CtyObject({r_name: CtyObject(attributes_cty_schema)}))}
                )
            )
        }
    )

    try:
        result = root_schema.validate(root_py_struct)
        return result  # type: ignore[no-any-return]
    except CtyError as e:
        logger.error("🏭❌ Resource creation failed", r_type=r_type, r_name=r_name, error=str(e))
        raise HclFactoryError(f"Internal error creating resource CtyValue: {e}") from e


# 📄⚙️🔚
