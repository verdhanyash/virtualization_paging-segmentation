# Implementation Details — Virtual Memory Simulator

## Overview

This project is a **real-time virtual memory management simulator** built with Flask (Python) + vanilla JavaScript. It visualizes two core OS memory management concepts — **Paging** and **Segmentation** — using live Windows process data from the host machine to drive the simulation, making it a pedagogical tool grounded in real-world system behavior.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│  FRONTEND (Browser)                                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐           │
│  │  FIFO    │  │   LRU    │  │ Optimal  │  │ Segment  │  Pages    │
│  │  Page    │  │   Page   │  │   Page   │  │   Page   │           │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘           │
│       │              │              │              │                │
│       └──────────────┼──────────────┘              │                │
│                      │                             │                │
│        paging-common.js                  segmentation.js            │
│           (shared logic)               (standalone logic)           │
│                      │                             │                │
│       XHR every 10s ─┘       XHR on START──────────┘                │
├─────────────────────────────────────────────────────────────────────┤
│  BACKEND (Flask — app.py)                                           │
│  ┌──────────────────────────────────────────┐                       │
│  │  /api/realtime-algorithms                │  ← paging endpoint    │
│  │  /api/live-segmentation                  │  ← seg endpoint       │
│  │  /api/live-seg-compare                   │  ← seg compare        │
│  │  /api/realtime-date                      │  ← live clock         │
│  └──────────────┬───────────────────────────┘                       │
│                 │                                                    │
│   ┌─────────────▼───────────────┐  ┌─────────────────────────┐     │
│   │  PowerShell: Get-Process    │  │  core/                  │     │
│   │  (real PIDs, CPU, memory)   │  │  ├── fifo.py            │     │
│   │  scripts/get_processes.ps1  │  │  ├── lru.py             │     │
│   └─────────────────────────────┘  │  ├── optimal.py         │     │
│                                    │  ├── segmentation.py    │     │
│                                    │  └── engine.py          │     │
│                                    └─────────────────────────┘     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Frontend Pages

The website has **5 pages**, each accessible from the top navigation bar:

### 1. Dashboard (`/` — Overview)

The landing page provides a bird's-eye summary of all modules.

| Section | What It Shows |
|---------|--------------|
| **Algorithm Cards** | Four clickable cards (FIFO, LRU, Optimal, Segmentation) with one-line descriptions and tags (Queue-based, Recency-based, Clairvoyant, Memory Alloc). Each links to its dedicated page. |
| **Quick Compare — All Algorithms** | Side-by-side comparison of FIFO vs LRU vs Optimal on the same reference string. Shows fault count cards, a grouped bar chart (Faults vs Hits), and highlights the best-performing algorithm with a green border. |
| **Bélady's Anomaly Chart** | Line chart plotting FIFO fault count vs frame count (1–10). Red dots mark anomaly points where more frames cause more faults. A pulsing "Anomaly Detected" badge appears when found. |
| **Cumulative Fault Race** | Three-line overlay chart showing how faults accumulate step-by-step for all three algorithms simultaneously. |
| **Segmentation Strategy Comparison** | Live comparison of First-Fit, Best-Fit, Worst-Fit, and Next-Fit strategies using real process data. Shows external fragmentation (bytes) and memory utilization (%) as bar charts. Strategy cards show internal/external fragmentation, utilization, and mark the best strategy. |
| **Key Concepts** | Educational callout boxes explaining Page Fault, Bélady's Anomaly, and External Fragmentation. |
| **Live Clock** | Top-right badge showing real-time system date/time, updated every 30 seconds. |

**Data Source**: Live Windows processes (default, checkbox checked) OR manual custom input.

---

### 2. FIFO Page (`/fifo`)

Dedicated deep-dive into the **First In, First Out** page replacement algorithm.

| Section | What It Shows |
|---------|--------------|
| **Algorithm Description** | Explains FIFO's queue-based eviction and how the live process connection works — CPU volatility drives page assignment. |
| **Controls Panel** | Live/Manual toggle, reference string input (readonly in live mode, editable in manual), frame count slider (1–10), playback buttons (Run, Step, Auto, Reset), speed slider. |
| **Live Process Source** | Chips showing each real Windows process contributing to the reference string. Each chip shows: process name, CPU time, activity percentage, and assigned integer page numbers (e.g., `Code 3533.0s CPU (40.8% Activity) → Pages [1,2,3,4]`). |
| **Step-by-Step Visualization** | Interactive step player showing: current step number, referenced page, FAULT/HIT pill indicator, evicted page (if any), cumulative faults so far, and the current frame contents as colored boxes (newly loaded pages flash with animation). |
| **Demand Paging Visualization** | Two side-by-side panels: (1) **Page Table** showing Valid/Invalid bits for every page in the reference string — green (V) if currently in a frame, red (I) if not; (2) **Backing Store** — a scrolling swap log showing SWAP-IN and SWAP-OUT events per step. |
| **Progress Bar** | Visual progress bar showing simulation completion percentage. |
| **Reference String Pills** | Clickable colored pills for every step — red for past faults, blue for past hits, highlighted for current, gray for future. Click any pill to jump to that step. |
| **Frame State History** | Full matrix table showing: step numbers, page accessed, each frame's contents per step (color-coded: new pages, existing pages, empty slots), evicted page, and fault indicator row. |
| **Statistics** | Summary cards: Algorithm name, total page faults, total hits, fault rate percentage. |
| **Bélady's Anomaly Chart** | Same as dashboard — FIFO faults vs frames (1–10) with anomaly detection. |
| **Cumulative Fault Timeline** | Line chart of faults accumulating over simulation steps. |

