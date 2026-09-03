# AI-Powered Criminal Network Analysis System

[![Python Version](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Framework](https://img.shields.io/badge/Streamlit-1.30%2B-red.svg)](https://streamlit.io/)
[![Graph Backend](https://img.shields.io/badge/Graph-Neo4j%20%26%20NetworkX-purple.svg)](https://neo4j.com/)

An enterprise-grade, full-stack intelligence analysis and crime network forensics system designed to ingest, normalize, and uncover hidden connections across heterogeneous criminal intelligence data. 

The system maps multidimensional relationships between **persons, phone numbers, vehicles, locations, front organizations, financial transactions, crime incidents, and unstructured surveillance reports**, utilizing graph theory, natural language processing (NLP), unsupervised machine learning anomaly detection, transparent rule-based triggers, explainable risk scoring, and a cryptographic blockchain-style immutable evidence ledger.

---

## 1. Problem Statement

Law enforcement and intelligence analysts face massive quantities of fragmented, multimodal data: call detail records (CDR), vehicle sightings, suspicious financial transactions, crime reports, and unstructured wiretap logs. Manually correlating cross-entity connections between disparate syndicates is error-prone, slow, and prone to oversight.

**This system solves this challenge by:**
1. Automatically extracting and normalizing structured and unstructured entities.
2. Constructing an interactive multi-relational knowledge graph.
3. Quantifying suspect influence via graph centrality metrics (Degree, Betweenness, PageRank, Closeness) and community detection.
4. Detecting complex financial and behavioral anomalies using Isolation Forest and forensic rule sets.
5. Providing an explainable 0–100 risk prioritization score.
6. Ensuring strict evidence chain-of-custody through SHA-256 blockchain-style immutable ledgering.
7. Generating court/investigation-ready forensic PDF dossiers.

> **Academic & Demonstration Notice**: This system operates on 100% synthetically generated, non-real demonstration data. Output metrics and risk scores are analytical prioritization tools for investigative assistance and do not constitute legal or criminal guilt.

---

## 2. System Architecture

```
                               ┌────────────────────────────────────────┐
                               │  HETEROGENEOUS DATA SOURCES            │
                               │  - Persons, CDR, Vehicles, Locations   │
                               │  - Financial Transactions, Incidents   │
                               │  - Free-Text Intelligence Bulletins    │
                               └──────────────────┬─────────────────────┘
                                                  │
                                                  ▼
                               ┌────────────────────────────────────────┐
                               │  INGESTION & HYBRID NLP PIPELINE       │
                               │  - Data Cleaning & Normalization       │
                               │  - spaCy NLP + Rule Gazetteers         │
                               │  - Multi-Entity & Relationship Linker  │
                               └──────────────────┬─────────────────────┘
                                                  │
                                                  ▼
                               ┌────────────────────────────────────────┐
                               │  DUAL-BACKEND KNOWLEDGE GRAPH          │
                               │  - Primary: Neo4j (Cypher Engine)      │
                               │  - Auto Fallback: NetworkX Graph Store │
                               └─────────┬────────────────────┬─────────┘
                                         │                    │
                   ┌─────────────────────┴──────┐      ┌──────┴────────────────────┐
                   ▼                            ▼      ▼                           ▼
    ┌──────────────────────────────┐ ┌───────────────────────────┐ ┌──────────────────────────────┐
    │  TOPOLOGY & GRAPH ANALYTICS  │ │  ML & SUSPICIOUS RULES    │ │  EVIDENCE INTEGRITY LEDGER   │
    │  - Degree & Betweenness      │ │  - Isolation Forest ML    │ │  - SHA-256 Hashing           │
    │  - PageRank & Closeness      │ │  - Smurfing & Layering    │ │  - Immutable Block Chaining  │
    │  - Community Partitioning    │ │  - Shared Devices/Vehicles│ │  - Tamper Detection Audit    │
    └──────────────┬───────────────┘ └─────────────┬─────────────┘ └──────────────┬───────────────┘
                   │                               │                              │
                   └───────────────────────┬───────┴──────────────────────────────┘
                                           │
                                           ▼
                               ┌────────────────────────────────────────┐
                               │  EXPLAINABLE 0–100 RISK ENGINE         │
                               │  (Centrality + Anomalies + Rules)      │
                               └──────────────────┬─────────────────────┘
                                                  │
                                                  ▼
                               ┌────────────────────────────────────────┐
                               │  STREAMLIT CYBER-INTEL DASHBOARD       │
                               │  - PyVis Interactive 2D/3D Graph       │
                               │  - Search & Suspect Dossiers           │
                               │  - Automated PDF Investigation Reports │
                               └────────────────────────────────────────┘
```

---

## 3. Technology Stack

| Layer | Component | Description |
|---|---|---|
| **Language** | Python 3.11+ | High-performance core backend runtime |
| **Frontend UI** | Streamlit | Dark cyber-intelligence multi-page dashboard |
| **Graph Visuals** | PyVis & Plotly | Interactive physics-based graph canvas & analytics charts |
| **Graph Engine** | Neo4j & NetworkX | Dual-backend: Enterprise Neo4j Cypher + local zero-config NetworkX fallback |
| **NLP Engine** | spaCy & Regex | Hybrid NER for Persons, Phones, Vehicles, Locations, Orgs, Currency |
| **Machine Learning**| scikit-learn | Isolation Forest multivariate anomaly detection |
| **Security & Integrity**| SHA-256 & Block Ledger | Cryptographic hashing with tamper-evident chain verification |
| **Reporting** | fpdf2 | Publication-grade PDF dossier generation |
| **Data Engine** | Pandas & NumPy | High-speed vectorized data transformation |

---

## 4. Project Folder Structure

```
criminal-network-analysis/
│
├── app.py                          # Main Streamlit Cyber Intelligence Dashboard
├── requirements.txt                # Production Python dependencies
├── README.md                       # Comprehensive system documentation
├── .env.example                    # Environment configuration template
├── .gitignore                      # Git exclusion rules
│
├── data/                           # Comprehensive Synthetic Intelligence Datasets
│   ├── generate_synthetic_data.py  # Reproducible dataset generator
│   ├── persons.csv                 # 125 synthetic suspects and civilians
│   ├── phone_records.csv           # 65 phone numbers, IMEI, and call logs
│   ├── vehicles.csv                # 60 vehicle registrations and models
│   ├── locations.csv               # 35 locations with geo-coordinates
│   ├── transactions.csv            # 265 financial transactions (smurfing/hawala)
│   ├── incidents.csv               # 115 crime and seizure incidents
│   ├── organizations.csv           # 8 syndicates, fronts, and shell companies
│   └── reports/                    # 55 rich unstructured intelligence bulletins
│
├── src/                            # Modular Core Engine
│   ├── __init__.py
│   ├── config.py                   # Global system constants, weights, and paths
│   ├── data_loader.py              # Universal file ingestion (CSV, JSON, TXT)
│   ├── data_cleaner.py             # Entity sanitization and schema validation
│   ├── entity_extractor.py         # Hybrid NLP + regex entity recognizer
│   ├── relationship_extractor.py   # Multi-entity graph relationship builder
│   ├── graph_manager.py            # Dual-backend Graph Database Manager (Neo4j + NetworkX)
│   ├── network_analysis.py         # Centralities, community detection, bridge nodes
│   ├── anomaly_detection.py        # Isolation Forest ML and financial anomaly detection
│   ├── suspicious_rules.py         # Rule-based forensic engine (SR-01 to SR-08)
│   ├── risk_scoring.py             # Explainable 0–100 risk prioritization scoring
│   ├── evidence_integrity.py       # SHA-256 cryptographic blockchain ledger
│   ├── report_generator.py         # Formal investigation dossier builder (PDF & MD)
│   └── utils.py                    # PyVis HTML graph generator & Plotly charts
│
├── graph/                          # Cypher Database Schema & Seeds
│   ├── schema.cypher               # Constraints and performance indexes
│   └── seed.cypher                 # Neo4j initialization queries
│
├── reports/                        # Target export folder for generated PDF dossiers
│
├── tests/                          # Automated Pytest Suite
│   ├── test_data.py                # Data loading and cleaning tests
│   ├── test_graph.py               # Graph operations and 1-hop/2-hop tests
│   ├── test_anomaly.py             # ML anomaly, rule engine, risk scoring tests
│   └── test_security.py            # Hashing and blockchain integrity tests
│
└── assets/                         # Theme styling & CSS
    └── custom.css                  # Dark cybersecurity intelligence theme stylesheet
```

---

## 5. Installation & Setup

### Step 1: Clone Repository & Create Virtual Environment
```bash
git clone <repository_url>
cd criminal-network-analysis

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

---

## 6. Running the Application

### Local Fallback Mode (Default — Zero Setup)
The application works immediately out-of-the-box using the high-performance local **NetworkX** graph engine. No external databases or services are required.

Run the Streamlit application:
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 7. Neo4j Graph Database Integration (Optional)

To run in full enterprise Neo4j mode:
1. Start Neo4j Desktop or a Docker container:
   ```bash
   docker run --name neo4j-intel \
     -p 7474:7474 -p 7687:7687 \
     -e NEO4J_AUTH=neo4j/password123 \
     -d neo4j:5.15.0
   ```
2. Update your `.env` file:
   ```env
   GRAPH_BACKEND=neo4j
   NEO4J_URI=bolt://localhost:7687
   NEO4J_USERNAME=neo4j
   NEO4J_PASSWORD=password123
   NEO4J_DATABASE=neo4j
   ```
3. Initialize the schema:
   Run `graph/schema.cypher` in the Neo4j Browser.
4. Launch the dashboard:
   ```bash
   streamlit run app.py
   ```
   *If Neo4j becomes unavailable, the system automatically falls back to Local NetworkX mode without crashing.*

---

## 8. Key Features & Workflow Demonstration

### Step-by-Step Demo Flow
1. **Executive Dashboard (`app.py`)**:
   - High-level KPIs: Active Entities (120+), Relationships (400+), High-Risk Suspects, Active Forensic Alerts.
   - Interactive preview of the global crime graph.
   - Entity distribution donut chart and top suspect leaderboard.
2. **Data Ingestion & NLP**:
   - Ingest CSV, JSON, or TXT intelligence reports.
   - Run NLP entity extraction on free-text surveillance transcripts (`PERSON`, `PHONE`, `VEHICLE`, `LOCATION`, `ORGANIZATION`, `MONEY`, `DATE`).
   - Dynamically append and link new records into the live graph.
3. **Interactive Network Explorer**:
   - Physics-based PyVis canvas.
   - Focus on any suspect with 1-Hop or 2-Hop expansion.
   - Filter by entity type (Person, Phone, Vehicle, Location, Org, Incident) and relationship types.
4. **Entity Search & Subject Dossier**:
   - Global auto-suggest search across suspect names, aliases, license plates, and phone numbers.
   - Complete dossier card, 0–100 risk score, and connected identifier tabs.
5. **Network Analytics**:
   - Centrality metrics: Degree, Betweenness (brokers), PageRank (commanders), Closeness.
   - Community detection partitioning into distinct syndicate clusters.
   - Articulation / bridge node identification.
6. **Suspicious Activity & ML Anomalies**:
   - Isolation Forest unsupervised outlier detection.
   - Rule-based alerts table with Rule IDs (`SR-01` to `SR-08`), severity badges, and explainable forensic reasons.
   - Financial smurfing and hawala timeline charts.
7. **Evidence Integrity & Blockchain Ledger**:
   - Immutable block sequence with SHA-256 cryptographic hashes.
   - File verification tool comparing external document digests against the sealed chain.
   - Live tamper simulation and automated audit detection.
8. **Investigation Dossier PDF Export**:
   - Select any subject entity.
   - Generate formal multi-page PDF report with case identifier, network statistics, alert logs, and evidence verification status.

---

## 9. Explainable 0–100 Risk Prioritization Scoring

The risk scoring engine computes an explainable prioritization index based on 6 weighted factors:

$$\text{Risk Score} = \sum w_i \cdot F_i$$

| Factor | Weight | Description |
|---|---|---|
| **Network Centrality** | 25% | Betweenness, PageRank, and direct connection volume |
| **Transaction Anomalies** | 20% | ML Isolation Forest outlier score and high-volume hawala flows |
| **Forensic Rule Triggers** | 20% | Number and severity of active rule violations |
| **Shared Identifiers** | 15% | Number of shared burner phones or getaway vehicles |
| **Community / Bridge Position** | 10% | Acting as articulation point connecting disjoint syndicates |
| **Incident Recurrence** | 10% | Number of linked criminal cases |

### Risk Tiers
- **0–29 (Low)**: Baseline civilian background activity.
- **30–59 (Moderate)**: Minor indirect associations or standard transaction activity.
- **60–79 (High)**: Substantial centrality, shared devices, or multiple rule alerts.
- **80–100 (Critical)**: Key syndicate orchestrators, cross-cluster bridge brokers, or active smurfing/hawala participants.

---

## 10. Automated Testing

The project includes an automated test suite verifying all subsystems:

```bash
python -m pytest tests/ -v
```

### Test Coverage Breakdown
- `tests/test_data.py`: Data loading, phone/vehicle/amount sanitization, synthetic dataset volume verification.
- `tests/test_graph.py`: Node/edge CRUD, search, 1-hop/2-hop neighborhood traversals, dataset graph build.
- `tests/test_anomaly.py`: Centrality metrics, community detection, Isolation Forest fitting, rule triggers, risk scoring boundaries.
- `tests/test_security.py`: SHA-256 digest correctness, block chaining, and tamper detection verification.

---

## 11. Limitations & Future Roadmap

### Current Limitations
- Operates on synthetic demonstration datasets for privacy and security compliance.
- Local mode graph size is memory-bounded (suitable for up to ~100,000 entities; enterprise datasets should use Neo4j).

### Future Roadmap
- **Real-Time Streaming**: Ingestion of real-time CDR and financial transaction streams via Apache Kafka.
- **Graph Neural Networks (GNN)**: Link prediction and automated syndicate role classification using PyTorch Geometric.
- **Multimodal Visual Surveillance**: Automated license plate recognition (ALPR) and facial recognition embedding links.
- **Geo-Spatial Heatmaps**: Interactive Mapbox / Kepler.gl integration for temporal movement trajectory mapping.

---

## 12. Ethical & Legal Considerations

1. **Analytical Support Only**: This platform is designed exclusively as an investigative prioritization aid. Automated risk scores and anomaly tags do not establish legal culpability or guilt.
2. **Data Privacy**: No real, confidential, or personally identifiable law enforcement data is included in this repository. All names, phone numbers, vehicle registrations, and scenarios are synthetic.
3. **Auditability & Explainability**: All machine learning scores are accompanied by clear factor breakdowns to eliminate "black-box" decision making in forensic workflows.

#   A I - P o w e r e d - C r i m i n a l - N e t w o r k - A n a l y s i s - S y s t e m  
 