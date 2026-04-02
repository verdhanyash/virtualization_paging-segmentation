"""
Algorithm Comparison — visualization/comparison.py (T7)

Server-side Plotly charts for comparing FIFO, LRU, and Optimal
page replacement algorithms side by side.

Functions:
    run_all_algorithms  — executes all three algorithms, returns combined dict
    build_comparison_bar — grouped bar chart: faults vs hits per algorithm
    build_fault_race     — overlaid line chart: cumulative faults over steps
    build_summary_table  — tabular figure with key metrics per algorithm
"""

import plotly.graph_objects as go
from typing import Dict, List

from core.fifo import run_fifo
from core.lru import run_lru
from core.optimal import run_optimal


# ─── Theme constants (matches project: jet-black / white) ────────────────────
_BG       = "#0a0a0a"
_BG_PANEL = "#111111"
_GRID     = "rgba(255,255,255,0.04)"
_BORDER   = "#2a2a2a"
_WHITE    = "#f0f0f0"
_GRAY     = "#888888"
_DARK     = "#444444"
_MUTED    = "#555555"
_FONT     = "Geist Mono, Courier New, monospace"

# Per-algorithm colours — consistent across every chart
_ALGO_COLORS = {
    "FIFO":    _WHITE,          # bright white
    "LRU":     _GRAY,           # mid gray
    "Optimal": _DARK,           # dark gray
}
_ALGO_ORDER = ["FIFO", "LRU", "Optimal"]


def _hex_to_rgba(hex_color: str, alpha: float) -> str:
    """Convert a hex colour like '#f0f0f0' to 'rgba(240,240,240,0.12)'."""
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


def _base_layout(**overrides) -> dict:
    """Shared dark-theme layout applied to every figure."""
    layout = dict(
        font=dict(family=_FONT, size=12, color=_WHITE),
        paper_bgcolor=_BG,
        plot_bgcolor=_BG_PANEL,
        margin=dict(l=60, r=30, t=50, b=50),
        xaxis=dict(
            gridcolor=_GRID,
            linecolor=_BORDER,
            tickfont=dict(color=_MUTED, size=11),
            title_font=dict(color=_GRAY, size=11),
        ),
        yaxis=dict(
            gridcolor=_GRID,
            linecolor=_BORDER,
            tickfont=dict(color=_MUTED, size=11),
            title_font=dict(color=_GRAY, size=11),
        ),
        legend=dict(
            font=dict(color=_GRAY, size=11),
            bgcolor="rgba(0,0,0,0)",
            borderwidth=0,
        ),
    )
    layout.update(overrides)
    return layout


# =====================================================================
# 1. RUN ALL ALGORITHMS
# =====================================================================
def run_all_algorithms(
    reference_string: List[int],
    frame_count: int,
) -> Dict[str, Dict]:
    """
    Execute FIFO, LRU, and Optimal on the same inputs.

    Args:
        reference_string: Sequence of page numbers.
        frame_count:      Number of physical frames.

    Returns:
        {"FIFO": result, "LRU": result, "Optimal": result}
        Each value follows the standard result dict format.
    """
    return {
        "FIFO":    run_fifo(reference_string, frame_count),
        "LRU":     run_lru(reference_string, frame_count),
        "Optimal": run_optimal(reference_string, frame_count),
    }


