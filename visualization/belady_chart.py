"""
Belady's Anomaly Chart — visualization/belady_chart.py (T8)

Server-side Plotly chart that visualizes Belady's Anomaly in FIFO
page replacement.  The chart highlights "violation" points where
increasing the frame count causes MORE page faults — a counter-
intuitive result unique to FIFO.

Theme: Strictly monotone (black / white / gray) to match the project.
Anomaly points are distinguished by SIZE, WEIGHT, and CONTRAST — not
colour.  The _base_layout helper is duplicated from comparison.py on
purpose so this module stays self-contained with zero local imports.

Functions:
    build_belady_chart — line chart with anomaly annotations
"""

import plotly.graph_objects as go
from typing import Dict, List


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

# Anomaly emphasis — still monotone, just brighter/bolder
_ANOMALY_POINT  = "#ffffff"                 # pure white — max contrast
_ANOMALY_FILL   = "rgba(255,255,255,0.06)"  # subtle white tint
_ANOMALY_BORDER = "rgba(255,255,255,0.25)"  # faint white outline
_NORMAL_POINT   = _GRAY                     # muted gray for normal points


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
# BELADY'S ANOMALY CHART
# =====================================================================
def build_belady_chart(anomaly_result: Dict) -> go.Figure:
    """
    Line chart visualizing Belady's Anomaly in FIFO page replacement.

    Plots fault count (y) vs frame count (x).  Under normal
    expectations, more frames → fewer faults.  When this is VIOLATED
    — faults INCREASE despite adding a frame — the chart highlights
    the violation with:

      - Larger, bright-white diamond markers on anomaly points
      - A bold white dashed line segment connecting the violation pair
      - A subtle shaded rectangle behind the violation zone
      - An annotation labeling the exact frame counts and fault delta

    All visuals stay strictly monotone (black / white / gray).

    Args:
        anomaly_result: Output of ``detect_beladys_anomaly()``::

            {
                "anomaly_found": bool,
                "fault_counts": {1: n, 2: n, ...},
                "anomaly_at": [(a, b), ...]
            }

            Each ``(a, b)`` pair means *b* frames produced MORE faults
            than *a* frames (b = a + 1).

    Returns:
        A ``plotly.graph_objects.Figure`` ready to be serialized or
        rendered.

    Raises:
        ValueError: If ``fault_counts`` is empty.

    Example::

        >>> from core.fifo import detect_beladys_anomaly
        >>> res = detect_beladys_anomaly([1,2,3,4,1,2,5,1,2,3,4,5], 10)
        >>> fig = build_belady_chart(res)
        >>> fig.write_html("belady.html")
    """
    fault_counts = anomaly_result["fault_counts"]
    anomaly_pairs = anomaly_result["anomaly_at"]
    anomaly_found = anomaly_result["anomaly_found"]

    # ── Guard: empty data ─────────────────────────────────────────
    if not fault_counts:
        raise ValueError(
            "fault_counts is empty — nothing to plot. "
            "Run detect_beladys_anomaly() with max_frames >= 1."
        )

    # Build x / y data sorted by frame count
    frame_nums: List[int] = sorted(fault_counts.keys())
    faults: List[int] = [fault_counts[f] for f in frame_nums]

    # Identify which frame counts belong to an anomaly pair
    anomaly_frames: set = set()
    for a, b in anomaly_pairs:
        anomaly_frames.add(a)
        anomaly_frames.add(b)

    # ── Per-point styling ─────────────────────────────────────────
    #    Anomaly  → large bright-white diamond  (stands out)
    #    Normal   → small muted-gray circle     (recedes)
    point_colors: List[str] = []
    point_sizes: List[int] = []
    point_symbols: List[str] = []

    for f in frame_nums:
        if f in anomaly_frames:
            point_colors.append(_ANOMALY_POINT)
            point_sizes.append(11)
            point_symbols.append("diamond")
        else:
            point_colors.append(_NORMAL_POINT)
            point_sizes.append(5)
            point_symbols.append("circle")

    # ── Main fault-count line ─────────────────────────────────────
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        name="Faults",
        x=frame_nums,
        y=faults,
        mode="lines+markers",
        line=dict(color=_GRAY, width=1.5),
        marker=dict(
            size=point_sizes,
            color=point_colors,
            symbol=point_symbols,
            line=dict(width=0),
        ),
        hovertemplate=(
            "<b>%{x} frames</b><br>"
            "Faults: %{y}"
            "<extra></extra>"
        ),
    ))

    # ── Violation highlights (one per anomaly pair) ───────────────
    for a, b in anomaly_pairs:
        faults_a = fault_counts[a]
        faults_b = fault_counts[b]

        # Bold white dashed segment connecting the two violation points
        fig.add_trace(go.Scatter(
            x=[a, b],
            y=[faults_a, faults_b],
            mode="lines",
            line=dict(color=_WHITE, width=2.5, dash="dash"),
            showlegend=False,
            hoverinfo="skip",
        ))

        # Subtle shaded rectangle behind the violation zone
        fig.add_shape(
            type="rect",
            x0=a - 0.2,
            x1=b + 0.2,
            y0=min(faults_a, faults_b) - 0.4,
            y1=max(faults_a, faults_b) + 0.4,
            fillcolor=_ANOMALY_FILL,
            line=dict(color=_ANOMALY_BORDER, width=1, dash="dot"),
            layer="below",
        )

        # Annotation arrow pointing at the higher-fault point
        delta = faults_b - faults_a
        fig.add_annotation(
            x=b,
            y=faults_b,
            text=(
                f"<b>▲ BELADY'S ANOMALY</b><br>"
                f"{a} frames → {faults_a} faults<br>"
                f"{b} frames → {faults_b} faults<br>"
                f"<i>+{delta} more fault{'s' if delta != 1 else ''}"
                f" with more frames</i>"
            ),
            showarrow=True,
            arrowhead=2,
            arrowsize=1.2,
            arrowwidth=1.5,
            arrowcolor=_WHITE,
            ax=60,
            ay=-55,
            font=dict(family=_FONT, size=10, color=_WHITE),
            align="left",
            bordercolor=_ANOMALY_BORDER,
            borderwidth=1,
            borderpad=6,
            bgcolor="rgba(255,255,255,0.05)",
        )

    # ── No-anomaly annotation ─────────────────────────────────────
    if not anomaly_found:
        fig.add_annotation(
            x=frame_nums[-1],
            y=faults[-1],
            text=(
                "<b>No anomaly detected</b><br>"
                "<i>Faults decrease monotonically as expected</i>"
            ),
            showarrow=True,
            arrowhead=2,
            arrowcolor=_DARK,
            ax=-50,
            ay=-40,
            font=dict(family=_FONT, size=10, color=_MUTED),
            bordercolor=_DARK,
            borderwidth=1,
            borderpad=6,
            bgcolor="rgba(68,68,68,0.08)",
        )

    # ── Layout ────────────────────────────────────────────────────
    y_max = max(faults)
    y_min = min(faults)

    fig.update_layout(
        **_base_layout(
            title=dict(
                text="Belady's Anomaly Detection — FIFO",
                font=dict(size=13, color=_GRAY),
                x=0.0,
                xanchor="left",
            ),
            xaxis=dict(
                gridcolor=_GRID,
                linecolor=_BORDER,
                tickfont=dict(color=_MUTED, size=11),
                title_text="Frame Count",
                title_font=dict(color=_GRAY, size=11),
                dtick=1,
                range=[frame_nums[0] - 0.4, frame_nums[-1] + 0.4],
            ),
            yaxis=dict(
                gridcolor=_GRID,
                linecolor=_BORDER,
                tickfont=dict(color=_MUTED, size=11),
                title_text="Total Page Faults",
                title_font=dict(color=_GRAY, size=11),
                range=[max(0, y_min - 1), y_max + 2],
                dtick=max(1, (y_max - y_min) // 6) if y_max > y_min else 1,
            ),
            showlegend=False,
            hovermode="x unified",
        )
    )

    return fig
