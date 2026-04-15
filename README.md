# Virtual Memory Simulator

A Flask-based virtual memory simulator that combines:

- Page replacement simulation: FIFO, LRU, Optimal
- Segmentation and fragmentation simulation: First Fit, Best Fit, Worst Fit, Next Fit
- Interactive browser UI with step playback and charts
- Optional live Windows process-driven workloads for realistic reference streams

The project is structured as reusable core algorithm modules plus a web application layer built from Flask templates and static assets.

## Highlights

- Algorithm pages for FIFO, LRU, and Optimal with step-by-step visualization
- Belady anomaly analysis for FIFO across multiple frame sizes
- Overview dashboard for side-by-side algorithm comparison
- Segmentation workspace with live process ingestion, allocation strategies, compaction, memory-map views, and operation history
- JSON APIs for direct integration and testing
- Unit test suite for core logic

## Tech Stack

- Backend: Python, Flask
- Algorithms: Pure Python modules in core
- Frontend: HTML templates, vanilla JavaScript, shared CSS
- Charts: Chart.js (client), Plotly helpers (server-side modules)
- Tests: pytest
- Runtime options: local Flask app, Gunicorn process, Vercel serverless target

## Project Structure

```text
.
├── app.py
├── app/
│   ├── templates/
│   │   ├── index.html
│   │   ├── fifo.html
│   │   ├── lru.html
│   │   ├── optimal.html
│   │   └── segmentation.html
│   └── static/
│       ├── css/styles.css
│       └── js/
│           ├── index.js
│           ├── fifo.js
│           ├── lru.js
│           ├── optimal.js
│           └── segmentation.js
├── core/
│   ├── engine.py
│   ├── fifo.py
│   ├── lru.py
│   ├── optimal.py
│   └── segmentation.py
├── visualization/
│   ├── charts.py
│   ├── comparison.py
│   └── belady_chart.py
├── tests/
│   ├── test_engine.py
│   ├── test_fifo.py
│   ├── test_lru.py
│   ├── test_optimal.py
│   └── test_segmentation.py
├── scripts/get_processes.ps1
├── requirements.txt
├── Procfile
└── vercel.json
```

## What Is Implemented

### Paging

- FIFO simulation with full step history and Belady anomaly detection
- LRU simulation using recency tracking
- Optimal simulation using future reference look-ahead
- Unified output shape across algorithms:
   - algorithm
   - reference_string
   - frame_count
   - steps with page, frames, fault, evicted
   - total_faults, total_hits, fault_positions

### Segmentation

- Segment and SegmentTable model with block alignment support
- Allocation strategies:
   - first_fit
   - best_fit
   - worst_fit
   - next_fit
- Free segment handling, hole tracking, and compaction
- Translation with bounds and fault checks
- Fragmentation metrics:
   - used
   - requested
   - internal_frag
   - external_frag
   - total_free
   - utilization
- Snapshot-driven simulation via simulate_fragmentation

### Live Mode

- Realtime date endpoint
- Realtime algorithm endpoint with optional live reference generation
- Windows process integration path using PowerShell process data
- Live segmentation endpoint that builds operations from active process snapshots

## Setup and Run

### Prerequisites

- Python 3.10+
- Windows is required for live Windows process telemetry paths
   - Non-Windows users can still use manual input and non-live simulation APIs

### Install

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### Start the app

```bash
python app.py
```

Open:

- http://127.0.0.1:5000

## Run Tests

```bash
.venv\Scripts\python.exe -m pytest -q
```

## Web Routes

- GET / : Overview dashboard
- GET /fifo : FIFO page
- GET /lru : LRU page
- GET /optimal : Optimal page
- GET /segmentation : Segmentation page

## API Reference

### GET /api/realtime-date

Returns current datetime metadata and day or night theme hint.

### GET /api/realtime-algorithms

Builds paging payload for one selected algorithm plus comparison results.

Key query params:

- reference_string: comma-separated or spaced pages
- frames: integer
- algorithm: FIFO or LRU or Optimal
- max_belady_frames: integer
- live: 0 or 1
- live_source: windows or synthetic
- window_size, max_page: live stream controls

Optional segmentation block can be included with:

- operations: JSON list
- strategy: first_fit or best_fit or worst_fit or next_fit
- total_memory
- block_size

### POST /api/simulate

Paging simulation from JSON body:

```json
{
   "reference_string": [7, 0, 1, 2, 0, 3, 0, 4],
   "frames": 3,
   "algorithm": "FIFO",
   "max_belady_frames": 10
}
```

### POST /api/segmentation

Runs operation sequence through segmentation engine.

```json
{
   "operations": [
      {"action": "alloc", "name": "code", "size": 200},
      {"action": "alloc", "name": "stack", "size": 300},
      {"action": "free", "name": "code"},
      {"action": "compact"}
   ],
   "strategy": "first_fit",
   "total_memory": 4096,
   "block_size": 16
}
```

### GET /api/live-segmentation

Builds segmentation operations from live Windows process snapshot, then runs simulation.

Key query params:

- strategy
- total_memory
- block_size
- max_processes
- extra_ops (JSON array)

## Deployment Notes

- Procfile is configured for Gunicorn:
   - web: gunicorn app:flask_app
- Vercel is configured through vercel.json to route all requests to app.py
- app.py exports app = flask_app for serverless compatibility

See docs/deployment/vercel.md for a step-by-step Vercel flow.

## Developer Notes

- Core logic is cleanly separated from UI-specific rendering code
- Frontend and backend are aligned around stable result payload contracts
- Test suite validates algorithm correctness and segmentation behavior across edge cases