"""
Virtual Memory Simulator Engine (T1 - Core Infrastructure)

This module provides BASE components for simulating virtual memory management:
- PageTable: mapping between virtual pages and physical frames
- FramePool: physical frame allocation/deallocation
- Address translation utilities
- Page fault detection

NOTE: Page replacement algorithms (FIFO, LRU, Optimal) are in separate modules:
- core/fifo.py (T2)
- core/lru.py (T3)
- core/optimal.py (T4)
"""

from __future__ import annotations
from typing import Optional, Dict, List, Tuple


class PageTable:
    """
    Manages the mapping between virtual pages and physical frames.
    
    The page table maintains a dictionary that maps virtual page numbers
    to physical frame numbers, enabling address translation in a virtual
    memory system.
    """
    
    def __init__(self) -> None:
        """Initialize an empty page table."""
        self._mappings: Dict[int, int] = {}
    
    def map_page(self, virtual: int, physical: int) -> None:
        """
        Create a mapping from a virtual page to a physical frame.
        
        Args:
            virtual: The virtual page number to map.
            physical: The physical frame number to map to.
        
        Raises:
            ValueError: If virtual or physical page numbers are negative.
        """
        if virtual < 0 or physical < 0:
            raise ValueError("Page and frame numbers must be non-negative")
        self._mappings[virtual] = physical
    
    def lookup(self, virtual: int) -> Optional[int]:
        """
        Look up the physical frame for a given virtual page.
        
        Args:
            virtual: The virtual page number to look up.
        
        Returns:
            The physical frame number if mapped, None otherwise.
        """
        return self._mappings.get(virtual)
    
    def is_loaded(self, page: int) -> bool:
        """
        Check if a virtual page is currently loaded in memory.
        
        Args:
            page: The virtual page number to check.
        
        Returns:
            True if the page is mapped to a physical frame, False otherwise.
        """
        return page in self._mappings
    
    def unmap_page(self, virtual: int) -> Optional[int]:
        """
        Remove the mapping for a virtual page.
        
        Args:
            virtual: The virtual page number to unmap.
        
        Returns:
            The physical frame that was mapped, or None if not mapped.
        """
        return self._mappings.pop(virtual, None)
    
    def get_all_mappings(self) -> Dict[int, int]:
        """
        Get a copy of all current page mappings.
        
        Returns:
            Dictionary of virtual page to physical frame mappings.
        """
        return self._mappings.copy()


class FramePool:
    """
    Manages a pool of physical memory frames.
    
    The frame pool tracks which frames are free and which are allocated,
    providing allocation and deallocation services for the memory manager.
    """
    
    def __init__(self, total_frames: int) -> None:
        """
        Initialize the frame pool with a specified number of frames.
        
        Args:
            total_frames: The total number of physical frames available.
        
        Raises:
            ValueError: If total_frames is not positive.
        """
        if total_frames <= 0:
            raise ValueError("Total frames must be positive")
        self._total_frames: int = total_frames
        self._free_frames: set[int] = set(range(total_frames))
        self._allocated_frames: set[int] = set()
    
    def allocate(self) -> Optional[int]:
        """
        Allocate a free frame from the pool.
        
        Returns:
            The frame number of the allocated frame, or None if no frames available.
        """
        if not self._free_frames:
            return None
        frame = min(self._free_frames)
        self._free_frames.remove(frame)
        self._allocated_frames.add(frame)
        return frame
    
    def free(self, frame: int) -> bool:
        """
        Return a frame to the free pool.
        
        Args:
            frame: The frame number to free.
        
        Returns:
            True if the frame was successfully freed, False if it wasn't allocated.
        
        Raises:
            ValueError: If frame number is out of valid range.
        """
        if frame < 0 or frame >= self._total_frames:
            raise ValueError(f"Frame {frame} is out of valid range [0, {self._total_frames})")
        if frame not in self._allocated_frames:
            return False
        self._allocated_frames.remove(frame)
        self._free_frames.add(frame)
        return True
    
    def get_free_count(self) -> int:
        """
        Get the number of free frames available.
        
        Returns:
            The count of unallocated frames.
        """
        return len(self._free_frames)
    
    def get_all_frames(self) -> List[Optional[int]]:
        """
        Get the state of all frames in the pool.
        
        Returns:
            List where index is frame number and value is the frame number
            if allocated, None if free.
        """
        return [
            frame if frame in self._allocated_frames else None
            for frame in range(self._total_frames)
        ]
    
    def is_full(self) -> bool:
        """
        Check if all frames are allocated.
        
        Returns:
            True if no free frames remain, False otherwise.
        """
        return len(self._free_frames) == 0


def translate_address(virtual_address: int, page_size: int) -> Tuple[int, int]:
    """
    Translate a virtual address into page number and offset.
    
    Args:
        virtual_address: The virtual memory address to translate.
        page_size: The size of each page in bytes.
    
    Returns:
        A tuple of (page_number, offset).
    
    Raises:
        ValueError: If virtual_address is negative or page_size is not positive.
    
    Example:
        >>> translate_address(4096, 4096)
        (1, 0)
        >>> translate_address(5000, 4096)
        (1, 904)
    """
    if virtual_address < 0:
        raise ValueError("Virtual address must be non-negative")
    if page_size <= 0:
        raise ValueError("Page size must be positive")
    
    page_number = virtual_address // page_size
    offset = virtual_address % page_size
    return (page_number, offset)


def detect_page_fault(page_number: int, page_table: PageTable) -> bool:
    """
    Detect whether accessing a page would cause a page fault.
    
    A page fault occurs when the requested page is not currently
    loaded in physical memory.
    
    Args:
        page_number: The virtual page number being accessed.
        page_table: The PageTable instance to check against.
    
    Returns:
        True if a page fault would occur (page not loaded),
        False if the page is already in memory.
    """
    return not page_table.is_loaded(page_number)

