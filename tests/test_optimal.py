import pytest
from core.optimal import run_optimal, _find_optimal_victim

def test_find_optimal_victim_never_used_again():
    """Test that a page never used again is chosen for eviction."""
    loaded_pages = [1, 2, 3]
    future_refs = [1, 2, 4, 5]
    # Page 3 is not in future_refs, so it should be evicted
    victim = _find_optimal_victim(loaded_pages, future_refs)
    assert victim == 3

def test_find_optimal_victim_farthest_in_future():
    """Test that the page used farthest in the future is evicted."""
    loaded_pages = [1, 2, 3]
    future_refs = [1, 3, 4, 2]
    # 1 is used at index 0
    # 3 is used at index 1
    # 2 is used at index 3
    # 2 is the farthest
    victim = _find_optimal_victim(loaded_pages, future_refs)
    assert victim == 2

def test_run_optimal_classic():
    """Test the classic Belady's sequence with 3 frames."""
    ref_string = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]
    frames = 3
    result = run_optimal(ref_string, frames)

    assert result["algorithm"] == "Optimal"
    assert result["frame_count"] == 3
    assert result["total_faults"] == 7
    assert result["total_hits"] == 5
    
    # Faults should happen at these exact positions according to standard Optimal behavior
    expected_faults = [0, 1, 2, 3, 6, 9, 10]
    assert result["fault_positions"] == expected_faults
    
def test_run_optimal_all_hits():
    """Test a scenario where pages are repeatedly accessed without faults after loading."""
    ref_string = [1, 2, 1, 2, 1, 2]
    frames = 2
    result = run_optimal(ref_string, frames)
    
    assert result["total_faults"] == 2
    assert result["total_hits"] == 4

def test_run_optimal_large_frames():
    """Test where frame count is larger than unique pages."""
    ref_string = [1, 2, 3, 1, 2, 3]
    frames = 5
    result = run_optimal(ref_string, frames)
    
    assert result["total_faults"] == 3
    assert result["total_hits"] == 3
