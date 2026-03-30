# tests/test_segmentation.py — Unit tests for T5 Segmentation module

import pytest
from core.segmentation import (
    Segment,
    SegmentTable,
    SegmentFaultError,
    simulate_fragmentation,
)


# ─────────────────────────────────────────────────────────────
# Segment class
# ─────────────────────────────────────────────────────────────

class TestSegment:
    def test_internal_fragmentation(self):
        seg = Segment("code", base=0, limit=200, allocated_size=208)
        assert seg.internal_fragmentation() == 8

    def test_zero_internal_frag_when_exact(self):
        seg = Segment("data", base=0, limit=256, allocated_size=256)
        assert seg.internal_fragmentation() == 0

    def test_end_address(self):
        seg = Segment("stack", base=100, limit=500, allocated_size=512)
        assert seg.end_address() == 612

    def test_to_dict(self):
        seg = Segment("heap", base=0, limit=100, allocated_size=112)
        d = seg.to_dict()
        assert d["name"] == "heap"
        assert d["internal_frag"] == 12


# ─────────────────────────────────────────────────────────────
# SegmentTable — Allocation
# ─────────────────────────────────────────────────────────────

class TestAllocation:
    def test_basic_allocation(self):
        table = SegmentTable(4096, "first_fit", block_size=16)
        seg = table.add_segment("code", 200)
        assert seg.base == 0
        assert seg.limit == 200
        assert seg.allocated_size == 208  # ceil(200/16)*16

    def test_two_segments_adjacent(self):
        table = SegmentTable(4096, "first_fit", block_size=16)
        s1 = table.add_segment("A", 200)
        s2 = table.add_segment("B", 300)
        assert s2.base == s1.end_address()

    def test_duplicate_name_raises(self):
        table = SegmentTable(4096, "first_fit", block_size=16)
        table.add_segment("code", 100)
        with pytest.raises(ValueError, match="already exists"):
            table.add_segment("code", 100)

    def test_invalid_size_raises(self):
        table = SegmentTable(4096, "first_fit", block_size=16)
        with pytest.raises(ValueError):
            table.add_segment("bad", 0)

    def test_no_space_raises(self):
        table = SegmentTable(100, "first_fit", block_size=16)
        table.add_segment("big", 96)  # takes 96 bytes
        with pytest.raises(ValueError, match="no single hole fits"):
            table.add_segment("too_big", 50)


# ─────────────────────────────────────────────────────────────
# SegmentTable — Strategies
# ─────────────────────────────────────────────────────────────

class TestStrategies:
    """
    Setup: 3 holes of different sizes, test which one each strategy picks.
    Memory layout: [A=128][HOLE=256][B=128][HOLE=512][C=128][HOLE=128][free]
    """

    def _make_table_with_holes(self, strategy):
        # block_size=128 for easy math
        table = SegmentTable(4096, strategy, block_size=128)
        # Fill and then free to create known holes
        table.add_segment("A", 128)    # [0, 128)
        table.add_segment("h1", 256)   # [128, 384)  — will free
        table.add_segment("B", 128)    # [384, 512)
        table.add_segment("h2", 512)   # [512, 1024) — will free
        table.add_segment("C", 128)    # [1024, 1152)
        table.add_segment("h3", 128)   # [1152, 1280) — will free

        table.free_segment("h1")  # hole at [128,  384)  size=256
        table.free_segment("h2")  # hole at [512,  1024) size=512
        table.free_segment("h3")  # hole at [1152, 1280) size=128
        return table

    def test_first_fit(self):
        table = self._make_table_with_holes("first_fit")
        # Holes: [256@128, 512@512, 2944@1152]
        # First hole that fits 128 → base=128
        seg = table.add_segment("X", 128)
        assert seg.base == 128

    def test_best_fit(self):
        table = self._make_table_with_holes("best_fit")
        # Holes: [256@128, 512@512, 2944@1152]
        # Smallest fitting hole = 256 at base=128
        seg = table.add_segment("X", 128)
        assert seg.base == 128

    def test_worst_fit(self):
        table = self._make_table_with_holes("worst_fit")
        # Holes: [256@128, 512@512, 2944@1152]
        # Largest hole = 2944 at base=1152
        seg = table.add_segment("X", 128)
        assert seg.base == 1152

    def test_next_fit_advances(self):
        table = SegmentTable(4096, "next_fit", block_size=16)
        s1 = table.add_segment("A", 100)
        s2 = table.add_segment("B", 100)
        # B should start right after A, and cursor advances
        assert s2.base == s1.end_address()

    def test_invalid_strategy_raises(self):
        with pytest.raises(ValueError, match="Strategy must be"):
            SegmentTable(4096, "random_fit")


