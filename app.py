"""
AI-POWERED CRIMINAL NETWORK ANALYSIS SYSTEM
Professional Law-Enforcement & Cyber Intelligence Multi-Page Dashboard
Main Streamlit Application Entrypoint
"""

import os
import json
import time
import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime

# Streamlit Page Setup
st.set_page_config(
    page_title="Criminal Network Analysis System",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import Core Subsystems
from src.config import (
    ASSETS_DIR, DATA_DIR, REPORTS_DIR, EXPORT_REPORTS_DIR,
    NODE_COLORS, RISK_LEVELS, DISCLAIMER_TEXT, GRAPH_BACKEND,
    NEO4J_URI, NEO4J_USERNAME, NEO4J_DATABASE
)
from src.data_loader import DataLoader
from src.data_cleaner import DataCleaner
from src.entity_extractor import EntityExtractor
from src.relationship_extractor import RelationshipExtractor
from src.graph_manager import GraphManager
from src.network_analysis import NetworkAnalysisEngine
from src.anomaly_detection import AnomalyDetectionEngine
from src.suspicious_rules import SuspiciousRulesEngine
from src.risk_scoring import RiskScoringEngine
from src.evidence_integrity import EvidenceIntegrityLedger
from src.report_generator import ReportGenerator
from src.utils import (
    generate_pyvis_html,
    plot_entity_distribution,
    plot_centrality_scatter,
    plot_transaction_volume_timeline
)

# -------------------------------------------------------------
# CSS Styling & Theme Injection
# -------------------------------------------------------------
def load_custom_css():
    css_file = ASSETS_DIR / "custom.css"
    if css_file.exists():
        with open(css_file, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_custom_css()

# -------------------------------------------------------------
# Application State Initialization
# -------------------------------------------------------------
@st.cache_resource(show_spinner="Initializing Intelligence Knowledge Graph...")
def initialize_system():
    """Initializes and builds the core system knowledge graph and models."""
    loader = DataLoader()
    datasets = loader.load_all_datasets()
    
    graph_mgr = GraphManager()
    
    # If persistent store exists, load from disk; otherwise build from datasets
    if graph_mgr.nx_graph.number_of_nodes() == 0:
        graph_mgr.build_from_datasets(datasets)
    
    net_engine = NetworkAnalysisEngine(graph_mgr.nx_graph)
    anom_engine = AnomalyDetectionEngine()
    rules_engine = SuspiciousRulesEngine()
    risk_engine = RiskScoringEngine()
    
    # Initialize Persistent Evidence Ledger
    ledger = EvidenceIntegrityLedger()
    reports_list = datasets.get("reports", [])
    if len(ledger.chain) <= 1:
        for rep in reports_list:
            rep_id = rep.get("report_id", "REP-000")
            filename = rep.get("filename", "report.txt")
            filepath = rep.get("filepath", "")
            if filepath and Path(filepath).exists():
                ledger.add_evidence(rep_id, filename, Path(filepath))
            else:
                ledger.add_evidence(rep_id, filename, rep.get("content", ""))

    return {
        "loader": loader,
        "datasets": datasets,
        "graph_mgr": graph_mgr,
        "net_engine": net_engine,
        "anom_engine": anom_engine,
        "rules_engine": rules_engine,
        "risk_engine": risk_engine,
        "ledger": ledger,
        "report_gen": ReportGenerator(),
        "rel_extractor": RelationshipExtractor(),
        "entity_extractor": EntityExtractor()
    }

sys_state = initialize_system()
loader = sys_state["loader"]
datasets = sys_state["datasets"]
graph_mgr = sys_state["graph_mgr"]
net_engine = sys_state["net_engine"]
anom_engine = sys_state["anom_engine"]
rules_engine = sys_state["rules_engine"]
risk_engine = sys_state["risk_engine"]
ledger = sys_state["ledger"]
report_gen = sys_state["report_gen"]
rel_extractor = sys_state["rel_extractor"]
entity_extractor = sys_state["entity_extractor"]

# Update Network Analysis Engine with current graph state
net_engine.nx_graph = graph_mgr.nx_graph

# Compute Centralities and Baseline Analyses
centralities = net_engine.calculate_centralities()
communities = net_engine.detect_communities()
bridge_nodes = net_engine.find_bridge_nodes()
leaderboard_df = net_engine.get_influential_persons_leaderboard(top_n=50)

# Evaluate Suspicion Rules & Anomalies
all_alerts = rules_engine.evaluate_all_rules(
    persons_df=datasets.get("persons"),
    transactions_df=datasets.get("transactions"),
    incidents_df=datasets.get("incidents"),
    centralities=centralities,
    communities=communities,
    graph_manager=graph_mgr
)

feature_matrix = anom_engine.build_entity_feature_matrix(
    persons_df=datasets.get("persons"),
    transactions_df=datasets.get("transactions"),
    incidents_df=datasets.get("incidents"),
    centrality_map=centralities,
    graph_manager=graph_mgr
)
scored_features = anom_engine.detect_anomalous_entities(feature_matrix)

all_risk_scores_df = risk_engine.compute_all_risk_scores(
    persons_df=datasets.get("persons"),
    feature_df=scored_features,
    centrality_map=centralities,
    all_alerts=all_alerts,
    bridge_nodes=bridge_nodes,
    graph_manager=graph_mgr
)

graph_stats = graph_mgr.get_graph_statistics()

# -------------------------------------------------------------
# Sidebar Navigation & System Status Banner
# -------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🛡️ CRIMINAL INTEL SYSTEM")
    st.markdown("<small style='color:#94a3b8;'>AI & Graph Network Forensics v2.0 (Persistent)</small>", unsafe_allow_html=True)
    st.markdown("---")

    backend_status = "🟢 Neo4j Database" if graph_mgr.is_neo4j_active() else "🔵 Local Persistent Engine"
    st.info(f"**Backend Mode:** {backend_status}")

    page = st.radio(
        "NAVIGATION",
        [
            "📊 Executive Dashboard",
            "📥 Data Ingestion & NLP",
            "🕸️ Interactive Network Explorer",
            "🔍 Entity Search & Dossier",
            "📈 Network Analytics",
            "🚨 Suspicious Activity & ML",
            "⛓️ Evidence Integrity Ledger",
            "📄 Investigation Dossier Export",
            "⚙️ System Settings"
        ],
        index=0
    )

    st.markdown("---")
    st.markdown(f"**Total Entities:** `{graph_stats['total_nodes']}`")
    st.markdown(f"**Active Relationships:** `{graph_stats['total_edges']}`")
    st.markdown(f"**Security Alerts:** `{len(all_alerts)}`")
    st.markdown(f"**Evidence Blocks:** `{len(ledger.chain)}`")
    
    st.markdown("---")
    st.caption("Forensic Intelligence System. Data backed by persistent store.")


# =============================================================
# PAGE 1: EXECUTIVE DASHBOARD
# =============================================================
if page == "📊 Executive Dashboard":
    st.markdown("""
    <div class="intel-header">
        <h1>🛡️ Criminal Network Intelligence Dashboard</h1>
        <p>Real-time topological relationship analysis, anomaly detection, and syndicate tracking.</p>
    </div>
    """, unsafe_allow_html=True)

    # High-Level KPI Cards
    kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5, kpi_col6 = st.columns(6)
    
    total_persons = graph_stats["node_counts"].get("Person", 0)
    total_phones = graph_stats["node_counts"].get("Phone", 0)
    total_vehicles = graph_stats["node_counts"].get("Vehicle", 0)
    total_tx = len(datasets.get("transactions", []))
    critical_alerts = sum(1 for a in all_alerts if a.get("severity") == "Critical")
    high_risk_suspects = len(all_risk_scores_df[all_risk_scores_df["risk_score"] >= 60]) if not all_risk_scores_df.empty else 0

    with kpi_col1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Total Entities</div>
            <div class="kpi-value">{graph_stats['total_nodes']}</div>
            <div class="kpi-subtitle">Across {len(graph_stats['node_counts'])} Labels</div>
        </div>
        """, unsafe_allow_html=True)

    with kpi_col2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Tracked Persons</div>
            <div class="kpi-value">{total_persons}</div>
            <div class="kpi-subtitle">Suspects & Civilians</div>
        </div>
        """, unsafe_allow_html=True)

    with kpi_col3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Relationships</div>
            <div class="kpi-value">{graph_stats['total_edges']}</div>
            <div class="kpi-subtitle">Connected Links</div>
        </div>
        """, unsafe_allow_html=True)

    with kpi_col4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Transactions</div>
            <div class="kpi-value">{total_tx}</div>
            <div class="kpi-subtitle">Financial Records</div>
        </div>
        """, unsafe_allow_html=True)

    with kpi_col5:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Active Alerts</div>
            <div class="kpi-value" style="color:#f43f5e;">{len(all_alerts)}</div>
            <div class="kpi-subtitle">{critical_alerts} Critical Flags</div>
        </div>
        """, unsafe_allow_html=True)

    with kpi_col6:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">High-Risk Suspects</div>
            <div class="kpi-value" style="color:#f59e0b;">{high_risk_suspects}</div>
            <div class="kpi-subtitle">Score &ge; 60/100</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Main Dashboard Visual Grid
    dash_col_left, dash_col_right = st.columns([1.4, 1.0])

    with dash_col_left:
        st.subheader("🌐 Global Network Overview Preview")
        preview_nodes = [dict(data, id=nid) for nid, data in list(graph_mgr.nx_graph.nodes(data=True))[:60]]
        preview_node_ids = {n["id"] for n in preview_nodes}
        preview_edges = [
            dict(edata, source=u, target=v, type=k)
            for u, v, k, edata in list(graph_mgr.nx_graph.edges(keys=True, data=True))
            if u in preview_node_ids and v in preview_node_ids
        ][:90]

        html_preview = generate_pyvis_html(preview_nodes, preview_edges, height="450px")
        st.components.v1.html(html_preview, height=460)

    with dash_col_right:
        st.subheader("📊 Entity Distribution Breakdown")
        fig_dist = plot_entity_distribution(graph_stats["node_counts"])
        st.plotly_chart(fig_dist, use_container_width=True)

    st.markdown("---")

    # Lower Grid: Top Influential Suspects + Live Suspicious Alerts Feed
    feed_col1, feed_col2 = st.columns([1.2, 1.0])

    with feed_col1:
        st.subheader("🏆 Top Influential / Prioritized Suspects")
        if not all_risk_scores_df.empty:
            top_suspects_display = all_risk_scores_df[["person_id", "name", "alias", "syndicate", "role", "risk_score", "risk_tier"]].head(8)
            st.dataframe(
                top_suspects_display,
                column_config={
                    "risk_score": st.column_config.ProgressColumn("Risk Score", min_value=0, max_value=100, format="%.1f"),
                    "person_id": "ID",
                    "name": "Full Name",
                    "alias": "Alias",
                    "syndicate": "Syndicate / Group",
                    "role": "Role",
                    "risk_tier": "Risk Tier"
                },
                hide_index=True,
                use_container_width=True
            )
        else:
            st.info("No persons registered yet.")

    with feed_col2:
        st.subheader("🚨 Recent Forensic Alerts Feed")
        if all_alerts:
            for alt in all_alerts[:5]:
                badge_type = "badge-critical" if alt["severity"] == "Critical" else ("badge-high" if alt["severity"] == "High" else "badge-moderate")
                st.markdown(f"""
                <div style="background:#1e293b; border-left:4px solid {'#f43f5e' if alt['severity']=='Critical' else '#f59e0b'}; padding:0.6rem 0.9rem; border-radius:6px; margin-bottom:0.5rem;">
                    <span class="badge {badge_type}">{alt['severity']}</span> 
                    <strong style="color:#ffffff; font-size:0.9rem;">{alt['rule_id']}: {alt['rule_name']}</strong>
                    <p style="color:#94a3b8; font-size:0.8rem; margin:0.2rem 0 0 0;">{alt['reason']}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("No suspicious alerts triggered.")


