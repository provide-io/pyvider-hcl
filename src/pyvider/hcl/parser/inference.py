#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Automatic CTY type inference from Python data structures.

This module provides HCL-specific wrappers around pyvider-cty's canonical
type inference implementation, which correctly handles lists, objects, and
all CTY types with sophisticated element type analysis and caching.
"""

from __future__ import annotations

from typing import Any

from pyvider.cty import CtyValue
from pyvider.cty.conversion import infer_cty_type_from_raw


def auto_infer_cty_type(raw_data: Any) -> CtyValue[Any]:
    """Automatically infer CTY type from raw Python data.

    This function takes Python data structures (typically from HCL parsing)
    and automatically infers appropriate CTY types using pyvider-cty's
    canonical inference implementation.

    Args:
        raw_data: Python data structure to infer types for

    Returns:
        CTY value with inferred types

    Example:
        >>> data = {"name": "test", "count": 5}
        >>> result = auto_infer_cty_type(data)
        >>> isinstance(result.type, CtyObject)
        True

    Note:
        This delegates to pyvider.cty.conversion.infer_cty_type_from_raw()
        which provides sophisticated type inference including:
        - List element type analysis (e.g., [1,2,3] → list(number))
        - Object attribute inference
        - Type unification for mixed collections
        - Caching and cycle detection
    """
    # Use pyvider-cty's canonical inference implementation
    inferred_type = infer_cty_type_from_raw(raw_data)
    return inferred_type.validate(raw_data)


# 📄⚙️🔚
