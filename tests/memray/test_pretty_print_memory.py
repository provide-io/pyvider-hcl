import pytest

from tests.memray.conftest import assert_allocation_within_threshold, run_memray_stress


@pytest.mark.memray
def test_pretty_print_memory(memray_output_dir, memray_baseline):
    bin_path, total_allocs = run_memray_stress("memray_pretty_print_stress", memray_output_dir)
    assert bin_path.exists()
    assert total_allocs > 0
    baseline = memray_baseline.get("pretty_print_total_allocations")
    assert_allocation_within_threshold(baseline, total_allocs, "pretty_print")
