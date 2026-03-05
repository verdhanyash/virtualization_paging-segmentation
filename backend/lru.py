# ============================================================
# Module 5 — LRU (Least Recently Used) Page Replacement
# Purpose: Simulates the LRU page replacement algorithm.
#
# HOW LRU WORKS:
#   When a page fault occurs and all frames are full,
#   LRU evicts the page that has NOT been used for the
#   LONGEST time. It tracks "recency" — the most recently
#   accessed page is the safest, the least recently accessed
#   page is the victim.
#
# EXAMPLE:
#   Reference string: [7, 0, 1, 2, 0, 3, 0, 4]
#   Frames: 3
#
#   Step 1: page 7 → frames = [7, -, -]        FAULT (cold start)
#   Step 2: page 0 → frames = [7, 0, -]        FAULT (cold start)
#   Step 3: page 1 → frames = [7, 0, 1]        FAULT (cold start)
#   Step 4: page 2 → frames = [2, 0, 1]        FAULT (evict 7 — least recent)
#   Step 5: page 0 → frames = [2, 0, 1]        HIT   (0 already in memory)
#   Step 6: page 3 → frames = [2, 0, 3]        FAULT (evict 1 — least recent)
#   Step 7: page 0 → frames = [2, 0, 3]        HIT   (0 already in memory)
#   Step 8: page 4 → frames = [4, 0, 3]        FAULT (evict 2 — least recent)
#
# DATA STRUCTURE:
#   We use a Python list as an ordered queue. The FRONT of
#   the list is the LEAST recently used (victim for eviction).
#   The BACK of the list is the MOST recently used (safest).
#   On every access (hit or fault-load), the page is moved
#   to the back of the list.
# ============================================================

from config import DEFAULT_FRAMES
from utils import validate_ref_string, validate_num_frames


# ---------------------------------------------------------------------------
# Core LRU Simulation
# ---------------------------------------------------------------------------

def simulate_lru(reference_string, num_frames=DEFAULT_FRAMES):
    """
    Run an LRU page replacement simulation.

    Args:
        reference_string (list[int] | str):
            Sequence of page numbers to access.
            Can be a list like [7, 0, 1, 2] or a string like "7, 0, 1, 2".
        num_frames (int):
            Number of physical memory frames available (default: 3).

    Returns:
        dict: {
            "reference_string": list[int],   — the validated input sequence
            "num_frames":       int,         — number of frames used
            "steps":            list[dict],  — one entry per page access
            "total_faults":     int,         — total page faults incurred
            "total_hits":       int,         — total page hits
            "fault_rate":       float,       — faults / total accesses (0.0–1.0)
            "hit_rate":         float        — hits / total accesses (0.0–1.0)
        }

        Each step dict contains:
        {
            "step":            int,       — 1-indexed step number
            "page":            int,       — page being accessed
            "frames_before":   list,      — frame state BEFORE this access
            "frames_after":    list,      — frame state AFTER this access
            "fault":           bool,      — True if this was a page fault
            "evicted":         int|None,  — page evicted (None if no eviction)
            "action":          str        — human-readable description
        }
    """
    # ── Step 1: Validate inputs ──────────────────────────────────────
    reference_string = validate_ref_string(reference_string)
    num_frames = validate_num_frames(num_frames)

    # ── Step 2: Initialize data structures ───────────────────────────
    #
    # frames:      The current pages loaded in memory.
    #              We use a list of length num_frames, initialized with
    #              None to represent empty slots.
    #
    # usage_order: Tracks recency of use. This is a list where:
    #              - Front (index 0) = LEAST recently used  → eviction victim
    #              - Back  (index -1) = MOST recently used  → safest page
    #              Every time a page is accessed (hit or loaded),
    #              it moves to the back of this list.

    frames = [None] * num_frames     # physical memory slots
    usage_order = []                  # recency tracker (LRU queue)

    steps = []           # step-by-step trace for visualization
    total_faults = 0     # running fault counter
    total_hits = 0       # running hit counter

    # ── Step 3: Process each page in the reference string ────────────
    for i, page in enumerate(reference_string):

        # Snapshot the frame state BEFORE this access
        frames_before = list(frames)

        evicted = None
        fault = False

        # ── CASE A: HIT — page is already in memory ─────────────────
        if page in frames:
            total_hits += 1
            action = f"Page {page} is already in memory (HIT)."

            # Update recency: move this page to the back of usage_order
            # (it was just accessed, so it's now the most recently used)
            usage_order.remove(page)
            usage_order.append(page)

        # ── CASE B: FAULT — page is NOT in memory ───────────────────
        else:
            total_faults += 1
            fault = True

            # Sub-case B1: There is an empty frame available
            #   → Simply load the page into the first empty slot
            if None in frames:
                empty_index = frames.index(None)
                frames[empty_index] = page
                action = f"Page {page} loaded into empty frame {empty_index} (FAULT)."

            # Sub-case B2: All frames are full — must evict
            #   → The victim is the FRONT of usage_order (least recent)
            else:
                # The least recently used page is at the front
                victim = usage_order.pop(0)

                # Find which frame the victim occupies and replace it
                victim_index = frames.index(victim)
                frames[victim_index] = page
                evicted = victim
                action = (
                    f"Page {page} loaded, evicted page {victim} "
                    f"from frame {victim_index} (FAULT — LRU eviction)."
                )

            # Either way, the newly loaded page is now the most recent
            usage_order.append(page)

        # Snapshot the frame state AFTER this access
        frames_after = list(frames)

        # ── Record this step ─────────────────────────────────────────
        steps.append({
            "step":          i + 1,
            "page":          page,
            "frames_before": frames_before,
            "frames_after":  frames_after,
            "fault":         fault,
            "evicted":       evicted,
            "action":        action,
        })

    # ── Step 4: Compute summary statistics ───────────────────────────
    total_accesses = len(reference_string)
    fault_rate = round(total_faults / total_accesses, 4) if total_accesses > 0 else 0.0
    hit_rate = round(total_hits / total_accesses, 4) if total_accesses > 0 else 0.0

    return {
        "reference_string": reference_string,
        "num_frames":       num_frames,
        "steps":            steps,
        "total_faults":     total_faults,
        "total_hits":       total_hits,
        "fault_rate":       fault_rate,
        "hit_rate":         hit_rate,
    }


