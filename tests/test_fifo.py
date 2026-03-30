import pytest
from core.fifo import run_fifo, detect_beladys_anomaly

def test_run_fifo_classic_3_frames():
    """Test the classic Belady's sequence with 3 frames."""
    ref_string = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]
    result = run_fifo(ref_string, 3)
    
    assert result["algorithm"] == "FIFO"
    assert result["frame_count"] == 3
    assert result["total_faults"] == 9
    assert result["total_hits"] == 3

def test_run_fifo_classic_4_frames():
    """Test the classic Belady's sequence with 4 frames (should have more faults)."""
    ref_string = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]
    result = run_fifo(ref_string, 4)
    
    assert result["algorithm"] == "FIFO"
    assert result["frame_count"] == 4
    assert result["total_faults"] == 10
    assert result["total_hits"] == 2

def test_run_fifo_all_hits():
    """Test when pages are already loaded in memory."""
    ref_string = [1, 2, 1, 2, 1, 2]
    result = run_fifo(ref_string, 2)
    
    assert result["total_faults"] == 2
    assert result["total_hits"] == 4

def test_detect_beladys_anomaly():
    """Test if Belady's Anomaly is correctly detected for the classic sequence."""
    ref_string = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]
    result = detect_beladys_anomaly(ref_string, 5)
    
    assert result["anomaly_found"] is True
    assert (3, 4) in result["anomaly_at"]
    assert result["fault_counts"][3] == 9
    assert result["fault_counts"][4] == 10
