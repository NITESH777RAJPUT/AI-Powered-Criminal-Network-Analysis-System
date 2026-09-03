"""
UI and Graph Visualization Utilities
Provides PyVis interactive network visualization builders,
Plotly chart generators for analytics, and formatting helpers.
"""

import json
import tempfile
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import plotly.express as px
import plotly.graph_objects as go
from pyvis.network import Network
from src.config import NODE_COLORS, NODE_SIZES

def generate_pyvis_html(
    nodes: List[Dict[str, Any]],
    edges: List[Dict[str, Any]],
    height: str = "600px",
    width: str = "100%",
    physics: bool = True
) -> str:
    """
    Builds an interactive dark-themed network graph using PyVis and returns standalone HTML.
    Nodes are visually distinguished by type (Person: Red, Phone: Blue, Vehicle: Amber, etc.).
    """
    net = Network(height=height, width=width, directed=True, bgcolor="#0b0f19", font_color="#f8fafc")
    
    # Physics options for stable, aesthetic graph layout
    if physics:
        net.barnes_hut(
            gravity=-3500,
            central_gravity=0.3,
            spring_length=120,
            spring_strength=0.04,
            damping=0.09
        )
    else:
        net.toggle_physics(False)

    # Add Nodes
    for n in nodes:
        nid = str(n.get("id"))
        lbl = n.get("label", "Entity")
        name = n.get("name", nid)
        alias = n.get("alias", "")
        role = n.get("role", "")
        syndicate = n.get("syndicate", "")

        # Format hover tooltip
        title_lines = [f"<b>Type:</b> {lbl}", f"<b>ID:</b> {nid}", f"<b>Name:</b> {name}"]
        if alias and alias != "None":
            title_lines.append(f"<b>Alias:</b> {alias}")
        if role:
            title_lines.append(f"<b>Role:</b> {role}")
        if syndicate:
            title_lines.append(f"<b>Syndicate:</b> {syndicate}")
        title = "<br>".join(title_lines)

        color = NODE_COLORS.get(lbl, "#94a3b8")
        size = NODE_SIZES.get(lbl, 16)

        # Highlight suspects with borders
        border_color = "#f43f5e" if n.get("is_suspect") else "#334155"

        net.add_node(
            nid,
            label=name[:20] + ("..." if len(name) > 20 else ""),
            title=title,
            color={"background": color, "border": border_color, "highlight": {"background": "#00e5ff", "border": "#ffffff"}},
            size=size,
            shape="dot",
            font={"size": 11, "color": "#f8fafc", "face": "Inter, sans-serif"}
        )

    # Add Edges
    for e in edges:
        source = str(e.get("source"))
        target = str(e.get("target"))
        rel_type = str(e.get("type", "CONNECTED_TO"))
        
        # Edge tooltip
        edge_title = f"<b>Relationship:</b> {rel_type}"
        for k, v in e.items():
            if k not in ["source", "target", "type"]:
                edge_title += f"<br><b>{k}:</b> {v}"

        # Color edges by type
        edge_color = "#3b82f6"
        if rel_type in ["TRANSFERRED"]:
            edge_color = "#ec4899"
        elif rel_type in ["USES"]:
            edge_color = "#f59e0b"
        elif rel_type in ["INVOLVED_IN"]:
            edge_color = "#ef4444"
        elif rel_type in ["MENTIONED_IN"]:
            edge_color = "#64748b"

        net.add_edge(
            source,
            target,
            title=edge_title,
            label=rel_type,
            color={"color": edge_color, "highlight": "#00e5ff", "opacity": 0.75},
            arrows="to",
            font={"size": 9, "color": "#94a3b8", "align": "middle"}
        )

    # Generate HTML content
    with tempfile.NamedTemporaryFile(delete=False, suffix=".html", mode="w", encoding="utf-8") as tf:
        net.write_html(tf.name)
        temp_path = tf.name

    with open(temp_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    try:
        Path(temp_path).unlink()
    except Exception:
        pass

    return html_content


def plot_entity_distribution(node_counts: Dict[str, int]) -> go.Figure:
    """Creates a dark Plotly donut chart showing distribution of entity categories."""
    labels = list(node_counts.keys())
    values = list(node_counts.values())
    colors = [NODE_COLORS.get(l, "#94a3b8") for l in labels]

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.55,
        marker=dict(colors=colors, line=dict(color="#0b0f19", width=2)),
        textinfo="label+value",
        hoverinfo="label+value+percent"
    )])

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#f8fafc", family="Inter, sans-serif"),
        margin=dict(t=30, b=20, l=20, r=20),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
    )
    return fig


def plot_centrality_scatter(df_leaderboard: Any) -> go.Figure:
    """Creates an interactive scatter chart of Betweenness vs PageRank."""
    if df_leaderboard.empty:
        return go.Figure()

    fig = px.scatter(
        df_leaderboard,
        x="betweenness_centrality",
        y="pagerank",
        size="raw_degree",
        color="syndicate",
        hover_name="name",
        hover_data=["alias", "role", "city", "Rank"],
        title="Influence Mapping: Betweenness (Brokers) vs PageRank (Commanders)",
        labels={
            "betweenness_centrality": "Betweenness Centrality (Bridge / Broker Index)",
            "pagerank": "PageRank Centrality (Influence / Prestige)",
            "raw_degree": "Direct Connections"
        },
        template="plotly_dark"
    )

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#111827",
        font=dict(color="#f8fafc", family="Inter, sans-serif"),
        margin=dict(t=40, b=30, l=40, r=30)
    )
    return fig


def plot_transaction_volume_timeline(transactions_df: Any) -> go.Figure:
    """Creates a bar chart of transaction volume by date with anomaly highlights."""
    if transactions_df.empty:
        return go.Figure()

    df = transactions_df.copy()
    df["date"] = df["timestamp"].astype(str).str[:10]
    daily = df.groupby(["date", "pattern_flag"])["amount"].sum().reset_index()

    fig = px.bar(
        daily,
        x="date",
        y="amount",
        color="pattern_flag",
        title="Transaction Volume Flow & Anomaly Detection",
        labels={"amount": "Total Amount (INR)", "date": "Transaction Date", "pattern_flag": "Pattern Type"},
        template="plotly_dark",
        color_discrete_map={
            "Normal Everyday Transfer": "#3b82f6",
            "Smurfing / Structuring": "#f59e0b",
            "High-Value Layering": "#ec4899",
            "Anomalous High Volume": "#ef4444"
        }
    )

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#111827",
        font=dict(color="#f8fafc", family="Inter, sans-serif"),
        margin=dict(t=40, b=30, l=40, r=30),
        xaxis=dict(tickangle=-45)
    )
    return fig

