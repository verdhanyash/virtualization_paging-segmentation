# ============================================================
# Module 1 — Config & Constants
# Purpose: Shared constants used across all backend modules
# ============================================================

# --- Default Simulation Parameters ---
DEFAULT_FRAMES = 3
DEFAULT_PAGE_SIZE = 512
DEFAULT_MEMORY_SIZE = 4096

# --- Validation Limits ---
MAX_REF_STRING_LENGTH = 50
MAX_FRAMES = 20
MAX_PAGE_SIZE = 4096
MAX_MEMORY_SIZE = 65536
MAX_SEGMENTS = 10
MAX_MEMORY_BLOCKS = 20
MAX_PROCESS_REQUESTS = 20

# --- Algorithm Choices ---
ALGORITHM_LRU = "lru"
ALGORITHM_OPTIMAL = "optimal"
ALGORITHM_BOTH = "both"
VALID_ALGORITHMS = [ALGORITHM_LRU, ALGORITHM_OPTIMAL, ALGORITHM_BOTH]

# --- Flask Server Config ---
HOST = "0.0.0.0"
PORT = 5000
DEBUG = True

# --- CORS Config ---
CORS_ORIGINS = "*"
