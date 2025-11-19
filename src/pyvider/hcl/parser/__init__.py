#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""HCL parsing module.

This module provides HCL parsing functionality with CTY type integration."""

from pyvider.hcl.parser.base import parse_hcl_to_cty
from pyvider.hcl.parser.context import parse_with_context
from pyvider.hcl.parser.inference import auto_infer_cty_type

__all__ = [
    "auto_infer_cty_type",
    "parse_hcl_to_cty",
    "parse_with_context",
]

# 📄⚙️🔚
