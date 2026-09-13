try:
    import plotly.graph_objects as go
    import plotly.express as px
    HAS_PLOTLY = True
except Exception:
    go = None
    px = None
    HAS_PLOTLY = False

import pandas as pd
from typing import List, Dict, Any, Optional

CHART_THEME = {
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "rgba(0,0,0,0)",
    "font": {"family": "Plus Jakarta Sans, sans-serif", "color": "#cbd5e1"},
    "margin": dict(l=20, r=20, t=40, b=20),
}

def plot_planned_vs_actual(tasks: List[Dict[str, Any]]) -> Optional[Any]:
    """Renders Real vs. Planned Durations for L4 & L5 activities to track bottlenecks."""
    if not HAS_PLOTLY or not go:
        return None
    filtered = [t for t in tasks if t["level"] in ("L4", "L5") and t.get("planned_duration", 0) > 0]
    if not filtered:
        return go.Figure()

    df = pd.DataFrame(filtered)
    df["variance"] = df["actual_duration"] - df["planned_duration"]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df["code"],
        y=df["planned_duration"],
        name="Planned Duration (Days)",
        marker_color="rgba(56, 189, 248, 0.7)",
        marker_line=dict(width=1, color="#38bdf8")
    ))
    fig.add_trace(go.Bar(
        x=df["code"],
        y=df["actual_duration"],
        name="Actual Spent (Days)",
        marker_color="rgba(245, 158, 11, 0.8)",
        marker_line=dict(width=1, color="#f59e0b")
    ))

    fig.update_layout(
        title="<b>Planned vs. Actual Duration by Activity (Days)</b>",
        barmode="group",
        xaxis_tickangle=-35,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        **CHART_THEME
    )
    fig.update_xaxes(showgrid=False, linecolor="rgba(255,255,255,0.1)")
    fig.update_yaxes(showgrid=True, gridcolor="rgba(255,255,255,0.06)")
    return fig

def plot_discipline_progress(tasks: List[Dict[str, Any]]) -> Optional[Any]:
    """Discipline bottleneck tracking across Civil, Piping, Electrical, Quality."""
    if not HAS_PLOTLY or not go:
        return None
    df = pd.DataFrame(tasks)
    if df.empty or "discipline" not in df:
        return go.Figure()

    # Filter out project management
    df_disc = df[df["discipline"] != "Project Management"].copy()
    disc_summary = df_disc.groupby("discipline")["progress_pct"].mean().reset_index()

    colors = ["#10b981", "#38bdf8", "#f59e0b", "#ec4899", "#8b5cf6"]

    fig = go.Figure(go.Bar(
        x=disc_summary["progress_pct"],
        y=disc_summary["discipline"],
        orientation="h",
        marker=dict(
            color=disc_summary["progress_pct"],
            colorscale=[[0, "#ef4444"], [0.5, "#f59e0b"], [1.0, "#10b981"]],
            line=dict(width=1, color="rgba(255,255,255,0.2)")
        ),
        text=[f"{p:.1f}%" for p in disc_summary["progress_pct"]],
        textposition="auto",
    ))

    fig.update_layout(
        title="<b>Average Progress Completion by Discipline (%)</b>",
        xaxis=dict(range=[0, 105], showgrid=True, gridcolor="rgba(255,255,255,0.06)"),
        yaxis=dict(showgrid=False),
        **CHART_THEME
    )
    return fig

def plot_status_distribution(tasks: List[Dict[str, Any]]) -> Optional[Any]:
    """Donut chart showing project status distribution."""
    if not HAS_PLOTLY or not go:
        return None
    df = pd.DataFrame(tasks)
    if df.empty:
        return go.Figure()

    status_counts = df["status"].value_counts().reset_index()
    status_counts.columns = ["status", "count"]

    color_map = {
        "COMPLETED": "#10b981",
        "IN_PROGRESS": "#38bdf8",
        "NOT_STARTED": "#64748b",
        "DELAYED": "#ef4444"
    }

    colors = [color_map.get(s, "#94a3b8") for s in status_counts["status"]]

    fig = go.Figure(go.Pie(
        labels=status_counts["status"],
        values=status_counts["count"],
        hole=0.6,
        marker=dict(colors=colors, line=dict(color="#0f172a", width=2)),
        textinfo="label+percent",
        hoverinfo="label+value"
    ))

    fig.update_layout(
        title="<b>Overall Task Status Distribution</b>",
        showlegend=False,
        **CHART_THEME
    )
    return fig

def plot_wbs_sunburst(tasks: List[Dict[str, Any]]) -> Optional[Any]:
    """Multi-level WBS Sunburst Hierarchy showing L1 through L6."""
    if not HAS_PLOTLY or not go:
        return None
    df = pd.DataFrame(tasks)
    if df.empty:
        return go.Figure()

    # Fill NaN parents with empty string
    df["parent_id"] = df["parent_id"].fillna("")
    df["hover_text"] = df["name"] + "<br>Progress: " + df["progress_pct"].astype(str) + "%"

    fig = go.Figure(go.Sunburst(
        ids=df["id"],
        labels=df["code"],
        parents=df["parent_id"],
        values=df["weight"].fillna(1.0),
        hovertext=df["hover_text"],
        branchvalues="total",
        marker=dict(
            colors=df["progress_pct"],
            colorscale=[[0, "#334155"], [0.3, "#f59e0b"], [0.7, "#38bdf8"], [1.0, "#10b981"]],
            showscale=True,
            colorbar=dict(title="Progress %", thickness=12, len=0.7)
        )
    ))

    fig.update_layout(
        title="<b>Interactive WBS Hierarchy (L1 → L6) with Roll-up Progress</b>",
        **CHART_THEME
    )
    return fig
