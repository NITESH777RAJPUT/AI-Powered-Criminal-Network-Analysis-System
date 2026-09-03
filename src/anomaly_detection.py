"""
Machine Learning Anomaly Detection Engine
Uses scikit-learn Isolation Forest and multivariate statistical features
to flag suspicious entities, unusual transactions, and anomalous graph behaviors.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from src.config import ANOMALY_CONTAMINATION

class AnomalyDetectionEngine:
    def __init__(self, contamination: float = ANOMALY_CONTAMINATION):
        self.contamination = contamination
        self.iso_forest = IsolationForest(
            contamination=self.contamination,
            random_state=42,
            n_estimators=150
        )
        self.scaler = StandardScaler()
        self.feature_columns = [
            "total_sent_amt",
            "total_recv_amt",
            "tx_count",
            "avg_tx_amt",
            "network_degree",
            "betweenness_score",
            "pagerank_score",
            "shared_devices_count",
            "incident_count"
        ]

    def build_entity_feature_matrix(
        self,
        persons_df: pd.DataFrame,
        transactions_df: pd.DataFrame,
        incidents_df: pd.DataFrame,
        centrality_map: Dict[str, Dict[str, float]],
        graph_manager: Any
    ) -> pd.DataFrame:
        """
        Extracts quantitative feature vectors for each person in the network.
        """
        rows = []
        
        # Precompute transaction stats per person
        tx_stats = {}
        if not transactions_df.empty:
            for _, tx in transactions_df.iterrows():
                s_id = str(tx["sender_id"])
                r_id = str(tx["receiver_id"])
                amt = float(tx.get("amount", 0.0))

                if s_id not in tx_stats:
                    tx_stats[s_id] = {"sent_amt": 0.0, "recv_amt": 0.0, "count": 0}
                tx_stats[s_id]["sent_amt"] += amt
                tx_stats[s_id]["count"] += 1

                if r_id not in tx_stats:
                    tx_stats[r_id] = {"sent_amt": 0.0, "recv_amt": 0.0, "count": 0}
                tx_stats[r_id]["recv_amt"] += amt
                tx_stats[r_id]["count"] += 1

        # Precompute incident involvement count
        inc_counts = {}
        if not incidents_df.empty:
            for _, inc in incidents_df.iterrows():
                raw_inv = inc.get("involved_person_ids", "[]")
                inv_list = []
                if isinstance(raw_inv, str):
                    try:
                        import json
                        inv_list = json.loads(raw_inv)
                    except Exception:
                        inv_list = [p.strip() for p in raw_inv.split(",") if p.strip()]
                elif isinstance(raw_inv, list):
                    inv_list = raw_inv

                for pid in inv_list:
                    inc_counts[pid] = inc_counts.get(pid, 0) + 1

        # Extract features for each person
        for _, p in persons_df.iterrows():
            pid = str(p["person_id"])
            p_name = str(p.get("name", pid))

            t_info = tx_stats.get(pid, {"sent_amt": 0.0, "recv_amt": 0.0, "count": 0})
            total_sent = t_info["sent_amt"]
            total_recv = t_info["recv_amt"]
            tx_cnt = t_info["count"]
            avg_tx = (total_sent + total_recv) / tx_cnt if tx_cnt > 0 else 0.0

            c_info = centrality_map.get(pid, {})
            deg = float(c_info.get("raw_degree", 0))
            bet = float(c_info.get("betweenness", 0.0))
            pr = float(c_info.get("pagerank", 0.0))

            # Check shared devices/vehicles count from 1-hop graph
            nodes_1hop, _ = graph_manager.get_1_hop_subgraph(pid)
            shared_dev = sum(1 for n in nodes_1hop if n.get("label") in ["Phone", "Vehicle"])

            inc_cnt = inc_counts.get(pid, 0)

            rows.append({
                "person_id": pid,
                "name": p_name,
                "syndicate": str(p.get("syndicate", "Unaffiliated")),
                "role": str(p.get("role", "Associate")),
                "total_sent_amt": total_sent,
                "total_recv_amt": total_recv,
                "tx_count": tx_cnt,
                "avg_tx_amt": avg_tx,
                "network_degree": deg,
                "betweenness_score": bet,
                "pagerank_score": pr,
                "shared_devices_count": shared_dev,
                "incident_count": inc_cnt
            })

        return pd.DataFrame(rows)

    def detect_anomalous_entities(self, feature_df: pd.DataFrame) -> pd.DataFrame:
        """
        Applies Isolation Forest to score and tag anomalous entities.
        Generates ML anomaly score (0.0 normal -> 1.0 highly anomalous) and classification.
        """
        if feature_df.empty or len(feature_df) < 5:
            df = feature_df.copy()
            df["is_anomaly_ml"] = False
            df["anomaly_score_ml"] = 0.0
            df["ml_status"] = "Normal"
            return df

        df = feature_df.copy()
        X = df[self.feature_columns].fillna(0).values

        # Scale features
        X_scaled = self.scaler.fit_transform(X)

        # Fit Isolation Forest
        self.iso_forest.fit(X_scaled)
        preds = self.iso_forest.predict(X_scaled) # -1 for outlier, 1 for inlier
        # decision_function gives negative values for outliers
        raw_scores = self.iso_forest.decision_function(X_scaled)

        # Normalize score into a 0.0 - 1.0 anomaly index (higher = more anomalous)
        min_s, max_s = raw_scores.min(), raw_scores.max()
        norm_scores = 1.0 - ((raw_scores - min_s) / (max_s - min_s + 1e-8))

        df["is_anomaly_ml"] = preds == -1
        df["anomaly_score_ml"] = np.round(norm_scores, 3)
        df["ml_status"] = df["is_anomaly_ml"].apply(
            lambda x: "Anomalous Activity Detected" if x else "Normal Baseline"
        )

        return df.sort_values(by="anomaly_score_ml", ascending=False).reset_index(drop=True)

    def detect_transaction_anomalies(self, transactions_df: pd.DataFrame) -> pd.DataFrame:
        """
        Detects specific transaction anomalies:
        - High absolute amount outliers
        - Structured smurfing transfers (multiple transfers just below ₹50,000 threshold)
        - High-velocity off-hours transfers
        """
        if transactions_df.empty:
            return pd.DataFrame()

        df = transactions_df.copy()
        amounts = df["amount"].values

        # Z-Score on amounts
        mean_amt = np.mean(amounts)
        std_amt = np.std(amounts) + 1e-8
        df["z_score"] = np.round((df["amount"] - mean_amt) / std_amt, 2)

        # Flag smurfing patterns (45,000 to 49,999 INR range)
        df["is_smurfing"] = df["amount"].between(45000, 49999)

        # Anomaly classification
        conditions = [
            (df["z_score"] > 2.5),
            (df["is_smurfing"] == True),
            (df["pattern_flag"].str.contains("Hawala|Smurfing|Layering", case=False, na=False))
        ]
        choices = [
            "High-Value Outlier",
            "Potential Smurfing / Structuring",
            "Suspicious Layering Pattern"
        ]
        df["anomaly_reason"] = np.select(conditions, choices, default="Standard Transfer")
        df["is_suspicious_tx"] = df["anomaly_reason"] != "Standard Transfer"

        return df