**Polling**: Every 10 seconds, the page fetches fresh Windows process data and rebuilds the reference string (if not in auto-playback mode).

---

### 3. LRU Page (`/lru`)

Same layout and features as the FIFO page, but running the **Least Recently Used** algorithm.

| Difference from FIFO | Detail |
|----------------------|--------|
| **Algorithm** | Evicts the page that has not been used for the longest time, using an `OrderedDict` to track access recency. |
| **Description** | Explains how LRU tracks recency with `OrderedDict`, and notes that unlike FIFO, LRU does **not** suffer from Bélady's Anomaly. |
| **Eviction logic** | On each access, the hit page moves to the end (most recent). On fault with full memory, the first item (least recent) is evicted. |

All other sections (step visualization, demand paging, charts, live process source) are identical and shared via `paging-common.js`.

---

### 4. Optimal Page (`/optimal`)

Same layout and features as FIFO/LRU, running the **Optimal (Clairvoyant)** algorithm.

| Difference from FIFO | Detail |
|----------------------|--------|
| **Algorithm** | Looks ahead in the reference string to find the page that will not be used for the longest time in the future. Produces the theoretical minimum number of faults. |
| **Description** | Explains that Optimal is a theoretical benchmark — it requires future knowledge and is not implementable in real systems, but serves as a lower bound for comparison. |
| **Eviction logic** | On fault with full memory, scans the future reference string for each loaded page, evicts the one whose next use is farthest away (or never used again). |

---

### 5. Segmentation Page (`/segmentation`)

Dedicated deep-dive into **variable-size memory allocation and fragmentation**.

| Section | What It Shows |
|---------|--------------|
| **Live Address Space** | Full-width composition bar showing the entire memory layout. Each segment is color-coded by process, with tooltips showing segment name and size. Holes are shown with a hatched red pattern. A color legend identifies all processes. |
| **Allocation Strategies** | Four selectable strategy buttons: First-Fit (01), Best-Fit (02), Worst-Fit (03), Next-Fit (04). Selecting a strategy re-runs the simulation with the chosen algorithm. An informational note explains that strategies only differ when holes exist. |
| **Configuration** | Total Memory (bytes), Block Size (bytes), Max Processes — all configurable. A toggle switches between Live Windows Telemetry and Manual Custom Operations. |
| **Custom Operations Builder** | (Manual mode only) Form to build a sequence of alloc/free/compact operations with process names and sizes. Operations appear as a live queue with remove buttons. |
| **Execution Engine** | START_SIMULATION button triggers the API call. COMPACT MEMORY button triggers compaction. RESET clears everything. |
| **Process List** | Shows the top processes captured from Windows, each with a color-coded card showing process name, PID, and an accent stripe matching the memory map colors. Shows count like "8 of 96 procs". |
| **Statistics Panel** | Six metric cards: In Use, Available, Internal Fragmentation (yellow warning), External Fragmentation (red warning), Hole Count (red warning if > 0), Utilization %. |
| **Block-Level Memory Grid** | Grid of tiny cells representing each block of memory. Segments are colored by process, internal fragmentation blocks show a hatched pattern, holes show a dark red hatch, free blocks are empty. Hovering shows a tooltip with block info (segment name, base address, requested vs allocated size, internal fragmentation). |
| **Segment Table** | Detailed card-style rows for each allocated segment: process icon (type-specific: 📝 text, 🗃️ data, 📦 heap, 📚 stack, ⚙ system), process name, segment type, base address, limit, allocated size, internal fragmentation. |
| **Free Holes Table** | Table listing genuine holes between segments (not trailing free space): hole number, base address, size in bytes, percentage of total memory. |
| **Operation History** | Scrollable log showing every alloc/free/compact operation in order, with ✓ OK or ✗ ERR status indicators. Each row shows the operation type, process name, segment type, and size. |

---

## Real-Time Data Pipeline

### How Live Process Data Drives the Simulation

