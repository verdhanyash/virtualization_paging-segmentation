# Virtual Memory Optimization Challenge

Welcome to the **Virtual Memory Optimization Challenge**! This repository is a modular, educational project simulating and analyzing virtual memory management algorithms, specifically focusing on page replacement strategies and memory segmentation.

This project is built using Python for the core backend logic and Dash/Plotly for an interactive, data-rich user interface.

---

## 🎯 Project Overview

The primary goal of this project is to simulate and compare different page replacement algorithms to analyze their performance and characteristics (such as the total number of page faults and the presence of Belady's Anomaly). 

The application is broken down into distinct, modular tasks so that multiple developers can easily collaborate without running into merge conflicts. 

### Supported Algorithms:
1. **FIFO (First-In, First-Out)**: Evicts the oldest page in memory. Also includes logic to detect **Belady's Anomaly**.
2. **LRU (Least Recently Used)**: Evicts the page that has not been accessed for the longest time.
3. **Optimal (MIN)**: Evicts the page that will not be used for the longest time in the future (theoretical minimum faults).

*(Upcoming: Segmentation and memory fragmentation simulations).*

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
│   └── segmentation.py           # (TODO) Segmentation & fragmentation
│
├── visualization/                # CHARTS & GRAPHS (Plotly)
│   ├── charts.py                 # Individual algorithm charts
│   ├── comparison.py             # Side-by-side algo comparison
│   └── belady_chart.py           # Belady's anomaly visualization
│
├── app/                          # UI COMPONENTS (Dash)
│   ├── layout.py                 # Page layout structure
│   ├── callbacks.py              # Dash callbacks and interactivity
│   ├── animation.py              # Step-by-step UI animation
│   └── main.py                   # Application entry point
│
├── assets/
│   └── theme.css                 # Custom Jet black/white styling
│
├── tests/                        # Pytest Unit Tests
│   ├── test_engine.py
│   ├── test_fifo.py
│   ├── test_lru.py
│   └── test_optimal.py
│
├── insane.txt                    # Project specification and task breakdown reference
└── requirements.txt
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
   *(Requires `dash`, `plotly`, and `pytest`)*

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
- [ ] **T5:** Segmentation & Fragmentation (`core/segmentation.py`)

### Visualization & UI
- [ ] **T6:** Algorithm Charts (`visualization/charts.py`)
- [ ] **T7:** Algorithm Comparison (`visualization/comparison.py`)
- [ ] **T8:** Belady's Anomaly Chart (`visualization/belady_chart.py`)
- [ ] **T9:** Page Layout (`app/layout.py`)
- [ ] **T10:** Callbacks (`app/callbacks.py`)
- [ ] **T11:** Animation (`app/animation.py`)
- [ ] **T12:** App Entry Point (`app/main.py`)
- [ ] **T13:** Theme CSS (`assets/theme.css`)

### Testing
- [x] **T14:** Unit Tests (`tests/`)

---

## 🛠️ Tech Stack

- **Language:** Python 3.10+
- **UI Framework:** Dash (by Plotly)
- **Data Visualization:** Plotly
- **Testing:** pytest
- **Styling:** Jet black (`#0a0a0a`) & White (`#f0f0f0`) Custom CSS

---
*Refer to `insane.txt` for detailed developer instructions, prompt references, and specific module goals.*