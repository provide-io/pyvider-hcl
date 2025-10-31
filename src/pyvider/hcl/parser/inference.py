#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Automatic CTY type inference from Python data structures."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from provide.foundation import logger

from pyvider.cty import CtyBool, CtyDynamic, CtyList, CtyNumber, CtyObject, CtyString, CtyValue


def _auto_infer_value_to_cty(raw_value: Any) -> CtyValue[Any]:
    """Recursively infers a Python value to its corresponding CtyValue.

    Args:
        raw_value: Python value to infer CTY type for

    Returns:
        CTY value with inferred type

    Note:
        Unknown types are returned as CtyDynamic with a warning logged.
    """
    if raw_value is None:
        return CtyDynamic().validate(None)  # type: ignore[no-any-return]
    if isinstance(raw_value, str):
        return CtyString().validate(raw_value)
    if isinstance(raw_value, bool):
        return CtyBool().validate(raw_value)
    if isinstance(raw_value, int | float | Decimal):
        return CtyNumber().validate(raw_value)
    if isinstance(raw_value, list):
        return CtyList(element_type=CtyDynamic()).validate(raw_value)  # type: ignore[no-any-return]
    if isinstance(raw_value, dict):
        inferred_attrs = {k: _auto_infer_value_to_cty(v) for k, v in raw_value.items()}
        inferred_attr_types = {k: v.type for k, v in inferred_attrs.items()}
        obj_type = CtyObject(inferred_attr_types)
        return CtyValue(vtype=obj_type, value=inferred_attrs)

    logger.warning(
        value_type=str(type(raw_value)),
        value_repr=repr(raw_value)[:100],
    )
    return CtyValue.unknown(CtyDynamic())


def auto_infer_cty_type(raw_data: Any) -> CtyValue[Any]:
    """Automatically infer CTY type from raw Python data.

    This function takes Python data structures (typically from HCL parsing)
    and automatically infers appropriate CTY types.

    Args:
        raw_data: Python data structure to infer types for

    Returns:
        CTY value with inferred types

    Example:
        >>> data = {"name": "test", "count": 5}
        >>> result = auto_infer_cty_type(data)
        >>> isinstance(result.type, CtyObject)
        True
    """
    return _auto_infer_value_to_cty(raw_data)

# 📄⚙️🔚
