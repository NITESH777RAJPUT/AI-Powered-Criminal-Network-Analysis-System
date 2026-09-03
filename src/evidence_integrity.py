"""
Evidence Integrity & Blockchain Ledger Module
Implements SHA-256 cryptographic hashing and an immutable, chained block ledger
persisted to disk for forensically verifying evidence files and chain-of-custody.
"""

import hashlib
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union
from src.config import DATA_DIR

PERSISTENT_DIR = DATA_DIR / "persistent"
LEDGER_FILE = PERSISTENT_DIR / "evidence_ledger.json"

class EvidenceBlock:
    def __init__(
        self,
        index: int,
        timestamp: str,
        evidence_id: str,
        filename: str,
        evidence_hash: str,
        previous_hash: str,
        block_hash: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.index = index
        self.timestamp = timestamp
        self.evidence_id = evidence_id
        self.filename = filename
        self.evidence_hash = evidence_hash
        self.previous_hash = previous_hash
        self.metadata = metadata or {}
        self.block_hash = block_hash or self.calculate_block_hash()

    def calculate_block_hash(self) -> str:
        """
        Calculates SHA-256 block hash over all block contents.
        SHA-256(index | timestamp | evidence_id | filename | evidence_hash | previous_hash)
        """
        block_string = (
            f"{self.index}|{self.timestamp}|{self.evidence_id}|{self.filename}|"
            f"{self.evidence_hash}|{self.previous_hash}"
        )
        return hashlib.sha256(block_string.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "evidence_id": self.evidence_id,
            "filename": self.filename,
            "evidence_hash": self.evidence_hash,
            "previous_hash": self.previous_hash,
            "block_hash": self.block_hash,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "EvidenceBlock":
        return cls(
            index=d["index"],
            timestamp=d["timestamp"],
            evidence_id=d["evidence_id"],
            filename=d["filename"],
            evidence_hash=d["evidence_hash"],
            previous_hash=d["previous_hash"],
            block_hash=d.get("block_hash"),
            metadata=d.get("metadata", {})
        )


class EvidenceIntegrityLedger:
    def __init__(self, ledger_file: Optional[Path] = None, auto_load: bool = True):
        self.chain: List[EvidenceBlock] = []
        self.ledger_file = ledger_file or LEDGER_FILE
        self.auto_load = auto_load
        PERSISTENT_DIR.mkdir(parents=True, exist_ok=True)
        
        if not (self.auto_load and self.load_from_disk()):
            self._create_genesis_block()
            if self.auto_load and self.ledger_file == LEDGER_FILE:
                self.save_to_disk()

    def _create_genesis_block(self):
        """Creates the foundational Genesis block of the evidence chain."""
        genesis = EvidenceBlock(
            index=0,
            timestamp=datetime(2025, 1, 1, 0, 0, 0).strftime("%Y-%m-%d %H:%M:%S"),
            evidence_id="GENESIS-BLOCK",
            filename="SYSTEM_GENESIS_ROOT",
            evidence_hash="0000000000000000000000000000000000000000000000000000000000000000",
            previous_hash="0000000000000000000000000000000000000000000000000000000000000000",
            metadata={"system": "Criminal Network Intelligence Ledger"}
        )
        self.chain = [genesis]

    def save_to_disk(self):
        """Persists the evidence ledger to disk."""
        if not self.auto_load and self.ledger_file != LEDGER_FILE:
            return
        try:
            payload = [b.to_dict() for b in self.chain]
            with open(self.ledger_file, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)
        except Exception as e:
            print(f"[EvidenceLedger] Error saving ledger to disk: {e}")

    def load_from_disk(self) -> bool:
        """Loads evidence ledger from disk if it exists."""
        if not self.ledger_file.exists():
            return False
        try:
            with open(self.ledger_file, "r", encoding="utf-8") as f:
                payload = json.load(f)
            if not payload or not isinstance(payload, list):
                return False

            self.chain = [EvidenceBlock.from_dict(b) for b in payload]
            return True
        except Exception as e:
            print(f"[EvidenceLedger] Error loading ledger from disk: {e}")
            return False

    @staticmethod
    def calculate_sha256(data: Union[str, bytes, Path]) -> str:
        """Calculates SHA-256 cryptographic digest of string, bytes, or file."""
        hasher = hashlib.sha256()
        if isinstance(data, Path) or (isinstance(data, str) and len(data) < 500 and Path(data).exists()):
            with open(data, "rb") as f:
                while chunk := f.read(65536):
                    hasher.update(chunk)
            return hasher.hexdigest()
        elif isinstance(data, bytes):
            hasher.update(data)
            return hasher.hexdigest()
        elif isinstance(data, str):
            hasher.update(data.encode("utf-8"))
            return hasher.hexdigest()
        return ""

    def add_evidence(
        self,
        evidence_id: str,
        filename: str,
        file_or_content: Union[str, bytes, Path],
        metadata: Optional[Dict[str, Any]] = None
    ) -> EvidenceBlock:
        """
        Hashes new evidence item, appends a cryptographically chained block, and saves to disk.
        """
        evidence_hash = self.calculate_sha256(file_or_content)
        prev_block = self.chain[-1]
        
        new_block = EvidenceBlock(
            index=len(self.chain),
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            evidence_id=evidence_id,
            filename=filename,
            evidence_hash=evidence_hash,
            previous_hash=prev_block.block_hash,
            metadata=metadata or {}
        )
        self.chain.append(new_block)
        self.save_to_disk()
        return new_block

    def verify_chain_integrity(self) -> Tuple[bool, str, List[Dict[str, Any]]]:
        """
        Audits all blocks in sequence:
        1. Recalculates block hash and verifies match.
        2. Verifies previous_hash points to prior block's hash.
        Returns: (is_valid: bool, status_message: str, audit_logs: List[Dict])
        """
        audit_logs = []
        
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            prev = self.chain[i - 1]

            # Check previous hash pointer
            if current.previous_hash != prev.block_hash:
                msg = f"CHAIN BROKEN at Block #{current.index} ({current.filename}). PrevHash mismatch!"
                audit_logs.append({
                    "block_index": current.index,
                    "evidence_id": current.evidence_id,
                    "status": "MODIFIED / TAMPERED",
                    "reason": f"Stored previous_hash {current.previous_hash[:16]}... does not match Block #{prev.index} hash {prev.block_hash[:16]}..."
                })
                return False, msg, audit_logs

            # Check self recalculated hash
            recalc_hash = current.calculate_block_hash()
            if current.block_hash != recalc_hash:
                msg = f"TAMPERING DETECTED at Block #{current.index} ({current.filename}). Hash mismatch!"
                audit_logs.append({
                    "block_index": current.index,
                    "evidence_id": current.evidence_id,
                    "status": "MODIFIED / TAMPERED",
                    "reason": f"Recalculated hash {recalc_hash[:16]}... does not match recorded block hash {current.block_hash[:16]}..."
                })
                return False, msg, audit_logs

            audit_logs.append({
                "block_index": current.index,
                "evidence_id": current.evidence_id,
                "filename": current.filename,
                "status": "VERIFIED",
                "hash_preview": f"{current.block_hash[:16]}..."
            })

        return True, "EVIDENCE LEDGER INTEGRITY VERIFIED (ALL HASHES MATCH)", audit_logs

    def verify_file_against_block(self, file_content: Union[str, bytes, Path], block_index: int) -> Tuple[bool, str, str]:
        """
        Hashes uploaded content and checks if it matches the hash recorded in block_index.
        Returns (is_match, calculated_hash, recorded_hash).
        """
        if block_index < 0 or block_index >= len(self.chain):
            return False, "", "BLOCK_NOT_FOUND"

        calc_hash = self.calculate_sha256(file_content)
        recorded_hash = self.chain[block_index].evidence_hash
        return (calc_hash == recorded_hash), calc_hash, recorded_hash

    def simulate_tampering(self, block_index: int, fake_content: str = "TAMPERED_RECORD"):
        """
        Simulates malicious tampering on a historical block for forensic demonstration.
        """
        if 0 < block_index < len(self.chain):
            target_block = self.chain[block_index]
            target_block.evidence_hash = hashlib.sha256(fake_content.encode("utf-8")).hexdigest()

    def get_ledger_history(self) -> List[Dict[str, Any]]:
        """Returns full chain history formatted as dictionary records."""
        return [b.to_dict() for b in self.chain]
