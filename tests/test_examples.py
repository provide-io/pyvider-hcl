#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Every file in `examples/` runs to completion and prints ASCII.

An example is documentation that claims to be executable, so it rots the moment
an API it demonstrates changes shape. Running each one here holds that claim to
the same standard as the rest of the suite -- 0.6.2 changed `create_resource_cty`
output and 0.6.3 added block emission, and nothing would have caught an example
left behind by either.

The ASCII check is not style policing. A Windows console defaults to cp1252 and
Python writes stdout with strict error handling, so one emoji in a `print` call
aborts the example mid-run with a `UnicodeEncodeError` -- which is exactly how
examples 02, 03, 07 and 08 were failing for every Windows user. Asserting it
here fails on any platform, rather than only on the one runner that has the
narrow encoding.
"""

from pathlib import Path
import subprocess
import sys

import pytest

EXAMPLES_DIR = Path(__file__).resolve().parent.parent / "examples"
EXAMPLES = sorted(EXAMPLES_DIR.glob("[0-9]*.py"))


def test_examples_are_discovered() -> None:
    """A glob that matches nothing would make every test below vacuous."""
    assert EXAMPLES, f"no examples found under {EXAMPLES_DIR}"


@pytest.mark.parametrize("example", EXAMPLES, ids=lambda path: path.stem)
def test_example_runs(example: Path) -> None:
    result = subprocess.run(
        [sys.executable, str(example)],
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    assert result.returncode == 0, f"{example.name} exited {result.returncode}\n{result.stderr}"
    assert result.stdout.strip(), f"{example.name} printed nothing"

    try:
        result.stdout.encode("ascii")
    except UnicodeEncodeError as e:
        offending = result.stdout[e.start : e.end]
        pytest.fail(f"{example.name} printed {offending!r}, which a cp1252 console cannot encode")


# 📄⚙️🔚
