# ============================================================
# Module 11 — Preset Scenarios
# Purpose: Pre-configured demo scenarios for each simulator
#          tab. Each preset returns a dict of parameters that
#          can be fed directly into the corresponding module.
# ============================================================


PRESETS = {

    # ── Page Replacement ─────────────────────────────────────
    "page_replacement_basic": {
        "tab":              "page_replacement",
        "label":            "Basic LRU vs Optimal",
        "description":      "Classic 8-page reference string with 3 frames.",
        "reference_string": "7, 0, 1, 2, 0, 3, 0, 4",
        "num_frames":       3,
        "algorithm":        "both",
    },
    "page_replacement_heavy": {
        "tab":              "page_replacement",
        "label":            "Heavy Workload",
        "description":      "20-page reference string with 4 frames — more faults.",
        "reference_string": "1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5, 6, 7, 8, 7, 8, 9, 7, 8",
        "num_frames":       4,
        "algorithm":        "both",
    },
    "page_replacement_locality": {
        "tab":              "page_replacement",
        "label":            "Locality Pattern",
        "description":      "Exhibits temporal locality — LRU shines here.",
        "reference_string": "1, 2, 3, 1, 2, 3, 1, 2, 3, 4, 5, 4, 5, 4, 5",
        "num_frames":       3,
        "algorithm":        "both",
    },

    # ── Paging ───────────────────────────────────────────────
    "paging_basic": {
        "tab":               "paging",
        "label":             "Basic Paging",
        "description":       "4 pages mapped to 8 frames, page size 512.",
        "page_size":         512,
        "page_table":        "0:5, 1:6, 2:1, 3:2",
        "logical_addresses": "0, 512, 1024, 1536, 2048, 700, 1200",
    },
    "paging_faults": {
        "tab":               "paging",
        "label":             "Paging with Faults",
        "description":       "Some addresses map to unmapped pages.",
        "page_size":         256,
        "page_table":        "0:3, 1:7, 3:2",
        "logical_addresses": "0, 256, 512, 768, 100, 300, 900",
    },

    # ── Segmentation ─────────────────────────────────────────
    "segmentation_basic": {
        "tab":        "segmentation",
        "label":      "Basic Segmentation",
        "description": "3 segments (code, data, stack) with valid accesses.",
        "segments":   [
            {"name": "code",  "base": 0,    "limit": 1000},
            {"name": "data",  "base": 1000, "limit": 500},
            {"name": "stack", "base": 2000, "limit": 800},
        ],
        "requests": [
            {"segment": "code",  "offset": 100},
            {"segment": "data",  "offset": 200},
            {"segment": "stack", "offset": 700},
            {"segment": "code",  "offset": 999},
        ],
    },
    "segmentation_faults": {
        "tab":        "segmentation",
        "label":      "Segmentation Faults",
        "description": "Includes protection fault and missing segment.",
        "segments":   [
            {"name": "code",  "base": 0,    "limit": 500},
            {"name": "data",  "base": 1000, "limit": 300},
        ],
        "requests": [
            {"segment": "code",  "offset": 100},
            {"segment": "code",  "offset": 500},
            {"segment": "data",  "offset": 299},
            {"segment": "heap",  "offset": 50},
        ],
    },

    # ── Fragmentation ────────────────────────────────────────
    "fragmentation_basic": {
        "tab":             "fragmentation",
        "label":           "Basic Fragmentation",
        "description":     "5 memory blocks, 4 process requests — first-fit.",
        "block_sizes":     "200, 500, 100, 300, 600",
        "process_sizes":   "150, 400, 90, 250",
        "strategy":        "first_fit",
    },
    "fragmentation_compare": {
        "tab":             "fragmentation",
        "label":           "Compare Strategies",
        "description":     "See how first-fit, best-fit, worst-fit differ.",
        "block_sizes":     "100, 500, 200, 300, 600",
        "process_sizes":   "212, 417, 112, 426",
        "strategy":        "all",
    },

    # ── Demand Paging ────────────────────────────────────────
    "demand_paging_basic": {
        "tab":              "demand_paging",
        "label":            "Basic Demand Paging",
        "description":      "12-page reference with 3 frames — all loaded on demand.",
        "reference_string": "1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5",
        "num_frames":       3,
    },
    "demand_paging_large": {
        "tab":              "demand_paging",
        "label":            "Large Working Set",
        "description":      "Working set exceeds frame count significantly.",
        "reference_string": "1, 2, 3, 4, 5, 6, 7, 8, 1, 2, 3, 4, 5, 6, 7, 8",
        "num_frames":       4,
    },
}


def get_preset(name):
    """
    Get a preset scenario by name.

    Args:
        name (str): Preset key.

    Returns:
        dict: Preset parameters.

    Raises:
        ValueError: If preset name is not recognised.
    """
    if name not in PRESETS:
        raise ValueError(
            f"Unknown preset: '{name}'. "
            f"Available presets: {', '.join(PRESETS.keys())}"
        )
    return dict(PRESETS[name])  # return a copy


def get_presets_for_tab(tab):
    """
    Get all presets for a specific tab.

    Args:
        tab (str): Tab name (e.g. "page_replacement").

    Returns:
        dict: {preset_name: preset_dict} for all matching presets.
    """
    return {
        name: dict(preset)
        for name, preset in PRESETS.items()
        if preset["tab"] == tab
    }


def list_presets():
    """Return a summary list of all available presets."""
    return [
        {"name": name, "tab": p["tab"], "label": p["label"], "description": p["description"]}
        for name, p in PRESETS.items()
    ]
