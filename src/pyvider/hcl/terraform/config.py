#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Terraform configuration parsing with block structure and source lines.

``hcl2.loads`` flattens a configuration into nested dicts, which loses both the
block/attribute distinction and every source position. This module parses to
python-hcl2's typed rule tree instead, so each top-level block keeps its type,
its labels, and the line range it occupies — the information diagnostics need
to point at a specific block.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import attrs
import hcl2
from hcl2.rules.base import AttributeRule, BlockRule

# IdentifierRule is defined in literal_rules; hcl2.rules.base only imports it,
# and mypy strict will not follow an implicit re-export.
from hcl2.rules.literal_rules import IdentifierRule
from hcl2.rules.strings import StringRule
from provide.foundation import logger

from pyvider.hcl.exceptions import HclParsingError
from pyvider.hcl.parser.diagnostics import source_location
from pyvider.hcl.parser.normalize import normalize_hcl_data, normalize_hcl_string

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


def _rule_text(node: Any) -> str:
    """Render a label or identifier rule as plain text."""
    serialized = node.serialize()
    return normalize_hcl_string(serialized) if isinstance(serialized, str) else str(serialized)


def _block_from_rule(rule: Any) -> TerraformBlock:
    """Build a :class:`TerraformBlock` from a python-hcl2 ``BlockRule``."""
    block_type = ""
    labels: list[str] = []

    for child in rule.children:
        if isinstance(child, IdentifierRule) and not block_type:
            block_type = _rule_text(child)
        elif isinstance(child, StringRule | IdentifierRule):
            labels.append(_rule_text(child))

    meta = getattr(rule, "_meta", None)
    body = normalize_hcl_data(_block_body(rule))
    return TerraformBlock(
        block_type=block_type,
        labels=tuple(labels),
        body=body if isinstance(body, dict) else {},
        start_line=getattr(meta, "line", None),
        end_line=getattr(meta, "end_line", None),
    )


def _block_body(rule: Any) -> Any:
    """Serialize a block's body, stripping the label nesting hcl2 adds."""
    serialized = rule.serialize()
    # hcl2 nests one dict level per label; unwrap them to reach the body.
    for _ in range(_label_count(rule)):
        if isinstance(serialized, dict) and len(serialized) == 1:
            serialized = next(iter(serialized.values()))
    return serialized


def _label_count(rule: Any) -> int:
    """Count a block's labels."""
    identifiers = 0
    labels = 0
    for child in rule.children:
        if isinstance(child, IdentifierRule):
            if identifiers:
                labels += 1
            identifiers += 1
        elif isinstance(child, StringRule):
            labels += 1
    return labels


def _top_level_children(tree: Any) -> list[Any]:
    """Return the children of the configuration's root body."""
    body = getattr(tree, "body", None)
    if body is None:
        return []
    return list(getattr(body, "children", []) or [])


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
        tree = hcl2.parses(content)
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

    blocks: list[TerraformBlock] = []
    attributes: dict[str, Any] = {}
    for child in _top_level_children(tree):
        if isinstance(child, BlockRule):
            blocks.append(_block_from_rule(child))
        elif isinstance(child, AttributeRule):
            serialized = normalize_hcl_data(child.serialize())
            if isinstance(serialized, dict):
                attributes.update(serialized)

    return TerraformConfig(
        blocks=tuple(blocks),
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
