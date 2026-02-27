# 🖥️ Virtual Memory Optimization Simulator

A comprehensive virtual memory management tool that visualizes paging, segmentation, page replacement algorithms, and memory fragmentation — built for understanding and experimenting with OS memory management concepts.

## ✨ Features

- **Paging Engine** — Logical-to-physical address translation via page tables
- **Segmentation Engine** — Segment-based address translation with bounds checking
- **LRU Page Replacement** — Step-by-step Least Recently Used simulation
- **Optimal Page Replacement** — Benchmark optimal algorithm simulation
- **Fragmentation Simulator** — Internal & external fragmentation analysis
- **Demand Paging** — Pages loaded only on demand, not preloaded
- **Visual Comparisons** — Bar charts, line graphs, heatmaps, and animated frame tables
- **Preset Scenarios** — One-click demo scenarios
- **Export** — Download results as CSV or PDF reports

## 🏗️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python, Flask |
| Frontend | HTML, CSS, JavaScript |
| Charts | Chart.js |
| Export | jsPDF |

## 📁 Project Structure

```
OS_PROJECT/
├── backend/
│   ├── app.py               # Flask API Gateway
│   ├── config.py             # Shared constants
│   ├── utils.py              # Input validation helpers
│   ├── paging.py             # Paging Engine
│   ├── segmentation.py       # Segmentation Engine
│   ├── lru.py                # LRU Algorithm
│   ├── optimal.py            # Optimal Algorithm
│   ├── fragmentation.py      # Fragmentation Simulator
│   ├── demand_paging.py      # Demand Paging Simulator
│   └── requirements.txt      # Dependencies
│
├── frontend/
│   ├── index.html            # Main page
│   ├── css/                  # Stylesheets
│   │   ├── base.css          # Theme & typography
│   │   ├── layout.css        # Grid & sidebar
│   │   ├── components.css    # Buttons, inputs, cards
│   │   └── visualization.css # Tables, charts, heatmap
│   ├── js/                   # JavaScript modules
│   │   ├── main.js           # App init & tab switching
│   │   ├── api.js            # API client
│   │   ├── input-config.js   # Configuration panel
│   │   ├── ref-string.js     # Reference string manager
│   │   ├── segmentation-panel.js
│   │   ├── paging-panel.js
│   │   ├── presets.js        # Preset scenarios
│   │   ├── frame-table.js    # Frame state table
│   │   ├── animator.js       # Step-by-step animator
│   │   ├── comparison-chart.js
│   │   ├── fault-graph.js
│   │   ├── fragmentation-heatmap.js
│   │   ├── result-display.js
│   │   └── export.js         # CSV & PDF export
│   └── lib/                  # Third-party libraries
│       ├── chart.min.js
│       └── jspdf.min.js
│
└── README.md
```

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- pip

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
python app.py
```
The API server will start on `http://localhost:5000`.

### Frontend
Open `frontend/index.html` in your browser, or serve it via Flask's static file serving.

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/paging` | POST | Logical → physical address translation |
| `/api/segmentation` | POST | Segment-based address translation |
| `/api/simulate` | POST | LRU / Optimal page replacement simulation |
| `/api/fragmentation` | POST | Internal & external fragmentation analysis |
| `/api/demand-paging` | POST | Demand paging timeline simulation |

## 🧩 Modules

| # | Module | Layer |
|---|--------|-------|
| M1 | Config & Requirements | Backend |
| M2 | Validation Utilities | Backend |
| M3 | Flask API Gateway | Backend |
| M4 | Paging Engine | Backend |
| M5 | Segmentation Engine | Backend |
| M6 | LRU Algorithm Engine | Backend |
| M7 | Optimal Algorithm Engine | Backend |
| M8 | Fragmentation Simulator | Backend |
| M9 | Demand Paging Simulator | Backend |
| M10 | HTML Page Skeleton | Frontend |
| M11–M14 | CSS (Base, Layout, Components, Viz) | Frontend |
| M15–M21 | JS Input Panels & Logic | Frontend |
| M22–M24 | Visualizations (Tables, Charts, Heatmap) | Visualization |
| M25 | Export & Report | Visualization |

## 📄 License

This project is for educational purposes.
