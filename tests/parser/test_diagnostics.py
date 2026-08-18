#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Tests for source location reporting on HCL parse failures."""

from pathlib import Path

import pytest

from pyvider.hcl import HclParsingError, parse_hcl_to_cty, parse_with_context
from pyvider.hcl.parser.diagnostics import SourceLocation, source_location

BROKEN_HCL = 'resource "t" "n" {\n  name =\n}\n'


class TestParseErrorLocation:
    """A syntax error carries the line and column the parser reported."""

    def test_parse_with_context_reports_line(self) -> None:
        with pytest.raises(HclParsingError) as exc_info:
            parse_with_context(BROKEN_HCL)
        assert exc_info.value.line == 2

    def test_parse_with_context_reports_column(self) -> None:
        with pytest.raises(HclParsingError) as exc_info:
            parse_with_context(BROKEN_HCL)
        assert exc_info.value.column is not None
        assert exc_info.value.column > 0

    def test_parse_hcl_to_cty_reports_line(self) -> None:
        with pytest.raises(HclParsingError) as exc_info:
            parse_hcl_to_cty(BROKEN_HCL)
        assert exc_info.value.line == 2

    def test_source_file_included_in_message(self) -> None:
        with pytest.raises(HclParsingError) as exc_info:
            parse_with_context(BROKEN_HCL, source_file=Path("main.tf"))
        rendered = str(exc_info.value)
        assert "main.tf" in rendered
        assert "line 2" in rendered

    def test_message_includes_source_snippet(self) -> None:
        with pytest.raises(HclParsingError) as exc_info:
            parse_with_context(BROKEN_HCL)
        assert "^" in str(exc_info.value)

    def test_valid_hcl_does_not_raise(self) -> None:
        assert parse_with_context('name = "x"') == {"name": "x"}

    def test_schema_failure_has_no_source_location(self) -> None:
        from pyvider.cty import CtyNumber, CtyObject

        schema = CtyObject({"name": CtyNumber()})
        with pytest.raises(HclParsingError) as exc_info:
            parse_hcl_to_cty('name = "x"', schema=schema)
        assert exc_info.value.line is None


class TestSourceLocation:
    """Direct tests for the extraction helper."""

    def test_plain_exception_has_no_location(self) -> None:
        assert source_location(ValueError("boom"), "x = 1") == SourceLocation()

    def test_reads_line_and_column_attributes(self) -> None:
        class Located(Exception):
            line = 3
            column = 7

        location = source_location(Located(), "a = 1\nb = 2\nc = 3\n")
        assert (location.line, location.column) == (3, 7)

    def test_rejects_non_positive_positions(self) -> None:
        class Located(Exception):
            line = 0
            column = -1

        assert source_location(Located(), "x = 1") == SourceLocation()

    def test_rejects_non_integer_positions(self) -> None:
        class Located(Exception):
            line = "nope"
            column = None

        assert source_location(Located(), "x = 1") == SourceLocation()

    def test_context_failure_is_tolerated(self) -> None:
        class Located(Exception):
            line = 1
            column = 1

            def get_context(self, text: str, span: int = 40) -> str:
                raise RuntimeError("cannot render")

        location = source_location(Located(), "x = 1")
        assert location.line == 1
        assert location.context is None

    def test_non_string_context_ignored(self) -> None:
        class Located(Exception):
            line = 1
            column = 1

            def get_context(self, text: str, span: int = 40) -> int:
                return 42

        assert source_location(Located(), "x = 1").context is None

    def test_context_is_stripped_of_trailing_newlines(self) -> None:
        class Located(Exception):
            line = 1
            column = 1

            def get_context(self, text: str, span: int = 40) -> str:
                return "x = 1\n    ^\n"

        assert source_location(Located(), "x = 1").context == "x = 1\n    ^"


# 📄⚙️🔚
