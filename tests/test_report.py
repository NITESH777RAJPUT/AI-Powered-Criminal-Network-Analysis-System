"""
Unit Tests for Investigation Dossier & Report Generation
"""

import pytest
from pathlib import Path
from src.data_loader import DataLoader
from src.graph_manager import GraphManager
from src.network_analysis import NetworkAnalysisEngine
from src.anomaly_detection import AnomalyDetectionEngine
from src.suspicious_rules import SuspiciousRulesEngine
from src.risk_scoring import RiskScoringEngine
from src.evidence_integrity import EvidenceIntegrityLedger
from src.report_generator import ReportGenerator
from src.config import DATA_DIR, EXPORT_REPORTS_DIR

def test_dossier_and_pdf_generation():
    loader = DataLoader(DATA_DIR)
    datasets = loader.load_all_datasets()
    
    gm = GraphManager(backend="local")
    gm.build_from_datasets(datasets)

    nae = NetworkAnalysisEngine(gm.nx_graph)
    ade = AnomalyDetectionEngine()
    sre = SuspiciousRulesEngine()
    rse = RiskScoringEngine()
    ledger = EvidenceIntegrityLedger()

    rg = ReportGenerator(EXPORT_REPORTS_DIR)
    dossier = rg.generate_dossier_data("PER-001", gm, rse, nae, ade, sre, ledger, datasets)

    assert dossier["person_id"] == "PER-001"
    assert "risk_score" in dossier
    assert "network_metrics" in dossier
    assert "alerts" in dossier

    # PDF Generation Test
    pdf_path = rg.generate_pdf_report(dossier)
    assert Path(pdf_path).exists()
    assert Path(pdf_path).stat().st_size > 500

    # Markdown Generation Test
    md_text = rg.generate_markdown_report(dossier)
    assert "CRIMINAL NETWORK INTELLIGENCE DOSSIER" in md_text
    assert "PER-001" in md_text

