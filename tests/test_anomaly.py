"""
Unit Tests for Machine Learning Anomaly Detection, Rules Engine, and Risk Scoring
"""

import pytest
import pandas as pd
from src.data_loader import DataLoader
from src.graph_manager import GraphManager
from src.network_analysis import NetworkAnalysisEngine
from src.anomaly_detection import AnomalyDetectionEngine
from src.suspicious_rules import SuspiciousRulesEngine
from src.risk_scoring import RiskScoringEngine
from src.config import DATA_DIR

def test_centrality_and_communities():
    loader = DataLoader(DATA_DIR)
    datasets = loader.load_all_datasets()
    
    gm = GraphManager(backend="local")
    gm.build_from_datasets(datasets)

    nae = NetworkAnalysisEngine(gm.nx_graph)
    centralities = nae.calculate_centralities()
    assert len(centralities) > 0
    assert "degree" in list(centralities.values())[0]
    assert "betweenness" in list(centralities.values())[0]
    assert "pagerank" in list(centralities.values())[0]

    communities = nae.detect_communities()
    assert len(communities) > 0

    leaderboard = nae.get_influential_persons_leaderboard(top_n=10)
    assert not leaderboard.empty
    assert len(leaderboard) <= 10
    assert "betweenness_centrality" in leaderboard.columns

def test_anomaly_detection_and_rules():
    loader = DataLoader(DATA_DIR)
    datasets = loader.load_all_datasets()
    
    gm = GraphManager(backend="local")
    gm.build_from_datasets(datasets)

    nae = NetworkAnalysisEngine(gm.nx_graph)
    centralities = nae.calculate_centralities()
    communities = nae.detect_communities()
    bridge_nodes = nae.find_bridge_nodes()

    # Isolation Forest
    ade = AnomalyDetectionEngine()
    feat_df = ade.build_entity_feature_matrix(
        persons_df=datasets["persons"],
        transactions_df=datasets["transactions"],
        incidents_df=datasets["incidents"],
        centrality_map=centralities,
        graph_manager=gm
    )
    assert not feat_df.empty

    scored = ade.detect_anomalous_entities(feat_df)
    assert "anomaly_score_ml" in scored.columns
    assert "is_anomaly_ml" in scored.columns

    # Suspicious Rules
    sre = SuspiciousRulesEngine()
    alerts = sre.evaluate_all_rules(
        persons_df=datasets["persons"],
        transactions_df=datasets["transactions"],
        incidents_df=datasets["incidents"],
        centralities=centralities,
        communities=communities,
        graph_manager=gm
    )
    assert len(alerts) > 0
    rule_ids = {a["rule_id"] for a in alerts}
    assert "SR-01" in rule_ids or "SR-02" in rule_ids or "SR-03" in rule_ids

    # Risk Scoring
    rse = RiskScoringEngine()
    risk_df = rse.compute_all_risk_scores(
        persons_df=datasets["persons"],
        feature_df=scored,
        centrality_map=centralities,
        all_alerts=alerts,
        bridge_nodes=bridge_nodes,
        graph_manager=gm
    )
    assert not risk_df.empty
    assert (risk_df["risk_score"] >= 0).all() and (risk_df["risk_score"] <= 100).all()
    assert "risk_tier" in risk_df.columns

