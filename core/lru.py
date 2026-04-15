"""
LRU Page Replacement Algorithm

Description:
Implements Least Recently Used (LRU) using OrderedDict.

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


def run_lru(reference_string: List[int], frames: int) -> Dict:
    if not isinstance(frames, int) or frames <= 0:
        raise ValueError(f"frames must be a positive integer, got {frames!r}")

    memory: OrderedDict[int, bool] = OrderedDict()

    steps: List[Dict] = []
    fault_positions: List[int] = []

    for idx, page in enumerate(reference_string):
        evicted: Optional[int] = None
        fault = False

        # HIT → move to most recent
        if page in memory:
            memory.move_to_end(page)

        # FAULT
        else:
            fault = True
            fault_positions.append(idx)

            if len(memory) >= frames:
                evicted, _ = memory.popitem(last=False)

            memory[page] = True

        # Frame state
        frame_state = list(memory.keys())
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


