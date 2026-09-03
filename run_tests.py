"""
Standalone Test Runner for AI-Powered Criminal Network Analysis System
Executes all unit, integration, ML, graph, and security tests.
"""

import sys
import traceback
from datetime import datetime

def main():
    print("=" * 70)
    print("AI-POWERED CRIMINAL NETWORK ANALYSIS SYSTEM - TEST RUNNER")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    try:
        # 1. Data Loader & Cleaner Tests
        print("\n[1/4] Running Data Loader & Cleaner Tests (test_data.py)...")
        import tests.test_data as td
        td.test_data_cleaner_phone()
        print("  [PASS] Phone number cleaner passed.")
        td.test_data_cleaner_vehicle()
        print("  [PASS] Vehicle plate cleaner passed.")
        td.test_data_cleaner_amount()
        print("  [PASS] Amount & currency cleaner passed.")
        td.test_synthetic_datasets_load()
        print("  [PASS] Synthetic dataset volume & schema verification passed.")

        # 2. Security & Blockchain Tests
        print("\n[2/4] Running Security & Blockchain Integrity Tests (test_security.py)...")
        import tests.test_security as ts
        ts.test_sha256_calculation()
        print("  [PASS] SHA-256 cryptographic digest calculation passed.")
        ts.test_blockchain_ledger_chaining_and_verification()
        print("  [PASS] Immutable block chaining & clean verification passed.")
        ts.test_blockchain_tamper_detection()
        print("  [PASS] Tampering detection & broken chain alert passed.")

        # 3. Graph Operations Tests
        print("\n[3/4] Running Graph Operations & Fallback Tests (test_graph.py)...")
        import tests.test_graph as tg
        tg.test_graph_manager_node_and_edge_crud()
        print("  [PASS] Node/Edge CRUD and 1-hop neighborhood passed.")
        tg.test_graph_build_from_datasets()
        print("  [PASS] Full multi-entity dataset graph construction passed.")

        # 4. ML Anomaly, Centrality, and Risk Scoring Tests
        print("\n[4/5] Running ML Anomaly, Centrality & Risk Tests (test_anomaly.py)...")
        import tests.test_anomaly as ta
        ta.test_centrality_and_communities()
        print("  [PASS] Degree, Betweenness, PageRank & Community detection passed.")
        ta.test_anomaly_detection_and_rules()
        print("  [PASS] Isolation Forest, Suspicious Rules & 0-100 Risk scoring passed.")

        # 5. Report Generator Tests
        print("\n[5/5] Running Investigation Dossier & PDF Export Tests (test_report.py)...")
        import tests.test_report as tr
        tr.test_dossier_and_pdf_generation()
        print("  [PASS] Dossier gathering, Markdown & PDF generation passed.")

        print("\n" + "=" * 70)
        print("SUCCESS: ALL 100% UNIT AND INTEGRATION TESTS PASSED!")
        print("=" * 70)
        return 0

    except Exception as e:
        print(f"\n[FAIL] TEST FAILURE: {e}")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
