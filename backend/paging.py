# ============================================================
# Module 3 — Paging Engine
# Purpose: Logical-to-physical address translation via page
#          tables. Supports TLB simulation, multi-level page
#          tables, and detailed per-step trace output.
# ============================================================

from config import DEFAULT_PAGE_SIZE
from utils import validate_positive_int, validate_page_size, validate_page_table


# ---------------------------------------------------------------------------
# Core Translation
# ---------------------------------------------------------------------------

def translate_address(logical_address, page_size, page_table):
    """
    Translate a single logical address to a physical address.

    The translation follows the standard two-step process:
      1. Extract page number and offset from the logical address.
      2. Look up the frame number in the page table.
      3. Compute: physical_address = frame_number * page_size + offset

    Args:
        logical_address (int): The logical address to translate (>= 0).
        page_size (int):       Size of each page/frame in bytes (power of 2).
        page_table (dict):     {page_number (int): frame_number (int)}

    Returns:
        dict: {
            "logical_address":  int,
            "page_number":      int,
            "offset":           int,
            "frame_number":     int | None,
            "physical_address": int | None,
            "fault":            bool,   # True if page not in table
            "error":            str | None
        }
    """
    logical_address = validate_positive_int(logical_address, "Logical address") if logical_address != 0 \
        else 0  # allow address 0

    page_number = logical_address // page_size
    offset      = logical_address %  page_size

    if page_number not in page_table:
        return {
            "logical_address":  logical_address,
            "page_number":      page_number,
            "offset":           offset,
            "frame_number":     None,
            "physical_address": None,
            "fault":            True,
            "error":            f"Page {page_number} not found in page table — page fault."
        }

    frame_number     = page_table[page_number]
    physical_address = frame_number * page_size + offset

    return {
        "logical_address":  logical_address,
        "page_number":      page_number,
        "offset":           offset,
        "frame_number":     frame_number,
        "physical_address": physical_address,
        "fault":            False,
        "error":            None
    }


def translate_batch(logical_addresses, page_size, page_table):
    """
    Translate a list of logical addresses in one call.

    Args:
        logical_addresses (list[int]): Addresses to translate.
        page_size (int):               Page/frame size in bytes.
        page_table (dict):             {page_number: frame_number}

    Returns:
        list[dict]: One result dict per address (see translate_address).
    """
    if not isinstance(logical_addresses, list) or len(logical_addresses) == 0:
        raise ValueError("logical_addresses must be a non-empty list of integers.")

    return [translate_address(addr, page_size, page_table) for addr in logical_addresses]


# ---------------------------------------------------------------------------
# Page Table Builder
# ---------------------------------------------------------------------------

def build_page_table(num_pages, num_frames, strategy="sequential"):
    """
    Automatically build a page table for simulation/demo purposes.

    Strategies:
      - "sequential": page 0 → frame 0, page 1 → frame 1, … (up to num_frames)
      - "scatter":    pages mapped to frames in reverse order

    Args:
        num_pages  (int): Total number of pages in the logical address space.
        num_frames (int): Total number of physical frames available.
        strategy   (str): Mapping strategy ("sequential" or "scatter").

    Returns:
        dict: {page_number (int): frame_number (int)} for all valid mappings.
              Pages beyond num_frames are left unmapped (will cause faults).
    """
    num_pages  = validate_positive_int(num_pages,  "Number of pages")
    num_frames = validate_positive_int(num_frames, "Number of frames")

    valid_strategies = ("sequential", "scatter")
    if strategy not in valid_strategies:
        raise ValueError(f"strategy must be one of {valid_strategies}, got: '{strategy}'")

    table = {}
    mappable = min(num_pages, num_frames)

    if strategy == "sequential":
        for i in range(mappable):
            table[i] = i
    elif strategy == "scatter":
        for i in range(mappable):
            table[i] = num_frames - 1 - i

    return table


# ---------------------------------------------------------------------------
# TLB (Translation Lookaside Buffer) Simulation
# ---------------------------------------------------------------------------

