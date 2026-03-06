# ============================================================
# Module 8 — Demand Paging Simulator
# Purpose: Simulates demand paging where pages are loaded into
#          memory only when accessed (not preloaded). Uses LRU
#          replacement when frames are full. Tracks page faults,
#          disk I/O, and working set over time.
# ============================================================

from config import DEFAULT_FRAMES
from utils import validate_ref_string, validate_num_frames


# ---------------------------------------------------------------------------
# Core Demand Paging Simulation
# ---------------------------------------------------------------------------

def simulate_demand_paging(reference_string, num_frames=DEFAULT_FRAMES):
    """
    Simulate demand paging with LRU replacement.

    In demand paging, NO pages are preloaded. Every first access
    to a page triggers a page fault (disk I/O). When frames are
    full, the LRU page is evicted.

    Args:
        reference_string (list[int] | str): Sequence of page accesses.
        num_frames (int): Number of physical frames available.

    Returns:
        dict: {
            "reference_string": list[int],
            "num_frames":       int,
            "steps":            list[dict],
            "total_faults":     int,
            "total_hits":       int,
            "fault_rate":       float,
            "hit_rate":         float,
            "disk_reads":       int,
            "disk_writes":      int,
            "working_set_sizes": list[int],
            "peak_working_set": int
        }
    """
    reference_string = validate_ref_string(reference_string)
    num_frames = validate_num_frames(num_frames)

    frames = []           # current pages in memory (ordered by LRU)
    dirty_pages = set()   # pages that have been "written" (modified)
    steps = []
    total_faults = 0
    total_hits = 0
    disk_reads = 0
    disk_writes = 0
    working_set_sizes = []

    for i, page in enumerate(reference_string):
        frames_before = list(frames)
        evicted = None
        fault = False
        disk_read = False
        disk_write = False

        if page in frames:
            # HIT — page already in memory
            total_hits += 1
            # Update LRU position
            frames.remove(page)
            frames.append(page)
            action = f"Page {page} is in memory (HIT). No disk I/O."
        else:
            # FAULT — page not in memory, must load from disk
            total_faults += 1
            fault = True
            disk_read = True
            disk_reads += 1

            if len(frames) >= num_frames:
                # Evict LRU page (front of list)
                victim = frames.pop(0)
                evicted = victim

                # If victim was dirty, write it back to disk
                if victim in dirty_pages:
                    disk_write = True
                    disk_writes += 1
                    dirty_pages.discard(victim)
                    action = (
                        f"Page {page} loaded from disk. "
                        f"Evicted dirty page {victim} (written back). "
                        f"FAULT + disk read + disk write."
                    )
                else:
                    action = (
                        f"Page {page} loaded from disk. "
                        f"Evicted clean page {victim}. "
                        f"FAULT + disk read."
                    )
            else:
                action = (
                    f"Page {page} loaded from disk into empty frame. "
                    f"FAULT + disk read."
                )

            frames.append(page)

        # Track working set (unique pages currently in memory)
        working_set_size = len(frames)
        working_set_sizes.append(working_set_size)

        frames_after = list(frames)

        steps.append({
            "step":           i + 1,
            "page":           page,
            "frames_before":  frames_before,
            "frames_after":   frames_after,
            "fault":          fault,
            "evicted":        evicted,
            "disk_read":      disk_read,
            "disk_write":     disk_write,
            "working_set":    working_set_size,
            "action":         action,
        })

    total_accesses = len(reference_string)
    fault_rate = round(total_faults / total_accesses, 4) if total_accesses > 0 else 0.0
    hit_rate = round(total_hits / total_accesses, 4) if total_accesses > 0 else 0.0

    return {
        "reference_string":   reference_string,
        "num_frames":         num_frames,
        "steps":              steps,
        "total_faults":       total_faults,
        "total_hits":         total_hits,
        "fault_rate":         fault_rate,
        "hit_rate":           hit_rate,
        "disk_reads":         disk_reads,
        "disk_writes":        disk_writes,
        "working_set_sizes":  working_set_sizes,
        "peak_working_set":   max(working_set_sizes) if working_set_sizes else 0,
    }
