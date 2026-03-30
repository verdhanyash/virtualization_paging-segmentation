# core/segmentation.py — Segmentation & Fragmentation Simulator (T5)
#
# Simulates segmented memory management:
#   - Variable-size segments (code, stack, heap, data, etc.)
#   - 4 allocation strategies: First-Fit, Best-Fit, Worst-Fit, Next-Fit
#   - Address translation with bounds checking (offset < limit)
#   - Internal fragmentation (from block-aligned allocation)
#   - External fragmentation (scattered holes between segments)
#   - Deallocation (free segments, create holes)
#   - Compaction (defragment: slide segments left, merge holes)
#
# Memory Model:
#   Total memory (default 4096 bytes) is one contiguous block.
#   Segments are allocated with block alignment (default 16 bytes),
#   meaning a request for 200 bytes actually reserves 208 bytes
#   (ceil(200/16) * 16). The extra 8 bytes = internal fragmentation.
#
# Usage:
#   table = SegmentTable(total_memory=4096, strategy="best_fit")
#   table.add_segment("code", 200)
#   table.add_segment("stack", 500)
#   addr = table.translate("code", 50)   # → 50
#   table.free_segment("code")           # creates hole at [0, 208)
#   table.compact()                      # slides stack to base=0

from __future__ import annotations
import math
from typing import Dict, List, Optional


# ─────────────────────────────────────────────────────────────
# Custom Exception
# ─────────────────────────────────────────────────────────────

class SegmentFaultError(Exception):
    """
    Raised when:
      - Accessing a segment that doesn't exist
      - Accessing a segment that is swapped out
      - Offset exceeds segment limit (out of bounds)

    This is the programmatic equivalent of "Segmentation fault (core dumped)".
    """
    pass


# ─────────────────────────────────────────────────────────────
# Segment Data Class
# ─────────────────────────────────────────────────────────────

class Segment:
    """
    Represents one memory segment.

    Attributes:
        name:           Logical name ("code", "stack", "heap", etc.)
        base:           Starting physical address in memory
        limit:          Size actually requested by the program (bytes)
        allocated_size: Size reserved in memory (>= limit, block-aligned)
        status:         "loaded" (in RAM) or "swapped" (on disk)

    Internal fragmentation = allocated_size - limit
    Example: request 200 bytes, block_size=16 → allocated=208, internal_frag=8
    """

    def __init__(self, name: str, base: int, limit: int,
                 allocated_size: int) -> None:
        self.name = name
        self.base = base
        self.limit = limit
        self.allocated_size = allocated_size
        self.status = "loaded"

    def internal_fragmentation(self) -> int:
        """Bytes wasted inside this segment (allocated - requested)."""
        return self.allocated_size - self.limit

    def end_address(self) -> int:
        """First address AFTER this segment (base + allocated_size)."""
        return self.base + self.allocated_size

    def to_dict(self) -> Dict:
        """Serialize segment to a dictionary."""
        return {
            "name": self.name,
            "base": self.base,
            "limit": self.limit,
            "allocated_size": self.allocated_size,
            "internal_frag": self.internal_fragmentation(),
            "status": self.status,
        }

    def __repr__(self) -> str:
        return (
            f"Segment(name={self.name!r}, base={self.base}, "
            f"limit={self.limit}, alloc={self.allocated_size}, "
            f"status={self.status!r})"
        )


# ─────────────────────────────────────────────────────────────
# Segment Table (Main Engine)
# ─────────────────────────────────────────────────────────────

