# 🖥️ Real-Time Windows Virtual Memory Simulator

Welcome to the **Virtual Memory Simulator**! This repository is a high-fidelity pedagogical tool designed to visually simulate and analyze Operating System Virtual Memory algorithms (Page Replacement and Segmentation). 

Instead of relying on random dummy data, this simulator **directly integrates with your live Windows machine**, pulling real process execution metrics to demonstrate exactly how memory functions under authentic workloads.

---

## ⚡ Core Features

### 1. 📊 Live OS Volatility Mapping
The simulator leverages PowerShell (`Get-Process`) to extract live telemetry from your host machine. Instead of using static memory sizes, it isolates the **most volatile metric: CPU Execution Time**. 
* Virtual memory pages are dynamically mapped to active processes (like `brave.exe` or `explorer.exe`).
* Highly active processes generate heavier page demands, driving the Page Replacement Algorithms using genuine **Spatial and Temporal Locality**.

### 2. 🎛️ Interactive Paging Algorithms
Analyze the core page replacement strategies step-by-step with a premium, Task Manager-inspired interface:
* **FIFO (First-In, First-Out):** Demonstrates strict queue-based eviction and visually highlights **Bélady's Anomaly**.
* **LRU (Least Recently Used):** Demonstrates temporal locality by evicting the most dormant pages.
* **Optimal (Furthest Future Use):** The benchmark theoretical algorithm.

### 3. 🎯 Click-to-Isolate Workload Analysis
See a heavy process crashing your memory? Simply **click on its process chip** in the UI! The simulator will instantly pause the global live feed and completely isolate that process's memory mapped pages, allowing you to run the algorithms specifically against a single app's workload.

### 4. 🧩 Live Segmentation Engine
A visual memory allocator demonstrating contiguous memory allocation.
* Ingests real Windows processes and visually allocates them into simulated physical memory.
* Select between **First-Fit, Best-Fit, Worst-Fit, and Next-Fit** to see how your live Windows apps generate Internal and External Fragmentation.

---

## 🚀 Getting Started

### Prerequisites
* Windows OS (Required for live PowerShell process telemetry)
* Python 3.10+

### Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Aamod007/VPS-Windows.git
   cd VPS-Windows
   ```

2. **Install dependencies:**
   ```bash
   pip install flask
   ```

3. **Run the Simulator Server:**
   ```bash
   python app.py
   ```

4. **Launch Application:**
   Open your browser and navigate to: `http://127.0.0.1:5000`

---

## 📁 Project Structure

* **`app.py`**: The core Flask backend API. Handles routing, data orchestration, CPU volatility mapping, and Reference String locality simulation.
* **`get_processes.ps1`**: The PowerShell telemetry collector for fetching precise Windows memory and CPU metrics.
* **`core/`**: The purely mathematical algorithm engines for FIFO, LRU, Optimal, and Segmentation algorithms.
* **`app/`**: The frontend directory containing the raw HTML, Vanilla CSS, and JavaScript generating the dynamic UI and visualizations without relying on heavy frameworks.

---

## 🎨 Design Philosophy

This project rejects basic MVP aesthetics. It features a custom **Jet Black / Glassmorphism** design system engineered to feel like a premium, state-of-the-art developer tool. Real-time data streams, smooth micro-animations, and dynamic polling ensure the UI feels responsive and alive.