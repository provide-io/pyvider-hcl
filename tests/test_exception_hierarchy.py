#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""`except HclError` catches everything this package raises.

`HclFactoryError` and `HclTypeParsingError` derived from `ValueError` alone, so
the one thing a caller would reasonably reach for -- catching the package's own
base class around a call into it -- silently missed both. They now derive from
`HclError` as well, and keep `ValueError` so code written against the old
hierarchy still works.
"""

from pathlib import Path

import pytest

from pyvider.hcl import (
    HclEmitError,
    HclError,
    HclFactoryError,
    HclParsingError,
    HclTypeParsingError,
    create_resource_cty,
    create_variable_cty,
    cty_to_hcl,
    parse_hcl_to_cty,
    parse_terraform_config,
)
from pyvider.hcl.factories import parse_hcl_type_string

EVERY_EXCEPTION = [HclParsingError, HclEmitError, HclFactoryError, HclTypeParsingError]


class TestHierarchy:
    """The declared relationships between the exception types."""

    @pytest.mark.parametrize("exc", EVERY_EXCEPTION)
    def test_derives_from_hcl_error(self, exc: type[Exception]) -> None:
        assert issubclass(exc, HclError)

    @pytest.mark.parametrize("exc", [HclFactoryError, HclTypeParsingError])
    def test_factory_errors_are_still_value_errors(self, exc: type[Exception]) -> None:
        """Kept deliberately: dropping it would break a caller catching ValueError."""
        assert issubclass(exc, ValueError)

    @pytest.mark.parametrize("exc", [HclParsingError, HclEmitError])
    def test_other_errors_are_not_value_errors(self, exc: type[Exception]) -> None:
        assert not issubclass(exc, ValueError)

    def test_the_two_factory_errors_are_siblings(self) -> None:
        """A type-string failure is re-raised as a factory error, so neither wraps the other."""
        assert not issubclass(HclFactoryError, HclTypeParsingError)
        assert not issubclass(HclTypeParsingError, HclFactoryError)

    def test_all_are_exported(self) -> None:
        import pyvider.hcl as package

        for exc in (HclError, *EVERY_EXCEPTION):
            assert exc.__name__ in package.__all__


class TestCatchingHclError:
    """Every raising path is caught by the package's base class."""

    def test_parse_failure(self) -> None:
        with pytest.raises(HclError):
            parse_hcl_to_cty('name = "x"\nport =\n')

    def test_terraform_read_failure(self, tmp_path: Path) -> None:
        with pytest.raises(HclError):
            parse_terraform_config(tmp_path / "absent.tf")

    def test_emit_failure(self) -> None:
        from pyvider.cty import CtyString, CtyValue

        with pytest.raises(HclError):
            cty_to_hcl(CtyValue.unknown(CtyString()))

    def test_variable_factory_failure(self) -> None:
        with pytest.raises(HclError):
            create_variable_cty(name="", type_str="string")

    def test_resource_factory_failure(self) -> None:
        with pytest.raises(HclError):
            create_resource_cty(r_type="", r_name="n", attributes_py={}, attributes_schema_py={})

    def test_type_string_failure(self) -> None:
        with pytest.raises(HclError):
            parse_hcl_type_string("custom_type")


class TestCatchingValueError:
    """The pre-existing behaviour the factory errors were written against."""

    def test_variable_factory(self) -> None:
        with pytest.raises(ValueError):
            create_variable_cty(name="", type_str="string")

    def test_type_string(self) -> None:
        with pytest.raises(ValueError):
            parse_hcl_type_string("custom_type")


class TestImportPaths:
    """The modules that used to define these still expose them."""

    def test_emitter_module(self) -> None:
        from pyvider.hcl.output.emitter import HclEmitError as FromModule

        assert FromModule is HclEmitError

    def test_types_module(self) -> None:
        from pyvider.hcl.factories.types import HclTypeParsingError as FromModule

        assert FromModule is HclTypeParsingError

    def test_variables_module(self) -> None:
        from pyvider.hcl.factories.variables import HclFactoryError as FromModule

        assert FromModule is HclFactoryError

    def test_subpackages(self) -> None:
        from pyvider.hcl.factories import HclFactoryError as FromFactories
        from pyvider.hcl.output import HclEmitError as FromOutput

        assert FromFactories is HclFactoryError
        assert FromOutput is HclEmitError


# 📄⚙️🔚
