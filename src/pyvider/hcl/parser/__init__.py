#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""HCL parsing module.

This module provides HCL parsing functionality with CTY type integration."""

from pyvider.hcl.parser.base import load_hcl_data, parse_hcl_to_cty
from pyvider.hcl.parser.context import parse_with_context
from pyvider.hcl.parser.inference import auto_infer_cty_type
from pyvider.hcl.parser.normalize import normalize_hcl_data
from pyvider.hcl.parser.required import null_required_attributes

__all__ = [
    "auto_infer_cty_type",
    "load_hcl_data",
    "normalize_hcl_data",
    "null_required_attributes",
    "parse_hcl_to_cty",
    "parse_with_context",
]

# 📄⚙️🔚