# =============================================================
# PAGE 2: DATA INGESTION & NLP EXTRACTION
# =============================================================
elif page == "📥 Data Ingestion & NLP":
    st.markdown("""
    <div class="intel-header">
        <h1>📥 Data Ingestion & Automated Entity Extraction</h1>
        <p>Upload structured CSV datasets or unstructured intelligence field reports to dynamically extract entities, infer relationships, and commit them directly to the database.</p>
    </div>
    """, unsafe_allow_html=True)

    tab_structured, tab_unstructured = st.tabs(["📁 Structured Dataset Ingestion (CSV / JSON)", "📝 Unstructured Text Report Extraction (TXT / Bulletins)"])

    with tab_structured:
        st.markdown("#### Upload Structured Intelligence Files")
        uploaded_file = st.file_uploader("Choose a CSV or JSON file to ingest into database", type=["csv", "json", "txt"], key="struct_uploader")

        if uploaded_file is not None:
            if st.button("🚀 Ingest, Clean & Commit to Database", key="btn_commit_csv"):
                with st.spinner("Executing data ingestion, schema validation, and graph commit..."):
                    res_stats = loader.ingest_and_commit(uploaded_file, graph_mgr)

                if res_stats["success"]:
                    st.success(f"File '{uploaded_file.name}' successfully ingested and committed to database!")
                    c1, c2, c3, c4, c5 = st.columns(5)
                    with c1:
                        st.metric("Rows Uploaded", res_stats["rows_uploaded"])
                    with c2:
                        st.metric("Rows Accepted", res_stats["rows_accepted"])
                    with c3:
                        st.metric("Rows Rejected", res_stats["rows_rejected"])
                    with c4:
                        st.metric("Nodes Created", res_stats["nodes_created"])
                    with c5:
                        st.metric("Edges Created", res_stats["relationships_created"])
                    
                    st.cache_resource.clear()
                    st.info("Knowledge Graph and persistent store updated successfully.")
                else:
                    st.error(f"Ingestion failed: {res_stats.get('message', 'Unknown error')}")
                    for err in res_stats.get("errors", []):
                        st.warning(err)

    with tab_unstructured:
        st.markdown("#### NLP Entity & Relationship Extractor on Free-Text Bulletins")
        sample_report_text = """Rahul Sharma met Amit Kumar near Pune railway station on 15 August 2026. Amit was using vehicle MH12AB1234 and contacted phone number 9876543210. A transaction of INR 85000 was recorded."""
        
        input_text = st.text_area("Paste Intelligence Text or Intercept Bulletin:", value=sample_report_text, height=140)
        report_title_input = st.text_input("Report Title / Reference:", value="Field Surveillance Intercept")

        col_nlp1, col_nlp2 = st.columns([1, 1])

        with col_nlp1:
            if st.button("🔍 Extract Entities via NLP", key="btn_run_nlp"):
                stats = entity_extractor.extract_summary_stats(input_text)
                st.session_state["last_nlp_stats"] = stats
                st.markdown(f"**Total Entities Identified:** `{stats['total_entities_found']}`")
                
                ents = stats["entities"]
                for ent_type, vals in ents.items():
                    if vals:
                        st.markdown(f"**{ent_type} ({len(vals)}):** " + " ".join([f"`{v}`" for v in vals]))

        with col_nlp2:
            st.markdown("##### Commit Extracted Entities into Database")
            if st.button("🚀 Commit Entities & Links to Knowledge Graph", key="btn_commit_nlp"):
                stats = entity_extractor.extract_summary_stats(input_text)
                commit_res = rel_extractor.commit_nlp_extraction_to_graph(
                    extracted=stats["entities"],
                    report_title=report_title_input,
                    graph_manager=graph_mgr
                )
                
                # Seal into Evidence Ledger
                block = ledger.add_evidence(
                    evidence_id=commit_res["report_id"],
                    filename=f"{report_title_input.replace(' ', '_')}.txt",
                    file_or_content=input_text,
                    metadata={"entity_count": stats["total_entities_found"]}
                )

                st.success(f"Entities committed into Database! Created {commit_res['nodes_created']} nodes and {commit_res['edges_created']} edges.")
                st.info(f"Evidence sealed in Block #{block.index} [SHA-256: `{block.evidence_hash[:16]}...`].")
                st.cache_resource.clear()