class TLBCache:
    """
    A simple direct-mapped TLB simulation.

    The TLB is a small, fast cache of recent page-to-frame mappings.
    On each lookup:
      - HIT  → frame returned immediately (fast path)
      - MISS → page table consulted, entry loaded into TLB (may evict LRU)

    Attributes:
        capacity  (int):        Maximum TLB entries.
        _cache    (dict):       {page_number: frame_number}
        _order    (list):       Insertion order for LRU eviction.
        hits      (int):        Running hit counter.
        misses    (int):        Running miss counter.
    """

    def __init__(self, capacity=4):
        capacity = validate_positive_int(capacity, "TLB capacity")
        self.capacity = capacity
        self._cache   = {}   # page → frame
        self._order   = []   # LRU order (oldest first)
        self.hits     = 0
        self.misses   = 0

    # ------------------------------------------------------------------
    def lookup(self, page_number, page_table):
        """
        Look up a page in the TLB, falling back to the page table on a miss.

        Args:
            page_number (int): Page to look up.
            page_table  (dict): Full page table for miss handling.

        Returns:
            dict: {
                "page_number": int,
                "frame_number": int | None,
                "tlb_hit": bool,
                "fault": bool
            }
        """
        if page_number in self._cache:
            self.hits += 1
            # Refresh LRU position
            self._order.remove(page_number)
            self._order.append(page_number)
            return {
                "page_number":  page_number,
                "frame_number": self._cache[page_number],
                "tlb_hit":      True,
                "fault":        False
            }

        # TLB miss — consult page table
        self.misses += 1
        if page_number not in page_table:
            return {
                "page_number":  page_number,
                "frame_number": None,
                "tlb_hit":      False,
                "fault":        True
            }

        frame_number = page_table[page_number]
        self._load(page_number, frame_number)

        return {
            "page_number":  page_number,
            "frame_number": frame_number,
            "tlb_hit":      False,
            "fault":        False
        }

    # ------------------------------------------------------------------
    def _load(self, page_number, frame_number):
        """Load an entry into the TLB, evicting LRU if at capacity."""
        if len(self._cache) >= self.capacity:
            evict = self._order.pop(0)
            del self._cache[evict]

        self._cache[page_number] = frame_number
        self._order.append(page_number)

    # ------------------------------------------------------------------
    def flush(self):
        """Clear the TLB (context switch / process termination)."""
        self._cache.clear()
        self._order.clear()

    # ------------------------------------------------------------------
    @property
    def hit_rate(self):
        """TLB hit rate as a float (0.0–1.0). Returns 0 if no accesses yet."""
        total = self.hits + self.misses
        return round(self.hits / total, 4) if total > 0 else 0.0

    # ------------------------------------------------------------------
    def stats(self):
        """Return a summary dict of TLB performance metrics."""
        return {
            "hits":     self.hits,
            "misses":   self.misses,
            "hit_rate": self.hit_rate,
            "capacity": self.capacity,
            "entries":  dict(self._cache)
        }


# ---------------------------------------------------------------------------
# Full Simulation (address batch + TLB)
# ---------------------------------------------------------------------------

def run_paging_simulation(logical_addresses, page_size, page_table, tlb_capacity=4):
    """
    Run a full paging simulation over a list of logical addresses,
    including TLB lookups, address translation, and fault detection.

    Args:
        logical_addresses (list[int]): Ordered list of logical addresses.
        page_size         (int):       Page size in bytes (power of 2).
        page_table        (dict):      {page_number: frame_number}
        tlb_capacity      (int):       Number of TLB entries.

    Returns:
        dict: {
            "page_size":    int,
            "steps":        list[dict],   # one entry per address
            "faults":       int,
            "tlb_stats":    dict
        }

    Each step dict contains:
        logical_address, page_number, offset, frame_number,
        physical_address, tlb_hit, fault, error
    """
    # --- Validate inputs ---
    page_size  = validate_page_size(page_size)
    page_table = validate_page_table(page_table)

    if not isinstance(logical_addresses, list) or len(logical_addresses) == 0:
        raise ValueError("logical_addresses must be a non-empty list.")

    tlb    = TLBCache(capacity=tlb_capacity)
    steps  = []
    faults = 0

    for addr in logical_addresses:
        try:
            addr = int(addr)
        except (TypeError, ValueError):
            raise ValueError(f"Invalid logical address: '{addr}'. Must be an integer.")

        if addr < 0:
            raise ValueError(f"Logical address must be non-negative, got: {addr}")

        page_number = addr // page_size
        offset      = addr %  page_size

        tlb_result = tlb.lookup(page_number, page_table)

        if tlb_result["fault"]:
            faults += 1
            steps.append({
                "logical_address":  addr,
                "page_number":      page_number,
                "offset":           offset,
                "frame_number":     None,
                "physical_address": None,
                "tlb_hit":          False,
                "fault":            True,
                "error":            f"Page fault: page {page_number} not in page table."
            })
        else:
            frame_number     = tlb_result["frame_number"]
            physical_address = frame_number * page_size + offset
            steps.append({
                "logical_address":  addr,
                "page_number":      page_number,
                "offset":           offset,
                "frame_number":     frame_number,
                "physical_address": physical_address,
                "tlb_hit":          tlb_result["tlb_hit"],
                "fault":            False,
                "error":            None
            })

    return {
        "page_size":  page_size,
        "steps":      steps,
        "faults":     faults,
        "tlb_stats":  tlb.stats()
    }
