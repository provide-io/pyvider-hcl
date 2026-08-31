#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Every file in `examples/` runs to completion, including under a narrow locale.

An example is documentation that claims to be executable, so it rots the moment
an API it demonstrates changes shape. Running each one here holds that claim to
the same standard as the rest of the suite -- 0.6.2 changed `create_resource_cty`
output and 0.6.3 added block emission, and nothing would have caught an example
left behind by either.

Each example is run with `PYTHONIOENCODING=cp1252`, which reproduces on every
platform what Windows does to redirected output. That is not a hypothetical: the
first CI run of this file failed on Windows because four examples print emoji and
Python encodes redirected stdout with the locale's codec, so each aborted
mid-run with a `UnicodeEncodeError`. The fix is for an example that prints
non-ASCII to reconfigure stdout to UTF-8; this test is what proves it did, and
that the characters survive rather than being dropped or replaced.
"""

import os
from pathlib import Path
import subprocess
import sys

import pytest

EXAMPLES_DIR = Path(__file__).resolve().parent.parent / "examples"
EXAMPLES = sorted(EXAMPLES_DIR.glob("[0-9]*.py"))

# The Windows default for redirected output. Anything an example prints that
# cp1252 cannot represent has to be carried by an explicit UTF-8 stdout.
NARROW_ENCODING = "cp1252"


def _run(example: Path) -> subprocess.CompletedProcess[str]:
    """Run one example as its own process, under the narrow locale."""
    return subprocess.run(
        [sys.executable, str(example)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        env={**os.environ, "PYTHONIOENCODING": NARROW_ENCODING},
        timeout=120,
        check=False,
    )


def test_examples_are_discovered() -> None:
    """A glob that matches nothing would make every test below vacuous."""
    assert EXAMPLES, f"no examples found under {EXAMPLES_DIR}"


@pytest.mark.parametrize("example", EXAMPLES, ids=lambda path: path.stem)
def test_example_runs(example: Path) -> None:
    result = _run(example)
    assert result.returncode == 0, f"{example.name} exited {result.returncode}\n{result.stderr}"
    assert result.stdout.strip(), f"{example.name} printed nothing"


def test_non_ascii_output_survives_a_narrow_locale() -> None:
    """At least one example prints non-ASCII, and it arrives intact.

    Without this the test above would still pass if every example were reduced
    to ASCII, which is a different fix than the one that was made.
    """
    printed = "".join(_run(example).stdout for example in EXAMPLES)
    non_ascii = {char for char in printed if ord(char) > 127}

    assert non_ascii, "no example prints non-ASCII, so nothing here is being exercised"
    assert "�" not in non_ascii, "output contains a replacement character"


# 📄⚙️🔚