# =============================================================
# PAGE 3: INTERACTIVE NETWORK EXPLORER
# =============================================================
elif page == "🕸️ Interactive Network Explorer":
    st.markdown("""
    <div class="intel-header">
        <h1>🕸️ Interactive Network Graph Explorer</h1>
        <p>Explore multi-hop ego networks, filter relationships, zoom, pan, and inspect topological connections directly from the graph database.</p>
    </div>
    """, unsafe_allow_html=True)

    # Filter & Control Ribbon
    ctrl_col1, ctrl_col2, ctrl_col3, ctrl_col4 = st.columns(4)

    all_persons_list = sorted([str(data.get("name", nid)) for nid, data in graph_mgr.nx_graph.nodes(data=True) if data.get("label") == "Person"])
    with ctrl_col1:
        selected_center_person = st.selectbox("Focus Center Entity (Person):", ["-- Entire Subgraph Overview --"] + all_persons_list)

    with ctrl_col2:
        hop_radius = st.radio("Expansion Radius:", ["1-Hop Direct Neighbors", "2-Hop Neighborhood"], horizontal=True)

    with ctrl_col3:
        selected_entity_types = st.multiselect(
            "Filter Entity Types:",
            ["Person", "Phone", "Vehicle", "Location", "Organization", "Incident", "Report"],
            default=["Person", "Phone", "Vehicle", "Location", "Organization", "Incident"]
        )

    with ctrl_col4:
        enable_physics = st.checkbox("Enable Physics Simulation", value=True)

    # Subgraph Extraction from Database / Graph
    if selected_center_person != "-- Entire Subgraph Overview --":
        if "1-Hop" in hop_radius:
            sub_nodes, sub_edges = graph_mgr.get_1_hop_subgraph(selected_center_person)
        else:
            sub_nodes, sub_edges = graph_mgr.get_2_hop_subgraph(selected_center_person)
    else:
        sub_nodes = [dict(data, id=nid) for nid, data in list(graph_mgr.nx_graph.nodes(data=True))[:120]]
        sub_ids = {n["id"] for n in sub_nodes}
        sub_edges = [
            dict(edata, source=u, target=v, type=k)
            for u, v, k, edata in list(graph_mgr.nx_graph.edges(keys=True, data=True))
            if u in sub_ids and v in sub_ids
        ][:180]

    # Apply Entity Type Filters
    filtered_nodes = [n for n in sub_nodes if n.get("label") in selected_entity_types]
    filtered_node_ids = {n["id"] for n in filtered_nodes}
    filtered_edges = [e for e in sub_edges if e["source"] in filtered_node_ids and e["target"] in filtered_node_ids]

    st.markdown(f"**Rendering Subgraph:** `{len(filtered_nodes)} Nodes` | `{len(filtered_edges)} Relationships`")

    # Legend Display
    legend_cols = st.columns(max(1, len(selected_entity_types)))
    for i, l in enumerate(selected_entity_types):
        with legend_cols[i]:
            col_hex = NODE_COLORS.get(l, "#94a3b8")
            st.markdown(f"<span style='color:{col_hex}; font-weight:700;'>●</span> {l}", unsafe_allow_html=True)

    # Render PyVis Graph
    graph_html = generate_pyvis_html(filtered_nodes, filtered_edges, height="620px", physics=enable_physics)
    st.components.v1.html(graph_html, height=640)


