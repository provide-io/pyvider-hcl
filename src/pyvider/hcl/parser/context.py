#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""HCL parsing with enhanced error context."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import hcl2
from provide.foundation import logger

from pyvider.hcl.exceptions import HclParsingError


def parse_with_context(content: str, source_file: Path | None = None) -> Any:
    """Parse HCL content with enhanced error context.

    This function parses HCL content and provides rich error context if parsing fails.
    It returns the raw parsed data (dict/list), not CTY values.

    Args:
        content: HCL content string to parse
        source_file: Optional source file path for error reporting

    Returns:
        Raw parsed data (typically dict or list)

    Raises:
        HclParsingError: If parsing fails, with source location information

    Example:
        >>> content = 'name = "example"'
        >>> data = parse_with_context(content)
        >>> data['name']
        'example'
    """
    source_str = str(source_file) if source_file else "string input"

    try:
        return hcl2.loads(content)
    except Exception as e:
        logger.error(
            "HCL parsing failed",
            source=source_str,
            error=str(e),
            exc_info=True,
        )
        raise HclParsingError(
            message=str(e),
            source_file=str(source_file) if source_file else None,
        ) from e


# 📄⚙️🔚
