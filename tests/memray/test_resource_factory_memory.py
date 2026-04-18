# SPDX-FileCopyrightText: Copyright (c) 2026 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path
from typing import Any

import pytest
from wrknv.memray.runner import run_memray_stress


@pytest.mark.memray
def test_resource_factory_memory(
    memray_output_dir: Path, memray_baseline: dict[str, Any], memray_baselines_path: Path
) -> None:
    run_memray_stress(
        script="scripts/memray/memray_resource_factory_stress.py",
        baseline_key="resource_factory_total_allocations",
        output_dir=memray_output_dir,
        baselines=memray_baseline,
        baselines_path=memray_baselines_path,
    )