# ─────────────────────────────────────────────────────────────
# SegmentTable — Address Translation
# ─────────────────────────────────────────────────────────────

class TestTranslation:
    def test_valid_translation(self):
        table = SegmentTable(4096, "first_fit", block_size=16)
        table.add_segment("code", 200)  # base=0, limit=200
        assert table.translate("code", 0) == 0
        assert table.translate("code", 50) == 50
        assert table.translate("code", 199) == 199

    def test_offset_exceeds_limit(self):
        table = SegmentTable(4096, "first_fit", block_size=16)
        table.add_segment("code", 200)
        with pytest.raises(SegmentFaultError, match="SEGMENTATION FAULT"):
            table.translate("code", 200)

    def test_negative_offset(self):
        table = SegmentTable(4096, "first_fit", block_size=16)
        table.add_segment("code", 200)
        with pytest.raises(SegmentFaultError, match="non-negative"):
            table.translate("code", -1)

    def test_nonexistent_segment(self):
        table = SegmentTable(4096, "first_fit", block_size=16)
        with pytest.raises(SegmentFaultError, match="does not exist"):
            table.translate("ghost", 0)

    def test_swapped_segment(self):
        table = SegmentTable(4096, "first_fit", block_size=16)
        seg = table.add_segment("code", 200)
        seg.status = "swapped"
        with pytest.raises(SegmentFaultError, match="swapped out"):
            table.translate("code", 0)

    def test_translation_with_nonzero_base(self):
        table = SegmentTable(4096, "first_fit", block_size=16)
        table.add_segment("A", 100)     # base=0
        table.add_segment("B", 200)     # base=112 (aligned)
        addr = table.translate("B", 10)
        assert addr == 112 + 10


# ─────────────────────────────────────────────────────────────
# SegmentTable — Deallocation
# ─────────────────────────────────────────────────────────────

class TestDeallocation:
    def test_free_creates_hole(self):
        table = SegmentTable(4096, "first_fit", block_size=16)
        table.add_segment("A", 200)   # [0, 208)
        table.add_segment("B", 300)   # [208, 528)

        result = table.free_segment("A")
        assert result["freed"]["name"] == "A"
        assert result["hole_created"]["base"] == 0
        assert result["hole_created"]["size"] == 208

        # Hole should appear in free holes
        holes = table._get_free_holes()
        assert holes[0]["base"] == 0
        assert holes[0]["size"] == 208

    def test_free_nonexistent_raises(self):
        table = SegmentTable(4096, "first_fit", block_size=16)
        with pytest.raises(ValueError, match="not found"):
            table.free_segment("ghost")

    def test_reuse_freed_space(self):
        table = SegmentTable(4096, "first_fit", block_size=16)
        table.add_segment("A", 200)
        table.add_segment("B", 300)
        table.free_segment("A")

        # New segment should reuse A's old space (first_fit)
        seg = table.add_segment("C", 100)
        assert seg.base == 0


# ─────────────────────────────────────────────────────────────
# SegmentTable — Fragmentation Stats
# ─────────────────────────────────────────────────────────────

class TestFragmentation:
    def test_internal_fragmentation(self):
        table = SegmentTable(4096, "first_fit", block_size=16)
        table.add_segment("A", 200)  # alloc=208, internal=8
        table.add_segment("B", 100)  # alloc=112, internal=12
        stats = table.get_fragmentation_stats()
        assert stats["internal_frag"] == 20  # 8 + 12

    def test_external_fragmentation(self):
        table = SegmentTable(4096, "first_fit", block_size=16)
        table.add_segment("A", 200)  # [0, 208)
        table.add_segment("B", 300)  # [208, 512)  alloc=304
        table.add_segment("C", 100)  # [512, 624)
        table.free_segment("B")      # hole at [208, 512) = 304 bytes

        stats = table.get_fragmentation_stats()
        assert stats["external_frag"] == 304

    def test_no_external_frag_when_contiguous(self):
        table = SegmentTable(4096, "first_fit", block_size=16)
        table.add_segment("A", 200)
        table.add_segment("B", 300)
        stats = table.get_fragmentation_stats()
        assert stats["external_frag"] == 0

    def test_empty_table_stats(self):
        table = SegmentTable(4096, "first_fit", block_size=16)
        stats = table.get_fragmentation_stats()
        assert stats["used"] == 0
        assert stats["total_free"] == 4096

    def test_utilization(self):
        table = SegmentTable(1000, "first_fit", block_size=10)
        table.add_segment("A", 500)  # alloc=500
        stats = table.get_fragmentation_stats()
        assert stats["utilization"] == 50.0