# =============================================================
# PAGE 4: ENTITY SEARCH & DOSSIER PROFILE
# =============================================================
elif page == "🔍 Entity Search & Dossier":
    st.markdown("""
    <div class="intel-header">
        <h1>🔍 Entity Search & Subject Dossier</h1>
        <p>Database-backed query across persons, aliases, phone numbers, vehicle registrations, locations, and organizations.</p>
    </div>
    """, unsafe_allow_html=True)

    search_col1, search_col2 = st.columns([2.5, 1.0])
    with search_col1:
        search_query = st.text_input("Enter Search Term (Name, ID, Phone, Plate, Location):", value="Rahul")
    with search_col2:
        label_filter = st.selectbox("Entity Filter:", ["All", "Person", "Phone", "Vehicle", "Location", "Organization", "Incident"])

    search_results = graph_mgr.search_nodes(search_query, label_filter)
    st.markdown(f"Found **{len(search_results)}** matching intelligence entities in database.")

    if search_results:
        selected_node = search_results[0]
        if len(search_results) > 1:
            node_options = [f"{n.get('id')} — {n.get('name')} ({n.get('label')})" for n in search_results]
            picked = st.selectbox("Select Target Subject Entity:", node_options)
            picked_id = picked.split(" — ")[0]
            selected_node = next((n for n in search_results if n["id"] == picked_id), search_results[0])

        target_id = selected_node["id"]
        target_label = selected_node.get("label", "Entity")

        st.markdown("---")

        # Profile Dossier Card
        dossier_col1, dossier_col2 = st.columns([1.5, 1.0])

        with dossier_col1:
            st.markdown(f"""
            <div class="dossier-card">
                <div class="dossier-title">👤 DOSSIER: {selected_node.get('name', target_id).upper()}</div>
                <p><strong>Entity ID:</strong> <code>{target_id}</code> | <strong>Classification:</strong> {selected_node.get('label', 'Entity')}</p>
                <p><strong>Alias / Moniker:</strong> {selected_node.get('alias', 'None')}</p>
                <p><strong>Syndicate Affiliation:</strong> {selected_node.get('syndicate', 'Unaffiliated')}</p>
                <p><strong>Operational Role:</strong> {selected_node.get('role', 'Associate')}</p>
                <p><strong>Base City:</strong> {selected_node.get('city', 'Unknown')}</p>
            </div>
            """, unsafe_allow_html=True)

        with dossier_col2:
            if target_label == "Person" or target_id.startswith("P") or target_id.startswith("PER"):
                p_risk_row = all_risk_scores_df[all_risk_scores_df["person_id"] == target_id]
                if not p_risk_row.empty:
                    p_risk = p_risk_row.iloc[0]
                    st.markdown(f"""
                    <div class="dossier-card" style="border-left: 4px solid {'#f43f5e' if p_risk['risk_score']>=60 else '#10b981'};">
                        <div class="dossier-title">🎯 Risk Prioritization Score</div>
                        <h1 style="color:{'#f43f5e' if p_risk['risk_score']>=60 else '#10b981'}; margin:0;">{p_risk['risk_score']:.1f}/100</h1>
                        <span class="badge {p_risk['badge_class']}">{p_risk['risk_tier']} TIER</span>
                        <h4 style="margin-top:0.75rem; font-size:0.85rem; color:#94a3b8;">Score Factor Contributions:</h4>
                    """, unsafe_allow_html=True)
                    for exp in p_risk["explanations"]:
                        st.markdown(f"<small>• {exp}</small>", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)

        # 1-Hop Ego Network for the Selected Entity
        st.subheader("🔗 Direct 1-Hop Network Neighborhood")
        ego_nodes, ego_edges = graph_mgr.get_1_hop_subgraph(target_id)
        if ego_nodes:
            ego_html = generate_pyvis_html(ego_nodes, ego_edges, height="450px")
            st.components.v1.html(ego_html, height=460)

            # Tabular breakdown of connections
            st.markdown("##### Connected Entities Breakdown")
            c_p, c_ph, c_v, c_l, c_inc = st.tabs(["Associates", "Phones", "Vehicles", "Locations", "Incidents"])
            
            with c_p:
                assocs = [n for n in ego_nodes if n.get("label") == "Person" and n["id"] != target_id]
                if assocs:
                    st.dataframe(pd.DataFrame(assocs), use_container_width=True)
                else:
                    st.info("No direct associate persons linked.")
            with c_ph:
                phones = [n for n in ego_nodes if n.get("label") == "Phone"]
                if phones:
                    st.dataframe(pd.DataFrame(phones), use_container_width=True)
                else:
                    st.info("No phone devices linked.")
            with c_v:
                vehs = [n for n in ego_nodes if n.get("label") == "Vehicle"]
                if vehs:
                    st.dataframe(pd.DataFrame(vehs), use_container_width=True)
                else:
                    st.info("No vehicles linked.")
            with c_l:
                locs = [n for n in ego_nodes if n.get("label") == "Location"]
                if locs:
                    st.dataframe(pd.DataFrame(locs), use_container_width=True)
                else:
                    st.info("No locations recorded.")
            with c_inc:
                incs = [n for n in ego_nodes if n.get("label") == "Incident"]
                if incs:
                    st.dataframe(pd.DataFrame(incs), use_container_width=True)
                else:
                    st.info("No incidents linked.")


