# ============================================================
# Module 9 — Chart Generator
# Purpose: Server-side Plotly chart generation. Each function
#          returns an HTML div string for direct embedding
#          in Jinja2 templates.
# ============================================================

import plotly.graph_objects as go
import plotly.io as pio


# ── Shared color palette ─────────────────────────────────────
COLORS = {
    "primary":    "#7c3aed",    # violet-600
    "secondary":  "#06b6d4",    # cyan-500
    "accent":     "#f59e0b",    # amber-500
    "success":    "#10b981",    # emerald-500
    "danger":     "#ef4444",    # red-500
    "bg":         "#0f172a",    # slate-900
    "card_bg":    "#1e293b",    # slate-800
    "text":       "#e2e8f0",    # slate-200
    "grid":       "#334155",    # slate-700
}

LAYOUT_DEFAULTS = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color=COLORS["text"], family="Inter, sans-serif"),
    margin=dict(l=50, r=30, t=50, b=50),
    xaxis=dict(gridcolor=COLORS["grid"], zerolinecolor=COLORS["grid"]),
    yaxis=dict(gridcolor=COLORS["grid"], zerolinecolor=COLORS["grid"]),
)


def _to_html(fig):
    """Convert a Plotly figure to an embeddable HTML div string."""
    return pio.to_html(fig, full_html=False, include_plotlyjs=False)


# ---------------------------------------------------------------------------
# 1. Fault Comparison Bar Chart  (LRU vs Optimal)
# ---------------------------------------------------------------------------

def fault_comparison_bar(lru_faults, optimal_faults, lru_hits, optimal_hits):
    """
    Side-by-side bar chart comparing LRU and Optimal faults/hits.

    Returns:
        str: Plotly HTML div.
    """
    fig = go.Figure()

    fig.add_trace(go.Bar(
        name="Faults",
        x=["LRU", "Optimal"],
        y=[lru_faults, optimal_faults],
        marker_color=[COLORS["danger"], COLORS["accent"]],
        text=[lru_faults, optimal_faults],
        textposition="auto",
    ))
    fig.add_trace(go.Bar(
        name="Hits",
        x=["LRU", "Optimal"],
        y=[lru_hits, optimal_hits],
        marker_color=[COLORS["primary"], COLORS["success"]],
        text=[lru_hits, optimal_hits],
        textposition="auto",
    ))

    fig.update_layout(
        **LAYOUT_DEFAULTS,
        title="Page Faults & Hits — LRU vs Optimal",
        barmode="group",
        yaxis_title="Count",
    )

    return _to_html(fig)


# ---------------------------------------------------------------------------
# 2. Faults-vs-Frames Line Graph
# ---------------------------------------------------------------------------

def fault_curve_line(lru_curve, optimal_curve=None):
    """
    Line graph: faults as a function of frame count.

    Args:
        lru_curve     (list[dict]): [{"frames": int, "faults": int}, ...]
        optimal_curve (list[dict]): Same format, or None to omit.

    Returns:
        str: Plotly HTML div.
    """
    fig = go.Figure()

    frames_lru = [p["frames"] for p in lru_curve]
    faults_lru = [p["faults"] for p in lru_curve]

    fig.add_trace(go.Scatter(
        x=frames_lru,
        y=faults_lru,
        mode="lines+markers",
        name="LRU",
        line=dict(color=COLORS["primary"], width=3),
        marker=dict(size=8),
    ))

    if optimal_curve:
        frames_opt = [p["frames"] for p in optimal_curve]
        faults_opt = [p["faults"] for p in optimal_curve]
        fig.add_trace(go.Scatter(
            x=frames_opt,
            y=faults_opt,
            mode="lines+markers",
            name="Optimal",
            line=dict(color=COLORS["secondary"], width=3),
            marker=dict(size=8),
        ))

    fig.update_layout(
        **LAYOUT_DEFAULTS,
        title="Page Faults vs Number of Frames",
        xaxis_title="Number of Frames",
        yaxis_title="Page Faults",
    )

    return _to_html(fig)


# ---------------------------------------------------------------------------
# 3. Frame State Heatmap
# ---------------------------------------------------------------------------

