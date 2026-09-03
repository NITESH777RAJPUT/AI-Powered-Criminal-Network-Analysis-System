import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
REPORTS_DIR = DATA_DIR / "reports"
EXPORT_REPORTS_DIR = BASE_DIR / "reports"
ASSETS_DIR = BASE_DIR / "assets"
GRAPH_DIR = BASE_DIR / "graph"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True, parents=True)
REPORTS_DIR.mkdir(exist_ok=True, parents=True)
EXPORT_REPORTS_DIR.mkdir(exist_ok=True, parents=True)
ASSETS_DIR.mkdir(exist_ok=True, parents=True)
GRAPH_DIR.mkdir(exist_ok=True, parents=True)

# System Mode: 'local' (NetworkX fallback) or 'neo4j'
GRAPH_BACKEND = os.getenv("GRAPH_BACKEND", "local").lower()

# Neo4j Settings
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password123")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")

# File constraints
MAX_UPLOAD_SIZE_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", 25))
ALLOWED_EXTENSIONS = {"csv", "json", "txt", "pdf"}

# Anomaly Detection & ML
ANOMALY_CONTAMINATION = float(os.getenv("ANOMALY_CONTAMINATION", 0.08))

# Risk / Intelligence Score Weights (Sum to 1.0)
RISK_WEIGHTS = {
    "centrality": float(os.getenv("RISK_WEIGHT_CENTRALITY", 0.25)),
    "anomaly": float(os.getenv("RISK_WEIGHT_ANOMALY", 0.20)),
    "rules": float(os.getenv("RISK_WEIGHT_RULES", 0.20)),
    "shared_id": float(os.getenv("RISK_WEIGHT_SHARED_ID", 0.15)),
    "community": float(os.getenv("RISK_WEIGHT_COMMUNITY", 0.10)),
    "incidents": float(os.getenv("RISK_WEIGHT_INCIDENTS", 0.10))
}

# Node Categories & UI Colors
NODE_COLORS = {
    "Person": "#ef4444",       # Red
    "Phone": "#3b82f6",        # Blue
    "Vehicle": "#f59e0b",      # Amber
    "Location": "#10b981",     # Green / Emerald
    "Organization": "#8b5cf6", # Purple
    "Transaction": "#ec4899",  # Pink
    "Incident": "#dc2626",     # Dark Red
    "Report": "#64748b"        # Slate
}

NODE_SIZES = {
    "Person": 22,
    "Phone": 16,
    "Vehicle": 16,
    "Location": 18,
    "Organization": 20,
    "Transaction": 14,
    "Incident": 18,
    "Report": 14
}

# Risk Level Thresholds
RISK_LEVELS = {
    "LOW": (0, 29),
    "MODERATE": (30, 59),
    "HIGH": (60, 79),
    "CRITICAL": (80, 100)
}

DISCLAIMER_TEXT = (
    "NOTICE: This system is an academic demonstration providing analytical prioritization "
    "and relationship mapping for investigation support. Output metrics, risk scores, and anomaly "
    "flags do not establish legal or criminal guilt."
)

