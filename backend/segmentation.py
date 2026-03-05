# ============================================================
# Module 4 — Segmentation Engine
# Purpose: Segment-based logical-to-physical address
#          translation with bounds checking. Supports
#          single-address lookup, batch translation, and
#          a full simulation trace.
# ============================================================

from utils import validate_non_negative_int, validate_positive_int, validate_segments


# ---------------------------------------------------------------------------
# Core Translation
# ---------------------------------------------------------------------------

def translate_segment_address(segment_name, offset, segment_table):
    """
    Translate a segmented logical address (segment_name, offset) to a
    physical address using the segment table.

    Translation rule:
        physical_address = segment.base + offset
    Bounds check:
        offset must be strictly less than segment.limit.

    Args:
        segment_name  (str):  Name of the target segment (e.g. "code").
        offset        (int):  Byte offset within that segment (>= 0).
        segment_table (dict): {segment_name (str): {"base": int, "limit": int}}

    Returns:
        dict: {
            "segment_name":     str,
            "offset":           int,
            "base":             int | None,
            "limit":            int | None,
            "physical_address": int | None,
            "protection_fault": bool,   # offset >= limit
            "seg_fault":        bool,   # segment not in table
            "error":            str | None
        }
    """
    offset = validate_non_negative_int(offset, "Offset")

    if segment_name not in segment_table:
        return {
            "segment_name":     segment_name,
            "offset":           offset,
            "base":             None,
            "limit":            None,
            "physical_address": None,
            "protection_fault": False,
            "seg_fault":        True,
            "error":            f"Segment '{segment_name}' not found in segment table."
        }

    seg   = segment_table[segment_name]
    base  = seg["base"]
    limit = seg["limit"]

    if offset >= limit:
        return {
            "segment_name":     segment_name,
            "offset":           offset,
            "base":             base,
            "limit":            limit,
            "physical_address": None,
            "protection_fault": True,
            "seg_fault":        False,
            "error": (
                f"Protection fault: offset {offset} >= limit {limit} "
                f"for segment '{segment_name}'."
            )
        }

    physical_address = base + offset

    return {
        "segment_name":     segment_name,
        "offset":           offset,
        "base":             base,
        "limit":            limit,
        "physical_address": physical_address,
        "protection_fault": False,
        "seg_fault":        False,
        "error":            None
    }


def translate_segment_batch(requests, segment_table):
    """
    Translate a list of (segment_name, offset) pairs in one call.

    Args:
        requests      (list): List of {"segment": str, "offset": int} dicts.
        segment_table (dict): {segment_name: {"base": int, "limit": int}}

    Returns:
        list[dict]: One result dict per request (see translate_segment_address).
    """
    if not isinstance(requests, list) or len(requests) == 0:
        raise ValueError("requests must be a non-empty list of {segment, offset} dicts.")

    results = []
    for i, req in enumerate(requests):
        if not isinstance(req, dict) or "segment" not in req or "offset" not in req:
            raise ValueError(
                f"Request {i + 1} must be a dict with 'segment' and 'offset' keys."
            )
        results.append(
            translate_segment_address(req["segment"], req["offset"], segment_table)
        )

    return results


# ---------------------------------------------------------------------------
# Segment Table Builder
# ---------------------------------------------------------------------------

def build_segment_table(segments):
    """
    Convert a validated list of segment definitions into a lookup dict.

    Args:
        segments (list[dict]): [{"name": str, "base": int, "limit": int}, ...]
                               (output of utils.validate_segments)

    Returns:
        dict: {segment_name (str): {"base": int, "limit": int}}
    """
    segments = validate_segments(segments)
    return {seg["name"]: {"base": seg["base"], "limit": seg["limit"]} for seg in segments}


# ---------------------------------------------------------------------------
# Memory Map
# ---------------------------------------------------------------------------

def get_memory_map(segment_table):
    """
    Return a sorted list of memory regions occupied by each segment.
    Useful for detecting overlaps and visualising the address space.

    Args:
        segment_table (dict): {segment_name: {"base": int, "limit": int}}

    Returns:
        list[dict]: Sorted by base address, each entry:
            {
                "segment_name": str,
                "base":         int,
                "limit":        int,
                "end":          int,   # base + limit - 1 (inclusive)
                "size":         int    # == limit
            }
    """
    regions = []
    for name, seg in segment_table.items():
        regions.append({
            "segment_name": name,
            "base":         seg["base"],
            "limit":        seg["limit"],
            "end":          seg["base"] + seg["limit"] - 1,
            "size":         seg["limit"]
        })

    regions.sort(key=lambda r: r["base"])
    return regions


def detect_overlaps(segment_table):
    """
    Detect overlapping memory regions in the segment table.

    Args:
        segment_table (dict): {segment_name: {"base": int, "limit": int}}

    Returns:
        list[dict]: Each overlap:
            {"seg_a": str, "seg_b": str, "overlap_start": int, "overlap_end": int}
        Empty list if no overlaps exist.
    """
    regions  = get_memory_map(segment_table)
    overlaps = []

    for i in range(len(regions)):
        for j in range(i + 1, len(regions)):
            a, b = regions[i], regions[j]
            start = max(a["base"], b["base"])
            end   = min(a["end"],  b["end"])
            if start <= end:
                overlaps.append({
                    "seg_a":         a["segment_name"],
                    "seg_b":         b["segment_name"],
                    "overlap_start": start,
                    "overlap_end":   end
                })

    return overlaps


# ---------------------------------------------------------------------------
# Full Simulation
# ---------------------------------------------------------------------------

def run_segmentation_simulation(requests, segments):
    """
    Run a full segmentation simulation over a list of access requests.

    Args:
        requests (list[dict]): [{"segment": str, "offset": int}, ...]
        segments (list[dict]): [{"name": str, "base": int, "limit": int}, ...]

    Returns:
        dict: {
            "segment_table":    dict,         # built from segments
            "memory_map":       list[dict],   # sorted regions
            "overlaps":         list[dict],   # detected overlaps (if any)
            "steps":            list[dict],   # one per request
            "total_accesses":   int,
            "seg_faults":       int,
            "protection_faults":int,
            "successful":       int
        }
    """
    segment_table = build_segment_table(segments)
    steps         = translate_segment_batch(requests, segment_table)

    seg_faults        = sum(1 for s in steps if s["seg_fault"])
    protection_faults = sum(1 for s in steps if s["protection_fault"])
    successful        = sum(1 for s in steps if not s["seg_fault"] and not s["protection_fault"])

    return {
        "segment_table":     segment_table,
        "memory_map":        get_memory_map(segment_table),
        "overlaps":          detect_overlaps(segment_table),
        "steps":             steps,
        "total_accesses":    len(steps),
        "seg_faults":        seg_faults,
        "protection_faults": protection_faults,
        "successful":        successful
    }