# =============================================================
# PAGE 5: NETWORK ANALYTICS
# =============================================================
elif page == "📈 Network Analytics":
    st.markdown("""
    <div class="intel-header">
        <h1>📈 Graph Network Analytics & Centrality Metrics</h1>
        <p>Algorithmic centrality calculation, community clustering, and bridge node identification computed dynamically from the active graph.</p>
    </div>
    """, unsafe_allow_html=True)

    tab_centrality, tab_community, tab_scatter = st.tabs(["🏆 Centrality Leaderboard", "🧩 Community Partitioning", "📊 Influence Scatter Map"])

    with tab_centrality:
        st.subheader("Key Centrality Ranking (Calculated Dynamically)")
        st.markdown("""
        - **Degree Centrality:** Measures direct connectivity and communication volume.
        - **Betweenness Centrality:** Identifies bridge brokers that connect separate clusters.
        - **PageRank:** Identifies structural importance and high-influence organizers.
        """)
        if not leaderboard_df.empty:
            st.dataframe(
                leaderboard_df,
                column_config={
                    "Rank": "Rank",
                    "name": "Person Name",
                    "alias": "Alias",
                    "syndicate": "Syndicate",
                    "raw_degree": "Degree",
                    "degree_centrality": "Deg Centrality",
                    "betweenness_centrality": "Betweenness",
                    "pagerank": "PageRank",
                    "community_id": "Community",
                    "is_bridge": "Is Bridge?"
                },
                hide_index=True,
                use_container_width=True
            )
        else:
            st.info("No entities available for centrality ranking.")

    with tab_community:
        st.subheader("Community & Cluster Distribution")
        comm_counts = {}
        for nid, c_id in communities.items():
            comm_counts[f"Cluster {c_id}"] = comm_counts.get(f"Cluster {c_id}", 0) + 1
        
        if comm_counts:
            st.bar_chart(comm_counts)
            st.markdown(f"**Total Distinct Sub-Communities Detected:** `{len(comm_counts)}`")
            st.markdown(f"**Identified Articulation / Bridge Nodes ({len(bridge_nodes)}):**")
            for b in bridge_nodes[:10]:
                b_node = graph_mgr.get_node(b) or {}
                st.markdown(f"- `{b}`: **{b_node.get('name', b)}** ({b_node.get('label', 'Entity')})")
        else:
            st.info("No communities detected.")

    with tab_scatter:
        st.subheader("Influence Mapping: Betweenness vs PageRank")
        if not leaderboard_df.empty:
            fig_scatter = plot_centrality_scatter(leaderboard_df)
            st.plotly_chart(fig_scatter, use_container_width=True)
        else:
            st.info("No data for scatter visualization.")


