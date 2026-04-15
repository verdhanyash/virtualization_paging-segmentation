"""
PDF Documentation Generator for the Virtual Memory Simulator Project.
Run: python generate_documentation.py
Output: OS_PROJECT_Documentation.pdf
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.lib.colors import HexColor, black, white
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, ListFlowable, ListItem, KeepTogether, HRFlowable
)
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.lib.colors import Color
import os

# ────────────────────────────────────────────────────────────────
# CONFIGURATION
# ────────────────────────────────────────────────────────────────

OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "OS_PROJECT_Documentation.pdf")

PRIMARY = HexColor("#1a1a2e")
ACCENT = HexColor("#16213e")
HIGHLIGHT = HexColor("#0f3460")
TEXT_COLOR = HexColor("#222222")
LIGHT_BG = HexColor("#f0f4f8")
CODE_BG = HexColor("#f5f5f5")
BORDER_COLOR = HexColor("#cccccc")
HEADING_COLOR = HexColor("#1a1a2e")
SUBHEADING_COLOR = HexColor("#2c3e50")

# ────────────────────────────────────────────────────────────────
# STYLES
# ────────────────────────────────────────────────────────────────

styles = getSampleStyleSheet()

styles.add(ParagraphStyle(
    name='DocTitle',
    parent=styles['Title'],
    fontSize=26,
    leading=32,
    textColor=HEADING_COLOR,
    spaceAfter=6,
    alignment=TA_CENTER,
    fontName='Helvetica-Bold',
))

styles.add(ParagraphStyle(
    name='DocSubtitle',
    parent=styles['Normal'],
    fontSize=13,
    leading=18,
    textColor=HexColor("#555555"),
    spaceAfter=20,
    alignment=TA_CENTER,
    fontName='Helvetica',
))

styles.add(ParagraphStyle(
    name='H1',
    parent=styles['Heading1'],
    fontSize=20,
    leading=26,
    textColor=HEADING_COLOR,
    spaceBefore=24,
    spaceAfter=12,
    fontName='Helvetica-Bold',
    borderWidth=0,
    borderPadding=0,
))

styles.add(ParagraphStyle(
    name='H2',
    parent=styles['Heading2'],
    fontSize=15,
    leading=20,
    textColor=SUBHEADING_COLOR,
    spaceBefore=16,
    spaceAfter=8,
    fontName='Helvetica-Bold',
))

styles.add(ParagraphStyle(
    name='H3',
    parent=styles['Heading3'],
    fontSize=12,
    leading=16,
    textColor=HexColor("#34495e"),
    spaceBefore=12,
    spaceAfter=6,
    fontName='Helvetica-Bold',
))

styles.add(ParagraphStyle(
    name='BodyText2',
    parent=styles['Normal'],
    fontSize=10,
    leading=15,
    textColor=TEXT_COLOR,
    spaceAfter=8,
    alignment=TA_JUSTIFY,
    fontName='Helvetica',
))

styles.add(ParagraphStyle(
    name='CodeBlock',
    parent=styles['Normal'],
    fontSize=8.5,
    leading=12,
    textColor=HexColor("#333333"),
    fontName='Courier',
    leftIndent=12,
    spaceAfter=8,
    spaceBefore=4,
    backColor=CODE_BG,
))

styles.add(ParagraphStyle(
    name='BulletText',
    parent=styles['Normal'],
    fontSize=10,
    leading=14,
    textColor=TEXT_COLOR,
    leftIndent=24,
    bulletIndent=12,
    spaceAfter=4,
    fontName='Helvetica',
))

styles.add(ParagraphStyle(
    name='InlineCode',
    parent=styles['Normal'],
    fontSize=9,
    fontName='Courier',
    textColor=HexColor("#c0392b"),
))


def heading(text, level=1):
    style_name = f'H{level}' if level <= 3 else 'H3'
    return Paragraph(text, styles[style_name])


def body(text):
    return Paragraph(text, styles['BodyText2'])


def code(text):
    escaped = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    return Paragraph(f"<pre>{escaped}</pre>", styles['CodeBlock'])


def bullet_list(items):
    """Create a bullet list from a list of strings."""
    flowables = []
    for item in items:
        flowables.append(Paragraph(f"• {item}", styles['BulletText']))
    return flowables


def separator():
    return HRFlowable(width="100%", thickness=0.5, color=BORDER_COLOR, spaceBefore=8, spaceAfter=8)


def table_block(data, col_widths=None):
    """Create a styled table."""
    t = Table(data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HIGHLIGHT),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8.5),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, LIGHT_BG]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    return t


# ────────────────────────────────────────────────────────────────
# DOCUMENT CONTENT
# ────────────────────────────────────────────────────────────────

def build_document():
    doc = SimpleDocTemplate(
        OUTPUT_FILE,
        pagesize=A4,
        leftMargin=0.8*inch,
        rightMargin=0.8*inch,
        topMargin=0.7*inch,
        bottomMargin=0.7*inch,
        title="Virtual Memory Simulator — Project Documentation",
        author="Yash Vardhan",
    )

    story = []
    W = doc.width  # usable width

    # ═══════════════════════════════════════════════════════════
    # TITLE PAGE
    # ═══════════════════════════════════════════════════════════
    story.append(Spacer(1, 1.5*inch))
    story.append(Paragraph(
        "Real-Time Windows<br/>Virtual Memory Simulator",
        styles['DocTitle']
    ))
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph(
        "Comprehensive Project Documentation",
        styles['DocSubtitle']
    ))
    story.append(Spacer(1, 0.3*inch))
    story.append(separator())
    story.append(Spacer(1, 0.15*inch))
    story.append(Paragraph(
        "<b>Subject:</b> Operating Systems   |   <b>Stack:</b> Python · Flask · Chart.js<br/>"
        "<b>Platform:</b> Windows (Live Process Telemetry)   |   <b>Deployment:</b> Vercel / Heroku",
        ParagraphStyle('CenterMeta', parent=styles['Normal'], fontSize=10,
                       leading=15, alignment=TA_CENTER, textColor=HexColor("#555555"))
    ))
    story.append(Spacer(1, 0.15*inch))
    story.append(separator())
    story.append(PageBreak())

    # ═══════════════════════════════════════════════════════════
    # TABLE OF CONTENTS (Manual)
    # ═══════════════════════════════════════════════════════════
    story.append(heading("Table of Contents"))
    toc_items = [
        "1. Project Title & Abstract",
        "2. Tech Stack",
        "3. System Architecture",
        "4. Project Directory Structure",
        "5. File-by-File Deep Dive",
        "6. Algorithm Implementations",
        "7. Real-Time Data Integration",
        "8. Dummy Data Logic",
        "9. Key Design Decisions",
    ]
    for item in toc_items:
        story.append(Paragraph(item, ParagraphStyle(
            'TOCItem', parent=styles['Normal'], fontSize=11,
            leading=18, leftIndent=20, fontName='Helvetica',
            textColor=HEADING_COLOR
        )))
    story.append(PageBreak())

    # ═══════════════════════════════════════════════════════════
    # 1. PROJECT TITLE & ABSTRACT
    # ═══════════════════════════════════════════════════════════
    story.append(heading("1. Project Title & Abstract"))
    story.append(Spacer(1, 4))

    story.append(heading("Project Title", 2))
    story.append(body(
        "<b>Real-Time Windows Virtual Memory Simulator</b> — A high-fidelity, web-based pedagogical tool that simulates "
        "and visualises core Operating System virtual memory management algorithms, driven by live Windows process telemetry."
    ))

    story.append(heading("Abstract", 2))
    story.append(body(
        "Virtual memory management is one of the most critical subsystems in any modern operating system. "
        "It creates the illusion that each process has its own large, contiguous address space, while in reality "
        "the physical memory (RAM) is finite and shared among all running processes. The two foundational mechanisms "
        "enabling this illusion are <b>paging</b> (fixed-size memory management) and <b>segmentation</b> (variable-size "
        "logical memory management)."
    ))
    story.append(body(
        "This project implements a <b>complete, interactive simulator</b> for both paradigms. On the paging side, it "
        "implements three classical page replacement algorithms — <b>FIFO</b>, <b>LRU</b>, and <b>Optimal</b> — and "
        "includes detection and visualisation of <b>Bélady's Anomaly</b>. On the segmentation side, it implements four "
        "memory allocation strategies — <b>First Fit</b>, <b>Best Fit</b>, <b>Worst Fit</b>, and <b>Next Fit</b> — "
        "along with segment deallocation, memory compaction, address translation with bounds checking, and fragmentation analysis."
    ))
    story.append(body(
        "What sets this project apart from typical OS course simulators is its <b>real-time data integration</b>. Rather "
        "than relying solely on hardcoded or random test sequences, the simulator connects directly to the live Windows "
        "operating system via PowerShell's <font face='Courier' size='9'>Get-Process</font> cmdlet. It fetches actual CPU "
        "execution times and working set memory sizes of currently running processes (e.g., Chrome, VS Code, explorer.exe) "
        "and transforms those into realistic page reference strings and segmentation workloads. This bridges the gap "
        "between textbook theory and real-world OS behaviour."
    ))

    story.append(heading("Academic / OS Relevance", 2))
    story.append(body(
        "This project directly addresses core curriculum topics in Operating Systems courses:"
    ))
    story.extend(bullet_list([
        "<b>Virtual Memory & Paging:</b> Demonstrates how a fixed-size page replacement system works, including page faults, frame allocation, and eviction policies.",
        "<b>Page Replacement Algorithms:</b> FIFO, LRU, and Optimal are the three canonical algorithms taught in every OS textbook (Silberschatz, Tanenbaum, Stallings).",
        "<b>Bélady's Anomaly:</b> A counter-intuitive phenomenon where FIFO can produce MORE page faults with MORE frames — the project detects and visually highlights this.",
        "<b>Memory Segmentation:</b> Variable-size memory allocation with logical segments (code, stack, heap, data), demonstrating how real programs partition memory.",
        "<b>Fragmentation:</b> Both internal fragmentation (wasted space within allocated blocks due to alignment) and external fragmentation (scattered free holes between segments).",
        "<b>Allocation Strategies:</b> First Fit, Best Fit, Worst Fit, and Next Fit — each with different performance and fragmentation trade-offs.",
        "<b>Memory Compaction:</b> The process of sliding segments contiguously to eliminate external fragmentation.",
        "<b>Address Translation:</b> Converting (segment, offset) pairs to physical addresses with bounds checking, mirroring how a real MMU operates.",
    ]))
    story.append(PageBreak())

    # ═══════════════════════════════════════════════════════════
    # 2. TECH STACK
    # ═══════════════════════════════════════════════════════════
    story.append(heading("2. Tech Stack"))

    story.append(heading("2.1 Backend / Core Logic", 2))

    tech_data = [
        ["Library / Tool", "Version", "What It Is", "Why Chosen", "How Used in This Project"],
        [
            "Flask",
            "3.1.0",
            "Lightweight Python web micro-framework for building REST APIs and serving HTML.",
            "Minimal boilerplate, no forced project structure, perfect for a simulator that needs a thin API layer on top of pure Python algorithm code.",
            "Serves all HTML pages (index, fifo, lru, optimal, segmentation), exposes REST API endpoints (/api/simulate, /api/segmentation, /api/realtime-algorithms, /api/live-segmentation, /api/realtime-date). Handles request parsing, JSON serialization, and error responses."
        ],
        [
            "Gunicorn",
            "23.0.0",
            "Production-grade WSGI HTTP server for Python web apps.",
            "The standard for deploying Flask in production (Heroku, cloud VMs). Handles concurrency via pre-fork worker model.",
            "Referenced in Procfile for Heroku deployment: 'web: gunicorn app:flask_app'. Not used during local development (Flask's built-in server suffices)."
        ],
        [
            "Pytest",
            "8.3.4",
            "Python's most popular testing framework with fixtures, parametrization, and assertion introspection.",
            "Clean syntax (plain assert), automatic test discovery, rich error messages. Industry standard for Python projects.",
            "Runs all unit tests in the tests/ directory: test_engine.py, test_fifo.py, test_lru.py, test_optimal.py, test_segmentation.py. Tests cover correctness of algorithms, edge cases, and error handling."
        ],
        [
            "Plotly",
            "5.20.0",
            "Interactive graphing library for Python. Can generate server-side chart figures as JSON or HTML.",
            "Produces rich, interactive charts with hover tooltips, zooming, and annotations. Charts can be serialized to JSON for frontend consumption.",
            "Used in the visualization/ package: charts.py (bar/line/heatmap for individual algorithms), comparison.py (side-by-side algorithm comparison charts), belady_chart.py (Bélady's Anomaly detection chart with annotation overlays). All use the 'go.Figure' API."
        ],
        [
            "PyQt5",
            "5.15.11",
            "Python bindings for the Qt5 application framework. Provides QDateTime for precise system clock access.",
            "QDateTime provides nanosecond-precision timestamps independent of Python's datetime. Used as an optional enhancement for real-time tick generation.",
            "Optionally imported in app.py. If available, _get_realtime_tick() uses QDateTime.currentDateTime().toSecsSinceEpoch() for the tick counter. If unavailable, gracefully falls back to Python's datetime.now().timestamp(). Also used for date formatting in _get_realtime_date_payload()."
        ],
        [
            "Python stdlib: json",
            "Built-in",
            "JSON parsing and serialization.",
            "Standard library — no dependency needed.",
            "Parses PowerShell JSON output for process snapshots. Parses incoming operation JSON from API requests. Used throughout app.py."
        ],
        [
            "Python stdlib: subprocess",
            "Built-in",
            "Spawn and manage child processes from Python.",
            "The only way to invoke PowerShell commands from Python and capture their output.",
            "Used in _get_windows_process_snapshot() to run 'powershell -NoProfile -Command ...' and capture the JSON output of Get-Process. Includes timeout (5s), error handling, and encoding configuration."
        ],
        [
            "Python stdlib: threading",
            "Built-in",
            "Thread-based parallelism and synchronization primitives.",
            "Needed to protect the shared live reference stream (global deque) from race conditions when multiple HTTP requests arrive concurrently.",
            "threading.Lock (_LIVE_REFERENCE_LOCK) guards all mutations of the global _LIVE_REFERENCE_STREAM deque in _next_live_reference()."
        ],
        [
            "Python stdlib: collections",
            "Built-in",
            "Specialized container data types: deque, OrderedDict, etc.",
            "deque provides O(1) append/popleft (perfect for FIFO queue). OrderedDict tracks insertion order with O(1) move-to-end (perfect for LRU).",
            "deque: Used in core/fifo.py for the FIFO insertion-order queue, and in app.py for the live reference stream buffer (maxlen=120). OrderedDict: Used in core/lru.py to track page recency — move_to_end() on hit, popitem(last=False) for LRU eviction."
        ],
        [
            "Python stdlib: math",
            "Built-in",
            "Mathematical functions.",
            "Needed for math.ceil() to perform block-size alignment in segmentation.",
            "Used in core/segmentation.py: _align() method uses math.ceil(size / block_size) * block_size to round allocation sizes up to the nearest block boundary."
        ],
    ]

    story.append(table_block(tech_data, col_widths=[W*0.14, W*0.06, W*0.18, W*0.26, W*0.36]))
    story.append(Spacer(1, 12))

    story.append(heading("2.2 Frontend Tech Stack", 2))
    story.append(body("The frontend is built with the following technologies (code details not covered per requirement):"))
    story.extend(bullet_list([
        "<b>HTML5:</b> Semantic markup for all 5 pages (index.html, fifo.html, lru.html, optimal.html, segmentation.html).",
        "<b>Vanilla CSS:</b> Custom dark-theme styling with glassmorphism effects, CSS variables, responsive grid layouts, smooth transitions, and micro-animations. No CSS frameworks used.",
        "<b>Vanilla JavaScript (ES6+):</b> fetch() API for AJAX calls to Flask endpoints, DOM manipulation for real-time UI updates, Chart.js integration for client-side charting, dynamic polling with setInterval() for live mode.",
        "<b>Chart.js:</b> Client-side charting library loaded via CDN. Used for bar charts (faults vs hits), line charts (fault progression), and doughnut charts. Configured with the dark theme matching the application's jet-black aesthetic.",
        "<b>Google Fonts:</b> Inter (headings/UI text) and Geist Mono (monospaced data/code displays) loaded via CDN.",
    ]))

    story.append(heading("2.3 Dummy Data Generation", 2))
    story.append(body(
        "Dummy/simulated data is generated at two levels:"
    ))
    story.extend(bullet_list([
        "<b>Default Reference String:</b> The API defaults to the classic Bélady's anomaly sequence [7,0,1,2,0,3,0,4,2,3,0,3,2] when no parameters are provided.",
        "<b>Synthetic Live Stream (_next_live_reference):</b> When live mode is active but Windows process data is unavailable, a deterministic synthetic reference string is generated using tick-based arithmetic with locality patterns. It alternates between temporal locality bursts (repeating recent pages) and calculated jumps to simulate realistic page access patterns.",
        "<b>Deterministic Segmentation Ops (_build_live_segmentation_operations):</b> Generates a fixed pattern of alloc/free/compact operations with sizes that vary based on the current timestamp tick, producing time-varying but deterministic workloads.",
    ]))

    story.append(heading("2.4 Real-Time System Data Collection", 2))
    story.append(body(
        "The simulator collects live Windows process data using PowerShell's Get-Process cmdlet invoked via Python's subprocess module. "
        "The command <font face='Courier' size='9'>Get-Process | Where-Object { $_.CPU -gt 0 } | Sort-Object CPU -Descending | "
        "Select-Object ProcessName, Id, CPU, @{N='WS';E={$_.WorkingSet64}} | ConvertTo-Json</font> fetches the top processes "
        "sorted by CPU execution time. The JSON output is then parsed, and processes are grouped by name, with CPU times and "
        "working set sizes aggregated. This real data drives both the page reference string generation (via volatility-weighted "
        "page assignments) and the segmentation workload generation (via proportional segment budget allocation)."
    ))
    story.append(PageBreak())

    # ═══════════════════════════════════════════════════════════
    # 3. SYSTEM ARCHITECTURE
    # ═══════════════════════════════════════════════════════════
    story.append(heading("3. System Architecture"))

    story.append(heading("3.1 Component-Level Architecture", 2))
    story.append(body(
        "The system follows a classic <b>three-tier architecture</b>: a browser-based frontend (presentation tier), "
        "a Flask HTTP server (application tier), and pure Python algorithm engines (logic tier). The tiers communicate "
        "via JSON over HTTP REST APIs."
    ))

    arch_data = [
        ["Tier", "Components", "Responsibility"],
        ["Presentation\n(Frontend)", "app/*.html\nVanilla JS\nChart.js\nCSS", "User interface, input forms, real-time visualisations, polling loop, chart rendering"],
        ["Application\n(Flask Server)", "app.py\nFlask routes\nAPI endpoints", "HTTP request handling, parameter validation, live data orchestration, response serialisation, process snapshot collection via PowerShell"],
        ["Logic\n(Algorithm Engines)", "core/engine.py\ncore/fifo.py\ncore/lru.py\ncore/optimal.py\ncore/segmentation.py", "Pure algorithmic computation — page replacement simulation, segmentation allocation, fragmentation analysis, address translation. Zero I/O or HTTP awareness."],
        ["Visualisation\n(Server-Side Charts)", "visualization/charts.py\nvisualization/comparison.py\nvisualization/belady_chart.py", "Plotly-based chart generation for faults/hits bars, fault progression lines, heatmaps, algorithm comparison, and Bélady's anomaly detection."],
        ["Testing", "tests/test_*.py", "Pytest unit tests covering all algorithm correctness, edge cases, and error handling."],
    ]
    story.append(table_block(arch_data, col_widths=[W*0.15, W*0.30, W*0.55]))
    story.append(Spacer(1, 12))

    story.append(heading("3.2 Data Flow", 2))
    story.append(body("<b>Manual Mode (Dummy Data):</b>"))
    story.extend(bullet_list([
        "User enters reference string + frame count + algorithm choice in the browser form.",
        "Browser sends POST /api/simulate with JSON body {reference_string, frames, algorithm}.",
        "app.py validates inputs via _normalize_reference_string(), calls _build_paging_payload().",
        "_build_paging_payload() invokes run_fifo(), run_lru(), run_optimal() from core/, plus detect_beladys_anomaly().",
        "Results (steps, faults, hits, Bélady data) are JSON-serialized and returned to the browser.",
        "JavaScript parses response, updates DOM tables, renders Chart.js charts.",
    ]))

    story.append(body("<b>Live Mode (Real-Time Windows Data):</b>"))
    story.extend(bullet_list([
        "Browser polls GET /api/realtime-algorithms?live=1&live_source=windows every few seconds.",
        "app.py calls _build_windows_live_reference() which invokes _get_windows_process_snapshot().",
        "_get_windows_process_snapshot() runs a PowerShell command via subprocess, parses the JSON output.",
        "Process data is grouped, ranked by CPU volatility, and mapped to virtual pages proportionally.",
        "A reference string is synthesised using weighted random selection with locality-of-reference patterns (70% spatial, 20% temporal, 10% random).",
        "The reference string feeds into all three algorithms; results are returned with process metadata.",
        "For segmentation: real process memory sizes are proportionally allocated as segments (.text, .heap, .data, .stack).",
    ]))

    story.append(body("<b>Segmentation Mode:</b>"))
    story.extend(bullet_list([
        "User submits operations via POST /api/segmentation or triggers live via GET /api/live-segmentation.",
        "app.py calls simulate_fragmentation() from core/segmentation.py with the operation list and strategy.",
        "simulate_fragmentation() creates a SegmentTable and replays each operation (alloc/free/compact), capturing a snapshot after each step.",
        "Each snapshot includes: segment table state, memory map, free holes, fragmentation stats.",
        "Results are returned as a list of snapshots that the frontend renders as an animated memory map.",
    ]))
    story.append(PageBreak())

    # ═══════════════════════════════════════════════════════════
    # 4. PROJECT DIRECTORY STRUCTURE
    # ═══════════════════════════════════════════════════════════
    story.append(heading("4. Project Directory Structure"))

    dir_data = [
        ["Path", "Type", "Role"],
        ["app.py", "File", "Main Flask application. All HTTP routes, API endpoints, real-time data orchestration, PowerShell integration, and live reference string generation."],
        ["requirements.txt", "File", "Python dependency manifest: flask, gunicorn, pytest, plotly, PyQt5."],
        ["Procfile", "File", "Heroku deployment config: 'web: gunicorn app:flask_app'."],
        ["vercel.json", "File", "Vercel serverless deployment config. Routes all requests to app.py via @vercel/python."],
        ["get_processes.ps1", "File", "Standalone PowerShell script for fetching top 30 Windows processes with memory metrics (WS, VM, PM, threads, handles). Used for manual debugging/testing."],
        [".gitignore", "File", "Git ignore rules for __pycache__, venv, IDE files, OS files, test caches, logs."],
        ["README.md", "File", "Project overview, features, getting started guide, directory structure, design philosophy."],
        ["DEPLOY_VERCEL.md", "File", "Vercel-specific deployment instructions."],
        ["insane.txt", "File", "Project roadmap/task tracker with detailed per-task descriptions and completion status."],
        ["core/", "Directory", "Algorithm engine package — all pure Python implementations. Zero I/O."],
        ["core/__init__.py", "File", "Package init. Exports PageTable, FramePool, translate_address, detect_page_fault."],
        ["core/engine.py", "File", "Core infrastructure: PageTable class (page↔frame mapping), FramePool class (frame allocation/deallocation), translate_address() (virtual→physical), detect_page_fault()."],
        ["core/fifo.py", "File", "FIFO page replacement algorithm (run_fifo) + Bélady's Anomaly detection (detect_beladys_anomaly)."],
        ["core/lru.py", "File", "LRU page replacement algorithm (run_lru) using OrderedDict for O(1) recency tracking."],
        ["core/optimal.py", "File", "Optimal (MIN/OPT) page replacement algorithm (run_optimal) with future look-ahead via _find_optimal_victim()."],
        ["core/segmentation.py", "File", "Full segmentation engine: Segment class, SegmentTable class (allocation, deallocation, compaction, translation, fragmentation stats, memory map), simulate_fragmentation() runner. 677 lines."],
        ["app/", "Directory", "Frontend directory served by Flask. Contains all HTML pages."],
        ["app/index.html", "File", "Home/landing page with FIFO simulator, algorithm overview, dark-theme UI."],
        ["app/fifo.html", "File", "Dedicated FIFO page replacement simulator with live mode, process chips, Bélady's detection."],
        ["app/lru.html", "File", "Dedicated LRU page replacement simulator with all the same live features."],
        ["app/optimal.html", "File", "Dedicated Optimal page replacement simulator page."],
        ["app/segmentation.html", "File", "Segmentation simulator. Memory map visualisation, strategy selector, alloc/free/compact operations, fragmentation gauges, segment tables. ~51KB of HTML/CSS/JS."],
        ["visualization/", "Directory", "Server-side Plotly chart generation package."],
        ["visualization/__init__.py", "File", "Empty package init."],
        ["visualization/charts.py", "File", "Individual algorithm charts: faults-vs-hits bar, fault progression line, frame heatmap, hit/fault timeline."],
        ["visualization/comparison.py", "File", "Cross-algorithm comparison: run_all_algorithms(), grouped bar chart, cumulative fault race line chart, summary table."],
        ["visualization/belady_chart.py", "File", "Bélady's Anomaly visualisation: line chart with anomaly-pair annotations, shaded violation zones, per-point styling."],
        ["tests/", "Directory", "Pytest unit test suite."],
        ["tests/test_engine.py", "File", "Tests for PageTable, FramePool, translate_address, detect_page_fault. 84 lines."],
        ["tests/test_fifo.py", "File", "Tests for run_fifo and detect_beladys_anomaly with classic Bélady sequence. 41 lines."],
        ["tests/test_lru.py", "File", "Tests for run_lru: classic sequence, eviction order, large-frame edge case. 39 lines."],
        ["tests/test_optimal.py", "File", "Tests for run_optimal and _find_optimal_victim: correctness, all-hits, large-frames. 55 lines."],
        ["tests/test_segmentation.py", "File", "Comprehensive segmentation tests: Segment class, allocation, strategies, translation, deallocation, fragmentation, compaction, simulation, memory map. 375 lines."],
        ["docs/", "Directory", "Documentation assets."],
        ["docs/overview_demo.webp", "File", "Demo screenshot/recording of the application UI."],
    ]

    story.append(table_block(dir_data, col_widths=[W*0.22, W*0.08, W*0.70]))
    story.append(PageBreak())

    # ═══════════════════════════════════════════════════════════
    # 5. FILE-BY-FILE DEEP DIVE
    # ═══════════════════════════════════════════════════════════
    story.append(heading("5. File-by-File Deep Dive"))

    # ─── core/__init__.py ─────────────────────────────────────
    story.append(heading("5.1 core/__init__.py", 2))
    story.append(body("<b>Purpose:</b> Package initialiser for the core module. Makes the core directory importable as a Python package and re-exports the primary engine classes for convenient top-level imports."))
    story.append(body("<b>Imports:</b>"))
    story.extend(bullet_list([
        "<font face='Courier' size='9'>from .engine import PageTable, FramePool, translate_address, detect_page_fault</font> — Re-exports all public API from engine.py so consumers can do <font face='Courier' size='9'>from core import PageTable</font> instead of <font face='Courier' size='9'>from core.engine import PageTable</font>.",
    ]))
    story.append(body("<b>Global Variables:</b>"))
    story.extend(bullet_list([
        "<font face='Courier' size='9'>__all__</font> — Explicit export list controlling what <font face='Courier' size='9'>from core import *</font> would import: [\"PageTable\", \"FramePool\", \"translate_address\", \"detect_page_fault\"].",
    ]))

    # ─── core/engine.py ───────────────────────────────────────
    story.append(heading("5.2 core/engine.py — Core Infrastructure (T1)", 2))
    story.append(body("<b>Purpose:</b> Provides the foundational building blocks for virtual memory simulation: a page table, a frame pool, address translation, and page fault detection. These are the base components that the replacement algorithms (FIFO, LRU, Optimal) build upon."))

    story.append(body("<b>Imports:</b>"))
    story.extend(bullet_list([
        "<font face='Courier' size='9'>from __future__ import annotations</font> — Enables PEP 604 style type hints (<font face='Courier' size='9'>int | None</font>) in Python 3.9+.",
        "<font face='Courier' size='9'>from typing import Optional, Dict, List, Tuple</font> — Type hint constructors for function signatures and class attributes.",
    ]))

    story.append(heading("Class: PageTable", 3))
    story.append(body("Manages the mapping between virtual page numbers and physical frame numbers. Internally uses a dictionary <font face='Courier' size='9'>_mappings: Dict[int, int]</font>."))

    funcs = [
        ["Method", "Signature", "Purpose", "Parameters", "Returns", "Edge Cases"],
        ["__init__", "__init__(self) -> None", "Initialise empty page table with an empty dictionary.", "None", "None", "N/A"],
        ["map_page", "map_page(self, virtual: int, physical: int) -> None", "Create a virtual→physical mapping.", "virtual: page number\nphysical: frame number", "None", "Raises ValueError if either is negative."],
        ["lookup", "lookup(self, virtual: int) -> Optional[int]", "Return the physical frame for a virtual page.", "virtual: page number", "Frame number or None", "Returns None if page not mapped."],
        ["is_loaded", "is_loaded(self, page: int) -> bool", "Check if a page is currently in memory.", "page: page number", "True/False", "N/A"],
        ["unmap_page", "unmap_page(self, virtual: int) -> Optional[int]", "Remove a page mapping, returning the freed frame.", "virtual: page number", "Freed frame or None", "Returns None if not mapped (no error)."],
        ["get_all_mappings", "get_all_mappings(self) -> Dict[int, int]", "Return a copy of all current mappings.", "None", "Dict copy", "Returns empty dict if no mappings."],
    ]
    story.append(table_block(funcs, col_widths=[W*0.10, W*0.22, W*0.20, W*0.16, W*0.14, W*0.18]))
    story.append(Spacer(1, 8))

    story.append(heading("Class: FramePool", 3))
    story.append(body("Manages a pool of physical memory frames using two sets: <font face='Courier' size='9'>_free_frames</font> and <font face='Courier' size='9'>_allocated_frames</font>. Provides O(1) allocation checks and O(n) allocation (uses min() to always allocate the lowest-numbered free frame for determinism)."))

    fp_funcs = [
        ["Method", "Purpose", "Key Logic"],
        ["__init__(total_frames)", "Initialise pool with N frames, all free.", "Creates set(range(total_frames)) as free frames. Raises ValueError if total_frames <= 0."],
        ["allocate() -> Optional[int]", "Allocate the lowest free frame.", "Returns min(free_frames), moves it to allocated_frames. Returns None if no free frames."],
        ["free(frame) -> bool", "Return an allocated frame to the free pool.", "Validates range [0, total). Returns False if frame wasn't allocated (not an error). Raises ValueError if out of range."],
        ["get_free_count() -> int", "Count of unallocated frames.", "Returns len(_free_frames)."],
        ["get_all_frames() -> List", "Full frame state array.", "Returns list where allocated frames show their number, free frames show None."],
        ["is_full() -> bool", "Check if all frames allocated.", "Returns len(_free_frames) == 0."],
    ]
    story.append(table_block(fp_funcs, col_widths=[W*0.25, W*0.30, W*0.45]))
    story.append(Spacer(1, 8))

    story.append(heading("Function: translate_address", 3))
    story.append(body("Translates a virtual address into a (page_number, offset) tuple by computing <font face='Courier' size='9'>page = address // page_size</font> and <font face='Courier' size='9'>offset = address % page_size</font>. Raises ValueError for negative addresses or non-positive page sizes."))

    story.append(heading("Function: detect_page_fault", 3))
    story.append(body("Returns True if the given page number is NOT loaded in the given PageTable (i.e., a page fault would occur). Simple wrapper: <font face='Courier' size='9'>return not page_table.is_loaded(page_number)</font>."))

    story.append(PageBreak())

    # ─── core/fifo.py ─────────────────────────────────────────
    story.append(heading("5.3 core/fifo.py — FIFO Page Replacement (T2)", 2))
    story.append(body("<b>Purpose:</b> Implements the FIFO (First-In, First-Out) page replacement algorithm and Bélady's Anomaly detection."))
    story.append(body("<b>Imports:</b>"))
    story.extend(bullet_list([
        "<font face='Courier' size='9'>from collections import deque</font> — Used as the FIFO queue to track page insertion order. O(1) append and popleft.",
        "<font face='Courier' size='9'>from typing import Optional, Dict, List, Tuple</font> — Type annotations.",
    ]))

    story.append(heading("Function: run_fifo(reference_string, frames) -> Dict", 3))
    story.append(body(
        "<b>Purpose:</b> Simulates FIFO page replacement on a given reference string with a given number of frames."
    ))
    story.append(body("<b>Data Structures:</b>"))
    story.extend(bullet_list([
        "<font face='Courier' size='9'>frame_list: List[Optional[int]]</font> — Array of frame slots (None = empty). Represents the physical frames.",
        "<font face='Courier' size='9'>queue: deque[int]</font> — Insertion-order tracker. The leftmost element is the oldest page (first candidate for eviction).",
        "<font face='Courier' size='9'>page_to_frame: Dict[int, int]</font> — Reverse lookup from page number → frame index for O(1) page presence checks.",
    ]))
    story.append(body("<b>Step-by-step Logic:</b>"))
    story.extend(bullet_list([
        "For each page in the reference string:",
        "  → Check if page is in page_to_frame (O(1) dict lookup). If yes = HIT, no action needed.",
        "  → If not found = PAGE FAULT. Call _find_free_frame() to find an empty frame slot.",
        "  → If free frame exists: place page in that frame, add to queue and page_to_frame.",
        "  → If no free frame: pop the oldest page from queue (popleft), remove it from page_to_frame, place new page in its frame slot, add new page to queue and page_to_frame.",
        "  → Record step: {page, frames snapshot, fault flag, evicted page}.",
        "Return: {algorithm, reference_string, frame_count, steps, total_faults, total_hits, fault_positions}.",
    ]))

    story.append(heading("Function: _find_free_frame(frame_list) -> Optional[int]", 3))
    story.append(body("Scans the frame list linearly and returns the index of the first None (free) slot. Returns None if all frames are occupied. O(n) where n = frame count."))

    story.append(heading("Function: detect_beladys_anomaly(reference_string, max_frames) -> Dict", 3))
    story.append(body(
        "<b>Purpose:</b> Detects Bélady's Anomaly by running FIFO for every frame count from 1 to max_frames and checking if faults ever increase when frames increase."
    ))
    story.append(body("<b>Logic:</b> For each frame count f in [1, max_frames], run run_fifo() and record fault count. Then compare: if fault_counts[f+1] > fault_counts[f], that pair (f, f+1) is an anomaly. Returns {anomaly_found: bool, fault_counts: {f: count}, anomaly_at: [(a,b),...]}."))
    story.append(Spacer(1, 8))

    # ─── core/lru.py ──────────────────────────────────────────
    story.append(heading("5.4 core/lru.py — LRU Page Replacement (T3)", 2))
    story.append(body("<b>Purpose:</b> Implements Least Recently Used page replacement using Python's OrderedDict."))
    story.append(body("<b>Imports:</b>"))
    story.extend(bullet_list([
        "<font face='Courier' size='9'>from collections import OrderedDict</font> — Maintains insertion order AND supports O(1) move_to_end(). The first item is always the least recently used.",
        "<font face='Courier' size='9'>from typing import Dict, List, Optional</font> — Type annotations.",
    ]))

    story.append(heading("Function: run_lru(reference_string, frames) -> Dict", 3))
    story.append(body("<b>Data Structure:</b> <font face='Courier' size='9'>memory: OrderedDict[int, bool]</font> — Keys are page numbers, values are dummy True. Order represents recency: first item = LRU, last item = MRU."))
    story.append(body("<b>Step-by-step Logic:</b>"))
    story.extend(bullet_list([
        "For each page in the reference string:",
        "  → If page IN memory: HIT. Call memory.move_to_end(page) to mark it as most recently used. O(1).",
        "  → If page NOT in memory: FAULT.",
        "    → If memory is full (len >= frames): evict LRU page via memory.popitem(last=False). This removes the first (oldest) item. O(1).",
        "    → Insert new page: memory[page] = True. It goes to the end (most recent). O(1).",
        "  → Build frame state: list(memory.keys()), padded with None to frame count.",
        "  → Record step: {page, frames, fault, evicted}.",
    ]))
    story.append(body("<b>Why OrderedDict over a list:</b> A naive list-based LRU requires O(n) removal and re-insertion on every hit. OrderedDict provides O(1) move_to_end(), making it optimal for LRU simulation."))

    story.append(PageBreak())

    # ─── core/optimal.py ──────────────────────────────────────
    story.append(heading("5.5 core/optimal.py — Optimal Page Replacement (T4)", 2))
    story.append(body("<b>Purpose:</b> Implements the Optimal (MIN/OPT/Clairvoyant) page replacement algorithm that evicts the page whose next use is farthest in the future."))
    story.append(body("<b>Imports:</b>"))
    story.extend(bullet_list([
        "<font face='Courier' size='9'>from typing import Dict, List, Optional</font> — Type annotations.",
    ]))

    story.append(heading("Function: _find_optimal_victim(loaded_pages, future_refs) -> int", 3))
    story.append(body("<b>Purpose:</b> Given the currently loaded pages and the remaining reference string, find which page to evict."))
    story.append(body("<b>Logic:</b>"))
    story.extend(bullet_list([
        "For each loaded page, search for its next occurrence in future_refs using list.index().",
        "If a page is NEVER used again (ValueError from .index()): return it immediately — best eviction candidate.",
        "Otherwise, track which page has the maximum (farthest) next-use index.",
        "Return the page with the farthest next-use. This guarantees minimum total page faults (proven optimal by Bélády, 1966).",
        "<b>Time Complexity:</b> O(loaded_pages × future_refs length) in the worst case. Acceptable since frames and reference strings are small in simulation.",
    ]))

    story.append(heading("Function: run_optimal(reference_string, frames) -> Dict", 3))
    story.append(body("<b>Logic:</b> Same structure as FIFO but with different eviction policy:"))
    story.extend(bullet_list([
        "For each page at index idx:",
        "  → If page in frame_list: HIT — no action.",
        "  → If page not in frame_list: FAULT.",
        "    → If free frame exists (None in frame_list): use it.",
        "    → If no free frame: compute future_refs = reference_string[idx+1:], call _find_optimal_victim(), evict the chosen page.",
        "  → Record step as usual.",
    ]))
    story.append(body("<b>Key Difference:</b> Unlike FIFO (which evicts the oldest regardless of future use) and LRU (which approximates future use via past recency), Optimal has perfect future knowledge. This makes it impractical for real systems but invaluable as a benchmark for comparing other algorithms."))

    story.append(Spacer(1, 8))

    # ─── core/segmentation.py ─────────────────────────────────
    story.append(heading("5.6 core/segmentation.py — Segmentation Engine (T5)", 2))
    story.append(body("<b>Purpose:</b> Complete segmentation memory management simulator. 677 lines implementing variable-size segment allocation with 4 strategies, address translation, deallocation, compaction, and fragmentation analysis."))
    story.append(body("<b>Imports:</b>"))
    story.extend(bullet_list([
        "<font face='Courier' size='9'>from __future__ import annotations</font> — Forward reference type hints.",
        "<font face='Courier' size='9'>import math</font> — ceil() for block alignment calculations.",
        "<font face='Courier' size='9'>from typing import Dict, List, Optional</font> — Type annotations.",
    ]))

    story.append(heading("Class: SegmentFaultError(Exception)", 3))
    story.append(body("Custom exception raised on: accessing a non-existent segment, accessing a swapped-out segment, or offset exceeding segment limit. Mirrors the real OS \"Segmentation fault (core dumped)\" error."))

    story.append(heading("Class: Segment", 3))
    story.append(body("Data class representing one memory segment."))
    seg_attrs = [
        ["Attribute", "Type", "Description"],
        ["name", "str", "Logical name: 'code', 'stack', 'heap', etc."],
        ["base", "int", "Starting physical address in memory."],
        ["limit", "int", "Size actually requested by the program (bytes)."],
        ["allocated_size", "int", "Size reserved in memory (>= limit, block-aligned)."],
        ["status", "str", "'loaded' (in RAM) or 'swapped' (on disk)."],
    ]
    story.append(table_block(seg_attrs, col_widths=[W*0.18, W*0.10, W*0.72]))
    story.append(body("Methods: internal_fragmentation() → allocated_size - limit; end_address() → base + allocated_size; to_dict() → serialise to dict."))

    story.append(heading("Class: SegmentTable — The Main Engine", 3))
    story.append(body("Central class managing all of segmented memory. Key internal state:"))
    story.extend(bullet_list([
        "<font face='Courier' size='9'>_total_memory: int</font> — Total physical memory in bytes (default 4096).",
        "<font face='Courier' size='9'>_strategy: str</font> — Active allocation strategy: first_fit, best_fit, worst_fit, or next_fit.",
        "<font face='Courier' size='9'>_block_size: int</font> — Alignment granularity (default 16 bytes). All allocations rounded up to multiples of this.",
        "<font face='Courier' size='9'>_segments: Dict[str, Segment]</font> — Active segment registry keyed by name.",
        "<font face='Courier' size='9'>_next_fit_cursor: int</font> — Tracks where the last allocation ended (for next_fit strategy).",
    ]))

    story.append(body("<b>Method: _align(size) → int</b> — Rounds size up to the next multiple of block_size: <font face='Courier' size='9'>math.ceil(size / block_size) * block_size</font>. Example: 200 → 208 with block_size=16."))
    story.append(body("<b>Method: _get_free_holes() → List[Dict]</b> — Walks through memory left-to-right, finds all gaps between segments and trailing free space. Returns [{base, size}, ...]."))
    story.append(body("<b>Method: _find_hole(needed) → Optional[Dict]</b> — Selects a hole using the active strategy from the list of fitting holes:"))
    story.extend(bullet_list([
        "first_fit: fitting[0] — first hole that fits.",
        "best_fit: min(fitting, key=size) — smallest fitting hole.",
        "worst_fit: max(fitting, key=size) — largest fitting hole.",
        "next_fit: first fitting hole at or after cursor, wrapping around.",
    ]))
    story.append(body("<b>Method: add_segment(name, size) → Segment</b> — Aligns size, finds a hole via _find_hole(), creates a Segment at the hole's base, registers it. Raises ValueError on duplicate name, size ≤ 0, or no fitting hole."))
    story.append(body("<b>Method: free_segment(name) → Dict</b> — Removes the segment from the table, leaving a free hole. Returns details of what was freed and the hole created. Adjacent holes are NOT auto-merged (realistic behaviour)."))
    story.append(body("<b>Method: translate(segment_name, offset) → int</b> — Converts (segment_name, offset) to physical address: base + offset. Raises SegmentFaultError if segment doesn't exist, is swapped out, offset is negative, or offset >= limit."))
    story.append(body("<b>Method: compact() → Dict</b> — Slides all loaded segments to the left, eliminating ALL holes between them. Updates base addresses, resets next_fit cursor. Returns {moves, holes_eliminated, space_recovered}."))
    story.append(body("<b>Method: get_fragmentation_stats() → Dict</b> — Computes: used bytes, requested bytes, internal fragmentation (allocated - requested), external fragmentation (holes between segments, NOT trailing free), total free, utilisation percentage."))
    story.append(body("<b>Method: get_memory_map() → List[Dict]</b> — Returns a complete ordered list of memory blocks covering the entire address space. Each entry is either {type: segment, ...}, {type: hole, ...}, or {type: free, ...} (trailing)."))

    story.append(heading("Function: simulate_fragmentation(operations, ...) → List[Dict]", 3))
    story.append(body("The 'movie' function. Creates a SegmentTable, replays each operation (alloc/free/compact) in sequence, and captures a full snapshot after each step. Errors are caught and recorded per-step without halting the simulation. Returns a list of snapshots that can be animated by the frontend."))

    story.append(PageBreak())

    # ─── app.py ───────────────────────────────────────────────
    story.append(heading("5.7 app.py — Flask Application Server", 2))
    story.append(body("<b>Purpose:</b> The central orchestration layer. Handles all HTTP routing, request validation, live data collection from Windows, reference string generation, and JSON response building. 702 lines."))

    story.append(body("<b>Imports:</b>"))
    imports_data = [
        ["Import", "Why"],
        ["json", "Parse PowerShell JSON output and incoming API operation payloads."],
        ["csv, io", "Available for CSV processing (used in some data export paths)."],
        ["os", "Check os.name ('nt') to detect Windows for PowerShell integration."],
        ["subprocess", "Invoke PowerShell commands to fetch live process data."],
        ["threading", "Lock for thread-safe access to the global live reference stream."],
        ["collections.deque", "Bounded buffer for the live reference stream (maxlen=120)."],
        ["core.segmentation.simulate_fragmentation", "Core segmentation simulation engine."],
        ["flask (Flask, request, jsonify, render_template)", "Web framework primitives."],
        ["core.fifo (run_fifo, detect_beladys_anomaly)", "FIFO algorithm + Bélady detection."],
        ["core.lru.run_lru", "LRU algorithm."],
        ["core.optimal.run_optimal", "Optimal algorithm."],
        ["PyQt5.QtCore.QDateTime (try/except)", "Optional high-precision timestamp. Falls back gracefully."],
    ]
    story.append(table_block(imports_data, col_widths=[W*0.35, W*0.65]))
    story.append(Spacer(1, 8))

    story.append(body("<b>Global Constants and Variables:</b>"))
    globals_data = [
        ["Variable", "Type", "Purpose"],
        ["flask_app", "Flask", "The Flask application instance. Configured with template_folder='app', static_folder='app'."],
        ["VALID_ALGOS", "set", "{'FIFO', 'LRU', 'Optimal'} — validated in _build_paging_payload()."],
        ["VALID_SEGMENTATION_STRATEGIES", "set", "{'first_fit', 'best_fit', 'worst_fit', 'next_fit'}."],
        ["LIVE_REFERENCE_MAXLEN", "int", "120 — maximum length of the live reference stream deque."],
        ["_LIVE_REFERENCE_LOCK", "threading.Lock", "Mutex protecting the shared live reference stream."],
        ["_LIVE_REFERENCE_STREAM", "deque", "Bounded buffer holding the evolving live reference string. Initialised with the classic Bélady sequence."],
        ["_LIVE_LAST_TICK", "int/None", "Timestamp of the last tick processed for the live stream."],
        ["_LIVE_COUNTER", "int", "Monotonic counter incremented each tick for locality pattern generation."],
    ]
    story.append(table_block(globals_data, col_widths=[W*0.22, W*0.12, W*0.66]))
    story.append(Spacer(1, 8))

    story.append(heading("Key Functions in app.py", 3))

    app_funcs = [
        ["Function", "Purpose", "Key Logic"],
        ["_parse_tasklist_mem_kb(mem_text)", "Extract numeric kilobytes from a text string.", "Strips all non-digit chars, converts to int. Used to parse Windows tasklist memory values."],
        ["_get_windows_process_snapshot(limit)", "Fetch live Windows process data via PowerShell.", "Runs 'powershell -NoProfile -Command Get-Process...' via subprocess. Parses JSON output. Returns list of {name, pid, mem_kb, cpu, volatility}. Returns [] on non-Windows or errors."],
        ["_build_windows_live_reference(window_size, max_page)", "Generate a realistic page reference string from real processes.", "Groups processes by name, assigns virtual pages proportional to CPU volatility, builds reference string using weighted random selection with 70% spatial / 20% temporal / 10% random locality patterns."],
        ["_size_from_process_mem(mem_kb)", "Map real process memory to simulated allocation sizes.", "Formula: 64 + ((mem_kb // 128) % 20) * 16. Keeps sizes within [64, 368] bytes for the segmentation simulator."],
        ["_build_windows_segmentation_operations(process_rows, live_tick)", "Build alloc/free/compact operations from real process data.", "Takes top 5 processes, allocates P1-P4, frees P2, optionally compacts (on even ticks), allocates P5."],
        ["_get_realtime_date_payload()", "Get current date/time with theme info.", "Uses QDateTime if available, otherwise datetime.now(). Returns {iso, display, hour, theme: 'day'/'night'}."],
        ["_get_realtime_tick()", "Get current epoch timestamp in seconds.", "Uses QDateTime.toSecsSinceEpoch() or datetime.timestamp()."],
        ["_is_truthy(value)", "Parse boolean query parameters.", "Returns True for '1', 'true', 'yes', 'on' (case-insensitive)."],
        ["_next_live_reference(window_size, max_page)", "Generate synthetic live reference stream.", "Thread-safe (uses Lock). Advances the deque by (current_tick - last_tick) steps. Alternates locality bursts and arithmetic jumps."],
        ["_build_live_segmentation_operations(live_tick)", "Generate deterministic segmentation ops from tick.", "Creates alloc A, alloc B, free A, alloc C, compact, alloc D with sizes varying by tick modular arithmetic."],
        ["_normalize_reference_string(raw)", "Parse and validate reference string input.", "Accepts comma-separated string or list. Converts to List[int]. Rejects empty or negative values."],
        ["_build_paging_payload(ref, frames, algo, max_belady)", "Run all three algorithms and package results.", "Calls run_fifo, run_lru, run_optimal, detect_beladys_anomaly. Returns unified payload with 'current' (selected algo), all three results, and Bélady data."],
    ]
    story.append(table_block(app_funcs, col_widths=[W*0.22, W*0.28, W*0.50]))
    story.append(Spacer(1, 8))

    story.append(heading("API Routes", 3))
    routes_data = [
        ["Route", "Method", "Purpose"],
        ["/", "GET", "Serve index.html (home page with FIFO simulator)."],
        ["/fifo", "GET", "Serve fifo.html (dedicated FIFO page)."],
        ["/lru", "GET", "Serve lru.html (dedicated LRU page)."],
        ["/optimal", "GET", "Serve optimal.html (dedicated Optimal page)."],
        ["/segmentation", "GET", "Serve segmentation.html (segmentation simulator)."],
        ["/api/realtime-date", "GET", "Return current date/time + day/night theme."],
        ["/api/realtime-algorithms", "GET", "Main paging API. Supports live mode (Windows processes or synthetic), manual mode, optional segmentation. Returns paging + segmentation results."],
        ["/api/simulate", "POST", "Stateless paging simulation. Accepts {reference_string, frames, algorithm} in body. Returns all three algorithm results + Bélady data."],
        ["/api/segmentation", "POST", "Stateless segmentation simulation. Accepts {operations, strategy, total_memory, block_size}. Returns snapshots."],
        ["/api/live-segmentation", "GET", "Live segmentation driven by real Windows processes. Fetches process data, builds proportional allocations with .text/.heap/.data/.stack segments, runs simulation."],
    ]
    story.append(table_block(routes_data, col_widths=[W*0.22, W*0.08, W*0.70]))

    story.append(PageBreak())

    # ─── visualization files ──────────────────────────────────
    story.append(heading("5.8 visualization/charts.py — Individual Algorithm Charts", 2))
    story.append(body("<b>Purpose:</b> Plotly chart builders for visualising a single algorithm's results."))
    story.append(body("<b>Import:</b> <font face='Courier' size='9'>plotly.graph_objects as go</font> — Plotly's object-oriented chart API."))
    story.append(body("<b>Functions:</b>"))
    story.extend(bullet_list([
        "plot_faults_hits(result) — Grouped bar chart showing total faults vs hits for one algorithm.",
        "plot_fault_progression(result) — Line chart showing cumulative faults over each step.",
        "plot_frame_heatmap(result) — Heatmap showing which pages are in which frames at each time step. None slots mapped to -1.",
        "plot_hit_fault_timeline(result) — Scatter plot showing fault (1) vs hit (0) at each step.",
    ]))

    story.append(heading("5.9 visualization/comparison.py — Cross-Algorithm Comparison", 2))
    story.append(body("<b>Purpose:</b> Charts comparing FIFO, LRU, and Optimal side by side. Includes dark-theme styling constants."))
    story.append(body("<b>Functions:</b>"))
    story.extend(bullet_list([
        "run_all_algorithms(reference_string, frame_count) — Executes all three algorithms, returns {FIFO: result, LRU: result, Optimal: result}.",
        "build_comparison_bar(all_results) — Grouped bar chart, faults (solid) vs hits (translucent outline) per algorithm.",
        "build_fault_race(all_results) — Overlaid line chart: cumulative faults over steps for all three algorithms on shared axes.",
        "build_summary_table(all_results) — Tabular Plotly figure: Algorithm | Faults | Hits | Fault Rate | Best? (★ for lowest faults).",
    ]))

    story.append(heading("5.10 visualization/belady_chart.py — Bélady's Anomaly Visualisation", 2))
    story.append(body("<b>Purpose:</b> Specialised chart for detecting and highlighting Bélady's Anomaly in FIFO."))
    story.append(body("build_belady_chart(anomaly_result): Plots fault count (y) vs frame count (x). Anomaly points get large white diamond markers, bold dashed connecting lines, shaded violation rectangles, and detailed annotations showing the frame counts and fault delta."))

    story.append(PageBreak())

    # ─── test files ───────────────────────────────────────────
    story.append(heading("5.11 Test Files (tests/)", 2))
    story.append(body("All tests use <b>pytest</b> with standard assert-based testing. No mocking needed since all algorithm modules are pure functions with no I/O."))

    test_summary = [
        ["Test File", "Lines", "Tests Covered"],
        ["test_engine.py", "84", "PageTable mapping/unmapping/validation, FramePool allocation/deallocation/bounds checking, translate_address with edge cases, page fault detection."],
        ["test_fifo.py", "41", "Classic Bélady sequence with 3 frames (9 faults) and 4 frames (10 faults), all-hits scenario, Bélady's Anomaly detection at (3→4)."],
        ["test_lru.py", "39", "Classic sequence (10 faults), eviction order verification (page 2 evicted), large-frame edge case (faults=unique pages)."],
        ["test_optimal.py", "55", "Victim selection (never-used-again priority, farthest-in-future), classic sequence (7 faults at exact positions), all-hits, large-frames."],
        ["test_segmentation.py", "375", "Segment internal frag, end address, to_dict. Allocation (basic, adjacent, duplicate name, invalid size, out of space). All 4 strategies (first/best/worst/next fit with known hole layouts). Translation (valid, offset exceeds limit, negative, nonexistent, swapped, nonzero base). Deallocation (hole creation, reuse freed space). Fragmentation stats (internal, external, contiguous, empty, utilisation). Compaction (hole removal, base updates, no-op). Simulation (basic 4-step, error recording, strategy comparison). Memory map (full coverage, hole detection)."],
    ]
    story.append(table_block(test_summary, col_widths=[W*0.16, W*0.06, W*0.78]))

    story.append(PageBreak())

    # ─── Other files ──────────────────────────────────────────
    story.append(heading("5.12 Configuration & Deployment Files", 2))

    story.append(heading("get_processes.ps1", 3))
    story.append(body("Standalone PowerShell script that fetches the top 30 processes by Working Set size. Returns JSON with fields: Id, ProcessName, WS_MB, VM_MB, PM_MB, Thr (thread count), Hnd (handle count). Used for manual testing and debugging. The actual app.py uses a different, CPU-sorted PowerShell command inline."))

    story.append(heading("requirements.txt", 3))
    story.append(body("Lists all Python dependencies: flask==3.1.0, gunicorn==23.0.0, pytest==8.3.4, plotly==5.20.0, PyQt5==5.15.11. Used by pip install -r requirements.txt."))

    story.append(heading("Procfile", 3))
    story.append(body("Heroku deployment config. Single line: 'web: gunicorn app:flask_app'. Tells Heroku to start the app using Gunicorn with the Flask WSGI callable."))

    story.append(heading("vercel.json", 3))
    story.append(body("Vercel serverless deployment config. Uses @vercel/python runtime with Python 3.10. Routes all requests (/(.*)) to app.py. Max lambda size: 15MB."))

    story.append(heading(".gitignore", 3))
    story.append(body("Ignores: __pycache__, virtual environments (venv/, .venv/), distribution files, IDE configs (.vscode/, .idea/), OS files (Thumbs.db, .DS_Store), test caches (.pytest_cache/), coverage files, logs."))

    story.append(PageBreak())

    # ═══════════════════════════════════════════════════════════
    # 6. ALGORITHM IMPLEMENTATIONS
    # ═══════════════════════════════════════════════════════════
    story.append(heading("6. Algorithm Implementations"))

    # ─── 6.1 FIFO ─────────────────────────────────────────────
    story.append(heading("6.1 FIFO (First-In, First-Out) Page Replacement", 2))

    story.append(heading("Theory Recap", 3))
    story.append(body(
        "FIFO is the simplest page replacement algorithm. It maintains a queue of pages in the order they were loaded. "
        "When a page fault occurs and all frames are full, the page at the front of the queue (the oldest loaded page) "
        "is evicted, regardless of how recently or frequently it was used. FIFO suffers from <b>Bélady's Anomaly</b>: "
        "adding more frames can paradoxically increase page faults for certain reference strings."
    ))

    story.append(heading("Implementation Logic", 3))
    story.append(body("<b>Data Structures:</b>"))
    story.extend(bullet_list([
        "<b>frame_list (List[Optional[int]]):</b> Array representing physical frames. Chosen over a set because we need indexed access to know WHICH frame a page is in (for replacement). None = empty frame.",
        "<b>queue (deque[int]):</b> Insertion-order queue. deque is chosen over list because popleft() is O(1) on deque but O(n) on list. This is critical for FIFO correctness — we always evict from the left (oldest).",
        "<b>page_to_frame (Dict[int, int]):</b> Reverse lookup: page → frame index. Chosen because checking 'page in frame_list' is O(n) but 'page in dict' is O(1). Essential for performance with large reference strings.",
    ]))

    story.append(heading("Example Walkthrough — Dummy Data", 3))
    story.append(body("Reference string: [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5], Frames: 3"))

    fifo_example = [
        ["Step", "Page", "Action", "Frames After", "Evicted", "Queue State"],
        ["0", "1", "FAULT (empty frame)", "[1, -, -]", "-", "[1]"],
        ["1", "2", "FAULT (empty frame)", "[1, 2, -]", "-", "[1, 2]"],
        ["2", "3", "FAULT (empty frame)", "[1, 2, 3]", "-", "[1, 2, 3]"],
        ["3", "4", "FAULT (evict oldest=1)", "[4, 2, 3]", "1", "[2, 3, 4]"],
        ["4", "1", "FAULT (evict oldest=2)", "[4, 1, 3]", "2", "[3, 4, 1]"],
        ["5", "2", "FAULT (evict oldest=3)", "[4, 1, 2]", "3", "[4, 1, 2]"],
        ["6", "5", "FAULT (evict oldest=4)", "[5, 1, 2]", "4", "[1, 2, 5]"],
        ["7", "1", "HIT", "[5, 1, 2]", "-", "[1, 2, 5]"],
        ["8", "2", "HIT", "[5, 1, 2]", "-", "[1, 2, 5]"],
        ["9", "3", "FAULT (evict oldest=1)", "[5, 3, 2]", "1", "[2, 5, 3]"],
        ["10", "4", "FAULT (evict oldest=2)", "[5, 3, 4]", "2", "[5, 3, 4]"],
        ["11", "5", "HIT", "[5, 3, 4]", "-", "[5, 3, 4]"],
    ]
    story.append(table_block(fifo_example, col_widths=[W*0.06, W*0.06, W*0.22, W*0.16, W*0.10, W*0.22]))
    story.append(body("<b>Result:</b> 9 faults, 3 hits. With 4 frames, this same sequence produces 10 faults — Bélady's Anomaly!"))

    story.append(heading("Example — Real-Time Windows Data", 3))
    story.append(body(
        "Suppose live processes are: chrome (CPU=45.2s), vscode (CPU=12.8s), explorer (CPU=3.1s). "
        "Chrome gets pages [1,2,3,4] (high volatility → more pages), vscode gets [5,6], explorer gets [7]. "
        "The weighted reference string might be: [1, 2, 1, 5, 3, 1, 4, 6, 2, 3, 7, 1] — Chrome-heavy due to its higher CPU usage. "
        "FIFO runs on this live string just as it would on dummy data, producing a realistic fault pattern."
    ))

    story.append(PageBreak())

    # ─── 6.2 LRU ──────────────────────────────────────────────
    story.append(heading("6.2 LRU (Least Recently Used) Page Replacement", 2))

    story.append(heading("Theory Recap", 3))
    story.append(body(
        "LRU evicts the page that hasn't been used for the longest time. It operates on the principle of <b>temporal locality</b>: "
        "pages used recently are likely to be used again soon. Unlike FIFO, LRU is a <b>stack algorithm</b> — it is immune to "
        "Bélady's Anomaly. More frames always means fewer or equal faults. LRU is widely used in real systems (with hardware "
        "approximations like clock/second-chance algorithms)."
    ))

    story.append(heading("Implementation Logic", 3))
    story.append(body("<b>Data Structure: OrderedDict[int, bool]</b>"))
    story.append(body(
        "Python's OrderedDict maintains insertion order AND provides O(1) move_to_end() — a perfect fit for LRU. "
        "The key insight: positions in the OrderedDict represent recency. The first key is always the LRU page, "
        "the last key is always the MRU page."
    ))
    story.extend(bullet_list([
        "<b>On HIT:</b> memory.move_to_end(page) — moves the accessed page to the end (most recent position). O(1).",
        "<b>On FAULT (memory full):</b> memory.popitem(last=False) — removes the first item (least recently used). O(1).",
        "<b>On FAULT (insert):</b> memory[page] = True — new page goes to the end (most recent). O(1).",
    ]))
    story.append(body("<b>Why not a plain list?</b> With a list, moving a page to the end on every hit requires O(n) remove + O(1) append = O(n) per access. OrderedDict's move_to_end is O(1) internally via a doubly-linked list."))

    story.append(heading("Example Walkthrough — Dummy Data", 3))
    story.append(body("Reference: [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5], Frames: 3"))

    lru_example = [
        ["Step", "Page", "Action", "OrderedDict (LRU→MRU)", "Evicted"],
        ["0", "1", "FAULT", "{1}", "-"],
        ["1", "2", "FAULT", "{1, 2}", "-"],
        ["2", "3", "FAULT", "{1, 2, 3}", "-"],
        ["3", "4", "FAULT (evict LRU=1)", "{2, 3, 4}", "1"],
        ["4", "1", "FAULT (evict LRU=2)", "{3, 4, 1}", "2"],
        ["5", "2", "FAULT (evict LRU=3)", "{4, 1, 2}", "3"],
        ["6", "5", "FAULT (evict LRU=4)", "{1, 2, 5}", "4"],
        ["7", "1", "HIT (move to end)", "{2, 5, 1}", "-"],
        ["8", "2", "HIT (move to end)", "{5, 1, 2}", "-"],
        ["9", "3", "FAULT (evict LRU=5)", "{1, 2, 3}", "5"],
        ["10", "4", "FAULT (evict LRU=1)", "{2, 3, 4}", "1"],
        ["11", "5", "FAULT (evict LRU=2)", "{3, 4, 5}", "2"],
    ]
    story.append(table_block(lru_example, col_widths=[W*0.06, W*0.06, W*0.22, W*0.30, W*0.10]))
    story.append(body("<b>Result:</b> 10 faults, 2 hits. Worse than FIFO on this pathological sequence, but immune to Bélady's Anomaly."))

    story.append(PageBreak())

    # ─── 6.3 Optimal ──────────────────────────────────────────
    story.append(heading("6.3 Optimal (MIN/OPT) Page Replacement", 2))

    story.append(heading("Theory Recap", 3))
    story.append(body(
        "The Optimal algorithm, also known as MIN or OPT (Bélády, 1966), replaces the page that will not be used "
        "for the longest time in the future. It provably produces the minimum number of page faults for any given "
        "reference string, making it the theoretical lower bound. It is <b>impractical</b> for real systems because "
        "it requires complete future knowledge of the reference string, but it serves as the gold standard benchmark."
    ))

    story.append(heading("Implementation Logic", 3))
    story.append(body("<b>Victim Selection (_find_optimal_victim):</b>"))
    story.extend(bullet_list([
        "For each loaded page, search future_refs (reference_string[idx+1:]) for the next occurrence using list.index().",
        "If a page is never used again (ValueError): return it immediately — evicting it has zero cost.",
        "Otherwise, track the page with the maximum future index (farthest next use).",
        "Return the farthest page. This greedy choice is provably optimal.",
    ]))

    story.append(heading("Example Walkthrough — Dummy Data", 3))
    story.append(body("Reference: [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5], Frames: 3"))

    opt_example = [
        ["Step", "Page", "Action", "Frames", "Evicted", "Future Look-Ahead"],
        ["0", "1", "FAULT (empty)", "[1, -, -]", "-", "-"],
        ["1", "2", "FAULT (empty)", "[1, 2, -]", "-", "-"],
        ["2", "3", "FAULT (empty)", "[1, 2, 3]", "-", "-"],
        ["3", "4", "FAULT (evict 3: farthest=idx 9)", "[1, 2, 4]", "3", "Future of 1:idx4, 2:idx5, 3:idx9 → 3 farthest"],
        ["4", "1", "HIT", "[1, 2, 4]", "-", "-"],
        ["5", "2", "HIT", "[1, 2, 4]", "-", "-"],
        ["6", "5", "FAULT (evict 4: farthest=idx 10)", "[1, 2, 5]", "4", "Future of 1:idx7, 2:idx8, 4:idx10 → 4 farthest"],
        ["7", "1", "HIT", "[1, 2, 5]", "-", "-"],
        ["8", "2", "HIT", "[1, 2, 5]", "-", "-"],
        ["9", "3", "FAULT (evict 1: not used again)", "[3, 2, 5]", "1", "1:never, 2:never, 5:idx11 → 1 never"],
        ["10", "4", "FAULT (evict 2: not used again)", "[3, 4, 5]", "2", "2:never, 5:idx11 → 2 never"],
        ["11", "5", "HIT", "[3, 4, 5]", "-", "-"],
    ]
    story.append(table_block(opt_example, col_widths=[W*0.05, W*0.05, W*0.18, W*0.12, W*0.08, W*0.36]))
    story.append(body("<b>Result:</b> 7 faults, 5 hits. The theoretical minimum — no algorithm can do better."))

    story.append(PageBreak())

    # ─── 6.4 Segmentation Algorithms ──────────────────────────
    story.append(heading("6.4 Segmentation — Memory Allocation Strategies", 2))

    story.append(heading("Theory Recap", 3))
    story.append(body(
        "In segmented memory, processes request variable-size blocks (segments) like code, stack, heap, and data. "
        "The OS must find a contiguous free region (hole) large enough to accommodate each request. Over time, "
        "as segments are allocated and freed, memory becomes fragmented with scattered holes. The allocation "
        "strategy determines WHICH hole to choose."
    ))

    # First Fit
    story.append(heading("First Fit", 3))
    story.append(body("<b>Rule:</b> Scan memory left → right, use the FIRST hole that is large enough."))
    story.append(body("<b>Implementation:</b> _find_hole() returns fitting[0] — the first element of the holes list (which is sorted by address)."))
    story.append(body("<b>Trade-offs:</b> Fast (stops at first match, average O(n/2)). Tends to fragment the beginning of memory because small allocations accumulate there. Leaves large holes at the end intact."))

    # Best Fit
    story.append(heading("Best Fit", 3))
    story.append(body("<b>Rule:</b> Use the SMALLEST hole that is large enough."))
    story.append(body("<b>Implementation:</b> _find_hole() returns min(fitting, key=lambda h: h['size'])."))
    story.append(body("<b>Trade-offs:</b> Minimises leftover space per allocation. But creates tiny, often unusable holes (external fragmentation). Requires scanning ALL holes (O(n))."))

    # Worst Fit
    story.append(heading("Worst Fit", 3))
    story.append(body("<b>Rule:</b> Use the LARGEST hole available."))
    story.append(body("<b>Implementation:</b> _find_hole() returns max(fitting, key=lambda h: h['size'])."))
    story.append(body("<b>Trade-offs:</b> Leaves the largest possible leftover, which may be reusable for future allocations. But wastes space if a larger allocation comes later. Requires scanning ALL holes (O(n))."))

    # Next Fit
    story.append(heading("Next Fit", 3))
    story.append(body("<b>Rule:</b> Like First Fit, but starts scanning from where the last allocation ended (wraps around)."))
    story.append(body("<b>Implementation:</b> _find_hole() iterates fitting holes, picks the first at or after _next_fit_cursor. If none found, wraps to fitting[0]. After allocation, cursor advances to segment.end_address()."))
    story.append(body("<b>Trade-offs:</b> Spreads allocations more evenly across memory (avoids beginning-heavy fragmentation of First Fit). Slightly faster than First Fit on average (skips already-scanned regions)."))

    story.append(heading("Example Walkthrough — Segmentation with Real Data", 3))
    story.append(body(
        "Suppose live processes are: chrome (WS=512MB), vscode (WS=256MB), slack (WS=128MB). "
        "Total memory = 4096 bytes (simulated). Using <b>Best Fit</b> strategy, block_size = 16:"
    ))
    story.extend(bullet_list([
        "Step 1: Alloc 'chrome.text' = 90B → aligned to 96B. Placed at base=0. Internal frag=6B.",
        "Step 2: Alloc 'chrome.heap' = 300B → aligned to 304B. Placed at base=96.",
        "Step 3: Alloc 'vscode.text' = 45B → aligned to 48B. Placed at base=400.",
        "Step 4: Free 'chrome.text' → hole at [0, 96). External frag = 96B.",
        "Step 5: Alloc 'slack.data' = 80B → aligned to 80B. Best Fit picks hole [0,96) (size=96, smallest that fits 80). Internal frag=0. Leftover hole: [80, 96) = 16B.",
        "Step 6: Compact → slides all segments left, eliminating holes. External frag → 0.",
    ]))

    story.append(PageBreak())

    # ═══════════════════════════════════════════════════════════
    # 7. REAL-TIME DATA INTEGRATION
    # ═══════════════════════════════════════════════════════════
    story.append(heading("7. Real-Time Data Integration"))

    story.append(heading("7.1 System Metrics Fetched", 2))

    metrics_data = [
        ["Metric", "Source", "PowerShell Property", "How Used"],
        ["Process Name", "Get-Process", "ProcessName", "Identifies which application the data belongs to (chrome, vscode, etc)."],
        ["Process ID (PID)", "Get-Process", "Id", "Unique process identifier, passed to frontend for display."],
        ["CPU Execution Time", "Get-Process", "CPU (seconds)", "Primary volatility metric. Processes with higher CPU time are deemed more 'active' and are assigned more virtual pages. Used as weights in the reference string generation."],
        ["Working Set (WS)", "Get-Process", "WorkingSet64 (bytes)", "Physical memory currently used by the process. Used for segmentation: proportional segment budget = (process WS / total WS) × target memory. Also used as fallback volatility metric when CPU is 0."],
    ]
    story.append(table_block(metrics_data, col_widths=[W*0.14, W*0.10, W*0.18, W*0.58]))

    story.append(heading("7.2 How Live Data Feeds Into Algorithms", 2))
    story.append(body("<b>Paging (Page Reference String Generation):</b>"))
    story.extend(bullet_list([
        "The function _get_windows_process_snapshot() fetches up to 96 processes with CPU > 0, sorted by CPU time descending.",
        "Processes are grouped by name (aggregating instances like multiple chrome.exe).",
        "The top 6-8 most volatile processes are selected.",
        "Each process is assigned virtual pages proportional to its share of total volatility. E.g., if Chrome has 60% of total CPU time and max_page=9, Chrome gets ~5-6 pages.",
        "Reference string is built by simulating CPU scheduling: processes are selected via weighted random (heavier = more time slices).",
        "Within each time slice, locality-of-reference is applied: 70% spatial (sequential pages within the process), 20% temporal (revisit recent pages), 10% random (page fault trigger).",
        "The resulting reference string is then fed to run_fifo(), run_lru(), and run_optimal() identically.",
    ]))

    story.append(body("<b>Segmentation (Live Segment Allocation):</b>"))
    story.extend(bullet_list([
        "The /api/live-segmentation endpoint fetches the top 8 processes by memory.",
        "Each process's memory is proportionally allocated across 4 segment types: .text (15%), .heap (50%), .data (12%), .stack (8%).",
        "Each segment size = max(block_size, int(process_budget × fraction)). The process budget = (process_WS / total_WS) × (total_memory × 0.72).",
        "These proportional allocations produce a realistic memory layout that mirrors how real processes are structured.",
    ]))

    story.append(heading("7.3 OS-Level APIs / System Calls", 2))
    story.extend(bullet_list([
        "<b>PowerShell Get-Process cmdlet:</b> This is the primary OS-level interface. It wraps the Win32 API calls OpenProcess(), GetProcessTimes(), and NtQueryVirtualMemory(). We access it via subprocess.run(['powershell', '-NoProfile', '-Command', ...]).",
        "<b>subprocess.run():</b> Python's interface to CreateProcess() on Windows. We use capture_output=True, text=True, encoding='utf-8', timeout=5 for safety.",
        "<b>QDateTime (optional):</b> If PyQt5 is available, uses the Qt framework's clock API (which wraps QueryPerformanceCounter on Windows) for high-precision timestamps.",
    ]))

    story.append(PageBreak())

    # ═══════════════════════════════════════════════════════════
    # 8. DUMMY DATA LOGIC
    # ═══════════════════════════════════════════════════════════
    story.append(heading("8. Dummy Data Logic"))

    story.append(heading("8.1 Paging — Default Reference Strings", 2))
    story.append(body("When the user does not enable live mode, the system uses manually specified or default reference strings:"))
    story.extend(bullet_list([
        "<b>Classic Bélady Sequence:</b> [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5] — The canonical example that demonstrably triggers Bélady's Anomaly in FIFO (9 faults with 3 frames, 10 faults with 4 frames).",
        "<b>Default API String:</b> [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2] — Used when /api/realtime-algorithms is called without a reference_string parameter. A general-purpose sequence with a mix of repeats and new pages.",
        "<b>User-Supplied:</b> Any comma-separated or space-separated string of non-negative integers via the POST /api/simulate endpoint.",
    ]))

    story.append(heading("8.2 Paging — Synthetic Live Stream", 2))
    story.append(body(
        "When live mode is active but Windows process data is unavailable (e.g., on Linux/macOS), the _next_live_reference() "
        "function generates a synthetic stream:"
    ))
    story.extend(bullet_list([
        "Uses a global deque with maxlen=120 as a sliding window buffer.",
        "Each call advances the stream by (current_tick - last_tick) steps (bounded to 8 to avoid bursts).",
        "Every 4th step uses temporal locality: repeats the page from 2 steps ago.",
        "Other steps use arithmetic jump: ((tick × 7) + (counter × 3)) % max_page + 1.",
        "This produces a stream with both locality bursts (realistic) and periodic jumps (causing faults).",
        "The deque is thread-safe via _LIVE_REFERENCE_LOCK (threading.Lock).",
    ]))

    story.append(heading("8.3 Segmentation — Deterministic Operations", 2))
    story.append(body("The _build_live_segmentation_operations(live_tick) function generates a fixed sequence of 6 operations with time-varying sizes:"))
    story.extend(bullet_list([
        "Alloc 'A': size = 128 + ((tick % 5) × 32) → varies between 128 and 256.",
        "Alloc 'B': size = 192 + (((tick//2) % 5) × 32) → varies between 192 and 320.",
        "Free 'A': creates a hole in the layout.",
        "Alloc 'C': size = 96 + (((tick//3) % 4) × 32) → varies between 96 and 192.",
        "Compact: eliminates the hole from freeing A.",
        "Alloc 'D': size = 64 + (((tick//4) % 6) × 16) → varies between 64 and 144.",
    ]))
    story.append(body("This creates a reproducible sequence that still varies over time, letting the user see how different sizes affect fragmentation without needing live data."))

    story.append(heading("8.4 How Dummy Data Maps to Real OS Concepts", 2))
    story.extend(bullet_list([
        "<b>Page numbers</b> represent virtual pages in a process's address space. Each page number corresponds to a fixed-size chunk of virtual memory (e.g., 4KB in real systems).",
        "<b>Reference strings</b> model the sequence of page accesses that the CPU makes as a program runs. In real systems, this is generated by the memory management unit (MMU) hardware.",
        "<b>Frames</b> represent physical RAM frames. The frame count simulates the finite size of physical memory available to the paging system.",
        "<b>Segments</b> represent the logical divisions of a program's memory: code (executable instructions), stack (function call frames), heap (dynamically allocated data), data (global/static variables).",
        "<b>Segment sizes</b> correspond to how much memory each section requires. In real systems, the code segment is typically small and fixed, while the heap grows dynamically.",
        "<b>Block alignment</b> mirrors hardware page alignment. Real CPUs require memory allocations to be aligned to page boundaries (typically 4KB). Our 16-byte blocks simulate this at a smaller scale.",
    ]))

    story.append(PageBreak())

    # ═══════════════════════════════════════════════════════════
    # 9. KEY DESIGN DECISIONS
    # ═══════════════════════════════════════════════════════════
    story.append(heading("9. Key Design Decisions"))

    story.append(heading("9.1 Data Structure Choices", 2))

    ds_data = [
        ["Decision", "Choice Made", "Alternative Considered", "Why This Choice"],
        [
            "FIFO eviction tracking",
            "collections.deque",
            "list",
            "deque.popleft() is O(1); list.pop(0) is O(n). For a simulator processing thousands of page references, this difference matters."
        ],
        [
            "LRU recency tracking",
            "OrderedDict",
            "list + linear search, or doubly-linked list + dict",
            "OrderedDict provides O(1) move_to_end() and O(1) popitem(last=False) — both operations LRU needs on every access. A raw list would be O(n) per move. A manual doubly-linked list + dict is the textbook approach but OrderedDict is a built-in that does exactly this internally."
        ],
        [
            "FIFO page presence check",
            "Dict (page_to_frame)",
            "Scanning frame_list",
            "O(1) dict lookup vs O(n) list scan. With frame counts up to 10+ and reference strings of 12+ pages, this measurably improves performance."
        ],
        [
            "Segment storage",
            "Dict[str, Segment]",
            "List[Segment]",
            "Segments are accessed by name (e.g., 'code', 'stack'). Dict provides O(1) lookup by name. A list would require O(n) linear search."
        ],
        [
            "FramePool free tracking",
            "Two sets (free + allocated)",
            "Single list with status flags",
            "Set membership testing is O(1). Allocation uses min(free_set) for deterministic ordering. Sets also prevent accidental duplicates."
        ],
        [
            "Live reference buffer",
            "deque(maxlen=120)",
            "list with manual trimming",
            "deque with maxlen automatically discards oldest elements when the buffer is full. Thread-safe append when combined with a Lock. Eliminates manual size management."
        ],
        [
            "Hole tracking (segmentation)",
            "Computed on-the-fly from sorted segments",
            "Explicit free list",
            "Computing holes dynamically from segment positions avoids the complexity of maintaining a separate free list that must be updated on every alloc/free/compact. Trade-off: O(n log n) per _get_free_holes() call due to sorting, but n (segment count) is small in simulation."
        ],
    ]
    story.append(table_block(ds_data, col_widths=[W*0.14, W*0.15, W*0.20, W*0.51]))
    story.append(Spacer(1, 12))

    story.append(heading("9.2 Architecture Decisions", 2))

    arch_decisions = [
        ["Decision", "Rationale"],
        [
            "Separate core/ from app.py",
            "The algorithm engines (core/) are pure functions with zero I/O, zero HTTP awareness, and zero side effects. This makes them independently testable with pytest, reusable outside Flask, and easy to reason about. The Flask layer (app.py) is purely an orchestration/plumbing layer."
        ],
        [
            "Flask over Django",
            "The project needs a thin API layer, not an ORM, admin panel, or middleware stack. Flask's micro-framework philosophy allows the API to be exactly as complex as needed without framework overhead."
        ],
        [
            "Chart.js (client-side) over Plotly (server-side) for the main UI",
            "The main UI uses Chart.js loaded via CDN for client-side rendering. This avoids sending large Plotly bundles and enables smooth real-time chart updates during live polling. The server-side Plotly charts in visualization/ exist as an alternative/complementary rendering pipeline."
        ],
        [
            "CPU time as primary volatility metric (not memory size)",
            "Memory size (WorkingSet) is relatively stable — a browser's memory doesn't change much second-to-second. CPU execution time (cumulative seconds) is the most volatile readily-available metric, making the reference string change meaningfully between polls."
        ],
        [
            "Thread-safe live stream with Lock",
            "Flask's development server is single-threaded, but Gunicorn (production) spawns multiple workers. The shared deque + Lock ensures the live reference stream is consistent even under concurrent requests."
        ],
        [
            "Block alignment in segmentation",
            "Real hardware allocates memory in page-aligned chunks. The block_size parameter (default 16) simulates this alignment, naturally producing internal fragmentation that students can observe and measure."
        ],
        [
            "Adjacent holes NOT auto-merged on free",
            "In real OS segment tables, individual deallocations are tracked separately. Merging holes requires explicit compaction. This design makes the fragmentation lifecycle visible: alloc → free → holes accumulate → compact → holes eliminated."
        ],
        [
            "Optional PyQt5 dependency",
            "PyQt5 is heavy (~80MB). Making it optional (try/except import) means the project runs on any system with just Flask installed. QDateTime is only used for marginally higher-precision timestamps."
        ],
    ]
    story.append(table_block(arch_decisions, col_widths=[W*0.25, W*0.75]))
    story.append(Spacer(1, 12))

    story.append(heading("9.3 Performance & Accuracy Trade-offs", 2))
    story.extend(bullet_list([
        "<b>Optimal algorithm is O(n × m × r)</b> (n=reference length, m=frame count, r=remaining refs per step). For small simulations (12-page strings, 3 frames), this is negligible. For very large inputs, a more efficient implementation using a priority queue could be used, but was avoided for code clarity.",
        "<b>PowerShell process snapshot has 5-second timeout.</b> This prevents the API from hanging if PowerShell is slow, but means the data might be slightly stale. The tick-based caching (rng = Random(tick // 5)) ensures the same reference string is served for 5-second windows, reducing computation.",
        "<b>Segmentation hole computation is O(n log n)</b> due to sorting segments by base address on every call. With the simulation's typical 4-10 segments, this is instantaneous. An explicit free list would be O(1) for access but requires complex update logic on every operation.",
        "<b>The live reference stream is bounded to 120 entries.</b> This prevents unbounded memory growth during long polling sessions while keeping enough history for the 12-page sliding window.",
        "<b>Fragmentation stats exclude trailing free space from external fragmentation.</b> Design choice: trailing space IS usable (it's contiguous), so counting it as 'fragmentation' would overstate the problem. Only scattered holes between segments are truly external fragmentation.",
    ]))

    story.append(Spacer(1, 24))
    story.append(separator())
    story.append(Spacer(1, 12))
    story.append(Paragraph(
        "<i>End of Documentation — Real-Time Windows Virtual Memory Simulator</i>",
        ParagraphStyle('EndNote', parent=styles['Normal'], fontSize=10,
                       textColor=HexColor("#888888"), alignment=TA_CENTER)
    ))

    # ── Build PDF ─────────────────────────────────────────────
    doc.build(story)
    print(f"\n[OK] PDF generated successfully: {OUTPUT_FILE}")
    print(f"   Size: {os.path.getsize(OUTPUT_FILE) / 1024:.1f} KB")


if __name__ == "__main__":
    build_document()
