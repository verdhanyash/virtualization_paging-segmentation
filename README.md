# 🖥️ Virtual Memory Optimization Simulator

A comprehensive virtual memory management tool that visualizes paging, segmentation, page replacement algorithms, and memory fragmentation — built for understanding and experimenting with OS memory management concepts.

## ✨ Features

- **Paging Engine** — Logical-to-physical address translation via page tables
- **Segmentation Engine** — Segment-based address translation with bounds checking
- **LRU Page Replacement** — Step-by-step Least Recently Used simulation
- **Optimal Page Replacement** — Benchmark optimal algorithm simulation
- **Fragmentation Simulator** — Internal & external fragmentation analysis
- **Demand Paging** — Pages loaded only on demand, not preloaded
- **Visual Comparisons** — Bar charts, line graphs, and heatmaps (Plotly)
- **Step-by-Step Animation** — Animated frame table playback
- **Preset Scenarios** — One-click demo scenarios
- **Export** — Download results as CSV or PDF reports

## 🏗️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend & Logic | Python, Flask, Jinja2 |
| Charts | Plotly (Python, server-side) |
| Export | Python csv + fpdf2 |
| Frontend | HTML, CSS, JS  |

## 📁 Project Structure

```
OS_PROJECT/
├── backend/
│   ├── app.py                    # Flask routes & template serving
│   ├── config.py                 # Shared constants
│   ├── utils.py                  # Input validation helpers
│   ├── paging.py                 # Paging Engine
│   ├── segmentation.py           # Segmentation Engine
│   ├── lru.py                    # LRU Algorithm
│   ├── optimal.py                # Optimal Algorithm
│   ├── fragmentation.py          # Fragmentation Simulator
│   ├── demand_paging.py          # Demand Paging Simulator
│   ├── chart_generator.py        # Plotly chart generation (Python)
│   ├── export_module.py          # CSV + PDF export (Python)
│   ├── presets.py                # Preset scenarios
│   └── requirements.txt          # Dependencies
│
├── templates/
│   ├── base.html                 # Base layout (sidebar + structure)
│   ├── page_replacement.html     # Page replacement tab
│   ├── paging.html               # Paging translator tab
│   ├── segmentation.html         # Segmentation tab
│   ├── fragmentation.html        # Fragmentation tab
│   └── demand_paging.html        # Demand paging tab
│
├── static/
│   ├── css/
│   │   ├── base.css              # Theme & typography
│   │   ├── layout.css            # Grid & sidebar
│   │   ├── components.css        # Buttons, inputs, cards
│   │   └── visualization.css     # Tables, heatmap, animator
│   └── js/
│       └── app.js                # Minimal JS (tabs, animation)
│
└── README.md
```

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- pip

### Setup & Run
```bash
cd backend
pip install -r requirements.txt
python app.py
```
Open `http://localhost:5000` in your browser.

## 📡 Routes

| Route | Method | Description |
|-------|--------|-------------|
| `/` | GET | Home → page replacement tab |
| `/page-replacement` | GET/POST | LRU / Optimal simulation |
| `/paging` | GET/POST | Logical → physical address translation |
| `/segmentation` | GET/POST | Segment-based address translation |
| `/fragmentation` | GET/POST | Internal & external fragmentation |
| `/demand-paging` | GET/POST | Demand paging timeline |
| `/export/csv` | POST | Download CSV |
| `/export/pdf` | POST | Download PDF report |

## 🧩 Modules

| # | Module | Language | File |
|---|--------|----------|------|
| M1 | Config & Requirements | Python | `config.py`, `requirements.txt` |
| M2 | Validation Utilities | Python | `utils.py` |
| M3 | Paging Engine | Python | `paging.py` |
| M4 | Segmentation Engine | Python | `segmentation.py` |
| M5 | LRU Algorithm | Python | `lru.py` |
| M6 | Optimal Algorithm | Python | `optimal.py` |
| M7 | Fragmentation Simulator | Python | `fragmentation.py` |
| M8 | Demand Paging Simulator | Python | `demand_paging.py` |
| M9 | Chart Generator | Python | `chart_generator.py` |
| M10 | Export Module | Python | `export_module.py` |
| M11 | Preset Scenarios | Python | `presets.py` |
| M12 | Flask App & Routes | Python | `app.py` |
| M13 | Base Template | Jinja2 | `templates/base.html` |
| M14–M18 | Page Templates | Jinja2 | `templates/*.html` |
| M19 | CSS Styles | CSS | `static/css/*.css` |
| M20 | Minimal App JS | JS | `static/js/app.js` |

## 📄 License

This project is for educational purposes.
