"""
Unit Tests for Dual-Backend Graph Manager and Traversal
"""

import pytest
import networkx as nx
from src.graph_manager import GraphManager
from src.data_loader import DataLoader
from src.config import DATA_DIR

def test_graph_manager_node_and_edge_crud():
    gm = GraphManager(backend="local", auto_load=False)
    assert gm.active_backend == "local"

    # Add nodes
    gm.add_node("P1", "Person", {"name": "Alice Smith", "role": "Suspect"})
    gm.add_node("PH1", "Phone", {"name": "9876543210"})
    gm.add_edge("P1", "PH1", "USES", {"status": "Active"})

    node = gm.get_node("P1")
    assert node is not None
    assert node["name"] == "Alice Smith"
    assert node["label"] == "Person"

    # Search
    search_res = gm.search_nodes("Alice")
    assert len(search_res) >= 1
    assert search_res[0]["id"] == "P1"

    # 1-Hop
    nodes_1h, edges_1h = gm.get_1_hop_subgraph("P1")
    assert len(nodes_1h) == 2
    assert len(edges_1h) == 1
    assert edges_1h[0]["type"] == "USES"

def test_graph_build_from_datasets():
    loader = DataLoader(DATA_DIR)
    datasets = loader.load_all_datasets()
    
    gm = GraphManager(backend="local")
    gm.build_from_datasets(datasets)

    stats = gm.get_graph_statistics()
    assert stats["total_nodes"] > 200
    assert stats["total_edges"] > 300
    assert "Person" in stats["node_counts"]
    assert "Phone" in stats["node_counts"]
    assert "Vehicle" in stats["node_counts"]

