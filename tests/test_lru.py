import pytest
from core.lru import run_lru

def test_run_lru_classic_3_frames():
    """Test the classic Belady's sequence with LRU using 3 frames."""
    ref_string = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]
    frames = 3
    result = run_lru(ref_string, frames)
    
    assert result["algorithm"] == "LRU"
    assert result["frame_count"] == 3
    assert result["total_faults"] == 10
    assert result["total_hits"] == 2

def test_run_lru_basic_eviction():
    """Test standard LRU eviction behavior."""
    ref_string = [1, 2, 3, 1, 4]
    frames = 3
    result = run_lru(ref_string, frames)
    
    # 1: fault, [1]
    # 2: fault, [1, 2]
    # 3: fault, [1, 2, 3]
    # 1: hit, [2, 3, 1] (1 moved to most recently used)
    # 4: fault, [3, 1, 4] (2 is least recently used, so 2 gets evicted)
    assert result["total_faults"] == 4
    assert result["total_hits"] == 1
    assert result["steps"][-1]["evicted"] == 2
    assert result["steps"][-1]["fault"] is True

def test_run_lru_large_frames():
    """Test behavior when frames are larger than unique page references."""
    ref_string = [1, 2, 3, 1, 2, 3]
    frames = 5
    result = run_lru(ref_string, frames)
    
    assert result["total_faults"] == 3
    assert result["total_hits"] == 3
