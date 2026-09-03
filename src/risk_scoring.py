"""
Explainable Risk / Intelligence Scoring Engine
Calculates a transparent, weighted 0–100 analytical prioritization score
with a complete mathematical breakdown of contributing factors.
"""

import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from src.config import RISK_WEIGHTS, RISK_LEVELS

class RiskScoringEngine:
    def __init__(self, weights: Optional[Dict[str, float]] = None):
        self.weights = weights or RISK_WEIGHTS

    def get_risk_tier(self, score: float) -> Tuple[str, str]:
        """Returns (Tier Name, CSS Badge Class) based on 0-100 score."""
        if score >= 80:
            return "CRITICAL", "badge-critical"
        elif score >= 60:
            return "HIGH", "badge-high"
        elif score >= 30:
            return "MODERATE", "badge-moderate"
        else:
            return "LOW", "badge-low"

    def calculate_person_risk_score(
        self,
        person_id: str,
        centrality_data: Dict[str, float],
        feature_row: Optional[pd.Series],
        alerts_for_person: List[Dict[str, Any]],
        shared_device_count: int,
        is_bridge: bool
    ) -> Dict[str, Any]:
        """
        Calculates explainable risk score (0–100) for an individual.
        Returns:
            - total_score (0-100 float)
            - tier (LOW, MODERATE, HIGH, CRITICAL)
            - badge_class
            - factor_contributions (Dict of float values)
            - explanation_lines (List of formatted strings with '+X Reason')
        """
        factors = {
            "centrality": 0.0,
            "anomaly": 0.0,
            "rules": 0.0,
            "shared_id": 0.0,
            "community": 0.0,
            "incidents": 0.0
        }
        explanations = []

        # 1. Centrality Contribution (Weight: 25%)
        # Composite of Betweenness (scaled), PageRank, and Degree
        bet = centrality_data.get("betweenness", 0.0)
        pr = centrality_data.get("pagerank", 0.0)
        deg = centrality_data.get("degree", 0.0)
        raw_deg = centrality_data.get("raw_degree", 0)

        # Scale centrality component to 0-100
        centrality_raw = min(100.0, (bet * 400.0) + (pr * 800.0) + (deg * 150.0))
        centrality_score = centrality_raw * self.weights["centrality"]
        factors["centrality"] = round(centrality_score, 1)
        if factors["centrality"] >= 8.0:
            explanations.append(f"+{factors['centrality']:.1f} High network centrality (Degree: {raw_deg}, Betweenness: {bet:.3f})")

        # 2. Transaction Anomaly Contribution (Weight: 20%)
        if feature_row is not None:
            ml_anom_score = float(feature_row.get("anomaly_score_ml", 0.0))
            is_ml_anom = bool(feature_row.get("is_anomaly_ml", False))
            tx_count = int(feature_row.get("tx_count", 0))
            total_vol = float(feature_row.get("total_sent_amt", 0.0)) + float(feature_row.get("total_recv_amt", 0.0))

            anom_raw = (ml_anom_score * 70.0) + (30.0 if is_ml_anom else 0.0)
            if total_vol > 1000000.0:
                anom_raw = min(100.0, anom_raw + 20.0)

            anom_score = min(100.0, anom_raw) * self.weights["anomaly"]
            factors["anomaly"] = round(anom_score, 1)
            if factors["anomaly"] >= 6.0:
                explanations.append(f"+{factors['anomaly']:.1f} Transaction anomaly & high volume (₹{total_vol:,.0f} across {tx_count} transfers)")

        # 3. Suspicious Rules Contribution (Weight: 20%)
        rule_score_accum = 0.0
        for alt in alerts_for_person:
            sev = alt.get("severity", "Medium")
            if sev == "Critical":
                rule_score_accum += 40.0
            elif sev == "High":
                rule_score_accum += 25.0
            else:
                rule_score_accum += 15.0

        rule_score = min(100.0, rule_score_accum) * self.weights["rules"]
        factors["rules"] = round(rule_score, 1)
        if factors["rules"] >= 6.0:
            explanations.append(f"+{factors['rules']:.1f} Triggered {len(alerts_for_person)} suspicion rule alert(s)")

        # 4. Shared Identifiers Contribution (Weight: 15%)
        # Phones / Vehicles shared
        shared_raw = min(100.0, shared_device_count * 35.0)
        shared_score = shared_raw * self.weights["shared_id"]
        factors["shared_id"] = round(shared_score, 1)
        if factors["shared_id"] >= 5.0:
            explanations.append(f"+{factors['shared_id']:.1f} Shared communication/transport identifiers ({shared_device_count} links)")

        # 5. Community / Bridge Position (Weight: 10%)
        comm_raw = 100.0 if is_bridge else (50.0 if bet > 0.05 else 10.0)
        comm_score = comm_raw * self.weights["community"]
        factors["community"] = round(comm_score, 1)
        if is_bridge:
            explanations.append(f"+{factors['community']:.1f} Cross-syndicate articulation bridge node")

        # 6. Incident Involvement Contribution (Weight: 10%)
        inc_count = int(feature_row.get("incident_count", 0)) if feature_row is not None else 0
        inc_raw = min(100.0, inc_count * 30.0)
        inc_score = inc_raw * self.weights["incidents"]
        factors["incidents"] = round(inc_score, 1)
        if factors["incidents"] >= 3.0:
            explanations.append(f"+{factors['incidents']:.1f} Directly linked to {inc_count} criminal incidents")

        # Calculate Total Score (0 - 100 clamped)
        total_score = min(100.0, max(5.0, sum(factors.values())))
        tier, badge_class = self.get_risk_tier(total_score)

        if not explanations:
            explanations.append("+5.0 Baseline normal civilian background activity")

        return {
            "person_id": person_id,
            "total_score": round(total_score, 1),
            "tier": tier,
            "badge_class": badge_class,
            "factor_breakdown": factors,
            "explanations": explanations
        }

    def compute_all_risk_scores(
        self,
        persons_df: pd.DataFrame,
        feature_df: pd.DataFrame,
        centrality_map: Dict[str, Dict[str, float]],
        all_alerts: List[Dict[str, Any]],
        bridge_nodes: List[str],
        graph_manager: Any
    ) -> pd.DataFrame:
        """Computes comprehensive risk dossier for every person."""
        bridge_set = set(bridge_nodes)
        records = []

        # Index alerts by person
        alerts_by_person: Dict[str, List[Dict[str, Any]]] = {}
        for alt in all_alerts:
            pid = alt.get("entity_id", "")
            if pid not in alerts_by_person:
                alerts_by_person[pid] = []
            alerts_by_person[pid].append(alt)

        # Index feature df
        feature_map = {}
        if not feature_df.empty:
            for _, row in feature_df.iterrows():
                feature_map[str(row["person_id"])] = row

        for _, p in persons_df.iterrows():
            pid = str(p["person_id"])
            c_data = centrality_map.get(pid, {})
            feat_row = feature_map.get(pid)
            p_alerts = alerts_by_person.get(pid, [])

            # Check shared devices
            nodes_1hop, _ = graph_manager.get_1_hop_subgraph(pid)
            shared_cnt = sum(1 for n in nodes_1hop if n.get("label") in ["Phone", "Vehicle"])

            score_res = self.calculate_person_risk_score(
                person_id=pid,
                centrality_data=c_data,
                feature_row=feat_row,
                alerts_for_person=p_alerts,
                shared_device_count=shared_cnt,
                is_bridge=(pid in bridge_set)
            )

            records.append({
                "person_id": pid,
                "name": p.get("name", pid),
                "alias": p.get("alias", "None"),
                "syndicate": p.get("syndicate", "Unaffiliated"),
                "role": p.get("role", "Associate"),
                "city": p.get("city", "Unknown"),
                "risk_score": score_res["total_score"],
                "risk_tier": score_res["tier"],
                "badge_class": score_res["badge_class"],
                "factor_breakdown": score_res["factor_breakdown"],
                "explanations": score_res["explanations"],
                "alert_count": len(p_alerts)
            })

        df = pd.DataFrame(records)
        if df.empty or "risk_score" not in df.columns:
            return pd.DataFrame(columns=[
                "person_id", "name", "alias", "syndicate", "role", "city",
                "risk_score", "risk_tier", "badge_class", "factor_breakdown",
                "explanations", "alert_count"
            ])
        return df.sort_values(by="risk_score", ascending=False).reset_index(drop=True)

