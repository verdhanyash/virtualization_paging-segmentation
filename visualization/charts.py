import plotly.graph_objects as go
from typing import Dict


# =====================================================
# 1. FAULTS VS HITS BAR CHART
# =====================================================
def plot_faults_hits(result: Dict) -> go.Figure:
    fig = go.Figure(data=[
        go.Bar(name="Faults", x=[result["algorithm"]], y=[result["total_faults"]]),
        go.Bar(name="Hits", x=[result["algorithm"]], y=[result["total_hits"]])
    ])

    fig.update_layout(
        title=f"{result['algorithm']} - Faults vs Hits",
        barmode="group",
        xaxis_title="Algorithm",
        yaxis_title="Count"
    )

    return fig


# =====================================================
# 2. FAULT PROGRESSION LINE CHART
# =====================================================
def plot_fault_progression(result: Dict) -> go.Figure:
    cumulative_faults = []
    count = 0

    for step in result["steps"]:
        if step["fault"]:
            count += 1
        cumulative_faults.append(count)

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=list(range(len(cumulative_faults))),
        y=cumulative_faults,
        mode="lines+markers",
        name="Fault Progression"
    ))

    fig.update_layout(
        title=f"{result['algorithm']} - Fault Progression",
        xaxis_title="Step",
        yaxis_title="Cumulative Faults"
    )

    return fig


# =====================================================
# 3. FRAME STATE HEATMAP
# =====================================================
def plot_frame_heatmap(result: Dict) -> go.Figure:
    frames_over_time = [step["frames"] for step in result["steps"]]

    processed = [
        [page if page is not None else -1 for page in frame]
        for frame in frames_over_time
    ]

    fig = go.Figure(data=go.Heatmap(
        z=processed,
        colorscale="Viridis",
        colorbar=dict(title="Page Number")
    ))

    fig.update_layout(
        title=f"{result['algorithm']} - Frame Heatmap",
        xaxis_title="Frame Index",
        yaxis_title="Time Step"
    )

    return fig


# =====================================================
# 4. HIT vs FAULT TIMELINE (NEW - IMPORTANT)
# =====================================================
def plot_hit_fault_timeline(result: Dict) -> go.Figure:
    x = list(range(len(result["steps"])))
    y = [1 if step["fault"] else 0 for step in result["steps"]]

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=x,
        y=y,
        mode="markers+lines",
        name="Fault(1) / Hit(0)"
    ))

    fig.update_layout(
        title=f"{result['algorithm']} - Hit vs Fault Timeline",
        xaxis_title="Step",
        yaxis_title="Fault (1) / Hit (0)"
    )

    return fig

