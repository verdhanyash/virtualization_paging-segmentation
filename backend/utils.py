# ============================================================
# Module 2 — Validation Utilities
# Purpose: Reusable input validation functions used by all
#          backend modules. Each function raises ValueError
#          with a clear message on invalid input.
# ============================================================

from config import (
    MAX_REF_STRING_LENGTH,
    MAX_FRAMES,
    MAX_PAGE_SIZE,
    MAX_MEMORY_SIZE,
    MAX_SEGMENTS,
    MAX_MEMORY_BLOCKS,
    MAX_PROCESS_REQUESTS,
    VALID_ALGORITHMS,
)


def validate_positive_int(value, name):
    """
    Ensure the value is a positive integer.

    Args:
        value: The value to validate.
        name: Human-readable name for error messages.

    Returns:
        int: The validated integer.

    Raises:
        ValueError: If value is not a positive integer.
    """
    try:
        result = int(value)
    except (TypeError, ValueError):
        raise ValueError(f"{name} must be a valid integer, got: {value}")

    if result <= 0:
        raise ValueError(f"{name} must be a positive integer, got: {result}")

    return result


def validate_non_negative_int(value, name):
    """
    Ensure the value is a non-negative integer (>= 0).

    Args:
        value: The value to validate.
        name: Human-readable name for error messages.

    Returns:
        int: The validated integer.

    Raises:
        ValueError: If value is not a non-negative integer.
    """
    try:
        result = int(value)
    except (TypeError, ValueError):
        raise ValueError(f"{name} must be a valid integer, got: {value}")

    if result < 0:
        raise ValueError(f"{name} must be non-negative, got: {result}")

    return result


def validate_ref_string(data):
    """
    Validate a page reference string.

    Accepts either:
      - A list of integers: [7, 0, 1, 2, 0, 3]
      - A comma/space separated string: "7, 0, 1, 2, 0, 3"

    Args:
        data: The reference string input.

    Returns:
        list[int]: Validated list of non-negative integers.

    Raises:
        ValueError: If input is empty, too long, or contains invalid values.
    """
    if isinstance(data, str):
        # Split by commas or spaces
        data = data.replace(",", " ").split()

    if not isinstance(data, list) or len(data) == 0:
        raise ValueError("Reference string must be a non-empty list of integers.")

    if len(data) > MAX_REF_STRING_LENGTH:
        raise ValueError(
            f"Reference string too long. Maximum {MAX_REF_STRING_LENGTH} pages allowed, got {len(data)}."
        )

    result = []
    for i, item in enumerate(data):
        try:
            page = int(item)
        except (TypeError, ValueError):
            raise ValueError(
                f"Invalid page at position {i + 1}: '{item}'. Must be an integer."
            )
        if page < 0:
            raise ValueError(
                f"Invalid page at position {i + 1}: {page}. Pages must be non-negative."
            )
        result.append(page)

    return result


def validate_num_frames(value):
    """
    Validate the number of memory frames.

    Args:
        value: The number of frames.

    Returns:
        int: Validated frame count (1 to MAX_FRAMES).

    Raises:
        ValueError: If value is out of range.
    """
    frames = validate_positive_int(value, "Number of frames")

    if frames > MAX_FRAMES:
        raise ValueError(
            f"Number of frames must be at most {MAX_FRAMES}, got: {frames}"
        )

    return frames


def validate_page_size(value):
    """
    Validate the page size.

    Args:
        value: The page size.

    Returns:
        int: Validated page size (must be a power of 2, up to MAX_PAGE_SIZE).

    Raises:
        ValueError: If value is invalid or not a power of 2.
    """
    size = validate_positive_int(value, "Page size")

    if size > MAX_PAGE_SIZE:
        raise ValueError(f"Page size must be at most {MAX_PAGE_SIZE}, got: {size}")

    # Check power of 2
    if size & (size - 1) != 0:
        raise ValueError(f"Page size must be a power of 2, got: {size}")

    return size


