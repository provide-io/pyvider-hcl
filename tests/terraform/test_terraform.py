#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Tests for Terraform configuration parsing."""

from pathlib import Path

import pytest

from pyvider.hcl import HclParsingError
from pyvider.hcl.terraform import (
    TERRAFORM_BLOCK_TYPES,
    TerraformConfig,
    parse_terraform_blocks,
    parse_terraform_config,
)

SAMPLE = """terraform {
  required_version = ">= 1.5"
}

variable "region" {
  type        = string
  default     = "us-west-2"
  description = "AWS region"
}

resource "aws_instance" "web" {
  ami           = "ami-123"
  instance_type = "t2.micro"

  tags = {
    Name = "web"
  }
}

output "instance_id" {
  value = aws_instance.web.id
}

locals {
  prefix = "app"
}
"""


class TestBlockExtraction:
    """Top-level blocks keep their type, labels, and body."""

    def test_all_blocks_found(self) -> None:
        config = parse_terraform_blocks(SAMPLE)
        assert config.block_types == ("terraform", "variable", "resource", "output", "locals")

    def test_block_addresses(self) -> None:
        config = parse_terraform_blocks(SAMPLE)
        addresses = [block.address for block in config.blocks]
        assert "resource.aws_instance.web" in addresses
        assert "variable.region" in addresses
        assert "locals" in addresses

    def test_labels_are_unquoted(self) -> None:
        config = parse_terraform_blocks(SAMPLE)
        block = config.block_at("resource", "aws_instance", "web")
        assert block is not None
        assert block.labels == ("aws_instance", "web")

    def test_body_is_normalized(self) -> None:
        config = parse_terraform_blocks(SAMPLE)
        block = config.block_at("resource", "aws_instance", "web")
        assert block is not None
        assert block.body == {
            "ami": "ami-123",
            "instance_type": "t2.micro",
            "tags": {"Name": "web"},
        }

    def test_unlabelled_block_body(self) -> None:
        config = parse_terraform_blocks(SAMPLE)
        block = config.block_at("locals")
        assert block is not None
        assert block.body == {"prefix": "app"}

    def test_expressions_preserved_in_body(self) -> None:
        config = parse_terraform_blocks(SAMPLE)
        block = config.block_at("output", "instance_id")
        assert block is not None
        assert block.body == {"value": "${aws_instance.web.id}"}

    def test_blocks_of_type(self) -> None:
        config = parse_terraform_blocks(SAMPLE)
        assert len(config.blocks_of("variable")) == 1
        assert config.blocks_of("data") == ()

    def test_missing_block_returns_none(self) -> None:
        config = parse_terraform_blocks(SAMPLE)
        assert config.block_at("resource", "aws_s3_bucket", "logs") is None

    def test_repeated_block_types_are_all_kept(self) -> None:
        content = 'resource "t" "a" {\n  x = 1\n}\nresource "t" "b" {\n  x = 2\n}\n'
        config = parse_terraform_blocks(content)
        assert [block.labels for block in config.blocks_of("resource")] == [("t", "a"), ("t", "b")]

    def test_known_block_types_constant(self) -> None:
        assert {"resource", "variable", "output", "locals"} <= TERRAFORM_BLOCK_TYPES


class TestSourceLines:
    """Every block records the source line range it occupies."""

    def test_first_block_starts_on_line_one(self) -> None:
        config = parse_terraform_blocks(SAMPLE)
        assert config.blocks[0].start_line == 1

    def test_line_ranges_are_ordered_and_bounded(self) -> None:
        config = parse_terraform_blocks(SAMPLE)
        for block in config.blocks:
            assert block.start_line is not None
            assert block.end_line is not None
            assert block.start_line <= block.end_line

    def test_resource_block_line_range(self) -> None:
        config = parse_terraform_blocks(SAMPLE)
        block = config.block_at("resource", "aws_instance", "web")
        assert block is not None
        assert block.start_line == 11
        assert block.end_line == 18


class TestTopLevelAttributes:
    """Attributes outside any block are collected separately."""

    def test_attributes_collected(self) -> None:
        config = parse_terraform_blocks('name = "x"\nport = 8080\n')
        assert config.attributes == {"name": "x", "port": 8080}
        assert config.blocks == ()

    def test_attributes_and_blocks_together(self) -> None:
        config = parse_terraform_blocks('name = "x"\nlocals {\n  a = 1\n}\n')
        assert config.attributes == {"name": "x"}
        assert len(config.blocks) == 1


class TestFileParsing:
    """The file entry point reads and reports on real paths."""

    def test_parses_a_file(self, tmp_path: Path) -> None:
        config_path = tmp_path / "main.tf"
        config_path.write_text(SAMPLE, encoding="utf-8")
        config = parse_terraform_config(config_path)
        assert isinstance(config, TerraformConfig)
        assert config.source_file == str(config_path)
        assert len(config.blocks) == 5

    def test_missing_file_raises(self, tmp_path: Path) -> None:
        with pytest.raises(HclParsingError, match="Could not read"):
            parse_terraform_config(tmp_path / "absent.tf")

    def test_invalid_syntax_reports_location(self, tmp_path: Path) -> None:
        config_path = tmp_path / "bad.tf"
        config_path.write_text('resource "t" "n" {\n  x =\n}\n', encoding="utf-8")
        with pytest.raises(HclParsingError) as exc_info:
            parse_terraform_config(config_path)
        error = exc_info.value
        assert error.source_file == str(config_path)
        assert error.line is not None

    def test_empty_file(self, tmp_path: Path) -> None:
        config_path = tmp_path / "empty.tf"
        config_path.write_text("", encoding="utf-8")
        config = parse_terraform_config(config_path)
        assert config.blocks == ()
        assert config.attributes == {}


# 📄⚙️🔚