# =============================================================
# PAGE 6: SUSPICIOUS ACTIVITY & ML ANOMALIES
# =============================================================
elif page == "🚨 Suspicious Activity & ML":
    st.markdown("""
    <div class="intel-header">
        <h1>🚨 Suspicious Activity & Machine Learning Anomaly Engine</h1>
        <p>Isolation Forest multivariate anomaly detection combined with transparent rule-based forensic triggers.</p>
    </div>
    """, unsafe_allow_html=True)

    tab_rules, tab_ml_iso, tab_tx_anom = st.tabs(["⚠️ Rule-Based Alerts Table", "🌲 Isolation Forest ML Detection", "💸 Transaction Flow Anomalies"])

    with tab_rules:
        st.subheader("Active Forensic Rule Alerts")
        sev_filter = st.multiselect("Filter by Severity:", ["Critical", "High", "Medium", "Low"], default=["Critical", "High", "Medium"])
        filtered_alerts = [a for a in all_alerts if a.get("severity") in sev_filter]

        st.markdown(f"Showing **{len(filtered_alerts)}** active alerts matching criteria.")

        alert_df = pd.DataFrame(filtered_alerts)
        if not alert_df.empty:
            st.dataframe(
                alert_df[["alert_id", "rule_id", "rule_name", "entity_name", "severity", "reason", "timestamp"]],
                column_config={
                    "alert_id": "Alert ID",
                    "rule_id": "Rule ID",
                    "rule_name": "Rule Trigger",
                    "entity_name": "Entities Implicated",
                    "severity": "Severity",
                    "reason": "Forensic Reasoning",
                    "timestamp": "Timestamp"
                },
                hide_index=True,
                use_container_width=True
            )
        else:
            st.info("No active alerts matching filter.")

    with tab_ml_iso:
        st.subheader("Unsupervised Isolation Forest Outlier Scores")
        st.markdown("Features fitted: *Transaction volume, frequency, degree, betweenness, PageRank, shared device count, and incident involvement*.")
        
        if not scored_features.empty:
            st.dataframe(
                scored_features[["person_id", "name", "syndicate", "role", "anomaly_score_ml", "ml_status", "total_sent_amt", "total_recv_amt", "tx_count"]],
                column_config={
                    "anomaly_score_ml": st.column_config.ProgressColumn("ML Anomaly Score", min_value=0.0, max_value=1.0, format="%.3f"),
                    "ml_status": "Status",
                    "total_sent_amt": st.column_config.NumberColumn("Total Sent", format="%.0f"),
                    "total_recv_amt": st.column_config.NumberColumn("Total Recv", format="%.0f"),
                    "tx_count": "Transactions"
                },
                hide_index=True,
                use_container_width=True
            )

    with tab_tx_anom:
        st.subheader("Financial Transactions Anomaly Timeline")
        tx_anom_df = anom_engine.detect_transaction_anomalies(datasets.get("transactions", pd.DataFrame()))
        if not tx_anom_df.empty:
            fig_tx = plot_transaction_volume_timeline(tx_anom_df)
            st.plotly_chart(fig_tx, use_container_width=True)
        else:
            st.info("No transactions available for timeline analysis.")


