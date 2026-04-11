# Virtual Memory Optimization Challenge

Welcome to the **Virtual Memory Optimization Challenge**! This repository is a modular, educational project simulating and analyzing virtual memory management algorithms, specifically focusing on page replacement strategies and memory segmentation.

This project is built using Flask for the core backend logic and vanilla HTML/JS with Chart.js for an interactive, data-rich user interface.

---

## 🎯 Project Overview

The primary goal of this project is to simulate and compare different page replacement algorithms to analyze their performance and characteristics (such as the total number of page faults and the presence of Belady's Anomaly). 

The application is broken down into distinct, modular tasks so that multiple developers can easily collaborate without running into merge conflicts. 

### Supported Algorithms:
1. **FIFO (First-In, First-Out)**: Evicts the oldest page in memory. Also includes logic to detect **Belady's Anomaly**.
2. **LRU (Least Recently Used)**: Evicts the page that has not been accessed for the longest time.
3. **Optimal (MIN)**: Evicts the page that will not be used for the longest time in the future (theoretical minimum faults).
4. **Segmentation**: Allows users to experiment with custom inputs for memory allocation, simulate memory fragmentation with strategies like First-Fit, Best-Fit, etc.

---

## 📁 Repository Structure

The project is structured to enforce a strict separation of concerns between core logic, visualizations, and UI components.

```text
virtual-memory-optimizer/
│
├── core/                         # BACKEND LOGIC (No UI)
│   ├── engine.py                 # Core infrastructure (PageTable, FramePool)
│   ├── fifo.py                   # FIFO algorithm & Belady's anomaly detection
│   ├── lru.py                    # LRU algorithm
│   ├── optimal.py                # Optimal (MIN) algorithm
│   └── segmentation.py           # Segmentation & fragmentation
│
├── app/                          # FRONTEND TEMPLATES & ASSETS
│   ├── index.html                # Paging UI
│   ├── segmentation.html         # Segmentation UI
│   ├── lru.html                  # LRU algorithm UI
│   ├── fifo.html                 # FIFO algorithm UI
│   └── optimal.html              # Optimal algorithm UI
│
├── app.py                        # Flask entry point and API Routes
│
├── tests/                        # Pytest Unit Tests
│   ├── test_engine.py
│   ├── test_fifo.py
│   ├── test_lru.py
│   ├── test_optimal.py
│   └── test_segmentation.py
│
├── insane.txt                    # Project specification and task breakdown reference
├── requirements.txt              # Dependencies used in the project
└── Procfile                      # Render deployment configuration
```

---

## ⚙️ Core Logic Specifications

All core algorithms (`fifo.py`, `lru.py`, `optimal.py`) are strictly backend files. They take in a reference string (list of integers) and a number of physical frames, and return a standardized dictionary containing the step-by-step simulation state.

### Standard Output Format
Every algorithm returns the following JSON/Dict structure to make it easily parsable by the visualization frontend:

```json
{
  "algorithm": "FIFO",           
  "reference_string": [1,2,3],   
  "frame_count": 3,              
  "steps": [                     
    {
      "page": 1,                 
      "frames": [1, null, null], 
      "fault": true,             
      "evicted": null            
    }
  ],
  "total_faults": 7,
  "total_hits": 5,
  "fault_positions": [0,1,2,4,6] 
}
```

---

## 🚀 Getting Started

### Prerequisites
Make sure you have Python 3.10+ installed.

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/verdhanyash/virtualization_paging-segmentation.git
   cd virtualization_paging-segmentation
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   *(Requires `flask`, `gunicorn`, and `pytest`)*

### Running the Application Locally
To start the Flask server locally, run:
```bash
python app.py
```
Access the application in your browser at `http://127.0.0.1:5000/`.

### Running the Tests
We use `pytest` to ensure all core algorithms run accurately and perfectly match their theoretical fault counts.

To run the entire test suite:
```bash
python -m pytest tests/
```

---

## 📋 Task Breakdown & Roadmap (Reference: `insane.txt`)

This project is built around a specific roadmap detailed in `insane.txt`. Below is the current progress:

### Core Algorithms
- [x] **T1:** Core Engine (`core/engine.py`)
- [x] **T2:** FIFO Algorithm + Belady's Anomaly (`core/fifo.py`)
- [x] **T3:** LRU Algorithm (`core/lru.py`)
- [x] **T4:** Optimal Algorithm (`core/optimal.py`)
- [x] **T5:** Segmentation Engine (`core/segmentation.py`)

### Visualization & UI
- [x] **T6:** Algorithm Charts
- [x] **T7:** Algorithm Comparison
- [x] **T8:** Belady's Anomaly Chart
- [x] **T9:** Paging Layout (`app/index.html`)
- [x] **T10:** Paging Callbacks (`app/index.html JS`)
- [x] **T11:** Paging Animation (`app/index.html CSS+JS`)
- [x] **T12:** App Entry Point (`app.py`)
- [x] **T13:** Theme CSS (`app/index.html`)
- [x] **T15:** Segmentation Layout (`app/segmentation.html`)
- [x] **T16:** Segmentation JS Logic (`app/segmentation.html`)
- [x] **T17:** Segmentation Animations (`app/segmentation.html`)
- [x] **T18:** Segmentation API Routes (`app.py`)

### Testing
- [x] **T14:** Unit Tests (`tests/`)

---

## 🛠️ Tech Stack

- **Language:** Python 3.10+
- **Web Framework:** Flask
- **Client Charts:** Chart.js 4.4.1
- **Testing:** pytest
- **Deployment:** Gunicorn + Render
- **Styling:** Jet black (`#0a0a0a`) & White (`#f0f0f0`) Custom CSS

---
*Refer to `insane.txt` for detailed developer instructions, prompt references, and specific module goals.*