def frame_heatmap(steps, num_frames):
    """
    Heatmap showing which page occupies each frame at every step.

    Args:
        steps      (list[dict]): Simulation steps with "frames_after".
        num_frames (int):        Number of frames.

    Returns:
        str: Plotly HTML div.
    """
    # Build matrix: rows = frames, cols = steps
    z = []
    for f_idx in range(num_frames):
        row = []
        for step in steps:
            frame_state = step["frames_after"]
            val = frame_state[f_idx] if f_idx < len(frame_state) else None
            row.append(val if val is not None else -1)
        z.append(row)

    step_labels = [f"S{s['step']}" for s in steps]
    frame_labels = [f"Frame {i}" for i in range(num_frames)]

    fig = go.Figure(data=go.Heatmap(
        z=z,
        x=step_labels,
        y=frame_labels,
        colorscale=[
            [0, "#1e293b"],
            [0.5, COLORS["primary"]],
            [1.0, COLORS["secondary"]],
        ],
        text=[[("—" if v == -1 else str(v)) for v in row] for row in z],
        texttemplate="%{text}",
        textfont=dict(size=12),
        showscale=False,
    ))

    fig.update_layout(
        **LAYOUT_DEFAULTS,
        title="Memory Frame State Over Time",
        xaxis_title="Step",
        yaxis_title="Frame",
        height=max(250, num_frames * 50 + 100),
    )

    return _to_html(fig)


# ---------------------------------------------------------------------------
# 4. Fragmentation Bar Chart
# ---------------------------------------------------------------------------

def fragmentation_bar(results):
    """
    Bar chart showing internal fragmentation per block and totals.

    Args:
        results (dict): Output from fragmentation.simulate_fragmentation().

    Returns:
        str: Plotly HTML div.
    """
    blocks = results["blocks"]
    block_labels = [f"Block {b['id']}" for b in blocks]
    block_sizes = [b["size"] for b in blocks]
    used_sizes = [b["used"] for b in blocks]
    int_frags = [b["internal_frag"] for b in blocks]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        name="Used",
        x=block_labels,
        y=used_sizes,
        marker_color=COLORS["success"],
        text=used_sizes,
        textposition="auto",
    ))

    fig.add_trace(go.Bar(
        name="Internal Fragmentation",
        x=block_labels,
        y=int_frags,
        marker_color=COLORS["danger"],
        text=int_frags,
        textposition="auto",
    ))

    fig.update_layout(
        **LAYOUT_DEFAULTS,
        title=f"Memory Allocation — {results['strategy'].replace('_', ' ').title()}",
        barmode="stack",
        xaxis_title="Memory Block",
        yaxis_title="Bytes",
    )

    return _to_html(fig)


# ---------------------------------------------------------------------------
# 5. Fragmentation Strategy Comparison
# ---------------------------------------------------------------------------

def fragmentation_comparison_bar(comparison):
    """
    Grouped bar chart comparing internal/external fragmentation
    across all three allocation strategies.

    Args:
        comparison (dict): Output from fragmentation.compare_strategies().

    Returns:
        str: Plotly HTML div.
    """
    strategies = list(comparison.keys())
    labels = [s.replace("_", " ").title() for s in strategies]
    internal = [comparison[s]["total_internal_frag"] for s in strategies]
    external = [comparison[s]["total_external_frag"] for s in strategies]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        name="Internal Fragmentation",
        x=labels,
        y=internal,
        marker_color=COLORS["accent"],
        text=internal,
        textposition="auto",
    ))

    fig.add_trace(go.Bar(
        name="External Fragmentation",
        x=labels,
        y=external,
        marker_color=COLORS["danger"],
        text=external,
        textposition="auto",
    ))

    fig.update_layout(
        **LAYOUT_DEFAULTS,
        title="Fragmentation Comparison Across Strategies",
        barmode="group",
        xaxis_title="Strategy",
        yaxis_title="Bytes",
    )

    return _to_html(fig)


# ---------------------------------------------------------------------------
# 6. Demand Paging Working Set Line Graph
# ---------------------------------------------------------------------------

def working_set_line(steps):
    """
    Line graph of working set size over time.

    Args:
        steps (list[dict]): Demand paging simulation steps.

    Returns:
        str: Plotly HTML div.
    """
    step_nums = [s["step"] for s in steps]
    ws_sizes = [s["working_set"] for s in steps]
    is_fault = [s["fault"] for s in steps]

    colors = [COLORS["danger"] if f else COLORS["success"] for f in is_fault]

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=step_nums,
        y=ws_sizes,
        mode="lines+markers",
        name="Working Set Size",
        line=dict(color=COLORS["primary"], width=2),
        marker=dict(size=8, color=colors, line=dict(width=1, color=COLORS["text"])),
    ))

    fig.update_layout(
        **LAYOUT_DEFAULTS,
        title="Working Set Size Over Time",
        xaxis_title="Step",
        yaxis_title="Pages in Memory",
    )

    return _to_html(fig)