# =============================================================
# PAGE 7: EVIDENCE INTEGRITY & BLOCKCHAIN LEDGER
# =============================================================
elif page == "⛓️ Evidence Integrity Ledger":
    st.markdown("""
    <div class="intel-header">
        <h1>⛓️ Cryptographic Evidence Integrity & Blockchain Ledger</h1>
        <p>Immutable append-only chained blocks with SHA-256 digests persisted on disk ensuring forensic evidence chain-of-custody.</p>
    </div>
    """, unsafe_allow_html=True)

    # Live Chain Verification Banner
    is_valid, verify_msg, audit_logs = ledger.verify_chain_integrity()
    if is_valid:
        st.markdown(f"""
        <div style="background:rgba(16, 185, 129, 0.15); border:1px solid #10b981; border-radius:8px; padding:1rem; margin-bottom:1.5rem;">
            <h3 style="color:#10b981; margin:0;">🔒 {verify_msg}</h3>
            <p style="color:#94a3b8; margin:0.2rem 0 0 0;">All {len(ledger.chain)} blocks in the persistent evidence chain are cryptographically valid and untampered.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="background:rgba(244, 63, 94, 0.15); border:1px solid #f43f5e; border-radius:8px; padding:1rem; margin-bottom:1.5rem;">
            <h3 style="color:#f43f5e; margin:0;">⚠️ {verify_msg}</h3>
            <p style="color:#ffffff; margin:0.2rem 0 0 0;">Potential evidence tampering detected in historical block sequence!</p>
        </div>
        """, unsafe_allow_html=True)

    tab_blocks, tab_upload_evidence, tab_verify_file, tab_tamper_demo = st.tabs(["📦 Block Explorer", "➕ Upload & Seal Evidence", "🔍 Verify File Hash", "🧪 Tamper Simulation Demo"])

    with tab_blocks:
        st.subheader(f"Immutable Block Sequence ({len(ledger.chain)} Blocks)")
        for b in ledger.chain:
            st.markdown(f"""
            <div class="block-card">
                <div style="display:flex; justify-content:space-between; margin-bottom:0.4rem;">
                    <strong>BLOCK #{b.index} [{b.evidence_id}]</strong>
                    <span style="color:#94a3b8;">{b.timestamp}</span>
                </div>
                <div><strong>File:</strong> {b.filename}</div>
                <div><strong>Evidence SHA-256:</strong> <span class="hash-text">{b.evidence_hash}</span></div>
                <div><strong>Previous Hash:</strong> <span style="color:#64748b; font-family:monospace;">{b.previous_hash}</span></div>
                <div><strong>Block Hash:</strong> <span class="hash-text">{b.block_hash}</span></div>
            </div>
            """, unsafe_allow_html=True)

    with tab_upload_evidence:
        st.subheader("Add and Seal New Evidence File")
        new_evid_file = st.file_uploader("Select Evidence Document to Seal into Ledger:", key="new_evid_uploader")
        evid_label = st.text_input("Evidence ID / Case Tag:", value=f"EVID-{datetime.now().strftime('%Y%m%d-%H%M%S')}")
        
        if new_evid_file is not None:
            if st.button("🔒 Compute SHA-256 & Seal Block to Disk", key="btn_seal_new_file"):
                content = new_evid_file.read()
                block = ledger.add_evidence(
                    evidence_id=evid_label,
                    filename=new_evid_file.name,
                    file_or_content=content,
                    metadata={"size_bytes": len(content)}
                )
                st.success(f"Evidence Sealed in Block #{block.index}!")
                st.markdown(f"**Evidence SHA-256:** `{block.evidence_hash}`")
                st.markdown(f"**Chained Block Hash:** `{block.block_hash}`")
                st.rerun()

    with tab_verify_file:
        st.subheader("Verify Integrity of an External Evidence File")
        verify_upload = st.file_uploader("Upload Evidence Document to Check Hash:", key="file_verify_uploader")
        if verify_upload is not None:
            content_bytes = verify_upload.read()
            computed_sha = ledger.calculate_sha256(content_bytes)
            st.markdown(f"**Computed SHA-256 Digest:** `{computed_sha}`")
            
            matched_block = next((b for b in ledger.chain if b.evidence_hash == computed_sha), None)
            if matched_block:
                st.success(f"MATCH FOUND! This file matches sealed Block #{matched_block.index} ({matched_block.evidence_id}). Status: 100% AUTHENTIC.")
            else:
                st.warning("No matching hash found in the active immutable ledger. Unregistered or altered document.")

    with tab_tamper_demo:
        st.subheader("🧪 Forensic Demonstration: Tamper Detection Simulation")
        st.markdown("Simulate a malicious database attack modifying the contents of a historical block:")
        
        target_block_idx = st.number_input("Select Block Index to Tamper with:", min_value=1, max_value=max(1, len(ledger.chain)-1), value=1)
        
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            if st.button("💥 Simulate Malicious Hash Tampering", key="btn_tamper"):
                ledger.simulate_tampering(target_block_idx, "ALTERED_FORGED_DATA")
                st.error(f"Injected fraudulent payload into Block #{target_block_idx}!")
                st.rerun()

        with col_t2:
            if st.button("🔄 Reset / Restore Clean Ledger", key="btn_reset_ledger"):
                ledger._create_genesis_block()
                ledger.save_to_disk()
                st.cache_resource.clear()
                st.rerun()