class SegmentTable:
    """
    Manages segmented memory with configurable allocation strategy.

    Strategies:
        first_fit — Scan left→right, use the FIRST hole that fits.
                    Fast. Tends to fragment the beginning of memory.

        best_fit  — Use the SMALLEST hole that fits.
                    Minimizes leftover per allocation.
                    Creates tiny, often unusable holes.

        worst_fit — Use the LARGEST hole that fits.
                    Leaves big leftover holes (more reusable).
                    Wastes space if large allocations come later.

        next_fit  — Like first_fit, but starts scanning from where
                    the last allocation ended (wraps around).
                    Spreads allocations across memory.

    Args:
        total_memory: Total physical memory in bytes (default 4096).
        strategy:     One of "first_fit", "best_fit", "worst_fit", "next_fit".
        block_size:   Alignment granularity in bytes (default 16).
                      All allocations are rounded up to multiples of this.
    """

    VALID_STRATEGIES = ("first_fit", "best_fit", "worst_fit", "next_fit")

    def __init__(
        self,
        total_memory: int = 4096,
        strategy: str = "first_fit",
        block_size: int = 16,
    ) -> None:
        if total_memory <= 0:
            raise ValueError("Total memory must be positive")
        if strategy not in self.VALID_STRATEGIES:
            raise ValueError(
                f"Strategy must be one of {self.VALID_STRATEGIES}, "
                f"got '{strategy}'"
            )
        if block_size <= 0:
            raise ValueError("Block size must be positive")

        self._total_memory = total_memory
        self._strategy = strategy
        self._block_size = block_size
        self._segments: Dict[str, Segment] = {}

        # next_fit tracks where the last allocation ended
        self._next_fit_cursor = 0

    # ── Properties ────────────────────────────────────────────

    @property
    def strategy(self) -> str:
        return self._strategy

    @property
    def total_memory(self) -> int:
        return self._total_memory

    @property
    def block_size(self) -> int:
        return self._block_size

    # ── Internal Helpers ──────────────────────────────────────

    def _align(self, size: int) -> int:
        """Round size UP to next multiple of block_size.

        Example (block_size=16):
            200 → 208  (13 blocks)
            256 → 256  (exact, 16 blocks)
            1   → 16   (1 block)
        """
        return math.ceil(size / self._block_size) * self._block_size

    def _sorted_segments(self) -> List[Segment]:
        """Return segments sorted by base address (left→right in memory)."""
        return sorted(self._segments.values(), key=lambda s: s.base)

    def _get_free_holes(self) -> List[Dict]:
        """
        Find all free holes (gaps) in memory.

        Walks through memory left→right, identifies gaps between segments
        and any trailing free space at the end.

        Returns:
            List of {"base": int, "size": int} sorted by address.
        """
        holes: List[Dict] = []
        sorted_segs = self._sorted_segments()

        if not sorted_segs:
            # No segments → entire memory is one big hole
            return [{"base": 0, "size": self._total_memory}]

        # Gap before first segment?
        if sorted_segs[0].base > 0:
            holes.append({
                "base": 0,
                "size": sorted_segs[0].base,
            })

        # Gaps between consecutive segments
        for i in range(len(sorted_segs) - 1):
            current_end = sorted_segs[i].end_address()
            next_base = sorted_segs[i + 1].base
            gap = next_base - current_end
            if gap > 0:
                holes.append({"base": current_end, "size": gap})

        # Trailing free space after last segment
        last_end = sorted_segs[-1].end_address()
        trailing = self._total_memory - last_end
        if trailing > 0:
            holes.append({"base": last_end, "size": trailing})

        return holes

    def _find_hole(self, needed: int) -> Optional[Dict]:
        """
        Select a free hole using the current allocation strategy.

        Args:
            needed: Block-aligned size required.

        Returns:
            The chosen hole {"base": int, "size": int}, or None if
            no hole is large enough.
        """
        holes = self._get_free_holes()
        fitting = [h for h in holes if h["size"] >= needed]

        if not fitting:
            return None

        if self._strategy == "first_fit":
            # First hole that fits (left to right)
            return fitting[0]

        elif self._strategy == "best_fit":
            # Smallest fitting hole → minimize leftover
            return min(fitting, key=lambda h: h["size"])

        elif self._strategy == "worst_fit":
            # Largest fitting hole → maximize leftover
            return max(fitting, key=lambda h: h["size"])

        elif self._strategy == "next_fit":
            # First fitting hole at or after cursor (wrap around)
            for h in fitting:
                if h["base"] >= self._next_fit_cursor:
                    return h
            # Wrap around: take the first fitting hole from the start
            return fitting[0]

        return None  # unreachable

    # ── Public API: Allocation ────────────────────────────────

    def add_segment(self, name: str, size: int) -> Segment:
        """
        Allocate a new segment in memory.

        Steps:
          1. Round size up to block alignment (causes internal frag)
          2. Find a suitable hole using the chosen strategy
          3. Place the segment at the start of that hole

        Args:
            name: Segment identifier (must be unique).
            size: Requested size in bytes.

        Returns:
            The created Segment object.

        Raises:
            ValueError: If name exists, size invalid, or no hole fits.

        Example:
            >>> table = SegmentTable(4096, "first_fit", block_size=16)
            >>> seg = table.add_segment("code", 200)
            >>> seg.allocated_size   # 208 (rounded up to 16-byte boundary)
            208
            >>> seg.internal_fragmentation()  # 8 bytes wasted
            8
        """
        if name in self._segments:
            raise ValueError(f"Segment '{name}' already exists")
        if size <= 0:
            raise ValueError("Segment size must be positive")

        aligned = self._align(size)

        hole = self._find_hole(aligned)
        if hole is None:
            total_free = sum(h["size"] for h in self._get_free_holes())
            raise ValueError(
                f"Cannot allocate '{name}' ({size}B, aligned to {aligned}B). "
                f"Strategy={self._strategy}. "
                f"Total free={total_free}B but no single hole fits."
            )

        segment = Segment(name, hole["base"], size, aligned)
        self._segments[name] = segment

        # Advance next_fit cursor past this allocation
        if self._strategy == "next_fit":
            self._next_fit_cursor = segment.end_address()

        return segment

    # ── Public API: Deallocation ──────────────────────────────

    def free_segment(self, name: str) -> Dict:
        """
        Deallocate a segment, creating a free hole.

        The segment is removed from the table. The space it occupied
        becomes a hole that may be used by future allocations.

        Adjacent holes are NOT automatically merged — this is realistic
        because real OS segment tables track individual deallocations.
        Use compact() to merge all holes.

        Args:
            name: Name of segment to free.

        Returns:
            Dict describing what was freed:
            {
                "freed": {segment details},
                "hole_created": {"base": int, "size": int}
            }

        Raises:
            ValueError: If segment doesn't exist.
        """
        if name not in self._segments:
            raise ValueError(f"Segment '{name}' not found")

        segment = self._segments.pop(name)

        return {
            "freed": segment.to_dict(),
            "hole_created": {
                "base": segment.base,
                "size": segment.allocated_size,
            },
        }

    # ── Public API: Address Translation ───────────────────────

    def translate(self, segment_name: str, offset: int) -> int:
        """
        Translate (segment_name, offset) → physical address.

        Formula: physical = base + offset (if offset < limit)

        Args:
            segment_name: Name of the segment.
            offset: Byte offset within the segment.

        Returns:
            Physical memory address.

        Raises:
            SegmentFaultError: If segment missing, swapped, or
                              offset out of bounds.

        Example:
            >>> table.add_segment("code", 200)  # base=0
            >>> table.translate("code", 50)
            50
            >>> table.translate("code", 300)
            SegmentFaultError: Offset 300 >= limit 200
        """
        if segment_name not in self._segments:
            raise SegmentFaultError(
                f"Segment '{segment_name}' does not exist"
            )

        seg = self._segments[segment_name]

        if seg.status == "swapped":
            raise SegmentFaultError(
                f"Segment '{segment_name}' is swapped out (not in RAM)"
            )

        if offset < 0:
            raise SegmentFaultError("Offset must be non-negative")

        if offset >= seg.limit:
            raise SegmentFaultError(
                f"Offset {offset} >= limit {seg.limit} "
                f"for segment '{segment_name}' — SEGMENTATION FAULT"
            )

        return seg.base + offset

    # ── Public API: Compaction ────────────────────────────────

    def compact(self) -> Dict:
        """
        Compact memory: slide all loaded segments to the left,
        eliminating all holes between them.

        Before: [A][HOLE][B][HOLE][C][── free ──]
        After:  [A][B][C][──────── all free ────]

        All segment base addresses are updated. This is expensive
        in real systems (requires copying memory + updating pointers)
        but eliminates external fragmentation completely.

        Returns:
            {
                "moves": [{"name", "old_base", "new_base"}, ...],
                "holes_eliminated": int,
                "space_recovered": int  (bytes of external frag removed)
            }
        """
        # Count external frag before compaction
        stats_before = self.get_fragmentation_stats()
        ext_frag_before = stats_before["external_frag"]

        # Count holes between segments (not trailing free)
        sorted_segs = self._sorted_segments()
        holes_between = 0
        if len(sorted_segs) >= 2:
            for i in range(len(sorted_segs) - 1):
                gap = sorted_segs[i + 1].base - sorted_segs[i].end_address()
                if gap > 0:
                    holes_between += 1
        # Also count hole before first segment
        if sorted_segs and sorted_segs[0].base > 0:
            holes_between += 1

        # Slide all segments to the left
        moves: List[Dict] = []
        current_base = 0

        for seg in sorted_segs:
            old_base = seg.base
            if old_base != current_base:
                seg.base = current_base
                moves.append({
                    "name": seg.name,
                    "old_base": old_base,
                    "new_base": current_base,
                })
            current_base += seg.allocated_size

        # Reset next_fit cursor
        self._next_fit_cursor = current_base

        return {
            "moves": moves,
            "holes_eliminated": holes_between,
            "space_recovered": ext_frag_before,
        }

    # ── Public API: Fragmentation Stats ───────────────────────

    def get_fragmentation_stats(self) -> Dict:
        """
        Calculate current memory fragmentation statistics.

        Internal fragmentation = sum of (allocated - requested) per segment.
            Caused by block alignment. Example: request 200, get 208 → 8 wasted.

        External fragmentation = free bytes in holes BETWEEN segments.
            Caused by alloc/free patterns. Trailing free space is NOT counted
            because it's contiguous and usable.

        Returns:
            {
                "used":           total allocated bytes,
                "requested":      total requested bytes,
                "internal_frag":  bytes wasted inside segments,
                "external_frag":  bytes trapped in holes between segments,
                "total_free":     total unallocated bytes,
                "total":          total memory size,
                "utilization":    percentage of memory used (0-100)
            }
        """
        if not self._segments:
            return {
                "used": 0,
                "requested": 0,
                "internal_frag": 0,
                "external_frag": 0,
                "total_free": self._total_memory,
                "total": self._total_memory,
                "utilization": 0.0,
            }

        used = sum(s.allocated_size for s in self._segments.values())
        requested = sum(s.limit for s in self._segments.values())
        internal_frag = used - requested

        # External frag = holes BETWEEN segments (not trailing free space)
        holes = self._get_free_holes()
        sorted_segs = self._sorted_segments()
        last_end = sorted_segs[-1].end_address()

        # Holes before or between segments (not after the last segment)
        external_frag = sum(
            h["size"] for h in holes
            if h["base"] + h["size"] <= last_end
        )

        total_free = self._total_memory - used

        return {
            "used": used,
            "requested": requested,
            "internal_frag": internal_frag,
            "external_frag": external_frag,
            "total_free": total_free,
            "total": self._total_memory,
            "utilization": round(used / self._total_memory * 100, 2),
        }

    # ── Public API: Memory Map ────────────────────────────────

    def get_memory_map(self) -> List[Dict]:
        """
        Get the full memory layout as a list of blocks.

        Returns a list covering the entire address space, where each
        entry is either a segment, a hole (between segments), or
        trailing free space.

        Returns:
            [
                {"type": "segment", "name": ..., "base": ..., ...},
                {"type": "hole", "base": ..., "size": ...},
                {"type": "free", "base": ..., "size": ...},   # trailing
            ]
        """
        memory_map: List[Dict] = []
        sorted_segs = self._sorted_segments()
        position = 0

        for seg in sorted_segs:
            # Hole before this segment?
            if seg.base > position:
                memory_map.append({
                    "type": "hole",
                    "base": position,
                    "size": seg.base - position,
                })

            # The segment itself
            memory_map.append({
                "type": "segment",
                "name": seg.name,
                "base": seg.base,
                "size": seg.allocated_size,
                "requested": seg.limit,
                "internal_frag": seg.internal_fragmentation(),
                "status": seg.status,
            })
            position = seg.end_address()

        # Trailing free space
        if position < self._total_memory:
            memory_map.append({
                "type": "free",
                "base": position,
                "size": self._total_memory - position,
            })

        return memory_map

    def get_segments(self) -> Dict[str, Dict]:
        """Get all segments as {name: segment_dict}."""
        return {name: seg.to_dict() for name, seg in self._segments.items()}


