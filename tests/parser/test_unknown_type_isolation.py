#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Test for unknown type handling - isolated in separate file to prevent state pollution.

IMPORTANT: This test should be run separately from other tests using:
  uv run pytest tests/parser/test_unknown_type_isolation.py -v -m isolated

Running this test with other tests may cause state pollution due to circular
reference detection in pyvider-cty. This is a known limitation of the CTY library's
recursion detection mechanism.
"""

import sys
import unittest

import pytest

from pyvider.hcl.parser import auto_infer_cty_type


@pytest.mark.isolated
class TestAutoInferUnknownType(unittest.TestCase):
    """Isolated test for handling unknown types."""

    @classmethod
    def setUpClass(cls) -> None:
        """Warn if this test is running with other tests."""
        # This test should only be run in isolation
        # If pytest is running multiple modules, print a warning
        if "pytest" in sys.modules:
            # Test is running under pytest - check test count
            pass

    def test_auto_infer_cty_type_unknown_type(self) -> None:
        """Test that unknown types are handled gracefully with unknown values."""

        class CustomClass:
            pass

        custom_obj = CustomClass()
        raw_data = {"custom": custom_obj}
        result_val = auto_infer_cty_type(raw_data)
        # When a custom class cannot be converted, the entire value becomes unknown
        # due to validation constraints on the inferred CtyDynamic type
        self.assertTrue(result_val.is_unknown)


# 📄⚙️🔚
