"""
Optimal Page Replacement Algorithm

Description:
Implements Optimal (MIN) page replacement algorithm, which replaces the page
that will not be used for the longest time in the future.

Rules:
- On HIT → do nothing (page already in memory)
- On FAULT → if free frame available, use it
- On FAULT → if no free frame, evict the page whose next use is farthest in the future
  (or never used again)

Example:
reference_string = [1,2,3,4,1,2,5,1,2,3,4,5]
frames = 3

Expected:
total_faults = 7
"""

from typing import Dict, List, Optional


def _find_optimal_victim(loaded_pages: list[int], future_refs: list[int]) -> int:
    """
    Helper function to find which page to evict.
    
    If a page is never used again, it's the best candidate to evict.
    Else, evict the page with the maximum "next use index".

    Args:
        loaded_pages: List of currently loaded pages.
        future_refs: The remainder of the reference string (look-ahead).

    Returns:
        The page number to evict.
    """
    farthest_page = -1
    farthest_index = -1

    for page in loaded_pages:
        try:
            # Find next occurrence of this page in future_refs
            index = future_refs.index(page)
            if index > farthest_index:
                farthest_index = index
                farthest_page = page
        except ValueError:
            # Page is never used again - prioritize for eviction
            return page

    # If all pages are used again, evict the one with the farthest next use
    return farthest_page


def run_optimal(reference_string: list[int], frames: int) -> dict:
    """
    Simulate the Optimal page replacement algorithm.

    Args:
        reference_string: List of page numbers references.
        frames: Number of available physical frames.

    Returns:
        Dictionary containing simulation results including steps, fault count, etc.
    """
    # Initialize frames as empty (None represents free frame)
    frame_list: List[Optional[int]] = [None] * frames

    steps: List[Dict] = []
    fault_positions: List[int] = []

    for idx, page in enumerate(reference_string):
        evicted: Optional[int] = None
        fault = False

        if page in frame_list:
            # Page hit - no action needed
            pass
        else:
            # Page fault
            fault = True
            fault_positions.append(idx)

            # Check if there's a free frame
            if None in frame_list:
                # Use free frame
                free_index = frame_list.index(None)
                frame_list[free_index] = page
            else:
                # No free frame - need to evict a page
                # We know all frames are loaded, so type hint handles no-None case
                loaded_pages = [p for p in frame_list if p is not None]
                future_refs = reference_string[idx + 1:]
                
                # Find the optimal victim
                evicted = _find_optimal_victim(loaded_pages, future_refs)
                
                # Replace the evicted page
                evicted_index = frame_list.index(evicted)
                frame_list[evicted_index] = page

        # Record step
        steps.append({
            "page": page,
            "frames": frame_list.copy(),
            "fault": fault,
            "evicted": evicted
        })

    return {
        "algorithm": "Optimal",
        "reference_string": reference_string,
        "frame_count": frames,
        "steps": steps,
        "total_faults": len(fault_positions),
        "total_hits": len(reference_string) - len(fault_positions),
        "fault_positions": fault_positions
    }