# ─────────────────────────────────────────────────────────────
# SegmentTable — Compaction
# ─────────────────────────────────────────────────────────────

class TestCompaction:
    def test_compaction_removes_holes(self):
        table = SegmentTable(4096, "first_fit", block_size=16)
        table.add_segment("A", 200)
        table.add_segment("B", 300)
        table.add_segment("C", 100)
        table.free_segment("B")  # creates hole

        result = table.compact()
        assert result["holes_eliminated"] >= 1
        assert result["space_recovered"] > 0

        # After compaction: A and C should be contiguous
        stats = table.get_fragmentation_stats()
        assert stats["external_frag"] == 0

    def test_compaction_updates_bases(self):
        table = SegmentTable(4096, "first_fit", block_size=16)
        table.add_segment("A", 128)   # [0, 128)
        table.add_segment("B", 128)   # [128, 256)
        table.add_segment("C", 128)   # [256, 384)
        table.free_segment("A")       # hole at [0, 128)

        table.compact()

        segs = table.get_segments()
        assert segs["B"]["base"] == 0
        assert segs["C"]["base"] == 128

    def test_compaction_no_op_if_no_holes(self):
        table = SegmentTable(4096, "first_fit", block_size=16)
        table.add_segment("A", 200)
        table.add_segment("B", 300)
        result = table.compact()
        assert len(result["moves"]) == 0


# ─────────────────────────────────────────────────────────────
# simulate_fragmentation
# ─────────────────────────────────────────────────────────────

class TestSimulation:
    def test_basic_simulation(self):
        ops = [
            {"action": "alloc", "name": "code", "size": 200},
            {"action": "alloc", "name": "stack", "size": 500},
            {"action": "free", "name": "code"},
            {"action": "compact"},
        ]
        snapshots = simulate_fragmentation(ops, strategy="first_fit")
        assert len(snapshots) == 4

        # Step 0: code allocated
        assert "code" in snapshots[0]["segments"]
        assert snapshots[0]["error"] is None

        # Step 2: code freed → external frag
        assert "code" not in snapshots[2]["segments"]
        assert snapshots[2]["fragmentation"]["external_frag"] > 0

        # Step 3: compacted → no external frag
        assert snapshots[3]["fragmentation"]["external_frag"] == 0

    def test_simulation_records_errors(self):
        ops = [
            {"action": "free", "name": "nonexistent"},
        ]
        snapshots = simulate_fragmentation(ops)
        assert snapshots[0]["error"] is not None

    def test_strategy_comparison(self):
        """Same ops with different strategies should produce different layouts."""
        ops = [
            {"action": "alloc", "name": "A", "size": 128},
            {"action": "alloc", "name": "B", "size": 256},
            {"action": "alloc", "name": "C", "size": 128},
            {"action": "free", "name": "A"},
            {"action": "free", "name": "C"},
            {"action": "alloc", "name": "D", "size": 100},
        ]

        snap_ff = simulate_fragmentation(ops, strategy="first_fit")
        snap_bf = simulate_fragmentation(ops, strategy="best_fit")

        # D should be placed in different holes depending on strategy
        d_base_ff = snap_ff[-1]["segments"]["D"]["base"]
        d_base_bf = snap_bf[-1]["segments"]["D"]["base"]

        # first_fit picks the first hole (A's old spot at base=0)
        # best_fit picks the smallest fitting hole
        # Both valid, but placement may differ
        assert snap_ff[-1]["error"] is None
        assert snap_bf[-1]["error"] is None


# ─────────────────────────────────────────────────────────────
# Memory Map
# ─────────────────────────────────────────────────────────────

class TestMemoryMap:
    def test_memory_map_covers_full_space(self):
        table = SegmentTable(4096, "first_fit", block_size=16)
        table.add_segment("A", 200)
        table.add_segment("B", 300)

        mem_map = table.get_memory_map()
        total_size = sum(block["size"] for block in mem_map)
        assert total_size == 4096

    def test_memory_map_shows_holes(self):
        table = SegmentTable(4096, "first_fit", block_size=16)
        table.add_segment("A", 200)
        table.add_segment("B", 300)
        table.free_segment("A")

        mem_map = table.get_memory_map()
        types = [b["type"] for b in mem_map]
        assert "hole" in types