def validate_page_table(table):
    """
    Validate a page table mapping (page number → frame number).

    Accepts either:
      - A dict: {"0": 5, "1": 6, "2": 1}
      - A list of tuples: [(0, 5), (1, 6), (2, 1)]

    Args:
        table: The page table data.

    Returns:
        dict[int, int]: Validated page table {page_number: frame_number}.

    Raises:
        ValueError: If table is empty or contains invalid entries.
    """
    if isinstance(table, dict):
        entries = table.items()
    elif isinstance(table, list):
        entries = table
    else:
        raise ValueError("Page table must be a dictionary or list of (page, frame) pairs.")

    if not entries:
        raise ValueError("Page table must have at least one entry.")

    result = {}
    for page, frame in entries:
        page_num = validate_non_negative_int(page, "Page number")
        frame_num = validate_non_negative_int(frame, "Frame number")
        result[page_num] = frame_num

    return result


def validate_segments(segments):
    """
    Validate a list of memory segment definitions.

    Each segment must have: name (str), base (int >= 0), limit (int > 0).

    Args:
        segments: List of segment dicts [{"name": "code", "base": 0, "limit": 1000}, ...]

    Returns:
        list[dict]: Validated list of segment dictionaries.

    Raises:
        ValueError: If segments are invalid.
    """
    if not isinstance(segments, list) or len(segments) == 0:
        raise ValueError("At least one segment must be defined.")

    if len(segments) > MAX_SEGMENTS:
        raise ValueError(
            f"Too many segments. Maximum {MAX_SEGMENTS} allowed, got {len(segments)}."
        )

    result = []
    names_seen = set()

    for i, seg in enumerate(segments):
        if not isinstance(seg, dict):
            raise ValueError(f"Segment {i + 1} must be a dictionary.")

        name = seg.get("name", "").strip()
        if not name:
            raise ValueError(f"Segment {i + 1} must have a non-empty name.")

        if name.lower() in names_seen:
            raise ValueError(f"Duplicate segment name: '{name}'.")
        names_seen.add(name.lower())

        base = validate_non_negative_int(seg.get("base"), f"Segment '{name}' base")
        limit = validate_positive_int(seg.get("limit"), f"Segment '{name}' limit")

        result.append({"name": name, "base": base, "limit": limit})

    return result


def validate_algorithm(value):
    """
    Validate the algorithm selection.

    Args:
        value: Algorithm string ("lru", "optimal", or "both").

    Returns:
        str: Validated algorithm name (lowercase).

    Raises:
        ValueError: If algorithm is not recognized.
    """
    if not isinstance(value, str):
        raise ValueError(f"Algorithm must be a string, got: {type(value).__name__}")

    algo = value.strip().lower()

    if algo not in VALID_ALGORITHMS:
        raise ValueError(
            f"Invalid algorithm: '{algo}'. Must be one of: {', '.join(VALID_ALGORITHMS)}"
        )

    return algo


def validate_memory_blocks(blocks):
    """
    Validate memory block sizes for fragmentation simulation.

    Args:
        blocks: List of block sizes (positive integers).

    Returns:
        list[int]: Validated list of block sizes.

    Raises:
        ValueError: If blocks are invalid.
    """
    if not isinstance(blocks, list) or len(blocks) == 0:
        raise ValueError("At least one memory block must be defined.")

    if len(blocks) > MAX_MEMORY_BLOCKS:
        raise ValueError(
            f"Too many memory blocks. Maximum {MAX_MEMORY_BLOCKS} allowed, got {len(blocks)}."
        )

    result = []
    for i, block in enumerate(blocks):
        size = validate_positive_int(block, f"Memory block {i + 1}")
        result.append(size)

    return result


def validate_process_requests(requests):
    """
    Validate process memory request sizes for fragmentation simulation.

    Args:
        requests: List of process request sizes (positive integers).

    Returns:
        list[int]: Validated list of request sizes.

    Raises:
        ValueError: If requests are invalid.
    """
    if not isinstance(requests, list) or len(requests) == 0:
        raise ValueError("At least one process request must be defined.")

    if len(requests) > MAX_PROCESS_REQUESTS:
        raise ValueError(
            f"Too many process requests. Maximum {MAX_PROCESS_REQUESTS} allowed, got {len(requests)}."
        )

    result = []
    for i, req in enumerate(requests):
        size = validate_positive_int(req, f"Process request {i + 1}")
        result.append(size)

    return result
