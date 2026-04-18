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
        table = SegmentTable(4096, block_size=16)
        seg = table.add_segment("code", 200)
        assert seg.base == 0
        assert seg.limit == 200
        assert seg.allocated_size == 208  # ceil(200/16)*16

    def test_two_segments_adjacent(self):
        table = SegmentTable(4096, block_size=16)
        s1 = table.add_segment("A", 200)
        s2 = table.add_segment("B", 300)
        assert s2.base == s1.end_address()

    def test_duplicate_name_raises(self):
        table = SegmentTable(4096, block_size=16)
        table.add_segment("code", 100)
        with pytest.raises(ValueError, match="already exists"):
            table.add_segment("code", 100)

    def test_invalid_size_raises(self):
        table = SegmentTable(4096, block_size=16)
        with pytest.raises(ValueError):
            table.add_segment("bad", 0)

    def test_no_space_raises(self):
        table = SegmentTable(100, block_size=16)
        table.add_segment("big", 96)  # takes 96 bytes
        with pytest.raises(ValueError, match="no single hole fits"):
            table.add_segment("too_big", 50)




# ─────────────────────────────────────────────────────────────
# SegmentTable — Address Translation
# ─────────────────────────────────────────────────────────────

class TestTranslation:
    def test_valid_translation(self):
        table = SegmentTable(4096, block_size=16)
        table.add_segment("code", 200)  # base=0, limit=200
        assert table.translate("code", 0) == 0
        assert table.translate("code", 50) == 50
        assert table.translate("code", 199) == 199

    def test_offset_exceeds_limit(self):
        table = SegmentTable(4096, block_size=16)
        table.add_segment("code", 200)
        with pytest.raises(SegmentFaultError, match="SEGMENTATION FAULT"):
            table.translate("code", 200)

    def test_negative_offset(self):
        table = SegmentTable(4096, block_size=16)
        table.add_segment("code", 200)
        with pytest.raises(SegmentFaultError, match="non-negative"):
            table.translate("code", -1)

    def test_nonexistent_segment(self):
        table = SegmentTable(4096, block_size=16)
        with pytest.raises(SegmentFaultError, match="does not exist"):
            table.translate("ghost", 0)

    def test_swapped_segment(self):
        table = SegmentTable(4096, block_size=16)
        seg = table.add_segment("code", 200)
        seg.status = "swapped"
        with pytest.raises(SegmentFaultError, match="swapped out"):
            table.translate("code", 0)

    def test_translation_with_nonzero_base(self):
        table = SegmentTable(4096, block_size=16)
        table.add_segment("A", 100)     # base=0
        table.add_segment("B", 200)     # base=112 (aligned)
        addr = table.translate("B", 10)
        assert addr == 112 + 10


# ─────────────────────────────────────────────────────────────
# SegmentTable — Deallocation
# ─────────────────────────────────────────────────────────────

class TestDeallocation:
    def test_free_creates_hole(self):
        table = SegmentTable(4096, block_size=16)
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
        table = SegmentTable(4096, block_size=16)
        with pytest.raises(ValueError, match="not found"):
            table.free_segment("ghost")

    def test_reuse_freed_space(self):
        table = SegmentTable(4096, block_size=16)
        table.add_segment("A", 200)
        table.add_segment("B", 300)
        table.free_segment("A")

        # New segment should reuse A's old space
        seg = table.add_segment("C", 100)
        assert seg.base == 0


# ─────────────────────────────────────────────────────────────
# SegmentTable — Fragmentation Stats
# ─────────────────────────────────────────────────────────────

class TestFragmentation:
    def test_internal_fragmentation(self):
        table = SegmentTable(4096, block_size=16)
        table.add_segment("A", 200)  # alloc=208, internal=8
        table.add_segment("B", 100)  # alloc=112, internal=12
        stats = table.get_fragmentation_stats()
        assert stats["internal_frag"] == 20  # 8 + 12

    def test_external_fragmentation(self):
        table = SegmentTable(4096, block_size=16)
        table.add_segment("A", 200)  # [0, 208)
        table.add_segment("B", 300)  # [208, 512)  alloc=304
        table.add_segment("C", 100)  # [512, 624)
        table.free_segment("B")      # hole at [208, 512) = 304 bytes

        stats = table.get_fragmentation_stats()
        assert stats["external_frag"] == 304

    def test_no_external_frag_when_contiguous(self):
        table = SegmentTable(4096, block_size=16)
        table.add_segment("A", 200)
        table.add_segment("B", 300)
        stats = table.get_fragmentation_stats()
        assert stats["external_frag"] == 0

    def test_empty_table_stats(self):
        table = SegmentTable(4096, block_size=16)
        stats = table.get_fragmentation_stats()
        assert stats["used"] == 0
        assert stats["total_free"] == 4096

    def test_utilization(self):
        table = SegmentTable(1000, block_size=10)
        table.add_segment("A", 500)  # alloc=500
        stats = table.get_fragmentation_stats()
        assert stats["utilization"] == 50.0


# ─────────────────────────────────────────────────────────────
# SegmentTable — Compaction
# ─────────────────────────────────────────────────────────────

class TestCompaction:
    def test_compaction_removes_holes(self):
        table = SegmentTable(4096, block_size=16)
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
        table = SegmentTable(4096, block_size=16)
        table.add_segment("A", 128)   # [0, 128)
        table.add_segment("B", 128)   # [128, 256)
        table.add_segment("C", 128)   # [256, 384)
        table.free_segment("A")       # hole at [0, 128)

        table.compact()

        segs = table.get_segments()
        assert segs["B"]["base"] == 0
        assert segs["C"]["base"] == 128

    def test_compaction_no_op_if_no_holes(self):
        table = SegmentTable(4096, block_size=16)
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
        snapshots = simulate_fragmentation(ops)
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



# ─────────────────────────────────────────────────────────────
# Memory Map
# ─────────────────────────────────────────────────────────────

class TestMemoryMap:
    def test_memory_map_covers_full_space(self):
        table = SegmentTable(4096, block_size=16)
        table.add_segment("A", 200)
        table.add_segment("B", 300)

        mem_map = table.get_memory_map()
        total_size = sum(block["size"] for block in mem_map)
        assert total_size == 4096

    def test_memory_map_shows_holes(self):
        table = SegmentTable(4096, block_size=16)
        table.add_segment("A", 200)
        table.add_segment("B", 300)
        table.free_segment("A")

        mem_map = table.get_memory_map()
        types = [b["type"] for b in mem_map]
        assert "hole" in types
