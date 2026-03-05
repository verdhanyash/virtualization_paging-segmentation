# ============================================================
# Module 6 — Optimal Page Replacement Algorithm
# Purpose: Simulates the Optimal (OPT / Bélády's) page
#          replacement algorithm.
#
# HOW OPTIMAL WORKS:
#   When a page fault occurs and all frames are full,
#   Optimal evicts the page that will NOT be used for the
#   LONGEST time IN THE FUTURE. Unlike LRU (which looks
#   backward at past usage), Optimal looks FORWARD at
#   upcoming references.
#
#   This is a theoretical "best case" algorithm — it gives
#   the FEWEST possible faults for any reference string.
#   It cannot be implemented in a real OS (you'd need to
#   predict the future), but it serves as a benchmark to
#   compare other algorithms against.
#
# EXAMPLE:
#   Reference string: [7, 0, 1, 2, 0, 3, 0, 4]
#   Frames: 3
#
#   Step 1: page 7 → frames = [7, -, -]        FAULT (cold start)
#   Step 2: page 0 → frames = [7, 0, -]        FAULT (cold start)
#   Step 3: page 1 → frames = [7, 0, 1]        FAULT (cold start)
#   Step 4: page 2 → frames = [2, 0, 1]        FAULT (evict 7 — not used again)
#   Step 5: page 0 → frames = [2, 0, 1]        HIT   (0 already in memory)
#   Step 6: page 3 → frames = [2, 0, 3]        FAULT (evict 1 — used farthest)
#   Step 7: page 0 → frames = [2, 0, 3]        HIT   (0 already in memory)
#   Step 8: page 4 → frames = [4, 0, 3]        FAULT (evict 2 — used farthest)
#
# KEY DIFFERENCE FROM LRU:
#   - LRU looks BACKWARD: "which page was used least recently?"
#   - Optimal looks FORWARD: "which page will be used farthest in the future?"
#   - For the example above, both get 6 faults, but for many
#     reference strings Optimal will get fewer faults than LRU.
#
# DATA STRUCTURE:
#   We use a simple list for frames. To decide which page to
#   evict, we scan the remaining reference string and find
#   the "next use" index for each page currently in memory.
#   The page with the highest "next use" (or one that is never
#   used again) is the eviction victim.
# ============================================================

from config import DEFAULT_FRAMES
from utils import validate_ref_string, validate_num_frames


# ---------------------------------------------------------------------------
# Helper: Find Next Use of a Page
# ---------------------------------------------------------------------------

def _find_next_use(page, reference_string, current_index):
    """
    Find the NEXT position where this page appears in the reference string,
    starting from current_index + 1.

    Args:
        page (int):              The page to search for.
        reference_string (list): The full reference string.
        current_index (int):     The current step we're processing.

    Returns:
        int: The index of the next occurrence, or float('inf') if the
             page is never used again (making it the ideal eviction
             candidate).
    """
    # Search through all future references (everything after current step)
    for future_index in range(current_index + 1, len(reference_string)):
        if reference_string[future_index] == page:
            return future_index

    # Page is never used again — return infinity so it's chosen for eviction
    return float("inf")


# ---------------------------------------------------------------------------
# Helper: Pick the Optimal Victim
# ---------------------------------------------------------------------------

def _pick_victim(frames, reference_string, current_index):
    """
    Among all pages currently in frames, find the one whose next use
    is FARTHEST in the future. That page is the optimal eviction victim.

    If a page is never used again (next_use = infinity), it is
    immediately chosen — no need to check further.

    Args:
        frames (list):           Current pages in memory.
        reference_string (list): The full reference string.
        current_index (int):     The current step being processed.

    Returns:
        int: The page that should be evicted (the optimal victim).
    """
    farthest_use = -1     # Track the largest "next use" index seen
    victim = None         # The page to evict

    for page in frames:
        if page is None:
            continue  # Skip empty slots (shouldn't happen when frames are full)

        next_use = _find_next_use(page, reference_string, current_index)

        # If this page is never used again, it's the perfect victim
        if next_use == float("inf"):
            return page

        # Otherwise, keep track of which page is used farthest away
        if next_use > farthest_use:
            farthest_use = next_use
            victim = page

    return victim


# ---------------------------------------------------------------------------
# Core Optimal Simulation
# ---------------------------------------------------------------------------

def simulate_optimal(reference_string, num_frames=DEFAULT_FRAMES):
    """
    Run an Optimal (Bélády's) page replacement simulation.

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
    # frames: The current pages loaded in memory.
    #         A list of length num_frames, initialized with None
    #         to represent empty slots.
    #
    # Unlike LRU, we do NOT need a usage_order tracker.
    # Instead, on each eviction we scan the FUTURE references to
    # decide which page to evict. This is more expensive (O(n*m)
    # per eviction), but gives the theoretical minimum faults.

    frames = [None] * num_frames     # physical memory slots

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

            # Unlike LRU, there is nothing to update on a hit.
            # Optimal doesn't track past usage — it only looks
            # forward when it needs to evict.

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
            #   → Find the page whose next use is FARTHEST in the future
            else:
                victim = _pick_victim(frames, reference_string, i)

                # Find which frame the victim occupies and replace it
                victim_index = frames.index(victim)
                frames[victim_index] = page
                evicted = victim

                # Build a descriptive action message
                next_use = _find_next_use(victim, reference_string, i)
                if next_use == float("inf"):
                    reason = "never used again"
                else:
                    reason = f"not needed until step {next_use + 1}"

                action = (
                    f"Page {page} loaded, evicted page {victim} "
                    f"from frame {victim_index} (FAULT — Optimal: {reason})."
                )

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

def optimal_fault_count(reference_string, num_frames=DEFAULT_FRAMES):
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
    result = simulate_optimal(reference_string, num_frames)
    return result["total_faults"]


# ---------------------------------------------------------------------------
# Fault-vs-Frames Curve (for line graphs)
# ---------------------------------------------------------------------------

def optimal_fault_curve(reference_string, max_frames=None):
    """
    Compute the number of Optimal faults for frame counts 1, 2, …, max_frames.

    This is useful for generating a "faults vs. frames" line graph that shows
    how increasing memory (more frames) reduces page faults under the Optimal
    algorithm — the theoretical best case.

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
                {"frames": 1, "faults": 8},
                {"frames": 2, "faults": 5},
                {"frames": 3, "faults": 4},
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
        faults = simulate_optimal(reference_string, n)["total_faults"]
        curve.append({"frames": n, "faults": faults})

    return curve
