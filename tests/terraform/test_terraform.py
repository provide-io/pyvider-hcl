#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""TODO: Add module docstring."""

from pathlib import Path
import unittest

from pyvider.hcl.terraform import parse_terraform_config


class TestTerraformConfig(unittest.TestCase):
    """Tests for the terraform module."""

    def test_parse_terraform_config_returns_placeholder(self) -> None:
        """Test that parse_terraform_config returns a placeholder response."""
        test_path = Path("/fake/path/main.tf")
        result = parse_terraform_config(test_path)

        # Currently the function returns a placeholder dict
        self.assertIsInstance(result, dict)
        self.assertEqual(result["status"], "not_implemented")
        self.assertEqual(result["path"], str(test_path))

    def test_parse_terraform_config_with_real_path(self) -> None:
        """Test with a real path that exists (even though parsing is not implemented)."""
        # Use a path that actually exists
        test_path = Path(__file__)
        result = parse_terraform_config(test_path)

        self.assertIsInstance(result, dict)
        self.assertEqual(result["status"], "not_implemented")
        self.assertEqual(result["path"], str(test_path))


# 📄⚙️🔚
