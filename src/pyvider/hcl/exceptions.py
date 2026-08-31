#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Every exception this package raises.

All of them derive from :class:`HclError`, so ``except HclError`` catches
anything the package raises. The two factory errors additionally derive from
``ValueError``, which is what they derived from alone before -- keeping it means
code written against that still works.
"""

from __future__ import annotations

from attrs import define, field
from provide.foundation.errors import FoundationError


class HclError(FoundationError):
    """Base class for errors related to HCL processing in Pyvider."""


@define(frozen=True, slots=True, auto_exc=True)
class HclParsingError(HclError):
    """
    Raised when HCL parsing or schema validation fails.

    This is an attrs-based exception class for structured error reporting.
    """

    message: str = field()
    source_file: str | None = field(default=None)
    line: int | None = field(default=None)
    column: int | None = field(default=None)

    def __str__(self) -> str:
        """Provides a detailed error message including source location if available."""
        if self.source_file and self.line is not None and self.column is not None:
            return f"{self.message} (at {self.source_file}, line {self.line}, column {self.column})"
        elif self.source_file and self.line is not None:
            return f"{self.message} (at {self.source_file}, line {self.line})"
        elif self.source_file:
            return f"{self.message} (at {self.source_file})"
        return self.message


class HclEmitError(HclError):
    """Raised when a CTY value cannot be represented as HCL."""


# `ValueError` is kept in the bases of both factory errors: they derived from it
# alone until they were brought under `HclError`, and dropping it would break a
# caller catching `ValueError` around a factory call.


class HclFactoryError(HclError, ValueError):
    """Raised when a factory function is given input it cannot build from."""


class HclTypeParsingError(HclError, ValueError):
    """Raised when an HCL type string is malformed."""


# 📄⚙️🔚
