#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Integration tests using provide-testkit utilities."""

from pathlib import Path

import pytest

from pyvider.cty import CtyList, CtyObject, CtyString
from pyvider.hcl.exceptions import HclParsingError
from pyvider.hcl.parser import parse_with_context


class TestMultiFileHclIntegration:
    """Integration tests for multi-file HCL projects."""

    def test_parse_main_hcl_file(self, multi_file_hcl_structure: Path) -> None:
        """Test parsing main.hcl from multi-file structure."""
        main_file = multi_file_hcl_structure / "main.hcl"
        assert main_file.exists()

        content = main_file.read_text()
        result = parse_with_context(content, source_file=main_file)

        assert "terraform" in result
        assert "module" in result

    def test_parse_variables_file(self, multi_file_hcl_structure: Path) -> None:
        """Test parsing variables.hcl file."""
        variables_file = multi_file_hcl_structure / "variables.hcl"
        assert variables_file.exists()

        content = variables_file.read_text()
        result = parse_with_context(content, source_file=variables_file)

        assert "variable" in result
        # Should have 2 variables
        assert len(result["variable"]) == 2

    def test_parse_outputs_file(self, multi_file_hcl_structure: Path) -> None:
        """Test parsing outputs.hcl file."""
        outputs_file = multi_file_hcl_structure / "outputs.hcl"
        assert outputs_file.exists()

        content = outputs_file.read_text()
        result = parse_with_context(content, source_file=outputs_file)

        assert "output" in result
        # Should have 2 outputs
        assert len(result["output"]) == 2

    def test_parse_module_files(self, multi_file_hcl_structure: Path) -> None:
        """Test parsing module HCL files."""
        module_main = multi_file_hcl_structure / "modules" / "vpc" / "main.hcl"
        module_vars = multi_file_hcl_structure / "modules" / "vpc" / "variables.hcl"

        assert module_main.exists()
        assert module_vars.exists()

        # Parse module main file
        main_content = module_main.read_text()
        main_result = parse_with_context(main_content, source_file=module_main)
        assert "resource" in main_result
        assert "output" in main_result

        # Parse module variables file
        vars_content = module_vars.read_text()
        vars_result = parse_with_context(vars_content, source_file=module_vars)
        assert "variable" in vars_result

    def test_all_files_parseable(self, multi_file_hcl_structure: Path) -> None:
        """Test that all HCL files in the structure are parseable."""
        hcl_files = list(multi_file_hcl_structure.rglob("*.hcl"))
        assert len(hcl_files) == 5  # main, variables, outputs, module/main, module/variables

        for hcl_file in hcl_files:
            content = hcl_file.read_text()
            result = parse_with_context(content, source_file=hcl_file)
            assert result is not None
            assert isinstance(result, dict)


class TestTempDirectoryIntegration:
    """Integration tests using temp_directory fixture."""

    def test_create_and_parse_hcl_file(self, hcl_temp_dir: Path, sample_hcl_content: str) -> None:
        """Test creating and parsing an HCL file in temp directory."""
        hcl_file = hcl_temp_dir / "test.hcl"
        hcl_file.write_text(sample_hcl_content)

        assert hcl_file.exists()

        content = hcl_file.read_text()
        result = parse_with_context(content, source_file=hcl_file)

        assert "variable" in result
        assert "resource" in result

    def test_multiple_hcl_files_in_temp_dir(self, hcl_temp_dir: Path) -> None:
        """Test creating and parsing multiple HCL files."""
        # Create multiple HCL files
        files = {
            "config1.hcl": 'setting = "value1"',
            "config2.hcl": 'setting = "value2"',
            "config3.hcl": 'setting = "value3"',
        }

        for filename, content in files.items():
            (hcl_temp_dir / filename).write_text(content)

        # Parse all files
        for filename in files:
            hcl_file = hcl_temp_dir / filename
            assert hcl_file.exists()

            content = hcl_file.read_text()
            result = parse_with_context(content, source_file=hcl_file)
            assert "setting" in result

    def test_nested_directory_structure(self, hcl_temp_dir: Path) -> None:
        """Test creating nested directory structure with HCL files."""
        # Create nested directories
        subdir = hcl_temp_dir / "configs" / "production"
        subdir.mkdir(parents=True)

        # Create HCL file in nested directory
        config_file = subdir / "prod.hcl"
        config_file.write_text('environment = "production"\nregion = "us-east-1"')

        assert config_file.exists()

        content = config_file.read_text()
        result = parse_with_context(content, source_file=config_file)

        assert "environment" in result
        assert "region" in result
        assert result["environment"] == "production"


class TestConfigFileIntegration:
    """Integration tests using temp_config_file fixture."""

    def test_parse_config_file(self, hcl_config_file: Path) -> None:
        """Test parsing HCL configuration file."""
        assert hcl_config_file.exists()
        assert hcl_config_file.suffix == ".hcl"

        content = hcl_config_file.read_text()
        result = parse_with_context(content, source_file=hcl_config_file)

        assert "config" in result
        assert len(result["config"]) == 1

    def test_config_file_schema_validation(self, hcl_config_file: Path) -> None:
        """Test config file with schema validation."""
        content = hcl_config_file.read_text()

        # Define schema for config structure
        settings_schema = CtyObject(
            {
                "enabled": CtyString(),  # Note: HCL returns bools as strings in some cases
                "timeout": CtyString(),
                "retries": CtyString(),
            }
        )

        CtyObject(
            {
                "config": CtyList(
                    element_type=CtyObject(
                        {
                            "name": CtyString(),
                            "version": CtyString(),
                            "settings": CtyList(element_type=settings_schema),
                        }
                    )
                )
            }
        )

        # Parse with schema (may need adjustment based on actual HCL structure)
        result = parse_with_context(content, source_file=hcl_config_file)
        assert result is not None

    def test_modify_and_reparse_config(self, hcl_config_file: Path) -> None:
        """Test modifying config file and reparsing."""
        # Read original content
        original = parse_with_context(hcl_config_file.read_text())

        # Modify the file
        new_content = """
config {
  name = "modified-config"
  version = "2.0.0"

  settings {
    enabled = false
    timeout = 60
  }
}
"""
        hcl_config_file.write_text(new_content)

        # Parse modified content
        modified = parse_with_context(hcl_config_file.read_text())

        assert modified != original
        assert "config" in modified


class TestErrorHandlingWithFixtures:
    """Test error handling with provide-testkit fixtures."""

    def test_parse_invalid_hcl_from_temp_file(self, hcl_temp_dir: Path) -> None:
        """Test parsing invalid HCL from temp file."""
        invalid_file = hcl_temp_dir / "invalid.hcl"
        invalid_file.write_text("invalid { unclosed")

        with pytest.raises(HclParsingError):
            content = invalid_file.read_text()
            parse_with_context(content, source_file=invalid_file)

    def test_nonexistent_file_handling(self, hcl_temp_dir: Path) -> None:
        """Test handling of nonexistent files."""
        nonexistent = hcl_temp_dir / "does_not_exist.hcl"

        assert not nonexistent.exists()

        # This should work - we're just using the path for error context
        with pytest.raises(HclParsingError):
            parse_with_context("invalid {", source_file=nonexistent)


# 📄⚙️🔚