# =============================================================
# PAGE 8: INVESTIGATION DOSSIER EXPORT
# =============================================================
elif page == "📄 Investigation Dossier Export":
    st.markdown("""
    <div class="intel-header">
        <h1>📄 Investigation Dossier & Report Export</h1>
        <p>Generate formal, publication-ready forensic investigation reports in PDF and Markdown formats directly from database records.</p>
    </div>
    """, unsafe_allow_html=True)

    all_persons_df = datasets.get("persons", pd.DataFrame())
    if not all_persons_df.empty:
        person_options = [f"{row['person_id']} — {row['name']} ({row.get('alias', 'None')})" for _, row in all_persons_df.iterrows()]
        selected_target = st.selectbox("Select Investigation Subject Entity:", person_options, index=0)
        target_person_id = selected_target.split(" — ")[0]

        with st.spinner("Compiling full analytical case dossier from database..."):
            dossier_data = report_gen.generate_dossier_data(
                person_id=target_person_id,
                graph_manager=graph_mgr,
                risk_scoring_engine=risk_engine,
                network_analysis_engine=net_engine,
                anomaly_engine=anom_engine,
                rules_engine=rules_engine,
                evidence_ledger=ledger,
                datasets=datasets
            )

        st.markdown("---")

        col_rep_left, col_rep_right = st.columns([1.5, 1.0])

        with col_rep_left:
            st.markdown(f"### Case Summary: `{dossier_data['case_id']}`")
            st.markdown(f"**Subject:** **{dossier_data['name']}** (Alias: *{dossier_data['alias']}*)")
            st.markdown(f"**Risk Prioritization:** `{dossier_data['risk_score']:.1f}/100` ({dossier_data['risk_tier']})")
            st.markdown(f"**Syndicate:** {dossier_data['syndicate']} | **Role:** {dossier_data['role']}")
            st.markdown(f"**Evidence Chain Status:** `{dossier_data['evidence_status']}`")

            st.markdown("##### Forensic Factor Explanations:")
            for exp in dossier_data["risk_explanations"]:
                st.markdown(f"- `{exp}`")

        with col_rep_right:
            st.markdown("### 📥 Download Report")
            
            pdf_path = report_gen.generate_pdf_report(dossier_data)
            with open(pdf_path, "rb") as f:
                pdf_bytes = f.read()

            st.download_button(
                label="📕 Download Formal PDF Dossier",
                data=pdf_bytes,
                file_name=Path(pdf_path).name,
                mime="application/pdf"
            )

            md_text = report_gen.generate_markdown_report(dossier_data)
            st.download_button(
                label="📝 Download Markdown Report",
                data=md_text,
                file_name=f"Dossier_{target_person_id}.md",
                mime="text/markdown"
            )

        st.markdown("---")
        st.markdown("#### Live Dossier Preview (Markdown)")
        st.markdown(md_text)
    else:
        st.warning("No persons in database to generate dossier.")


# =============================================================
# PAGE 9: SYSTEM SETTINGS
# =============================================================
elif page == "⚙️ System Settings":
    st.markdown("""
    <div class="intel-header">
        <h1>⚙️ System Settings & Environment Configuration</h1>
        <p>Manage Neo4j graph database connectivity, test latency, and control persistent datasets.</p>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("Database & Backend Configuration")
    
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.text_input("Neo4j Bolt URI:", value=NEO4J_URI, disabled=True)
        st.text_input("Neo4j Username:", value=NEO4J_USERNAME, disabled=True)
        st.text_input("Neo4j Database:", value=NEO4J_DATABASE, disabled=True)

    with col_s2:
        st.markdown("##### Live Connection Status")
        st.markdown(f"**Active Mode:** `{graph_mgr.active_backend.upper()}`")
        
        if st.button("⚡ Test Neo4j Connection", key="btn_test_neo"):
            with st.spinner("Pinging Neo4j Bolt endpoint..."):
                conn_ok, latency, msg = graph_mgr.test_connection()
            if conn_ok:
                st.success(f"CONNECTED! Round-trip latency: **{latency} ms**.")
                st.info(msg)
            else:
                st.error(f"Connection Failed: {msg}")
                st.caption("Ensure Neo4j Desktop or Docker is running on bolt://localhost:7687")

    st.markdown("---")
    st.subheader("Dataset Lifecycle & Reset Controls")
    
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        st.markdown("##### Re-Seed Demo Dataset")
        st.markdown("Populates database with synthetic persons, phones, vehicles, transactions, and incidents.")
        if st.button("🔄 Load Demo Dataset", key="btn_reseed"):
            with st.spinner("Generating and seeding datasets..."):
                from data.generate_synthetic_data import generate_all_synthetic_data
                generate_all_synthetic_data()
                st.cache_resource.clear()
            st.success("Demo dataset seeded and committed! Reloading...")
            st.rerun()

    with col_c2:
        st.markdown("##### Clear Data Store")
        st.markdown("Safely wipes graph and datasets.")
        confirm_wipe = st.checkbox("I confirm I want to clear the graph data", key="chk_confirm_wipe")
        if st.button("🗑️ Clear Demo Data", disabled=not confirm_wipe, key="btn_clear_data"):
            graph_mgr.clear_graph()
            st.cache_resource.clear()
            st.warning("Graph data cleared from persistent store.")
            st.rerun()

    st.markdown("---")
    st.caption(f"Legal & Ethical Notice: {DISCLAIMER_TEXT}")
