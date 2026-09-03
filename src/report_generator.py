"""
Investigation Dossier & Report Generator
Generates comprehensive forensic investigation reports in PDF and Markdown formats
with analytical risk breakdowns, network metrics, alert history, and evidence hash verification.
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from fpdf import FPDF
from src.config import EXPORT_REPORTS_DIR, DISCLAIMER_TEXT

class InvestigationPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 5, "CONFIDENTIAL // LAW ENFORCEMENT ANALYTICAL DOSSIER", ln=True, align="R")
        self.ln(2)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}} | Case Investigation Support System", align="C")


class ReportGenerator:
    def __init__(self, output_dir: Path = EXPORT_REPORTS_DIR):
        self.output_dir = output_dir
        self.output_dir.mkdir(exist_ok=True, parents=True)

    def generate_dossier_data(
        self,
        person_id: str,
        graph_manager: Any,
        risk_scoring_engine: Any,
        network_analysis_engine: Any,
        anomaly_engine: Any,
        rules_engine: Any,
        evidence_ledger: Any,
        datasets: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Gathers all analytical data for a specific subject entity."""
        node = graph_manager.get_node(person_id) or {}
        name = node.get("name", person_id)

        # 1. Network Centralities
        centralities = network_analysis_engine.calculate_centralities()
        communities = network_analysis_engine.detect_communities()
        bridge_nodes = set(network_analysis_engine.find_bridge_nodes())

        p_cent = centralities.get(person_id, {})
        comm_id = communities.get(person_id, 1)

        # 2. Ego Subgraph
        nodes_1hop, edges_1hop = graph_manager.get_1_hop_subgraph(person_id)

        # 3. Alerts
        all_alerts = rules_engine.evaluate_all_rules(
            persons_df=datasets.get("persons"),
            transactions_df=datasets.get("transactions"),
            incidents_df=datasets.get("incidents"),
            centralities=centralities,
            communities=communities,
            graph_manager=graph_manager
        )
        p_alerts = [a for a in all_alerts if person_id in str(a.get("entity_id", "")) or name in a.get("entities_involved", [])]

        # 4. Feature and Risk Score
        feat_df = anomaly_engine.build_entity_feature_matrix(
            persons_df=datasets.get("persons"),
            transactions_df=datasets.get("transactions"),
            incidents_df=datasets.get("incidents"),
            centrality_map=centralities,
            graph_manager=graph_manager
        )
        scored_feats = anomaly_engine.detect_anomalous_entities(feat_df)
        feat_row = None
        if not scored_feats.empty:
            m = scored_feats[scored_feats["person_id"] == person_id]
            if not m.empty:
                feat_row = m.iloc[0]

        shared_cnt = sum(1 for n in nodes_1hop if n.get("label") in ["Phone", "Vehicle"])
        risk_info = risk_scoring_engine.calculate_person_risk_score(
            person_id=person_id,
            centrality_data=p_cent,
            feature_row=feat_row,
            alerts_for_person=p_alerts,
            shared_device_count=shared_cnt,
            is_bridge=(person_id in bridge_nodes)
        )

        # 5. Connected Devices and Associates
        phones = [n.get("name") for n in nodes_1hop if n.get("label") == "Phone"]
        vehicles = [n.get("name") for n in nodes_1hop if n.get("label") == "Vehicle"]
        associates = [n.get("name") for n in nodes_1hop if n.get("label") == "Person" and n.get("id") != person_id]
        orgs = [n.get("name") for n in nodes_1hop if n.get("label") == "Organization"]
        incidents = [n.get("name") for n in nodes_1hop if n.get("label") == "Incident"]

        # 6. Ledger Verification
        is_chain_valid, chain_msg, _ = evidence_ledger.verify_chain_integrity()

        case_id = f"CASE-INTEL-{datetime.now().strftime('%Y%m%d')}-{person_id.replace('PER-', '')}"

        return {
            "case_id": case_id,
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "person_id": person_id,
            "name": name,
            "alias": node.get("alias", "None"),
            "syndicate": node.get("syndicate", "Unaffiliated"),
            "role": node.get("role", "Associate"),
            "city": node.get("city", "Unknown"),
            "status": node.get("status", "Under Investigation"),
            "risk_score": risk_info["total_score"],
            "risk_tier": risk_info["tier"],
            "factor_breakdown": risk_info["factor_breakdown"],
            "risk_explanations": risk_info["explanations"],
            "network_metrics": {
                "raw_degree": p_cent.get("raw_degree", 0),
                "degree_centrality": round(p_cent.get("degree", 0.0), 4),
                "betweenness_centrality": round(p_cent.get("betweenness", 0.0), 4),
                "pagerank": round(p_cent.get("pagerank", 0.0), 4),
                "community": f"Cluster {comm_id}",
                "is_bridge": (person_id in bridge_nodes)
            },
            "connections": {
                "phones": phones,
                "vehicles": vehicles,
                "associates": associates,
                "organizations": orgs,
                "incidents": incidents
            },
            "alerts": p_alerts,
            "evidence_status": "VERIFIED" if is_chain_valid else "TAMPERED / MODIFIED",
            "chain_message": chain_msg
        }

    @staticmethod
    def _clean_pdf_text(text: Any) -> str:
        """Sanitizes unicode characters (like ₹ and em-dash) for standard Latin-1 PDF rendering."""
        if text is None:
            return ""
        s = str(text)
        s = s.replace("₹", "INR ").replace("Rs.", "INR ").replace("—", "-").replace("–", "-")
        s = s.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'")
        # Ensure only latin-1 compatible chars
        return s.encode("latin-1", "replace").decode("latin-1")

    def generate_pdf_report(self, dossier: Dict[str, Any]) -> str:
        """Generates a professional multi-page PDF investigation report."""
        filename = f"Investigation_Report_{dossier['person_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        output_path = self.output_dir / filename

        pdf = InvestigationPDF()
        pdf.alias_nb_pages()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)

        # Title Block
        pdf.set_font("Helvetica", "B", 18)
        pdf.set_text_color(20, 30, 50)
        pdf.cell(0, 10, self._clean_pdf_text("CRIMINAL NETWORK INTELLIGENCE DOSSIER"), ln=True, align="L")

        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 6, self._clean_pdf_text(f"Case Identifier: {dossier['case_id']} | Date: {dossier['generated_at']}"), ln=True)
        pdf.line(10, pdf.get_y() + 2, 200, pdf.get_y() + 2)
        pdf.ln(5)

        # Subject Profile Box
        pdf.set_fill_color(240, 244, 248)
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_text_color(15, 23, 42)
        pdf.cell(0, 8, self._clean_pdf_text(f"1. SUBJECT PROFILE: {dossier['name'].upper()} (Alias: '{dossier['alias']}')"), ln=True, fill=True)
        pdf.ln(2)

        pdf.set_font("Helvetica", "", 10)
        col_w = 95
        pdf.cell(col_w, 6, self._clean_pdf_text(f"Person ID: {dossier['person_id']}"), ln=False)
        pdf.cell(col_w, 6, self._clean_pdf_text(f"Operational Base: {dossier['city']}"), ln=True)
        pdf.cell(col_w, 6, self._clean_pdf_text(f"Syndicate: {dossier['syndicate']}"), ln=False)
        pdf.cell(col_w, 6, self._clean_pdf_text(f"Network Role: {dossier['role']}"), ln=True)
        pdf.cell(col_w, 6, self._clean_pdf_text(f"Status: {dossier['status']}"), ln=False)
        pdf.cell(col_w, 6, self._clean_pdf_text(f"Evidence Ledger: {dossier['evidence_status']}"), ln=True)
        pdf.ln(4)

        # Risk Score Assessment Box
        if dossier['risk_tier'] in ['HIGH', 'CRITICAL']:
            pdf.set_fill_color(254, 242, 242)
            pdf.set_text_color(185, 28, 28)
        else:
            pdf.set_fill_color(240, 253, 244)
            pdf.set_text_color(21, 128, 61)
        pdf.cell(0, 8, self._clean_pdf_text(f"2. ANALYTICAL PRIORITIZATION SCORE: {dossier['risk_score']}/100 [{dossier['risk_tier']} TIER]"), ln=True, fill=True)
        pdf.ln(2)

        pdf.set_font("Helvetica", "B", 9)
        pdf.set_text_color(50, 50, 50)
        pdf.cell(0, 6, self._clean_pdf_text("Contributing Factor Breakdown:"), ln=True)
        pdf.set_font("Helvetica", "", 9)
        for exp in dossier["risk_explanations"]:
            pdf.cell(5)
            pdf.cell(0, 5, self._clean_pdf_text(f"- {exp}"), ln=True)
        pdf.ln(4)

        # Network Graph Metrics
        pdf.set_fill_color(240, 244, 248)
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_text_color(15, 23, 42)
        pdf.cell(0, 8, self._clean_pdf_text("3. NETWORK TOPOLOGY & CENTRALITY METRICS"), ln=True, fill=True)
        pdf.ln(2)

        pdf.set_font("Helvetica", "", 10)
        nm = dossier["network_metrics"]
        pdf.cell(col_w, 6, self._clean_pdf_text(f"Direct Degree Connections: {nm['raw_degree']}"), ln=False)
        pdf.cell(col_w, 6, self._clean_pdf_text(f"Degree Centrality: {nm['degree_centrality']}"), ln=True)
        pdf.cell(col_w, 6, self._clean_pdf_text(f"Betweenness Centrality: {nm['betweenness_centrality']}"), ln=False)
        pdf.cell(col_w, 6, self._clean_pdf_text(f"PageRank Influence: {nm['pagerank']}"), ln=True)
        pdf.cell(col_w, 6, self._clean_pdf_text(f"Community Partition: {nm['community']}"), ln=False)
        pdf.cell(col_w, 6, self._clean_pdf_text(f"Articulation Bridge Node: {'YES (Key Broker)' if nm['is_bridge'] else 'NO'}"), ln=True)
        pdf.ln(4)

        # Direct & Second-Degree Associations
        pdf.set_fill_color(240, 244, 248)
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, self._clean_pdf_text("4. LINKED IDENTIFIERS & ASSOCIATES"), ln=True, fill=True)
        pdf.ln(2)

        conn = dossier["connections"]
        pdf.set_font("Helvetica", "", 9)
        pdf.cell(0, 5, self._clean_pdf_text(f"Associated Phone Terminals: {', '.join(conn['phones']) if conn['phones'] else 'None Logged'}"), ln=True)
        pdf.cell(0, 5, self._clean_pdf_text(f"Associated Fleet Vehicles: {', '.join(conn['vehicles']) if conn['vehicles'] else 'None Logged'}"), ln=True)
        pdf.cell(0, 5, self._clean_pdf_text(f"Direct Person Associates: {', '.join(conn['associates'][:8]) if conn['associates'] else 'None Logged'}"), ln=True)
        pdf.cell(0, 5, self._clean_pdf_text(f"Front Organizations: {', '.join(conn['organizations']) if conn['organizations'] else 'None Logged'}"), ln=True)
        pdf.cell(0, 5, self._clean_pdf_text(f"Linked Crime Incidents: {', '.join(conn['incidents'][:5]) if conn['incidents'] else 'None Logged'}"), ln=True)
        pdf.ln(4)

        # Suspicious Activity Alerts
        pdf.set_fill_color(240, 244, 248)
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, self._clean_pdf_text(f"5. FORENSIC SUSPICION ALERTS ({len(dossier['alerts'])} Active Flags)"), ln=True, fill=True)
        pdf.ln(2)

        if dossier["alerts"]:
            for alt in dossier["alerts"][:6]:
                pdf.set_font("Helvetica", "B", 9)
                if alt.get("severity") in ["Critical", "High"]:
                    pdf.set_text_color(185, 28, 28)
                else:
                    pdf.set_text_color(50, 50, 50)
                pdf.cell(0, 5, self._clean_pdf_text(f"[{alt.get('rule_id')}] {alt.get('rule_name')} - Severity: {alt.get('severity')}"), ln=True)
                pdf.set_font("Helvetica", "", 8)
                pdf.set_text_color(70, 70, 70)
                pdf.multi_cell(0, 4, self._clean_pdf_text(f"Reason: {alt.get('reason')}"))
                pdf.ln(1)
        else:
            pdf.set_font("Helvetica", "I", 9)
            pdf.set_text_color(100, 100, 100)
            pdf.cell(0, 5, self._clean_pdf_text("No active automated rule violations flagged for this subject."), ln=True)
        pdf.ln(4)

        # Legal Disclaimer
        pdf.set_font("Helvetica", "I", 8)
        pdf.set_text_color(120, 120, 120)
        pdf.multi_cell(0, 4, self._clean_pdf_text(DISCLAIMER_TEXT))

        pdf.output(str(output_path))
        return str(output_path)

    def generate_markdown_report(self, dossier: Dict[str, Any]) -> str:
        """Generates markdown text representation of the investigation report."""
        md = f"""# CRIMINAL NETWORK INTELLIGENCE DOSSIER
**Case ID:** `{dossier['case_id']}`  
**Generated At:** `{dossier['generated_at']}`  
**Classification:** `CONFIDENTIAL // LAW ENFORCEMENT DEMO ONLY`

---

## 1. Subject Profile
- **Name:** **{dossier['name']}**
- **Alias:** *{dossier['alias']}*
- **Person ID:** `{dossier['person_id']}`
- **Syndicate:** {dossier['syndicate']}
- **Role:** {dossier['role']}
- **Operational City:** {dossier['city']}
- **Status:** {dossier['status']}

---

## 2. Risk & Intelligence Score
**Prioritization Score:** **{dossier['risk_score']} / 100** ({dossier['risk_tier']} Risk)

### Contributing Factor Breakdown:
"""
        for exp in dossier["risk_explanations"]:
            md += f"- `{exp}`\n"

        md += f"""
---

## 3. Network Metrics & Topology
- **Direct Degree:** {dossier['network_metrics']['raw_degree']}
- **Degree Centrality:** {dossier['network_metrics']['degree_centrality']}
- **Betweenness Centrality:** {dossier['network_metrics']['betweenness_centrality']}
- **PageRank Influence:** {dossier['network_metrics']['pagerank']}
- **Community Partition:** {dossier['network_metrics']['community']}
- **Key Bridge Node:** {'YES' if dossier['network_metrics']['is_bridge'] else 'NO'}

---

## 4. Connected Identifiers & Associates
- **Phones:** {', '.join(dossier['connections']['phones']) or 'None'}
- **Vehicles:** {', '.join(dossier['connections']['vehicles']) or 'None'}
- **Associates:** {', '.join(dossier['connections']['associates']) or 'None'}
- **Organizations:** {', '.join(dossier['connections']['organizations']) or 'None'}
- **Incidents:** {', '.join(dossier['connections']['incidents']) or 'None'}

---

## 5. Active Suspicious Alerts ({len(dossier['alerts'])})
"""
        for a in dossier["alerts"]:
            md += f"- **[{a.get('rule_id')}] {a.get('rule_name')}** ({a.get('severity')}): {a.get('reason')}\n"

        md += f"""
---
*DISCLAIMER: {DISCLAIMER_TEXT}*
"""
        return md
