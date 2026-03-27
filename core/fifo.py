# core/fifo.py - FIFO Page Replacement Algorithm (T2)
# Includes Belady's Anomaly detection

from collections import deque
from typing import Optional, Dict, List, Tuple


def run_fifo(reference_string: List[int], frames: int) -> Dict:
    # FIFO: evict the oldest page (first in, first out)
    
    frame_list: List[Optional[int]] = [None] * frames
    queue: deque[int] = deque()  # tracks insertion order
    page_to_frame: Dict[int, int] = {}
    
    steps: List[Dict] = []
    fault_positions: List[int] = []
    
    for idx, page in enumerate(reference_string):
        evicted: Optional[int] = None
        fault = False
        
        if page not in page_to_frame:
            # page fault
            fault = True
            fault_positions.append(idx)
            
            # find free frame
            free_frame = _find_free_frame(frame_list)
            
            if free_frame is not None:
                # use free frame
                frame_list[free_frame] = page
                page_to_frame[page] = free_frame
                queue.append(page)
            else:
                # evict oldest page
                evicted = queue.popleft()
                evicted_frame = page_to_frame.pop(evicted)
                frame_list[evicted_frame] = page
                page_to_frame[page] = evicted_frame
                queue.append(page)
        
        # record step
        steps.append({
            "page": page,
            "frames": frame_list.copy(),
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


def _find_free_frame(frame_list: List[Optional[int]]) -> Optional[int]:
    # returns index of first free frame, or None if full
    for i, f in enumerate(frame_list):
        if f is None:
            return i
    return None


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
