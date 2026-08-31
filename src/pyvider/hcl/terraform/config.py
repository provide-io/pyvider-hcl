#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Terraform configuration parsing with block structure and source lines.

``hcl2.loads`` flattens a configuration into nested dicts, which loses both the
block/attribute distinction and every source position. This module reads
python-hcl2's typed rule tree through ``hcl2.query`` instead, so each top-level
block keeps its type, its labels, and the line range it occupies — the
information diagnostics need to point at a specific block.

Source lines come from ``BlockView.start_line`` and ``BlockView.end_line``, the
same numbers ``SerializationOptions(with_meta=True)`` would serialize, without
serializing the block to reach them.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import attrs
from hcl2.query import BlockView, DocumentView
from hcl2.utils import process_escape_sequences
from provide.foundation import logger

from pyvider.hcl.exceptions import HclParsingError
from pyvider.hcl.parser.diagnostics import source_location
from pyvider.hcl.parser.normalize import HCL2_OPTIONS, normalize_hcl_data

# Terraform's own top-level block types, for callers that want to distinguish
# them from provider- or tool-specific blocks.
TERRAFORM_BLOCK_TYPES = frozenset(
    {
        "data",
        "check",
        "import",
        "locals",
        "module",
        "moved",
        "output",
        "provider",
        "removed",
        "resource",
        "terraform",
        "variable",
    }
)


@attrs.define(frozen=True, slots=True)
class TerraformBlock:
    """One top-level block in a Terraform configuration."""

    block_type: str = attrs.field()
    labels: tuple[str, ...] = attrs.field(default=())
    body: dict[str, Any] = attrs.field(factory=dict)
    start_line: int | None = attrs.field(default=None)
    end_line: int | None = attrs.field(default=None)

    @property
    def address(self) -> str:
        """The block's dotted address, e.g. ``resource.aws_instance.web``."""
        return ".".join((self.block_type, *self.labels))


@attrs.define(frozen=True, slots=True)
class TerraformConfig:
    """A parsed Terraform configuration."""

    blocks: tuple[TerraformBlock, ...] = attrs.field(default=())
    attributes: dict[str, Any] = attrs.field(factory=dict)
    source_file: str | None = attrs.field(default=None)

    def blocks_of(self, block_type: str) -> tuple[TerraformBlock, ...]:
        """Return every block of ``block_type``, in source order."""
        return tuple(block for block in self.blocks if block.block_type == block_type)

    def block_at(self, block_type: str, *labels: str) -> TerraformBlock | None:
        """Return the first block matching ``block_type`` and ``labels``."""
        wanted = tuple(labels)
        for block in self.blocks:
            if block.block_type == block_type and block.labels == wanted:
                return block
        return None

    @property
    def block_types(self) -> tuple[str, ...]:
        """The distinct block types present, in first-appearance order."""
        seen: dict[str, None] = {}
        for block in self.blocks:
            seen.setdefault(block.block_type, None)
        return tuple(seen)


def _block_from_view(view: BlockView) -> TerraformBlock:
    """Build a :class:`TerraformBlock` from an ``hcl2.query`` block view.

    ``name_labels`` drops the block type and the quotes around each label but
    leaves escapes raw, so a quoted label still needs resolving. An unquoted
    label is an identifier and cannot carry an escape, so the same call is a
    no-op for it.
    """
    body = normalize_hcl_data(view.body.to_dict(options=HCL2_OPTIONS))
    return TerraformBlock(
        block_type=view.block_type,
        labels=tuple(process_escape_sequences(label) for label in view.name_labels),
        body=body if isinstance(body, dict) else {},
        start_line=view.start_line,
        end_line=view.end_line,
    )


def parse_terraform_blocks(content: str, source_file: Path | None = None) -> TerraformConfig:
    """Parse Terraform configuration text into blocks and attributes.

    Args:
        content: HCL text of a Terraform configuration.
        source_file: Optional path used in error reporting.

    Returns:
        The parsed configuration, with per-block source line ranges.

    Raises:
        HclParsingError: If the configuration cannot be parsed.

    Example:
        >>> config = parse_terraform_blocks('variable "a" {\\n  type = string\\n}\\n')
        >>> config.blocks[0].address
        'variable.a'
    """
    try:
        document = DocumentView.parse(content)
    except Exception as e:
        location = source_location(e, content)
        logger.error(
            "Terraform config parsing failed",
            source=str(source_file) if source_file else "string input",
            line=location.line,
            column=location.column,
            error=str(e),
        )
        message = str(e) if not location.context else f"{e}\n{location.context}"
        raise HclParsingError(
            message=message,
            source_file=str(source_file) if source_file else None,
            line=location.line,
            column=location.column,
        ) from e

    attributes: dict[str, Any] = {}
    for attribute in document.attributes():
        serialized = normalize_hcl_data(attribute.to_dict(options=HCL2_OPTIONS))
        if isinstance(serialized, dict):
            attributes.update(serialized)

    return TerraformConfig(
        blocks=tuple(_block_from_view(view) for view in document.blocks()),
        attributes=attributes,
        source_file=str(source_file) if source_file else None,
    )


def parse_terraform_config(config_path: Path) -> TerraformConfig:
    """Parse a Terraform configuration file.

    Args:
        config_path: Path to a ``.tf`` file.

    Returns:
        The parsed configuration, with per-block source line ranges.

    Raises:
        HclParsingError: If the file cannot be read or parsed.

    Example:
        >>> from pathlib import Path
        >>> config = parse_terraform_config(Path("main.tf"))  # doctest: +SKIP
        >>> [block.address for block in config.blocks]  # doctest: +SKIP
        ['variable.region', 'resource.aws_instance.web']
    """
    logger.debug("Parsing Terraform config", config_path=str(config_path))

    try:
        content = config_path.read_text(encoding="utf-8")
    except OSError as e:
        logger.error("Terraform config unreadable", config_path=str(config_path), error=str(e))
        raise HclParsingError(
            message=f"Could not read Terraform config: {e}",
            source_file=str(config_path),
        ) from e

    config = parse_terraform_blocks(content, source_file=config_path)
    logger.debug(
        "Parsed Terraform config",
        config_path=str(config_path),
        blocks=len(config.blocks),
        block_types=list(config.block_types),
    )
    return config


# 📄⚙️🔚