# ─────────────────────────────────────────────────────────────
# Simulation Runner
# ─────────────────────────────────────────────────────────────

def simulate_fragmentation(
    operations: List[Dict],
    total_memory: int = 4096,
    strategy: str = "first_fit",
    block_size: int = 16,
) -> List[Dict]:
    """
    Run a sequence of alloc/free/compact operations and return
    a snapshot of memory state after each step.

    This is the "movie" function — it lets you see how memory
    evolves over time, how holes form, and how fragmentation grows.

    Args:
        operations: List of operation dicts:
            {"action": "alloc", "name": "code", "size": 200}
            {"action": "free", "name": "code"}
            {"action": "compact"}
        total_memory: Total memory size (default 4096).
        strategy: Allocation strategy (default "first_fit").
        block_size: Block alignment (default 16).

    Returns:
        List of snapshots, one per operation:
        {
            "step": step number (0-indexed),
            "operation": the operation dict,
            "segments": {name: segment_dict, ...},
            "memory_map": full memory layout,
            "free_holes": list of holes,
            "fragmentation": fragmentation stats,
            "error": error message or None
        }

    Example:
        >>> ops = [
        ...     {"action": "alloc", "name": "code", "size": 200},
        ...     {"action": "alloc", "name": "stack", "size": 500},
        ...     {"action": "free", "name": "code"},
        ...     {"action": "compact"},
        ... ]
        >>> snapshots = simulate_fragmentation(ops, strategy="best_fit")
        >>> for s in snapshots:
        ...     print(s["fragmentation"]["external_frag"])
        0
        0
        208     # hole left behind by freeing "code"
        0       # compaction removed the hole
    """
    table = SegmentTable(total_memory, strategy, block_size)
    snapshots: List[Dict] = []

    for step, op in enumerate(operations):
        error: Optional[str] = None

        try:
            action = op["action"]

            if action == "alloc":
                table.add_segment(op["name"], op["size"])

            elif action == "free":
                table.free_segment(op["name"])

            elif action == "compact":
                table.compact()

            else:
                error = f"Unknown action: {action!r}"

        except (ValueError, SegmentFaultError, KeyError) as exc:
            error = str(exc)

        snapshots.append({
            "step": step,
            "operation": op,
            "segments": table.get_segments(),
            "memory_map": table.get_memory_map(),
            "free_holes": table._get_free_holes(),
            "fragmentation": table.get_fragmentation_stats(),
            "error": error,
        })

    return snapshots
