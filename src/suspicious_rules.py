"""
Rule-Based Suspicion Engine
Evaluates explicit, transparent intelligence and cyber-crime rules.
Produces explainable alerts with Rule IDs, Severity, and forensic reasoning.
"""

import json
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any, Optional, Set

class SuspiciousRulesEngine:
    def __init__(self):
        self.rules_definitions = {
            "SR-01": {"name": "Shared Phone Terminal", "severity": "High", "desc": "Multiple individuals utilizing the same mobile/burner line."},
            "SR-02": {"name": "Shared Fleet Vehicle", "severity": "High", "desc": "Multiple individuals operating the same vehicle."},
            "SR-03": {"name": "Smurfing & Structuring", "severity": "Critical", "desc": "Repetitive transactions just below reporting regulatory thresholds."},
            "SR-04": {"name": "Cross-Syndicate Bridge Node", "severity": "Critical", "desc": "High-betweenness broker acting as sole connector across clusters."},
            "SR-05": {"name": "High-Velocity Multi-City Sighting", "severity": "Medium", "desc": "Presence in multiple distant operational locations."},
            "SR-06": {"name": "Offshore / Hawala Capital Spike", "severity": "Critical", "desc": "Anomalous high-value transfer (> ₹ 1,000,000 INR)."},
            "SR-07": {"name": "Dense Crime Ring Clique", "severity": "Medium", "desc": "High interconnectedness within closed criminal cell."},
            "SR-08": {"name": "Chronic Incident Involvements", "severity": "High", "desc": "Individual linked to multiple active crime incidents."}
        }

    def evaluate_all_rules(
        self,
        persons_df: pd.DataFrame,
        transactions_df: pd.DataFrame,
        incidents_df: pd.DataFrame,
        centralities: Dict[str, Dict[str, float]],
        communities: Dict[str, int],
        graph_manager: Any
    ) -> List[Dict[str, Any]]:
        """
        Executes all suspicious rule evaluations across the entire intelligence graph.
        Returns a list of structured alert objects.
        """
        alerts: List[Dict[str, Any]] = []
        alert_counter = 1

        # -------------------------------------------------------------
        # Rule SR-01: Shared Phone Terminal
        # -------------------------------------------------------------
        flagged_phones = set()
        if not persons_df.empty and "primary_phone" in persons_df.columns:
            phone_groups = persons_df.groupby("primary_phone")
            for phone, grp in phone_groups:
                if phone and phone != "UNAVAILABLE" and len(grp) > 1:
                    p_names = grp["name"].tolist()
                    p_ids = grp["person_id"].tolist()
                    flagged_phones.add(phone)
                    alerts.append({
                        "alert_id": f"ALT-{alert_counter:04d}",
                        "rule_id": "SR-01",
                        "rule_name": self.rules_definitions["SR-01"]["name"],
                        "entity_id": p_ids[0],
                        "entity_name": ", ".join(p_names),
                        "entity_type": "Phone",
                        "severity": "High",
                        "reason": f"Phone number {phone} is shared across {len(grp)} distinct persons: {', '.join(p_names)}.",
                        "entities_involved": p_names + [phone],
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
                    alert_counter += 1

        # Also inspect graph for shared phone incoming links
        for nid, data in graph_manager.nx_graph.nodes(data=True):
            if data.get("label") == "Phone":
                p_num = data.get("name", nid)
                if p_num not in flagged_phones:
                    users = [u for u, _ in graph_manager.nx_graph.in_edges(nid) if str(u).startswith("P") or str(u).startswith("PER")]
                    if len(users) > 1:
                        flagged_phones.add(p_num)
                        u_names = [graph_manager.get_node(u).get("name", u) for u in users]
                        alerts.append({
                            "alert_id": f"ALT-{alert_counter:04d}",
                            "rule_id": "SR-01",
                            "rule_name": self.rules_definitions["SR-01"]["name"],
                            "entity_id": users[0],
                            "entity_name": ", ".join(u_names),
                            "entity_type": "Phone",
                            "severity": "High",
                            "reason": f"Phone number {p_num} is linked to {len(users)} distinct individuals: {', '.join(u_names)}.",
                            "entities_involved": u_names + [p_num],
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        })
                        alert_counter += 1

        # -------------------------------------------------------------
        # Rule SR-02: Shared Fleet Vehicle
        # -------------------------------------------------------------
        flagged_vehs = set()
        if not persons_df.empty and "primary_vehicle" in persons_df.columns:
            veh_groups = persons_df.groupby("primary_vehicle")
            for veh, grp in veh_groups:
                if veh and veh != "UNKNOWN_PLATE" and len(grp) > 1:
                    p_names = grp["name"].tolist()
                    p_ids = grp["person_id"].tolist()
                    flagged_vehs.add(veh)
                    alerts.append({
                        "alert_id": f"ALT-{alert_counter:04d}",
                        "rule_id": "SR-02",
                        "rule_name": self.rules_definitions["SR-02"]["name"],
                        "entity_id": p_ids[0],
                        "entity_name": ", ".join(p_names),
                        "entity_type": "Vehicle",
                        "severity": "High",
                        "reason": f"Vehicle plate {veh} is registered/operated by {len(grp)} distinct persons: {', '.join(p_names)}.",
                        "entities_involved": p_names + [veh],
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
                    alert_counter += 1

        # Also inspect graph for shared vehicle incoming links
        for nid, data in graph_manager.nx_graph.nodes(data=True):
            if data.get("label") == "Vehicle":
                plate = data.get("name", nid)
                if plate not in flagged_vehs:
                    users = [u for u, _ in graph_manager.nx_graph.in_edges(nid) if str(u).startswith("P") or str(u).startswith("PER")]
                    if len(users) > 1:
                        flagged_vehs.add(plate)
                        u_names = [graph_manager.get_node(u).get("name", u) for u in users]
                        alerts.append({
                            "alert_id": f"ALT-{alert_counter:04d}",
                            "rule_id": "SR-02",
                            "rule_name": self.rules_definitions["SR-02"]["name"],
                            "entity_id": users[0],
                            "entity_name": ", ".join(u_names),
                            "entity_type": "Vehicle",
                            "severity": "High",
                            "reason": f"Vehicle plate {plate} is operated by {len(users)} distinct individuals: {', '.join(u_names)}.",
                            "entities_involved": u_names + [plate],
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        })
                        alert_counter += 1

        # -------------------------------------------------------------
        # Rule SR-03: Smurfing & Layering Financial Transactions
        # -------------------------------------------------------------
        if not transactions_df.empty:
            # Group by sender-receiver pair and check for multiple transfers in 45k-50k
            smurf_tx = transactions_df[transactions_df["amount"].between(45000, 49999)]
            pair_groups = smurf_tx.groupby(["sender_id", "receiver_id"])
            for (s_id, r_id), grp in pair_groups:
                if len(grp) >= 2:
                    s_name = grp.iloc[0].get("sender_name", s_id)
                    r_name = grp.iloc[0].get("receiver_name", r_id)
                    total_amt = grp["amount"].sum()
                    alerts.append({
                        "alert_id": f"ALT-{alert_counter:04d}",
                        "rule_id": "SR-03",
                        "rule_name": self.rules_definitions["SR-03"]["name"],
                        "entity_id": s_id,
                        "entity_name": f"{s_name} -> {r_name}",
                        "entity_type": "Transaction Ring",
                        "severity": "Critical",
                        "reason": f"Detected {len(grp)} structured micro-transfers (Total: ₹{total_amt:,.2f}) just below threshold between {s_name} and {r_name}.",
                        "entities_involved": [s_name, r_name],
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
                    alert_counter += 1

        # -------------------------------------------------------------
        # Rule SR-04: Cross-Syndicate Bridge Node (High Betweenness)
        # -------------------------------------------------------------
        bridge_nodes = set(graph_manager.nx_graph.nodes())
        for pid, c_dict in centralities.items():
            if str(pid).startswith("PER"):
                bet = c_dict.get("betweenness", 0.0)
                if bet > 0.08: # Top broker threshold
                    p_node = graph_manager.get_node(pid) or {}
                    p_name = p_node.get("name", pid)
                    alerts.append({
                        "alert_id": f"ALT-{alert_counter:04d}",
                        "rule_id": "SR-04",
                        "rule_name": self.rules_definitions["SR-04"]["name"],
                        "entity_id": pid,
                        "entity_name": p_name,
                        "entity_type": "Person",
                        "severity": "Critical",
                        "reason": f"High Betweenness Centrality ({bet:.4f}). {p_name} acts as a pivotal communication and financial bridge across syndicates.",
                        "entities_involved": [p_name],
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
                    alert_counter += 1

        # -------------------------------------------------------------
        # Rule SR-06: Offshore / Hawala Single-Transaction Spike
        # -------------------------------------------------------------
        if not transactions_df.empty:
            huge_tx = transactions_df[transactions_df["amount"] >= 1000000.0]
            for _, tx in huge_tx.iterrows():
                s_name = str(tx.get("sender_name", tx["sender_id"]))
                r_name = str(tx.get("receiver_name", tx["receiver_id"]))
                amt = float(tx["amount"])
                alerts.append({
                    "alert_id": f"ALT-{alert_counter:04d}",
                    "rule_id": "SR-06",
                    "rule_name": self.rules_definitions["SR-06"]["name"],
                    "entity_id": str(tx["sender_id"]),
                    "entity_name": f"{s_name} -> {r_name}",
                    "entity_type": "Transaction",
                    "severity": "Critical",
                    "reason": f"High-Value Outlier: ₹ {amt:,.2f} transfer via {tx.get('channel', 'Wire')} flagged for hawala investigation.",
                    "entities_involved": [s_name, r_name],
                    "timestamp": str(tx.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                })
                alert_counter += 1

        # -------------------------------------------------------------
        # Rule SR-08: Chronic Incident Involvements (3+ Incidents)
        # -------------------------------------------------------------
        if not incidents_df.empty:
            inc_person_counts = {}
            for _, inc in incidents_df.iterrows():
                raw_inv = inc.get("involved_person_ids", "[]")
                inv_list = []
                if isinstance(raw_inv, str):
                    try:
                        inv_list = json.loads(raw_inv)
                    except Exception:
                        inv_list = [p.strip() for p in raw_inv.split(",") if p.strip()]
                elif isinstance(raw_inv, list):
                    inv_list = raw_inv

                for pid in inv_list:
                    inc_person_counts[pid] = inc_person_counts.get(pid, 0) + 1

            for pid, count in inc_person_counts.items():
                if count >= 3:
                    p_node = graph_manager.get_node(pid) or {}
                    p_name = p_node.get("name", pid)
                    alerts.append({
                        "alert_id": f"ALT-{alert_counter:04d}",
                        "rule_id": "SR-08",
                        "rule_name": self.rules_definitions["SR-08"]["name"],
                        "entity_id": pid,
                        "entity_name": p_name,
                        "entity_type": "Person",
                        "severity": "High",
                        "reason": f"Recurring Incident Association: {p_name} is directly implicated in {count} active criminal case files.",
                        "entities_involved": [p_name],
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
                    alert_counter += 1

        return alerts

