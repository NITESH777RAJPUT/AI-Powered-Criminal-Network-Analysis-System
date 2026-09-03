"""
Data Cleaner and Sanitization Engine
Provides robust data normalization, schema validation, deduplication,
and flexible mapping for intelligence entities across arbitrary dataset schemas.
"""

import re
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional

class DataCleaner:
    @staticmethod
    def clean_name(name: Any) -> str:
        """Standardize person names (Title Case, stripped whitespace)."""
        if pd.isna(name) or not str(name).strip():
            return "Unknown Person"
        name_str = str(name).strip()
        name_str = re.sub(r'\s+', ' ', name_str)
        return name_str.title()

    @staticmethod
    def clean_phone_number(phone: Any) -> str:
        """
        Standardize phone numbers into 10-digit or clean format.
        Strips hyphens, spaces, country code prefixes where applicable.
        """
        if pd.isna(phone) or not str(phone).strip():
            return "UNAVAILABLE"
        raw = str(phone).strip()
        digits = re.sub(r'[^\d]', '', raw)
        
        if len(digits) == 12 and digits.startswith("91"):
            digits = digits[2:]
        elif len(digits) == 11 and digits.startswith("0"):
            digits = digits[1:]
            
        if len(digits) == 10:
            return digits
        elif len(digits) > 10:
            return digits[-10:]
        elif len(digits) >= 6:
            return digits
        return raw.upper()

    @staticmethod
    def clean_vehicle_plate(plate: Any) -> str:
        """
        Standardize vehicle license plates: uppercase, alphanumeric.
        E.g., 'mh-12 ad 0001' -> 'MH12AD0001'
        """
        if pd.isna(plate) or not str(plate).strip():
            return "UNKNOWN_PLATE"
        clean = re.sub(r'[^A-Za-z0-9]', '', str(plate)).upper()
        return clean if clean else "UNKNOWN_PLATE"

    @staticmethod
    def clean_amount(val: Any) -> float:
        """Extract float numeric value from string or numbers."""
        if pd.isna(val):
            return 0.0
        if isinstance(val, (int, float)):
            return float(val)
        val_str = str(val).strip()
        cleaned_str = re.sub(r'[^\d.]', '', val_str)
        try:
            return float(cleaned_str) if cleaned_str else 0.0
        except ValueError:
            return 0.0

    @staticmethod
    def clean_date_str(date_val: Any) -> str:
        """Standardize date strings to ISO YYYY-MM-DD HH:MM:SS format."""
        if pd.isna(date_val) or not str(date_val).strip():
            return "1970-01-01 00:00:00"
        try:
            dt = pd.to_datetime(date_val)
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            return str(date_val).strip()

    @classmethod
    def clean_persons_dataframe(cls, df: pd.DataFrame) -> pd.DataFrame:
        """Sanitize and standardize persons dataset with flexible column schemas."""
        if df.empty:
            return pd.DataFrame(columns=["person_id", "name", "alias", "syndicate", "role", "city", "primary_phone", "primary_vehicle", "status", "is_suspect"])

        df = df.copy()
        # Normalize column names to lowercase stripped
        df.columns = [str(c).strip().lower() for c in df.columns]

        # Map person_id
        if "person_id" not in df.columns:
            for cand in ["id", "p_id", "pid", "uid"]:
                if cand in df.columns:
                    df["person_id"] = df[cand]
                    break
            else:
                df["person_id"] = [f"PER-{i+1:03d}" for i in range(len(df))]

        df["person_id"] = df["person_id"].astype(str).str.strip()

        # Name
        name_col = next((c for c in ["name", "full_name", "person_name"] if c in df.columns), None)
        if name_col:
            df["name"] = df[name_col].apply(cls.clean_name)
        else:
            df["name"] = df["person_id"]

        # Alias
        alias_col = next((c for c in ["alias", "moniker", "nickname"] if c in df.columns), None)
        df["alias"] = df[alias_col].fillna("None").astype(str).str.strip() if alias_col else "None"

        # Syndicate
        synd_col = next((c for c in ["syndicate", "gang", "group", "organization", "org"] if c in df.columns), None)
        df["syndicate"] = df[synd_col].fillna("Unaffiliated").astype(str).str.strip() if synd_col else "Unaffiliated"

        # Role
        role_col = next((c for c in ["role", "designation", "position"] if c in df.columns), None)
        df["role"] = df[role_col].fillna("Associate").astype(str).str.strip() if role_col else "Associate"

        # City
        city_col = next((c for c in ["city", "location", "address", "state"] if c in df.columns), None)
        df["city"] = df[city_col].fillna("Unknown").astype(str).str.strip() if city_col else "Unknown"

        # Phone
        phone_col = next((c for c in ["primary_phone", "phone", "phone_number", "mobile"] if c in df.columns), None)
        if phone_col:
            df["primary_phone"] = df[phone_col].apply(cls.clean_phone_number)
        else:
            df["primary_phone"] = "UNAVAILABLE"

        # Vehicle
        veh_col = next((c for c in ["primary_vehicle", "vehicle", "plate_number", "registration_number"] if c in df.columns), None)
        if veh_col:
            df["primary_vehicle"] = df[veh_col].apply(cls.clean_vehicle_plate)
        else:
            df["primary_vehicle"] = "UNKNOWN_PLATE"

        # Status & is_suspect
        if "status" not in df.columns:
            df["status"] = "Normal"
        if "is_suspect" not in df.columns:
            df["is_suspect"] = False

        return df.drop_duplicates(subset=["person_id"]).reset_index(drop=True)

    @classmethod
    def clean_transactions_dataframe(cls, df: pd.DataFrame) -> pd.DataFrame:
        """Sanitize transactions dataset with flexible column schemas."""
        if df.empty:
            return pd.DataFrame(columns=["transaction_id", "sender_id", "sender_name", "receiver_id", "receiver_name", "amount", "currency", "timestamp", "channel", "pattern_flag", "is_suspicious"])

        df = df.copy()
        df.columns = [str(c).strip().lower() for c in df.columns]

        # Transaction ID
        if "transaction_id" not in df.columns:
            for cand in ["id", "tx_id", "txid"]:
                if cand in df.columns:
                    df["transaction_id"] = df[cand]
                    break
            else:
                df["transaction_id"] = [f"TX-{i+1:04d}" for i in range(len(df))]

        df["transaction_id"] = df["transaction_id"].astype(str).str.strip()

        # Sender & Receiver
        s_col = next((c for c in ["sender_id", "sender", "from_id", "from"] if c in df.columns), None)
        df["sender_id"] = df[s_col].astype(str).str.strip() if s_col else "UNKNOWN_SENDER"

        r_col = next((c for c in ["receiver_id", "receiver", "to_id", "to"] if c in df.columns), None)
        df["receiver_id"] = df[r_col].astype(str).str.strip() if r_col else "UNKNOWN_RECEIVER"

        # Amount
        amt_col = next((c for c in ["amount", "value", "amt", "total"] if c in df.columns), None)
        df["amount"] = df[amt_col].apply(cls.clean_amount) if amt_col else 0.0

        # Timestamp / Date
        time_col = next((c for c in ["timestamp", "date", "time", "datetime", "created_at"] if c in df.columns), None)
        df["timestamp"] = df[time_col].apply(cls.clean_date_str) if time_col else "1970-01-01 00:00:00"

        # Channel & Flags
        if "channel" not in df.columns:
            df["channel"] = "Wire"
        if "pattern_flag" not in df.columns:
            df["pattern_flag"] = "Normal"
        if "is_suspicious" not in df.columns:
            df["is_suspicious"] = False

        return df.drop_duplicates(subset=["transaction_id"]).reset_index(drop=True)

    @classmethod
    def clean_vehicles_dataframe(cls, df: pd.DataFrame) -> pd.DataFrame:
        """Sanitize vehicles dataset with flexible column schemas."""
        if df.empty:
            return pd.DataFrame(columns=["vehicle_id", "plate_number", "model", "color", "vehicle_type", "status", "person_id"])

        df = df.copy()
        df.columns = [str(c).strip().lower() for c in df.columns]

        if "vehicle_id" not in df.columns:
            for cand in ["id", "v_id", "vid"]:
                if cand in df.columns:
                    df["vehicle_id"] = df[cand]
                    break
            else:
                df["vehicle_id"] = [f"VEH-{i+1:03d}" for i in range(len(df))]

        df["vehicle_id"] = df["vehicle_id"].astype(str).str.strip()

        # Plate / Registration Number
        plate_col = next((c for c in ["plate_number", "registration_number", "license_plate", "plate", "vehicle_number"] if c in df.columns), None)
        if plate_col:
            df["plate_number"] = df[plate_col].apply(cls.clean_vehicle_plate)
        else:
            df["plate_number"] = df["vehicle_id"]

        if "model" not in df.columns:
            df["model"] = "Unknown Model"
        if "color" not in df.columns:
            df["color"] = "Unknown"
        if "vehicle_type" not in df.columns:
            df["vehicle_type"] = "Automobile"
        if "status" not in df.columns:
            df["status"] = "Normal"

        return df.drop_duplicates(subset=["vehicle_id"]).reset_index(drop=True)

    @classmethod
    def clean_phones_dataframe(cls, df: pd.DataFrame) -> pd.DataFrame:
        """Sanitize phone records dataset with flexible column schemas."""
        if df.empty:
            return pd.DataFrame(columns=["phone_id", "phone_number", "carrier", "imei", "is_burner", "status", "person_id"])

        df = df.copy()
        df.columns = [str(c).strip().lower() for c in df.columns]

        if "phone_id" not in df.columns:
            for cand in ["id", "ph_id", "phid"]:
                if cand in df.columns:
                    df["phone_id"] = df[cand]
                    break
            else:
                df["phone_id"] = [f"PH-{i+1:03d}" for i in range(len(df))]

        df["phone_id"] = df["phone_id"].astype(str).str.strip()

        phone_col = next((c for c in ["phone_number", "number", "mobile", "msisdn", "phone"] if c in df.columns), None)
        if phone_col:
            df["phone_number"] = df[phone_col].apply(cls.clean_phone_number)
        else:
            df["phone_number"] = df["phone_id"]

        if "carrier" not in df.columns:
            df["carrier"] = "Unknown"
        if "imei" not in df.columns:
            df["imei"] = ""
        if "is_burner" not in df.columns:
            df["is_burner"] = False
        if "status" not in df.columns:
            df["status"] = "Active"

        return df.drop_duplicates(subset=["phone_id"]).reset_index(drop=True)

    @classmethod
    def clean_locations_dataframe(cls, df: pd.DataFrame) -> pd.DataFrame:
        """Sanitize locations dataset."""
        if df.empty:
            return pd.DataFrame(columns=["location_id", "name", "city", "lat", "lon", "type"])

        df = df.copy()
        df.columns = [str(c).strip().lower() for c in df.columns]

        id_col = next((c for c in ["location_id", "id", "loc_id"] if c in df.columns), None)
        df["location_id"] = df[id_col].astype(str).str.strip() if id_col else [f"LOC-{i+1:03d}" for i in range(len(df))]

        name_col = next((c for c in ["location_name", "name", "title", "place"] if c in df.columns), None)
        df["name"] = df[name_col].astype(str).str.strip() if name_col else df["location_id"]

        if "city" not in df.columns:
            # Try to infer city from location_name (e.g. "Pune Central" -> "Pune")
            df["city"] = df["name"].apply(lambda x: str(x).split()[0] if str(x) else "Unknown")
        if "lat" not in df.columns:
            df["lat"] = 0.0
        if "lon" not in df.columns:
            df["lon"] = 0.0
        if "type" not in df.columns:
            df["type"] = "Location"

        return df.drop_duplicates(subset=["location_id"]).reset_index(drop=True)

    @classmethod
    def clean_incidents_dataframe(cls, df: pd.DataFrame) -> pd.DataFrame:
        """Sanitize incidents dataset."""
        if df.empty:
            return pd.DataFrame(columns=["incident_id", "title", "incident_type", "severity", "location_id", "city", "timestamp", "description", "involved_person_ids", "involved_person_names"])

        df = df.copy()
        df.columns = [str(c).strip().lower() for c in df.columns]

        id_col = next((c for c in ["incident_id", "id", "inc_id"] if c in df.columns), None)
        df["incident_id"] = df[id_col].astype(str).str.strip() if id_col else [f"INC-{i+1:03d}" for i in range(len(df))]

        name_col = next((c for c in ["title", "incident_name", "name", "description"] if c in df.columns), None)
        df["title"] = df[name_col].astype(str).str.strip() if name_col else df["incident_id"]

        if "incident_type" not in df.columns:
            df["incident_type"] = "Incident"
        if "severity" not in df.columns:
            df["severity"] = "Medium"
        if "location_id" not in df.columns:
            df["location_id"] = ""
        if "city" not in df.columns:
            df["city"] = "Unknown"

        time_col = next((c for c in ["timestamp", "date", "time", "datetime"] if c in df.columns), None)
        df["timestamp"] = df[time_col].apply(cls.clean_date_str) if time_col else "1970-01-01 00:00:00"

        if "description" not in df.columns:
            df["description"] = df["title"]

        # If person_id is present as a single column, wrap it into involved_person_ids list
        if "person_id" in df.columns and "involved_person_ids" not in df.columns:
            df["involved_person_ids"] = df["person_id"].apply(lambda x: [str(x).strip()] if pd.notna(x) else [])
        elif "involved_person_ids" not in df.columns:
            df["involved_person_ids"] = [[] for _ in range(len(df))]

        return df.drop_duplicates(subset=["incident_id"]).reset_index(drop=True)