```
Windows OS
    │
    ▼
PowerShell: Get-Process
(Name, Id, CPU, WorkingSet64)
    │
    ▼
_get_windows_process_snapshot()
→ Returns: [{name, pid, mem_kb, cpu, volatility}, ...]
    │
    ▼
_build_windows_live_reference()
→ Groups by process name, sorts by volatility (CPU time)
→ Top 8 processes selected
→ Each gets integer pages proportional to CPU activity
→ Reference string built with locality patterns:
   • 20% temporal locality (revisit recent page)
   • 70% spatial locality (page from same process)
   • 10% random access (cross-process page fault)
    │
    ▼
Reference String: [5, 4, 4, 4, 1, 1, 9, 3, 1, 1, 6, 1]
+ Process metadata for UI display
```

### Polling Intervals

| Component | Interval | Behavior |
|-----------|----------|----------|
| Paging pages (FIFO/LRU/Optimal) | 10 seconds | Fetches new process snapshot, rebuilds reference string, re-runs algorithm. Paused during auto-playback. |
| Dashboard comparison | 10 seconds | Re-runs all three algorithms with fresh data. |
| Live clock badge | 30 seconds | Updates the date/time display in the navbar. |
| Segmentation | On-demand | Only runs when user clicks START_SIMULATION. |

---

## Core Algorithms

### Page Replacement (core/)

| Algorithm | File | Complexity | Data Structure | Key Behavior |
|-----------|------|-----------|----------------|-------------|
| FIFO | `core/fifo.py` | O(1) per access | `deque` | Evicts oldest page (queue front). Subject to Bélady's Anomaly. |
| LRU | `core/lru.py` | O(1) per access | `OrderedDict` | On hit: `move_to_end()`. On fault: `popitem(last=False)`. Immune to Bélady's. |
| Optimal | `core/optimal.py` | O(n·f) per access | List scan | Scans future references for each loaded page. Evicts the one used farthest out. |
| Bélady's Anomaly | `core/fifo.py` | O(f·n) total | Runs FIFO for frames 1..max | Detects cases where fault_count[f+1] > fault_count[f]. |

### Segmentation (core/segmentation.py)

| Strategy | How It Selects a Hole |
|----------|----------------------|
| First-Fit | Scans holes from the start, picks the **first** hole large enough. |
| Best-Fit | Scans all holes, picks the **smallest** hole that fits (minimizes leftover). |
| Worst-Fit | Scans all holes, picks the **largest** hole (maximizes leftover for future use). |
| Next-Fit | Like First-Fit, but resumes scanning from the last allocation point instead of the start. |

Additional features:
- **Compaction**: Slides all segments to the left, merging all free space into one contiguous block at the end.
- **Internal Fragmentation**: Tracked per segment when block-aligned allocation exceeds the requested size.
- **External Fragmentation**: Calculated as the total free space in holes between allocated segments (excluding trailing free space).
- **Address Translation**: Validates that an offset falls within a segment's limit before computing the physical address.

---

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.10+, Flask 3.1 |
| Frontend | Vanilla HTML/CSS/JavaScript |
| Charts | Chart.js 4.4 (client-side) |
| Process Telemetry | PowerShell `Get-Process` (Windows) |
| Tests | pytest (54 tests) |
| Styling | Custom CSS (dark theme, alice blue + blue palette) |
| Font | JetBrains Mono (monospace) |

---

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/realtime-algorithms` | GET | Run paging algorithms (FIFO/LRU/Optimal) with live or custom input. Returns step-by-step results, Bélady's analysis, and process metadata. |
| `/api/simulate` | POST | Run a single paging simulation with JSON body. |
| `/api/segmentation` | POST | Run segmentation with custom operations (alloc/free/compact). |
| `/api/live-segmentation` | GET | Run segmentation using real Windows process data. |
| `/api/live-seg-compare` | GET | Compare all four segmentation strategies side-by-side. |
| `/api/realtime-date` | GET | Get current system date/time for the live clock badge. |

---

## Key Design Decisions

1. **Integer page IDs** — Live processes are mapped to small integers (1, 2, 3...) rather than raw hex addresses, ensuring compatibility with all paging algorithms and clean UI display.

2. **CPU volatility as the allocation metric** — Processes are ranked by total CPU execution time, not just memory size. This makes the reference string reflect actual system activity rather than static memory footprint.

3. **Locality of reference** — The reference string generator simulates real CPU scheduling patterns: temporal locality (20% chance to revisit a recently accessed page) and spatial locality (70% chance to access a page from the currently scheduled process).

4. **No dummy data** — All live mode paths require real Windows process data. If telemetry fails, the system returns a clear error rather than fabricating fake data.

5. **Shared JS module** — All three paging pages (FIFO, LRU, Optimal) share a single `paging-common.js` file. Each page's JS file is a 2-line stub that sets `window.ALGO` before the shared module loads.

6. **Block-aligned allocation** — Segmentation uses a configurable block size. Allocated segments are rounded up to the nearest block boundary, and the difference is tracked as internal fragmentation.
