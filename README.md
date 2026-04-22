# Virtual Memory Management Simulator

A comprehensive, interactive virtual memory simulator built with Flask that demonstrates core operating system memory management concepts through real-time visualization and live Windows process telemetry.

## Overview

This project simulates two fundamental OS memory management techniques:

1. **Paging** — Fixed-size page replacement using FIFO, LRU, and Optimal algorithms with step-by-step playback, frame visualization, Bélády's Anomaly detection, and demand paging simulation.

2. **Segmentation** — Variable-size segment allocation with block-aligned memory, internal/external fragmentation tracking, compaction (defragmentation), address translation with bounds checking, and trap detection.

Both modules can operate in **manual mode** (user-supplied inputs) or **live mode** (driven by real Windows process data via PowerShell telemetry).

---

## Key Features

### Paging Module
- **Three algorithms**: FIFO (First-In-First-Out), LRU (Least Recently Used), Optimal (MIN / Bélády's algorithm)
- **Step-by-step playback**: Walk through each page reference one at a time, or auto-play at configurable speed
- **Frame state visualization**: Color-coded frame boxes showing page loads, hits, faults, and evictions
- **History table**: Full reference string trace with fault/hit indicators per step
- **Demand paging panel**: Page table (Valid/Invalid bits) and backing store swap log
- **Bélády's Anomaly chart**: Runs FIFO across frame counts 1–10 and highlights anomaly points where more frames cause more faults
- **Fault timeline chart**: Bar + cumulative line chart tracking faults over time
- **Side-by-side comparison** (Overview page): Bar chart comparing fault counts across all three algorithms, plus a fault race chart

### Segmentation Module
- **Live Address Space bar**: Color-coded composition bar showing segments, holes, and free space
- **Block-level memory map**: Grid of memory blocks with hover tooltips showing base, size, internal fragmentation, and valid offset ranges. Clickable blocks prefill the address translator
- **Segment Table**: Detailed card view per segment showing process name, segment type (.text/.data/.heap/.stack), base address, limit, allocated size, internal fragmentation, max valid offset, and trap threshold
- **Free Holes table**: Lists gaps between segments with base address, size, and percentage of total memory
- **Address Translator**: Interactive logical-to-physical address translation with step-by-step breakdown (lookup → bounds check → result) and flash animation on the memory grid
- **Memory compaction**: One-click defragmentation that slides all segments left and eliminates external fragmentation
- **Operation History**: Filterable log of all alloc/free/compact/translate operations with status indicators
- **Fragmentation stats**: Real-time metrics for memory in use, available, internal fragmentation, external fragmentation, hole count, utilization %, and trap count
- **Manual mode**: Build custom operation sequences (alloc/free/compact) with a queue UI

### Live Windows Telemetry
- Reads real process data from Windows via `Get-Process` PowerShell commands
- **Paging**: Generates reference strings weighted by CPU time and working set size, simulating realistic locality patterns (temporal, spatial, and random access)
- **Segmentation**: Maps top processes by memory usage into proportional segment allocations (.text, .heap, .data, .stack), creating a realistic memory layout from your actual running processes

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.10+, Flask 3.1 |
| **Core Algorithms** | Pure Python modules (no external dependencies) |
| **Frontend** | HTML5 templates, vanilla JavaScript, CSS |
| **Charts** | Chart.js (loaded via CDN) |
| **Process Telemetry** | PowerShell `Get-Process` (Windows only) |
| **Testing** | pytest 8.3 |

---

## Project Structure

```
.
├── app.py                          # Flask application — all routes and API endpoints
├── requirements.txt                # Python dependencies (flask, gunicorn, pytest)
│
├── core/                           # Pure algorithm modules (no Flask dependency)
│   ├── __init__.py                 # Package init — re-exports engine.py classes
│   ├── engine.py                   # Base infrastructure: PageTable, FramePool,
│   │                               #   translate_address(), detect_page_fault()
│   ├── fifo.py                     # FIFO page replacement + Bélády's Anomaly detection
│   ├── lru.py                      # LRU page replacement using OrderedDict
│   ├── optimal.py                  # Optimal (MIN) page replacement with future look-ahead
│   └── segmentation.py            # Segment table, allocation, compaction, translation,
│                                   #   fragmentation stats, simulate_fragmentation()
│
├── app/
│   ├── templates/                  # Jinja2 HTML templates
│   │   ├── index.html              # Overview dashboard — side-by-side algorithm comparison
│   │   ├── fifo.html               # FIFO algorithm page
│   │   ├── lru.html                # LRU algorithm page
│   │   ├── optimal.html            # Optimal algorithm page
│   │   └── segmentation.html       # Segmentation workspace
│   │
│   └── static/
│       ├── css/
│       │   └── styles.css          # Full design system — dark theme, panels, grids,
│       │                           #   animations, memory map cells, charts
│       └── js/
│           ├── index.js            # Overview page logic — comparison charts, polling
│           ├── paging-common.js     # Shared paging logic for FIFO/LRU/Optimal pages:
│           │                       #   step playback, history table, Bélády chart,
│           │                       #   timeline chart, demand paging, process source
│           └── segmentation.js     # Segmentation page logic — memory map, segment table,
│                                   #   address translator, operation history, auto-translate
│
├── tests/                          # Unit test suite
│   ├── test_fifo.py                # FIFO algorithm correctness tests
│   ├── test_lru.py                 # LRU algorithm correctness tests
│   ├── test_optimal.py             # Optimal algorithm + victim selection tests
│   └── test_segmentation.py        # Segmentation: allocation, translation, compaction,
│                                   #   fragmentation stats, bounds checking, edge cases
│
└── scripts/
    └── get_processes.ps1           # Standalone PowerShell script for process inspection
```

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                        BROWSER (Client)                         │
│                                                                  │
│  index.html ──► index.js            fifo/lru/optimal.html       │
│  (Overview)     (comparison         ──► paging-common.js        │
│                  charts, polling)       (step playback, charts)  │
│                                                                  │
│  segmentation.html ──► segmentation.js                          │
│  (Seg workspace)       (memory map, translator, history)        │
│                                                                  │
│  styles.css ─── shared dark theme design system                 │
│  Chart.js ───── bar charts, line charts, anomaly visualization  │
└──────────┬───────────────────────────────────────────────────────┘
           │  XHR / JSON
           ▼
┌──────────────────────────────────────────────────────────────────┐
│                     FLASK SERVER (app.py)                        │
│                                                                  │
│  Page Routes:                                                   │
│    GET /              → index.html                              │
│    GET /fifo          → fifo.html                               │
│    GET /lru           → lru.html                                │
│    GET /optimal       → optimal.html                            │
│    GET /segmentation  → segmentation.html                       │
│                                                                  │
│  API Routes:                                                    │
│    GET  /api/realtime-algorithms  → paging + optional seg data  │
│    POST /api/simulate            → paging from JSON body        │
│    POST /api/segmentation        → manual segmentation ops      │
│    GET  /api/live-segmentation   → live process-driven seg      │
│                                                                  │
│  Windows Telemetry:                                             │
│    _get_windows_process_snapshot() ──► PowerShell subprocess    │
│    _build_windows_live_reference() ──► weighted page ref gen    │
└──────────┬───────────────────────────────────────────────────────┘
           │  function calls
           ▼
┌──────────────────────────────────────────────────────────────────┐
│                    CORE MODULES (core/)                          │
│                                                                  │
│  fifo.py ────── run_fifo(), detect_beladys_anomaly()            │
│  lru.py ─────── run_lru()                                       │
│  optimal.py ─── run_optimal(), _find_optimal_victim()           │
│  segmentation.py ── SegmentTable, Segment, SegmentFaultError,   │
│                     simulate_fragmentation()                     │
│  engine.py ──── PageTable, FramePool (base infrastructure)      │
└──────────────────────────────────────────────────────────────────┘
```

---

## How Each Algorithm Works

### FIFO (First-In, First-Out)
- Maintains a queue of loaded pages in insertion order
- On **page fault**: if frames are full, evict the **oldest** page (front of queue)
- Susceptible to **Bélády's Anomaly**: increasing frame count can increase faults
- Classic anomaly example: reference string `1,2,3,4,1,2,5,1,2,3,4,5` with 3 vs 4 frames

### LRU (Least Recently Used)
- Tracks recency using an `OrderedDict`
- On **hit**: move page to most-recent position
- On **fault**: evict the **least recently used** page (front of OrderedDict)
- Never exhibits Bélády's Anomaly (stack algorithm)

### Optimal (Bélády's Algorithm / MIN)
- Looks **ahead** in the reference string to find future usage
- On **fault**: evict the page that **won't be used for the longest time** (or never again)
- Produces the theoretical minimum number of faults — used as a benchmark
- Not implementable in real systems (requires future knowledge)

### Segmentation
- Memory is divided into **variable-size segments** (code, heap, data, stack)
- Each segment has a **base** (starting physical address) and **limit** (requested size)
- Allocations are **block-aligned** (rounded up to block size multiples), causing **internal fragmentation**
- Deallocation creates **holes** between segments, causing **external fragmentation**
- **Compaction** slides all segments left to eliminate holes
- **Address translation**: `Physical Address = Base + Offset` (if `Offset < Limit`, else TRAP)

---

## Setup and Run

### Prerequisites

- **Python 3.10+**
- **Windows** is required for live process telemetry features
  - Non-Windows users can still use all manual/non-live simulation features

### Install

```bash
# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Start the Application

```bash
python app.py
```

Open your browser to **http://127.0.0.1:5000**

### Run Tests

```bash
python -m pytest -q
```

---

## Web Pages

| Route | Page | Description |
|-------|------|-------------|
| `GET /` | Overview | Side-by-side comparison of FIFO vs LRU vs Optimal with bar chart, Bélády chart, and fault race chart |
| `GET /fifo` | FIFO | Step-by-step FIFO simulation with frame visualization, history table, demand paging panel, Bélády anomaly analysis, and fault timeline |
| `GET /lru` | LRU | Same UI as FIFO but using LRU algorithm |
| `GET /optimal` | Optimal | Same UI as FIFO but using Optimal algorithm |
| `GET /segmentation` | Segmentation | Full segmentation workspace with memory map, segment table, address translator, compaction, and operation history |

---

## API Reference

### `GET /api/realtime-algorithms`

Main paging API. Returns results for all three algorithms plus Bélády analysis.

**Query Parameters:**

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `reference_string` | string | `7,0,1,2,0,3,0,4,2,3,0,3,2` | Comma-separated page numbers |
| `frames` | int | `3` | Number of physical frames |
| `algorithm` | string | `FIFO` | Selected algorithm: `FIFO`, `LRU`, or `Optimal` |
| `max_belady_frames` | int | `10` | Max frames to test for Bélády analysis |
| `live` | bool | `0` | Enable live Windows process mode |
| `live_source` | string | `windows` | Live data source (only `windows` supported) |
| `window_size` | int | `12` | Reference string length in live mode |
| `max_page` | int | `9` | Max page number in live mode |

**Response:** JSON with `timestamp`, `paging` (containing `current`, `fifo`, `lru`, `optimal`, `belady`, `meta`)

### `POST /api/simulate`

Paging simulation from a JSON body.

**Request Body:**
```json
{
  "reference_string": [7, 0, 1, 2, 0, 3, 0, 4],
  "frames": 3,
  "algorithm": "FIFO",
  "max_belady_frames": 10
}
```

**Response:** JSON with `current`, `fifo`, `lru`, `optimal`, `belady`, `meta`

### `POST /api/segmentation`

Run a manual segmentation operation sequence.

**Request Body:**
```json
{
  "operations": [
    {"action": "alloc", "name": "code", "size": 200},
    {"action": "alloc", "name": "stack", "size": 300},
    {"action": "free", "name": "code"},
    {"action": "compact"}
  ],
  "total_memory": 4096,
  "block_size": 16
}
```

**Response:** JSON array of snapshots, one per operation, each containing `segments`, `memory_map`, `free_holes`, `fragmentation`, and `error`

### `GET /api/live-segmentation`

Builds segmentation operations from real Windows processes, then runs the simulation.

**Query Parameters:**

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `total_memory` | int | `16384` | Total simulated memory (bytes) |
| `block_size` | int | `64` | Block alignment size (bytes) |
| `max_processes` | int | `8` | Max processes to include (2–12) |
| `extra_ops` | JSON string | `null` | Additional operations to append (e.g., free, compact) |

**Response:** JSON with `processes` (real process details), `system` (totals), `simulation` (operations + snapshots), `timestamp`

---

## Fragmentation Metrics

The segmentation simulator tracks these metrics in real time:

| Metric | Formula | Description |
|--------|---------|-------------|
| **Used** | `Σ allocated_size` | Total bytes reserved by all segments |
| **Requested** | `Σ limit` | Total bytes actually requested by programs |
| **Internal Frag** | `Used - Requested` | Bytes wasted inside segments due to block alignment |
| **External Frag** | `Σ hole_size (between segments)` | Bytes trapped in gaps between segments (trailing free space is NOT counted) |
| **Total Free** | `total_memory - Used` | Total unallocated bytes |
| **Utilization** | `Used / total_memory × 100` | Percentage of memory occupied |

---

## Developer Notes

- **Core modules are framework-agnostic**: `core/` has zero Flask imports — algorithms can be used independently or integrated into other projects
- **Shared paging frontend**: All three algorithm pages (FIFO, LRU, Optimal) use `paging-common.js` — each page only sets `window.ALGO` to select which algorithm's results to display
- **Unified output shape**: All paging algorithms return the same structure (`algorithm`, `reference_string`, `frame_count`, `steps[]`, `total_faults`, `total_hits`, `fault_positions`)
- **Address translation is client-side**: The segmentation page performs address translation in JavaScript for instant feedback. The Python `SegmentTable.translate()` method exists for correctness validation in tests
- **Auto-polling**: Paging pages poll `/api/realtime-algorithms` every 10 seconds for live updates; segmentation polls `/api/live-segmentation` every 5 seconds when in live mode
- **`engine.py` provides base infrastructure**: `PageTable` and `FramePool` classes define the canonical data structures for virtual memory. While the algorithm modules use lightweight internal equivalents for performance, `engine.py` serves as the foundational reference and is required by the package init