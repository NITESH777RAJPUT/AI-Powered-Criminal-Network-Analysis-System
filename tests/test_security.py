"""
Unit Tests for Cryptographic SHA-256 Hashing and Blockchain Ledger
"""

import pytest
import hashlib
from src.evidence_integrity import EvidenceIntegrityLedger, EvidenceBlock

def test_sha256_calculation():
    raw_str = "Test Evidence Document Content 12345"
    expected = hashlib.sha256(raw_str.encode("utf-8")).hexdigest()
    assert EvidenceIntegrityLedger.calculate_sha256(raw_str) == expected

def test_blockchain_ledger_chaining_and_verification():
    ledger = EvidenceIntegrityLedger(auto_load=False)
    assert len(ledger.chain) == 1 # Genesis Block
    assert ledger.chain[0].evidence_id == "GENESIS-BLOCK"

    # Add evidence blocks
    b1 = ledger.add_evidence("EVID-001", "report_001.txt", "Intelligence Note 1")
    b2 = ledger.add_evidence("EVID-002", "wiretap_002.txt", "Wiretap Transcript 2")
    b3 = ledger.add_evidence("EVID-003", "cctv_log.txt", "CCTV Sighting Log 3")

    assert len(ledger.chain) == 4
    assert b1.previous_hash == ledger.chain[0].block_hash
    assert b2.previous_hash == b1.block_hash
    assert b3.previous_hash == b2.block_hash

    # Verify clean chain
    is_valid, msg, logs = ledger.verify_chain_integrity()
    assert is_valid is True
    assert "VERIFIED" in msg

def test_blockchain_tamper_detection():
    ledger = EvidenceIntegrityLedger(auto_load=False)
    ledger.add_evidence("EVID-001", "file1.txt", "Content 1")
    ledger.add_evidence("EVID-002", "file2.txt", "Content 2")
    ledger.add_evidence("EVID-003", "file3.txt", "Content 3")

    # Tamper with block 2
    ledger.simulate_tampering(2, "FORGED_MALICIOUS_CONTENT")

    is_valid, msg, logs = ledger.verify_chain_integrity()
    assert is_valid is False
    assert "TAMPERING DETECTED" in msg or "CHAIN BROKEN" in msg

