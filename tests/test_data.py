"""
Unit Tests for Data Loader, Cleaner, and Synthetic Datasets
"""

import pytest
import pandas as pd
from pathlib import Path
from src.data_cleaner import DataCleaner
from src.data_loader import DataLoader
from src.config import DATA_DIR

def test_data_cleaner_phone():
    assert DataCleaner.clean_phone_number("+91-98765-43210") == "9876543210"
    assert DataCleaner.clean_phone_number("09876543210") == "9876543210"
    assert DataCleaner.clean_phone_number("9876543210") == "9876543210"
    assert DataCleaner.clean_phone_number("") == "UNAVAILABLE"

def test_data_cleaner_vehicle():
    assert DataCleaner.clean_vehicle_plate("mh-12 ab 1234") == "MH12AB1234"
    assert DataCleaner.clean_vehicle_plate("DL 04 C 9988") == "DL04C9988"
    assert DataCleaner.clean_vehicle_plate("") == "UNKNOWN_PLATE"

def test_data_cleaner_amount():
    assert DataCleaner.clean_amount("₹ 45,000.00") == 45000.0
    assert DataCleaner.clean_amount("$ 1,250.50") == 1250.50
    assert DataCleaner.clean_amount(50000) == 50000.0
    assert DataCleaner.clean_amount(None) == 0.0

def test_synthetic_datasets_load():
    loader = DataLoader(DATA_DIR)
    datasets = loader.load_all_datasets()
    
    assert "persons" in datasets
    assert len(datasets["persons"]) >= 100
    assert "phones" in datasets
    assert len(datasets["phones"]) >= 50
    assert "vehicles" in datasets
    assert len(datasets["vehicles"]) >= 50
    assert "locations" in datasets
    assert len(datasets["locations"]) >= 30
    assert "transactions" in datasets
    assert len(datasets["transactions"]) >= 200
    assert "incidents" in datasets
    assert len(datasets["incidents"]) >= 100
    assert "reports" in datasets
    assert len(datasets["reports"]) >= 50

