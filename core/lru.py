"""
LRU Page Replacement Algorithm (T3)
Uses core/engine.py PageTable + FramePool for memory management

Description:
Implements Least Recently Used (LRU) using OrderedDict for recency tracking.

Rules:
- On HIT → move page to end (most recent)
- On FAULT → if full, remove least recently used (first item)

Example:
reference_string = [1,2,3,4,1,2,5,1,2,3,4,5]
frames = 3

Expected:
total_faults = 10
"""

from collections import OrderedDict
from typing import Dict, List, Optional
from core.engine import PageTable, FramePool, detect_page_fault


def run_lru(reference_string: List[int], frames: int) -> Dict:
    page_table = PageTable()
    frame_pool = FramePool(frames)
    recency: OrderedDict[int, bool] = OrderedDict()  # LRU-specific: tracks access order

    steps: List[Dict] = []
    fault_positions: List[int] = []

    for idx, page in enumerate(reference_string):
        evicted: Optional[int] = None
        fault = False

        if not detect_page_fault(page, page_table):
            # HIT — update recency (move to most recent)
            recency.move_to_end(page)
        else:
            # FAULT
            fault = True
            fault_positions.append(idx)

            if frame_pool.is_full():
                # Evict least recently used (first in OrderedDict)
                evicted = next(iter(recency))
                freed_frame = page_table.unmap_page(evicted)
                frame_pool.free(freed_frame)
                del recency[evicted]

            # Allocate new frame and map
            new_frame = frame_pool.allocate()
            page_table.map_page(page, new_frame)
            recency[page] = True

        # Frame state: use recency order (matches original LRU output format)
        frame_state = list(recency.keys())
        while len(frame_state) < frames:
            frame_state.append(None)

        steps.append({
            "page": page,
            "frames": frame_state.copy(),
            "fault": fault,
            "evicted": evicted
        })

    return {
        "algorithm": "LRU",
        "reference_string": reference_string,
        "frame_count": frames,
        "steps": steps,
        "total_faults": len(fault_positions),
        "total_hits": len(reference_string) - len(fault_positions),
        "fault_positions": fault_positions
    }