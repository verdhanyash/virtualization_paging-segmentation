# 🧠 Virtual Memory Simulator

A modern, interactive Flask-based virtual memory simulator that visualizes page replacement algorithms and memory segmentation dynamics. It bridges the gap between theoretical operating system concepts and real-world execution by featuring an optional **Live Windows Process Feed** that pulls telemetry from your actual OS processes to simulate realistic memory workloads.

---

## ✨ Key Features

- **Page Replacement Simulation**
  - Visualize algorithms: **FIFO**, **LRU**, and **Optimal**.
  - Interactive step-by-step playback to see hits, faults, and evictions occur in real-time.
  - Automatic mathematical demonstration of **Belady's Anomaly** across memory frame sizes.

- **Segmentation & Fragmentation**
  - Live segmentation workspace with dynamic visual memory mapping.
  - Granular operation tracking for allocations, frees, and system compactions.
  - Real-time calculation of **Internal & External Fragmentation** metrics.

- **Live Windows Integration**
  - Drive simulations using *actual* running processes on your Windows host.
  - Extracts process Working Set (WS) memory and CPU logic via PowerShell.
  - Synthesizes realistic reference strings incorporating proper spatial and temporal locality.

---

## 🛠️ Tech Stack

- **Backend:** Python 3.10+, Flask
- **Core Algorithms:** Pure Python (Zero external mathematical dependencies)
- **Frontend:** Vanilla JavaScript, HTML5 templates, CSS
- **Visualization:** Chart.js (client-side)
- **Testing:** Pytest

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.10+**
- **Windows OS** (Optional, but highly recommended for the live telemetry feed. Non-Windows users can still use manual inputs or pre-programmed simulations.)

### Installation

Clone the repository and set up your virtual environment:

```bash
# Clone the repository
git clone https://github.com/verdhanyash/virtualization_paging-segmentation.git
cd OS_PROJECT

# Create and activate a Virtual Environment
python -m venv .venv
.venv\Scripts\activate   # On Windows
# source .venv/bin/activate # On Unix/MacOS

# Install Dependencies
pip install -r requirements.txt
```

### Running the App

Start the Flask development server:

```bash
python app.py
```

Open your browser and navigate to: [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## 🧪 Testing

The project includes a comprehensive suite of **48 Unit Tests** logically separated across the core modules of the memory simulator to guarantee mathematical precision.

To run the entire test suite, make sure your virtual environment is active and execute:

```bash
python -m pytest -v
```

### Test Coverage Breakdown

- **Segmentation Memory Tests (30 Tests):** Validation for contiguous block allocation, boundaries & addressing exceptions, defragmentation/compaction algorithms, hole recycling, and real-time computation of external and internal fragmentation.
- **Page Replacement Data Structures (12 Tests):** Algorithmic verification spanning across queue cache logic for **FIFO** & **LRU**, predictive caching behavior for the **Optimal** algorithm, and explicitly validating **Belady's Anomaly**.
- **Core Engine Mechanics (6 Tests):** Tests baseline operations such as virtual-to-physical translation functions, page fault flaggers, bounds limiters, and basic initialization routines.

---

## 🔌 Core APIs

The simulation logic is decoupled from the UI, allowing you to interface directly with the simulation engines via JSON endpoints.

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/realtime-algorithms` | Returns simulated or live results for a paging algorithm. |
| `POST` | `/api/simulate` | Submit a custom JSON payload containing a reference string to step through Paging. |
| `POST` | `/api/segmentation` | Run a custom sequence of allocation/free operations through the Segmentation engine. |
| `GET` | `/api/live-segmentation` | Builds operations from a live Windows process snapshot and runs the simulation. |

*(For full API parameter references, inspect `app.py` directly).*

---

## 📁 Project Architecture

```text
OS_PROJECT/
├── app.py                   # Main Flask Application
├── app/                     # Frontend Application
│   ├── templates/           # HTML views (index, fifo, lru, optimal, segmentation)
│   └── static/              # Vanilla JS logic & raw CSS styles
├── core/                    # Core Simulation Engines
│   ├── engine.py            # Base constructs (Pages, Frames, Tables)
│   ├── fifo.py              # FIFO logic
│   ├── lru.py               # LRU logic
│   ├── optimal.py           # Optimal logic
│   └── segmentation.py      # Segmentation logic
├── tests/                   # Pytest suite
└── requirements.txt         # Dependencies
```

---

## 🚢 Deployment

The repository is built serverless-ready for **Vercel** (`vercel.json`) and incorporates `gunicorn` mapping for environments like **Heroku/Render** natively.

*Note: Live Windows metrics endpoints will fall back to pseudo-random simulation if queried on a non-Windows cloud deployment.*
