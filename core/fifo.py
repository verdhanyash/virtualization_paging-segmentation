# core/fifo.py - FIFO Page Replacement Algorithm (T2)
# Uses core/engine.py PageTable + FramePool for memory management
# Includes Belady's Anomaly detection

from collections import deque
from typing import Optional, Dict, List, Tuple
from core.engine import PageTable, FramePool, detect_page_fault


def run_fifo(reference_string: List[int], frames: int) -> Dict:
    # FIFO: evict the oldest page (first in, first out)
    
    page_table = PageTable()
    frame_pool = FramePool(frames)
    queue: deque[int] = deque()  # tracks insertion order (FIFO policy)
    
    steps: List[Dict] = []
    fault_positions: List[int] = []
    
    for idx, page in enumerate(reference_string):
        evicted: Optional[int] = None
        fault = False
        
        if detect_page_fault(page, page_table):
            # page fault
            fault = True
            fault_positions.append(idx)
            
            # try to allocate a free frame
            free_frame = frame_pool.allocate()
            
            if free_frame is not None:
                # use free frame
                page_table.map_page(page, free_frame)
                queue.append(page)
            else:
                # evict oldest page (FIFO policy)
                evicted = queue.popleft()
                freed_frame = page_table.unmap_page(evicted)
                frame_pool.free(freed_frame)
                
                new_frame = frame_pool.allocate()
                page_table.map_page(page, new_frame)
                queue.append(page)
        
        # Build frame state from page table mappings
        frame_state: List[Optional[int]] = [None] * frames
        for vpage, phys_frame in page_table.get_all_mappings().items():
            frame_state[phys_frame] = vpage
        
        # record step
        steps.append({
            "page": page,
            "frames": frame_state,
            "fault": fault,
            "evicted": evicted
        })
    
    return {
        "algorithm": "FIFO",
        "reference_string": reference_string,
        "frame_count": frames,
        "steps": steps,
        "total_faults": len(fault_positions),
        "total_hits": len(reference_string) - len(fault_positions),
        "fault_positions": fault_positions
    }


def detect_beladys_anomaly(reference_string: List[int], max_frames: int) -> Dict:
    # Belady's Anomaly: more frames can cause MORE faults (only in FIFO)
    # Classic example: [1,2,3,4,1,2,5,1,2,3,4,5] with 3 vs 4 frames
    
    fault_counts: Dict[int, int] = {}
    anomaly_at: List[Tuple[int, int]] = []
    
    # run FIFO for each frame count
    for f in range(1, max_frames + 1):
        result = run_fifo(reference_string, f)
        fault_counts[f] = result["total_faults"]
    
    # detect anomaly: faults increase when frames increase
    for f in range(1, max_frames):
        if fault_counts[f + 1] > fault_counts[f]:
            anomaly_at.append((f, f + 1))
    
    return {
        "anomaly_found": len(anomaly_at) > 0,
        "fault_counts": fault_counts,
        "anomaly_at": anomaly_at
    }
