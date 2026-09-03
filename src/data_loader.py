"""
Universal Data Loader Engine
Loads structured (CSV, JSON) and unstructured (TXT, PDF) intelligence data.
Gracefully handles missing files, empty uploads, and schema mismatches.
"""

import os
import json
import io
import pandas as pd
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Union
from src.config import DATA_DIR, REPORTS_DIR, ALLOWED_EXTENSIONS
from src.data_cleaner import DataCleaner

class DataLoader:
    def __init__(self, data_dir: Path = DATA_DIR):
        self.data_dir = data_dir
        self.reports_dir = data_dir / "reports"
        self.cleaner = DataCleaner()

    def load_all_datasets(self) -> Dict[str, Any]:
        """Loads all standard system datasets with fallback defaults."""
        datasets = {
            "persons": self.load_persons(),
            "phones": self.load_phones(),
            "vehicles": self.load_vehicles(),
            "locations": self.load_locations(),
            "transactions": self.load_transactions(),
            "incidents": self.load_incidents(),
            "organizations": self.load_organizations(),
            "reports": self.load_reports()
        }
        return datasets

    def load_persons(self, file_path: Optional[Path] = None) -> pd.DataFrame:
        path = file_path or (self.data_dir / "persons.csv")
        if not path.exists():
            return pd.DataFrame(columns=["person_id", "name", "alias", "syndicate", "role", "city", "primary_phone", "primary_vehicle", "status", "is_suspect"])
        try:
            df = pd.read_csv(path)
            return self.cleaner.clean_persons_dataframe(df)
        except Exception as e:
            print(f"[DataLoader] Warning loading persons from {path}: {e}")
            return pd.DataFrame()

    def load_phones(self, file_path: Optional[Path] = None) -> pd.DataFrame:
        path = file_path or (self.data_dir / "phone_records.csv")
        if not path.exists():
            return pd.DataFrame(columns=["phone_id", "phone_number", "carrier", "imei", "is_burner", "status"])
        try:
            df = pd.read_csv(path)
            return self.cleaner.clean_phones_dataframe(df)
        except Exception as e:
            print(f"[DataLoader] Warning loading phones from {path}: {e}")
            return pd.DataFrame()

    def load_vehicles(self, file_path: Optional[Path] = None) -> pd.DataFrame:
        path = file_path or (self.data_dir / "vehicles.csv")
        if not path.exists():
            return pd.DataFrame(columns=["vehicle_id", "plate_number", "model", "color", "vehicle_type", "status"])
        try:
            df = pd.read_csv(path)
            return self.cleaner.clean_vehicles_dataframe(df)
        except Exception as e:
            print(f"[DataLoader] Warning loading vehicles from {path}: {e}")
            return pd.DataFrame()

    def load_locations(self, file_path: Optional[Path] = None) -> pd.DataFrame:
        path = file_path or (self.data_dir / "locations.csv")
        if not path.exists():
            return pd.DataFrame(columns=["location_id", "name", "city", "lat", "lon", "type"])
        try:
            df = pd.read_csv(path)
            return self.cleaner.clean_locations_dataframe(df)
        except Exception as e:
            print(f"[DataLoader] Warning loading locations: {e}")
            return pd.DataFrame()

    def load_transactions(self, file_path: Optional[Path] = None) -> pd.DataFrame:
        path = file_path or (self.data_dir / "transactions.csv")
        if not path.exists():
            return pd.DataFrame(columns=["transaction_id", "sender_id", "sender_name", "receiver_id", "receiver_name", "amount", "currency", "timestamp", "channel", "pattern_flag", "is_suspicious"])
        try:
            df = pd.read_csv(path)
            return self.cleaner.clean_transactions_dataframe(df)
        except Exception as e:
            print(f"[DataLoader] Warning loading transactions: {e}")
            return pd.DataFrame()

    def load_incidents(self, file_path: Optional[Path] = None) -> pd.DataFrame:
        path = file_path or (self.data_dir / "incidents.csv")
        if not path.exists():
            return pd.DataFrame(columns=["incident_id", "title", "incident_type", "severity", "location_id", "location_name", "city", "timestamp", "description", "involved_person_ids", "involved_person_names"])
        try:
            df = pd.read_csv(path)
            return self.cleaner.clean_incidents_dataframe(df)
        except Exception as e:
            print(f"[DataLoader] Warning loading incidents: {e}")
            return pd.DataFrame()

    def load_organizations(self, file_path: Optional[Path] = None) -> pd.DataFrame:
        path = file_path or (self.data_dir / "organizations.csv")
        if not path.exists():
            return pd.DataFrame(columns=["id", "name", "type", "city"])
        try:
            return pd.read_csv(path)
        except Exception as e:
            print(f"[DataLoader] Warning loading organizations: {e}")
            return pd.DataFrame()

    def load_reports(self) -> List[Dict[str, Any]]:
        """Loads all unstructured text reports and returns a list of dictionaries."""
        reports = []
        if not self.reports_dir.exists():
            return reports

        txt_files = sorted(list(self.reports_dir.glob("*.txt")))
        for idx, file_path in enumerate(txt_files):
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                reports.append({
                    "report_id": f"REP-{idx+1:03d}",
                    "filename": file_path.name,
                    "filepath": str(file_path),
                    "content": content,
                    "size_bytes": file_path.stat().st_size
                })
            except Exception as e:
                print(f"[DataLoader] Error reading report file {file_path.name}: {e}")
        return reports

    def parse_uploaded_file(self, uploaded_file: Any) -> Tuple[str, Union[pd.DataFrame, Dict, str], str]:
        """
        Parses an uploaded file object from Streamlit or API.
        Returns (data_type, parsed_content, status_message).
        """
        filename = uploaded_file.name
        ext = filename.split(".")[-1].lower() if "." in filename else ""

        if ext not in ALLOWED_EXTENSIONS:
            return "invalid", None, f"Unsupported file extension: .{ext}. Allowed: {ALLOWED_EXTENSIONS}"

        try:
            if ext == "csv":
                df = pd.read_csv(uploaded_file)
                # Determine table type by columns
                cols = set(df.columns.str.lower())
                if "person_id" in cols or "alias" in cols or ("name" in cols and "syndicate" in cols):
                    return "persons", self.cleaner.clean_persons_dataframe(df), f"Successfully loaded {len(df)} Person records."
                elif "amount" in cols and ("sender_id" in cols or "receiver_id" in cols):
                    return "transactions", self.cleaner.clean_transactions_dataframe(df), f"Successfully loaded {len(df)} Transaction records."
                elif "plate_number" in cols or "vehicle_id" in cols:
                    return "vehicles", self.cleaner.clean_vehicles_dataframe(df), f"Successfully loaded {len(df)} Vehicle records."
                elif "phone_number" in cols or "imei" in cols:
                    return "phones", self.cleaner.clean_phones_dataframe(df), f"Successfully loaded {len(df)} Phone records."
                elif "incident_id" in cols or "incident_type" in cols:
                    return "incidents", df, f"Successfully loaded {len(df)} Incident records."
                elif "lat" in cols and "lon" in cols:
                    return "locations", df, f"Successfully loaded {len(df)} Location records."
                else:
                    return "generic_csv", df, f"Loaded {len(df)} records from {filename}."

            elif ext == "json":
                data = json.load(uploaded_file)
                return "json", data, f"Successfully parsed JSON file with {len(data) if isinstance(data, list) else 1} items."

            elif ext == "txt":
                text = uploaded_file.read().decode("utf-8", errors="ignore")
                return "text_report", text, f"Loaded text document: {filename} ({len(text)} characters)."

            elif ext == "pdf":
                raw_bytes = uploaded_file.read()
                return "binary_doc", raw_bytes, f"Loaded binary PDF document: {filename} ({len(raw_bytes)} bytes)."

        except Exception as e:
            return "error", None, f"Error processing file '{filename}': {str(e)}"

        return "unknown", None, "Unable to determine file content."

    def ingest_and_commit(
        self,
        uploaded_file: Any,
        graph_manager: Any
    ) -> Dict[str, Any]:
        """
        Executes full end-to-end ingestion pipeline:
        1. Reads and validates file.
        2. Normalizes and cleans records.
        3. Persists to disk CSV/file storage.
        4. Upserts nodes and relationships into GraphManager (Neo4j / Persistent Store).
        5. Returns actual operation statistics.
        """
        dtype, parsed, msg = self.parse_uploaded_file(uploaded_file)
        if dtype in ["invalid", "error", "unknown"] or parsed is None:
            return {
                "success": False,
                "data_type": dtype,
                "rows_uploaded": 0,
                "rows_accepted": 0,
                "rows_rejected": 0,
                "nodes_created": 0,
                "relationships_created": 0,
                "errors": [msg],
                "message": msg
            }

        stats = {
            "success": True,
            "data_type": dtype,
            "rows_uploaded": len(parsed) if isinstance(parsed, (pd.DataFrame, list)) else 1,
            "rows_accepted": 0,
            "rows_rejected": 0,
            "nodes_created": 0,
            "relationships_created": 0,
            "errors": [],
            "message": msg
        }

        try:
            if isinstance(parsed, pd.DataFrame):
                df = parsed
                stats["rows_accepted"] = len(df)

                # Persist to disk
                target_csv_map = {
                    "persons": self.data_dir / "persons.csv",
                    "phones": self.data_dir / "phone_records.csv",
                    "vehicles": self.data_dir / "vehicles.csv",
                    "locations": self.data_dir / "locations.csv",
                    "transactions": self.data_dir / "transactions.csv",
                    "incidents": self.data_dir / "incidents.csv"
                }

                target_path = target_csv_map.get(dtype)
                if target_path:
                    if target_path.exists():
                        try:
                            existing_df = pd.read_csv(target_path)
                            merged_df = pd.concat([existing_df, df], ignore_index=True)
                            # Deduplicate by primary key
                            pk_map = {
                                "persons": "person_id",
                                "phones": "phone_id",
                                "vehicles": "vehicle_id",
                                "locations": "location_id",
                                "transactions": "transaction_id",
                                "incidents": "incident_id"
                            }
                            pk = pk_map.get(dtype)
                            if pk and pk in merged_df.columns:
                                merged_df = merged_df.drop_duplicates(subset=[pk]).reset_index(drop=True)
                            merged_df.to_csv(target_path, index=False)
                        except Exception as ex:
                            df.to_csv(target_path, index=False)
                    else:
                        df.to_csv(target_path, index=False)

                # Commit to Graph
                nodes_before = graph_manager.nx_graph.number_of_nodes()
                edges_before = graph_manager.nx_graph.number_of_edges()

                if dtype == "persons":
                    for _, row in df.iterrows():
                        pid = str(row["person_id"])
                        graph_manager.add_node(pid, "Person", {
                            "name": str(row.get("name", pid)),
                            "alias": str(row.get("alias", "None")),
                            "syndicate": str(row.get("syndicate", "Unaffiliated")),
                            "role": str(row.get("role", "Associate")),
                            "city": str(row.get("city", "Unknown")),
                            "primary_phone": str(row.get("primary_phone", "")),
                            "primary_vehicle": str(row.get("primary_vehicle", "")),
                            "status": str(row.get("status", "Normal")),
                            "is_suspect": bool(row.get("is_suspect", False))
                        })
                        if row.get("primary_phone") and str(row.get("primary_phone")) != "UNAVAILABLE":
                            ph = str(row.get("primary_phone"))
                            graph_manager.add_node(f"PH_{ph}", "Phone", {"name": ph})
                            graph_manager.add_edge(pid, f"PH_{ph}", "USES", {"role": "Primary"})
                        if row.get("primary_vehicle") and str(row.get("primary_vehicle")) != "UNKNOWN_PLATE":
                            vh = str(row.get("primary_vehicle"))
                            graph_manager.add_node(f"VEH_{vh}", "Vehicle", {"name": vh})
                            graph_manager.add_edge(pid, f"VEH_{vh}", "USES", {"role": "Primary"})

                elif dtype == "transactions":
                    for _, row in df.iterrows():
                        sid = str(row.get("sender_id", ""))
                        rid = str(row.get("receiver_id", ""))
                        if sid and rid:
                            graph_manager.add_edge(sid, rid, "TRANSFERRED", {
                                "amount": float(row.get("amount", 0.0)),
                                "timestamp": str(row.get("timestamp", "")),
                                "transaction_id": str(row.get("transaction_id", ""))
                            })

                elif dtype == "vehicles":
                    for _, row in df.iterrows():
                        plate = str(row.get("plate_number", ""))
                        if plate:
                            graph_manager.add_node(f"VEH_{plate}", "Vehicle", {
                                "name": plate,
                                "model": str(row.get("model", "Unknown")),
                                "color": str(row.get("color", "Unknown")),
                                "status": str(row.get("status", "Normal"))
                            })
                            if "person_id" in row and pd.notna(row["person_id"]):
                                graph_manager.add_edge(str(row["person_id"]), f"VEH_{plate}", "USES", {"role": "Owner"})

                elif dtype == "phones":
                    for _, row in df.iterrows():
                        ph = str(row.get("phone_number", ""))
                        if ph:
                            graph_manager.add_node(f"PH_{ph}", "Phone", {
                                "name": ph,
                                "carrier": str(row.get("carrier", "Unknown")),
                                "status": str(row.get("status", "Active"))
                            })
                            if "person_id" in row and pd.notna(row["person_id"]):
                                graph_manager.add_edge(str(row["person_id"]), f"PH_{ph}", "USES", {"role": "Owner"})

                elif dtype == "incidents":
                    for _, row in df.iterrows():
                        inc_id = str(row["incident_id"])
                        graph_manager.add_node(inc_id, "Incident", {
                            "name": str(row.get("title", inc_id)),
                            "severity": str(row.get("severity", "Medium")),
                            "timestamp": str(row.get("timestamp", ""))
                        })
                        inv_persons = row.get("involved_person_ids", [])
                        if isinstance(inv_persons, list):
                            for p in inv_persons:
                                graph_manager.add_edge(str(p), inc_id, "INVOLVED_IN", {})

                # Persist updated graph to disk
                graph_manager.save_to_disk()
                stats["nodes_created"] = graph_manager.nx_graph.number_of_nodes() - nodes_before
                stats["relationships_created"] = graph_manager.nx_graph.number_of_edges() - edges_before

            elif dtype == "text_report":
                # Save to data/reports/
                self.reports_dir.mkdir(parents=True, exist_ok=True)
                new_idx = len(list(self.reports_dir.glob("*.txt"))) + 1
                report_file = self.reports_dir / f"uploaded_report_{new_idx:03d}_{uploaded_file.name}"
                with open(report_file, "w", encoding="utf-8") as f:
                    f.write(parsed)
                stats["rows_accepted"] = 1
                stats["message"] = f"Report '{uploaded_file.name}' saved and indexed into intelligence store."

        except Exception as e:
            stats["errors"].append(str(e))
            stats["success"] = False

        return stats

