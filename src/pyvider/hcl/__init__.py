#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""pyvider-hcl: HCL parsing with CTY type system integration.

This package provides HCL (HashiCorp Configuration Language) parsing capabilities
with seamless integration into the pyvider ecosystem through the CTY type system."""

from provide.foundation.utils.versioning import get_version

__version__ = get_version("pyvider-hcl", caller_file=__file__)
from pyvider.hcl.exceptions import HclError, HclParsingError
from pyvider.hcl.factories import (
    HclFactoryError,
    HclTypeParsingError,
    create_resource_cty,
    create_variable_cty,
)
from pyvider.hcl.output import pretty_print_cty
from pyvider.hcl.parser import auto_infer_cty_type, parse_hcl_to_cty, parse_with_context
from pyvider.hcl.terraform import parse_terraform_config

__all__ = [
    "HclError",
    "HclFactoryError",
    "HclParsingError",
    "HclTypeParsingError",
    "__version__",
    "auto_infer_cty_type",
    "create_resource_cty",
    "create_variable_cty",
    "parse_hcl_to_cty",
    "parse_terraform_config",
    "parse_with_context",
    "pretty_print_cty",
]

# 📄⚙️🔚