# =====================================================================
# 2. COMPARISON BAR CHART — Faults vs Hits
# =====================================================================
def build_comparison_bar(all_results: Dict[str, Dict]) -> go.Figure:
    """
    Grouped bar chart comparing page faults and hits across algorithms.

    Bars are grouped per algorithm (FIFO, LRU, Optimal).
    Fault bars use each algo's signature colour; hit bars use a
    translucent outline variant so faults — the critical metric —
    dominate visually.

    Args:
        all_results: Output of run_all_algorithms().

    Returns:
        A Plotly Figure object.
    """
    algos  = _ALGO_ORDER
    faults = [all_results[a]["total_faults"] for a in algos]
    hits   = [all_results[a]["total_hits"]   for a in algos]
    colors = [_ALGO_COLORS[a] for a in algos]

    fig = go.Figure()

    # — Fault bars (solid, prominent) —
    fig.add_trace(go.Bar(
        name="Faults",
        x=algos,
        y=faults,
        marker=dict(
            color=colors,
            line=dict(width=0),
            cornerradius=3,
        ),
        text=faults,
        textposition="outside",
        textfont=dict(color=_WHITE, size=13, family=_FONT),
        width=0.32,
        offset=-0.18,
    ))

    # — Hit bars (translucent outline, secondary) —
    hit_fill   = [_hex_to_rgba(c, 0.12) for c in colors]
    hit_border = [_hex_to_rgba(c, 0.35) for c in colors]

    fig.add_trace(go.Bar(
        name="Hits",
        x=algos,
        y=hits,
        marker=dict(
            color=hit_fill,
            line=dict(color=hit_border, width=1.5),
            cornerradius=3,
        ),
        text=hits,
        textposition="outside",
        textfont=dict(color=_MUTED, size=13, family=_FONT),
        width=0.32,
        offset=0.18,
    ))

    # — Layout —
    y_max = max(max(faults), max(hits)) if faults and hits else 10
    fig.update_layout(
        **_base_layout(
            title=dict(
                text="Algorithm Comparison — Faults vs Hits",
                font=dict(size=13, color=_GRAY),
                x=0.0,
                xanchor="left",
            ),
            barmode="group",
            bargap=0.35,
            yaxis=dict(
                gridcolor=_GRID,
                linecolor=_BORDER,
                tickfont=dict(color=_MUTED, size=11),
                title_text="Count",
                title_font=dict(color=_GRAY, size=11),
                range=[0, y_max * 1.2],
                dtick=max(1, y_max // 5),
            ),
            xaxis=dict(
                gridcolor="rgba(0,0,0,0)",
                linecolor=_BORDER,
                tickfont=dict(color=_WHITE, size=12),
                title_text="",
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.04,
                xanchor="right",
                x=1,
                font=dict(color=_GRAY, size=11),
            ),
        )
    )

    return fig


# =====================================================================
# 3. FAULT RACE — Cumulative Faults Over Steps
# =====================================================================
def build_fault_race(all_results: Dict[str, Dict]) -> go.Figure:
    """
    Overlaid line chart showing cumulative page faults per step
    for each algorithm on a shared axis.

    Allows instant visual comparison of how quickly each algorithm
    accumulates faults. Optimal should always be the lowest line.

    Args:
        all_results: Output of run_all_algorithms().

    Returns:
        A Plotly Figure object.
    """
    fig = go.Figure()

    for algo in _ALGO_ORDER:
        result = all_results[algo]
        steps  = result["steps"]

        # Build cumulative fault counts
        cumulative: List[int] = []
        running = 0
        for step in steps:
            if step["fault"]:
                running += 1
            cumulative.append(running)

        step_nums = list(range(1, len(steps) + 1))

        fig.add_trace(go.Scatter(
            name=algo,
            x=step_nums,
            y=cumulative,
            mode="lines+markers",
            line=dict(
                color=_ALGO_COLORS[algo],
                width=2,
            ),
            marker=dict(
                size=5,
                color=_ALGO_COLORS[algo],
                line=dict(width=0),
            ),
            hovertemplate=(
                f"<b>{algo}</b><br>"
                "Step %{x}<br>"
                "Cumulative Faults: %{y}"
                "<extra></extra>"
            ),
        ))

    # — Layout —
    max_steps = max(
        len(all_results[a]["steps"]) for a in _ALGO_ORDER
    )
    max_faults = max(
        all_results[a]["total_faults"] for a in _ALGO_ORDER
    )

    fig.update_layout(
        **_base_layout(
            title=dict(
                text="Cumulative Fault Race — All Algorithms",
                font=dict(size=13, color=_GRAY),
                x=0.0,
                xanchor="left",
            ),
            xaxis=dict(
                gridcolor=_GRID,
                linecolor=_BORDER,
                tickfont=dict(color=_MUTED, size=11),
                title_text="Step",
                title_font=dict(color=_GRAY, size=11),
                range=[0.5, max_steps + 0.5],
                dtick=max(1, max_steps // 12),
            ),
            yaxis=dict(
                gridcolor=_GRID,
                linecolor=_BORDER,
                tickfont=dict(color=_MUTED, size=11),
                title_text="Cumulative Faults",
                title_font=dict(color=_GRAY, size=11),
                range=[0, max_faults + 1],
                dtick=max(1, max_faults // 6),
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.04,
                xanchor="right",
                x=1,
                font=dict(color=_GRAY, size=11),
            ),
            hovermode="x unified",
        )
    )

    return fig


# =====================================================================
# 4. SUMMARY TABLE — Key Metrics At a Glance
# =====================================================================
def build_summary_table(all_results: Dict[str, Dict]) -> go.Figure:
    """
    Compact table figure highlighting the most important metrics
    for each algorithm in a scannable layout.

    Columns: Algorithm | Faults | Hits | Fault Rate | Best?
    The algorithm with the fewest faults is flagged with a ★.

    Args:
        all_results: Output of run_all_algorithms().

    Returns:
        A Plotly Figure (Table trace).
    """
    algos      = _ALGO_ORDER
    faults     = [all_results[a]["total_faults"] for a in algos]
    hits       = [all_results[a]["total_hits"]   for a in algos]
    totals     = [f + h for f, h in zip(faults, hits)]
    rates      = [f"{(f / t * 100):.1f}%" if t > 0 else "—"
                  for f, t in zip(faults, totals)]
    best_val   = min(faults)
    best_flags = ["★" if f == best_val else "" for f in faults]

    # Row fill: subtly highlight the best-performing row
    row_fills = [
        "#1a1a1a" if f == best_val else _BG_PANEL
        for f in faults
    ]

    fig = go.Figure(data=[go.Table(
        columnwidth=[140, 80, 80, 100, 60],
        header=dict(
            values=["Algorithm", "Faults", "Hits", "Fault Rate", "Best"],
            fill_color="#161616",
            font=dict(family=_FONT, size=11, color=_GRAY),
            align=["left", "right", "right", "right", "center"],
            line=dict(color=_BORDER, width=1),
            height=32,
        ),
        cells=dict(
            values=[algos, faults, hits, rates, best_flags],
            fill_color=[row_fills],
            font=dict(
                family=_FONT,
                size=12,
                color=[
                    [_ALGO_COLORS[a] for a in algos],  # algo name colour
                    [_WHITE] * 3,                       # faults
                    [_MUTED] * 3,                       # hits
                    [_GRAY]  * 3,                       # rate
                    [_WHITE] * 3,                       # best flag
                ],
            ),
            align=["left", "right", "right", "right", "center"],
            line=dict(color=_BORDER, width=1),
            height=30,
        ),
    )])

    fig.update_layout(
        paper_bgcolor=_BG,
        margin=dict(l=0, r=0, t=40, b=10),
        title=dict(
            text="Performance Summary",
            font=dict(family=_FONT, size=13, color=_GRAY),
            x=0.0,
            xanchor="left",
        ),
    )

    return fig