# ---------------------------------------------------------------------------
# Fault Count Helper (for comparison charts)
# ---------------------------------------------------------------------------

def lru_fault_count(reference_string, num_frames=DEFAULT_FRAMES):
    """
    Convenience function that returns ONLY the total fault count.

    Useful when you just need the number (e.g. for comparison bar charts
    between LRU and Optimal) and don't need the full step trace.

    Args:
        reference_string (list[int] | str): Page reference sequence.
        num_frames (int): Number of frames available.

    Returns:
        int: Total number of page faults.
    """
    result = simulate_lru(reference_string, num_frames)
    return result["total_faults"]


# ---------------------------------------------------------------------------
# Fault-vs-Frames Curve (for line graphs)
# ---------------------------------------------------------------------------

def lru_fault_curve(reference_string, max_frames=None):
    """
    Compute the number of LRU page faults for frame counts 1, 2, …, max_frames.

    This is useful for generating a "faults vs. frames" line graph that shows
    how increasing memory (more frames) reduces page faults.

    Args:
        reference_string (list[int] | str): Page reference sequence.
        max_frames (int | None):
            Upper bound on frames to test.
            Defaults to the number of unique pages in the reference string
            (beyond which faults = number of unique pages, since every page
            fits in memory).

    Returns:
        list[dict]: One entry per frame count:
            [
                {"frames": 1, "faults": 9},
                {"frames": 2, "faults": 7},
                {"frames": 3, "faults": 5},
                ...
            ]
    """
    # Validate once, then reuse the validated list
    reference_string = validate_ref_string(reference_string)

    # Default max_frames = number of unique pages (beyond this, faults plateau)
    if max_frames is None:
        max_frames = len(set(reference_string))
    else:
        max_frames = validate_num_frames(max_frames)

    curve = []
    for n in range(1, max_frames + 1):
        faults = simulate_lru(reference_string, n)["total_faults"]
        curve.append({"frames": n, "faults": faults})

    return curve
