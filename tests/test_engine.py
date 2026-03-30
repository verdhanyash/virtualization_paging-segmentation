import pytest
from core.engine import PageTable, FramePool, translate_address, detect_page_fault

def test_page_table_mapping():
    """Test PageTable mapping functionality."""
    pt = PageTable()
    
    assert pt.is_loaded(0) is False
    assert pt.lookup(0) is None
    
    pt.map_page(0, 5)
    assert pt.is_loaded(0) is True
    assert pt.lookup(0) == 5
    
    unmapped = pt.unmap_page(0)
    assert unmapped == 5
    assert pt.is_loaded(0) is False
    assert pt.lookup(0) is None

def test_page_table_invalid_mapping():
    """Test PageTable validation for negative inputs."""
    pt = PageTable()
    with pytest.raises(ValueError):
        pt.map_page(-1, 5)
    with pytest.raises(ValueError):
        pt.map_page(0, -5)

def test_frame_pool_allocation():
    """Test FramePool basic allocation and deallocation."""
    fp = FramePool(3)
    
    assert fp.get_free_count() == 3
    assert fp.is_full() is False
    
    frame1 = fp.allocate()
    assert frame1 is not None
    assert fp.get_free_count() == 2
    
    fp.allocate()
    fp.allocate()
    assert fp.is_full() is True
    assert fp.get_free_count() == 0
    assert fp.allocate() is None
    
    assert fp.free(frame1) is True
    assert fp.is_full() is False
    assert fp.get_free_count() == 1

def test_frame_pool_invalid_free():
    """Test FramePool invalid free operations."""
    fp = FramePool(3)
    
    # Freeing unallocated frame
    assert fp.free(0) is False
    
    # Freeing out of bounds frame
    with pytest.raises(ValueError):
        fp.free(5)
    with pytest.raises(ValueError):
        fp.free(-1)

def test_translate_address():
    """Test virtual address translation."""
    page, offset = translate_address(4096, 4096)
    assert page == 1
    assert offset == 0
    
    page, offset = translate_address(5000, 4096)
    assert page == 1
    assert offset == 904
    
    with pytest.raises(ValueError):
        translate_address(-100, 4096)
    with pytest.raises(ValueError):
        translate_address(4096, 0)

def test_detect_page_fault():
    """Test page fault detection logic."""
    pt = PageTable()
    pt.map_page(2, 10)
    
    assert detect_page_fault(2, pt) is False  # Page is loaded (no fault)
    assert detect_page_fault(3, pt) is True   # Page is NOT loaded (fault)
