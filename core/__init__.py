"""Core virtual memory simulation module."""
from .engine import PageTable, FramePool, translate_address, detect_page_fault

__all__ = ["PageTable", "FramePool", "translate_address", "detect_page_fault"]
