#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""HCL parsing with enhanced error context."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import hcl2
from provide.foundation import logger

from pyvider.hcl.exceptions import HclParsingError
from pyvider.hcl.parser.diagnostics import source_location
from pyvider.hcl.parser.normalize import normalize_hcl_data


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
        return normalize_hcl_data(hcl2.loads(content))
    except Exception as e:
        location = source_location(e, content)
        logger.error(
            "HCL parsing failed",
            source=source_str,
            line=location.line,
            column=location.column,
            error=str(e),
            exc_info=True,
        )
        message = str(e)
        if location.context:
            message = f"{message}\n{location.context}"
        raise HclParsingError(
            message=message,
            source_file=str(source_file) if source_file else None,
            line=location.line,
            column=location.column,
        ) from e


# 📄⚙️🔚
