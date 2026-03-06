# ============================================================
# Module 7 — Fragmentation Simulator
# Purpose: Simulates memory allocation to demonstrate internal
#          and external fragmentation. Supports first-fit,
#          best-fit, and worst-fit allocation strategies.
# ============================================================

from utils import validate_memory_blocks, validate_process_requests


# ---------------------------------------------------------------------------
# Allocation Strategies
# ---------------------------------------------------------------------------

def _first_fit(blocks, request_size):
    """
    First-fit: allocate into the FIRST block that is large enough.

    Args:
        blocks (list[dict]): Current block state.
        request_size (int):  Size requested by the process.

    Returns:
        int | None: Index of the chosen block, or None if no fit.
    """
    for i, block in enumerate(blocks):
        if not block["allocated"] and block["size"] >= request_size:
            return i
    return None


def _best_fit(blocks, request_size):
    """
    Best-fit: allocate into the SMALLEST block that is large enough.
    Minimises leftover space (internal fragmentation for that block).

    Returns:
        int | None: Index of the chosen block, or None if no fit.
    """
    best_index = None
    best_leftover = float("inf")

    for i, block in enumerate(blocks):
        if not block["allocated"] and block["size"] >= request_size:
            leftover = block["size"] - request_size
            if leftover < best_leftover:
                best_leftover = leftover
                best_index = i

    return best_index


def _worst_fit(blocks, request_size):
    """
    Worst-fit: allocate into the LARGEST available block.
    Leaves the biggest leftover fragment (sometimes useful to
    keep large free blocks available).

    Returns:
        int | None: Index of the chosen block, or None if no fit.
    """
    worst_index = None
    worst_leftover = -1

    for i, block in enumerate(blocks):
        if not block["allocated"] and block["size"] >= request_size:
            leftover = block["size"] - request_size
            if leftover > worst_leftover:
                worst_leftover = leftover
                worst_index = i

    return worst_index


STRATEGY_MAP = {
    "first_fit": _first_fit,
    "best_fit":  _best_fit,
    "worst_fit": _worst_fit,
}


# ---------------------------------------------------------------------------
# Core Simulation
# ---------------------------------------------------------------------------

def simulate_fragmentation(block_sizes, process_sizes, strategy="first_fit"):
    """
    Run a fragmentation simulation.

    Memory is divided into fixed-size blocks. Processes request memory
    and are allocated into blocks according to the chosen strategy.
    After all allocations, internal and external fragmentation are
    computed.

    Internal fragmentation = space wasted INSIDE allocated blocks
        (block_size - process_size for each allocation).
    External fragmentation = total free space in unallocated blocks
        that cannot satisfy any remaining unallocated process.

    Args:
        block_sizes   (list[int]): Sizes of memory blocks.
        process_sizes (list[int]): Sizes of process memory requests.
        strategy      (str):      "first_fit", "best_fit", or "worst_fit".

    Returns:
        dict: {
            "strategy":               str,
            "blocks":                 list[dict],
            "steps":                  list[dict],
            "total_internal_frag":    int,
            "total_external_frag":    int,
            "total_allocated":        int,
            "total_unallocated":      int,
            "allocation_success_rate": float
        }
    """
    block_sizes = validate_memory_blocks(block_sizes)
    process_sizes = validate_process_requests(process_sizes)

    if strategy not in STRATEGY_MAP:
        raise ValueError(
            f"Invalid strategy: '{strategy}'. "
            f"Must be one of: {', '.join(STRATEGY_MAP.keys())}"
        )

    allocator = STRATEGY_MAP[strategy]

    # Initialize block structures
    blocks = []
    for i, size in enumerate(block_sizes):
        blocks.append({
            "id":        i,
            "size":      size,
            "allocated": False,
            "process":   None,
            "used":      0,
            "internal_frag": 0,
        })

    steps = []
    allocated_count = 0

    # Process each request
    for proc_idx, req_size in enumerate(process_sizes):
        proc_name = f"P{proc_idx + 1}"
        chosen = allocator(blocks, req_size)

        if chosen is not None:
            block = blocks[chosen]
            block["allocated"] = True
            block["process"] = proc_name
            block["used"] = req_size
            block["internal_frag"] = block["size"] - req_size
            allocated_count += 1

            steps.append({
                "process":       proc_name,
                "request_size":  req_size,
                "allocated":     True,
                "block_id":      chosen,
                "block_size":    block["size"],
                "internal_frag": block["internal_frag"],
                "action": (
                    f"{proc_name} ({req_size} bytes) → Block {chosen} "
                    f"({block['size']} bytes). "
                    f"Internal frag: {block['internal_frag']} bytes."
                ),
            })
        else:
            steps.append({
                "process":       proc_name,
                "request_size":  req_size,
                "allocated":     False,
                "block_id":      None,
                "block_size":    None,
                "internal_frag": 0,
                "action": (
                    f"{proc_name} ({req_size} bytes) → No suitable block found. "
                    f"Request DENIED."
                ),
            })

    # ── Compute fragmentation totals ──
    total_internal = sum(b["internal_frag"] for b in blocks if b["allocated"])
    free_blocks = [b for b in blocks if not b["allocated"]]
    total_free_space = sum(b["size"] for b in free_blocks)

    # External fragmentation: total free space that exists but can't serve
    # any remaining unallocated request
    unallocated_procs = [s for s in steps if not s["allocated"]]
    if unallocated_procs and total_free_space > 0:
        total_external = total_free_space
    else:
        total_external = 0

    total_procs = len(process_sizes)
    success_rate = round(allocated_count / total_procs, 4) if total_procs > 0 else 0.0

    return {
        "strategy":                strategy,
        "blocks":                  blocks,
        "steps":                   steps,
        "total_internal_frag":     total_internal,
        "total_external_frag":     total_external,
        "total_allocated":         allocated_count,
        "total_unallocated":       total_procs - allocated_count,
        "allocation_success_rate": success_rate,
    }


# ---------------------------------------------------------------------------
# Compare Strategies
# ---------------------------------------------------------------------------

def compare_strategies(block_sizes, process_sizes):
    """
    Run the simulation with all three strategies and return results
    side-by-side for easy comparison.

    Returns:
        dict: { "first_fit": {...}, "best_fit": {...}, "worst_fit": {...} }
    """
    results = {}
    for strategy in STRATEGY_MAP:
        results[strategy] = simulate_fragmentation(
            list(block_sizes), list(process_sizes), strategy
        )
    return results
