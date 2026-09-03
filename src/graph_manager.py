"""
Dual-Backend Graph Database Manager
Supports local NetworkX in-memory and disk-persisted graph with full Neo4j integration.
Provides parameterized Cypher queries, 1-hop/2-hop ego-network traversals, global search,
and persistent disk backup.
"""

import json
import time
from pathlib import Path
import networkx as nx
import pandas as pd
from typing import Dict, List, Any, Optional, Set, Tuple, Union
from src.config import (
    GRAPH_BACKEND, NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD, NEO4J_DATABASE,
    DATA_DIR
)
from src.relationship_extractor import RelationshipExtractor

PERSISTENT_DIR = DATA_DIR / "persistent"
GRAPH_STORE_FILE = PERSISTENT_DIR / "graph_store.json"

class GraphManager:
    def __init__(self, backend: Optional[str] = None, auto_load: bool = True):
        self.requested_backend = (backend or GRAPH_BACKEND).lower()
        self.active_backend = "local"
        self.neo4j_driver = None
        self.nx_graph = nx.MultiDiGraph()
        self.relationship_extractor = RelationshipExtractor()
        self.node_lookup: Dict[str, Dict[str, Any]] = {}
        self.auto_load = auto_load

        PERSISTENT_DIR.mkdir(parents=True, exist_ok=True)
        self._initialize_backend()

    def _initialize_backend(self):
        """Initializes Neo4j connection if configured, otherwise sets Local mode."""
        if self.requested_backend == "neo4j":
            try:
                from neo4j import GraphDatabase
                self.neo4j_driver = GraphDatabase.driver(
                    NEO4J_URI,
                    auth=(NEO4J_USERNAME, NEO4J_PASSWORD)
                )
                # Verify connectivity
                with self.neo4j_driver.session(database=NEO4J_DATABASE) as session:
                    session.run("RETURN 1 AS test")
                self.active_backend = "neo4j"
                print(f"[GraphManager] Successfully connected to Neo4j at {NEO4J_URI}")
            except Exception as e:
                print(f"[GraphManager] Neo4j connection failed ({e}). Falling back to Local NetworkX mode.")
                self.active_backend = "local"
                self.neo4j_driver = None
        else:
            self.active_backend = "local"

        # Load persisted local graph if enabled
        if self.auto_load and self.nx_graph.number_of_nodes() == 0 and GRAPH_STORE_FILE.exists():
            self.load_from_disk()

    def get_all_nodes(self, label_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """Returns all nodes with attributes, optionally filtered by label."""
        nodes = []
        for nid, data in self.nx_graph.nodes(data=True):
            if label_filter and data.get("label") != label_filter:
                continue
            nd = dict(data)
            nd["id"] = nid
            nodes.append(nd)
        return nodes

    def get_all_edges(self) -> List[Dict[str, Any]]:
        """Returns all edges with attributes."""
        edges = []
        for u, v, k, data in self.nx_graph.edges(keys=True, data=True):
            ed = dict(data)
            ed["source"] = u
            ed["target"] = v
            ed["type"] = k
            edges.append(ed)
        return edges

    def is_neo4j_active(self) -> bool:
        return self.active_backend == "neo4j" and self.neo4j_driver is not None

    def test_connection(self) -> Tuple[bool, float, str]:
        """
        Tests Neo4j connectivity and measures round-trip latency in milliseconds.
        Returns (is_connected, latency_ms, message).
        """
        if not self.is_neo4j_active():
            # Try initializing temporary driver
            try:
                from neo4j import GraphDatabase
                t0 = time.time()
                driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
                with driver.session(database=NEO4J_DATABASE) as session:
                    result = session.run("RETURN 1 AS test").single()
                latency = round((time.time() - t0) * 1000, 2)
                driver.close()
                return True, latency, f"Neo4j is reachable ({latency}ms). Database: {NEO4J_DATABASE}"
            except Exception as e:
                return False, 0.0, str(e)
        else:
            try:
                t0 = time.time()
                with self.neo4j_driver.session(database=NEO4J_DATABASE) as session:
                    session.run("RETURN 1 AS test").single()
                latency = round((time.time() - t0) * 1000, 2)
                return True, latency, f"Connected to Neo4j ({latency}ms). Database: {NEO4J_DATABASE}"
            except Exception as e:
                return False, 0.0, str(e)

    def close(self):
        if self.neo4j_driver:
            try:
                self.neo4j_driver.close()
            except Exception:
                pass

    # -------------------------------------------------------------
    # Disk Persistence (Local Mode)
    # -------------------------------------------------------------
    def save_to_disk(self):
        """Serializes current graph state to persistent disk storage."""
        try:
            nodes_data = []
            for nid, data in self.nx_graph.nodes(data=True):
                nd = dict(data)
                nd["_id"] = nid
                nodes_data.append(nd)

            edges_data = []
            for u, v, k, data in self.nx_graph.edges(keys=True, data=True):
                ed = dict(data)
                ed["_source"] = u
                ed["_target"] = v
                ed["_key"] = k
                edges_data.append(ed)

            payload = {
                "nodes": nodes_data,
                "edges": edges_data,
                "saved_at": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            with open(GRAPH_STORE_FILE, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)
        except Exception as e:
            print(f"[GraphManager] Error saving graph to disk: {e}")

    def load_from_disk(self) -> bool:
        """Loads graph state from persistent disk storage."""
        if not GRAPH_STORE_FILE.exists():
            return False
        try:
            with open(GRAPH_STORE_FILE, "r", encoding="utf-8") as f:
                payload = json.load(f)

            self.nx_graph.clear()
            self.node_lookup.clear()

            for nd in payload.get("nodes", []):
                nid = nd.pop("_id")
                self.nx_graph.add_node(nid, **nd)
                self.node_lookup[nid] = nd

            for ed in payload.get("edges", []):
                u = ed.pop("_source")
                v = ed.pop("_target")
                k = ed.pop("_key", "RELATED_TO")
                self.nx_graph.add_edge(u, v, key=k, **ed)

            print(f"[GraphManager] Loaded persisted graph: {self.nx_graph.number_of_nodes()} nodes, {self.nx_graph.number_of_edges()} edges.")
            return True
        except Exception as e:
            print(f"[GraphManager] Error loading graph from disk: {e}")
            return False

    # -------------------------------------------------------------
    # Unified Node and Relationship CRUD Operations
    # -------------------------------------------------------------
    def add_node(self, node_id: str, label: str, properties: Optional[Dict[str, Any]] = None) -> bool:
        """Adds or updates a node with label and attributes."""
        if not node_id:
            return False

        props = properties or {}
        props["id"] = node_id
        props["label"] = label
        props["name"] = props.get("name", node_id)

        # Local NetworkX store
        self.nx_graph.add_node(node_id, **props)
        self.node_lookup[node_id] = props

        # Neo4j if active
        if self.is_neo4j_active():
            try:
                with self.neo4j_driver.session(database=NEO4J_DATABASE) as session:
                    cypher = f"""
                    MERGE (n:`{label}` {{id: $id}})
                    SET n += $props
                    """
                    session.run(cypher, id=node_id, props=props)
            except Exception as e:
                print(f"[GraphManager] Neo4j add_node error for {node_id}: {e}")

        return True

    def add_edge(self, source_id: str, target_id: str, rel_type: str, properties: Optional[Dict[str, Any]] = None) -> bool:
        """Adds or updates a directed edge with relation type and properties."""
        if not source_id or not target_id:
            return False

        props = properties or {}
        props["type"] = rel_type

        # Ensure both nodes exist in local graph
        if not self.nx_graph.has_node(source_id):
            self.add_node(source_id, "Entity", {"name": source_id})
        if not self.nx_graph.has_node(target_id):
            self.add_node(target_id, "Entity", {"name": target_id})

        # Local NetworkX store
        self.nx_graph.add_edge(source_id, target_id, key=rel_type, **props)

        # Neo4j if active
        if self.is_neo4j_active():
            try:
                with self.neo4j_driver.session(database=NEO4J_DATABASE) as session:
                    cypher = f"""
                    MATCH (a {{id: $source_id}}), (b {{id: $target_id}})
                    MERGE (a)-[r:`{rel_type}`]->(b)
                    SET r += $props
                    """
                    session.run(cypher, source_id=source_id, target_id=target_id, props=props)
            except Exception as e:
                print(f"[GraphManager] Neo4j add_edge error: {e}")

        return True

    def clear_graph(self):
        """Wipes the in-memory graph and clears Neo4j if active."""
        self.nx_graph.clear()
        self.node_lookup.clear()

        if GRAPH_STORE_FILE.exists():
            try:
                GRAPH_STORE_FILE.unlink()
            except Exception:
                pass

        if self.is_neo4j_active():
            try:
                with self.neo4j_driver.session(database=NEO4J_DATABASE) as session:
                    session.run("MATCH (n) DETACH DELETE n")
                print("[GraphManager] Neo4j database wiped clean.")
            except Exception as e:
                print(f"[GraphManager] Error clearing Neo4j: {e}")

    # -------------------------------------------------------------
    # Querying and Traversal
    # -------------------------------------------------------------
    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves node data by ID or fuzzy name match."""
        if node_id in self.node_lookup:
            return self.node_lookup[node_id]
        if self.nx_graph.has_node(node_id):
            return dict(self.nx_graph.nodes[node_id])
        
        # Fuzzy check on name
        for nid, data in self.node_lookup.items():
            if str(data.get("name", "")).lower() == str(node_id).lower():
                return data
        return None

    def search_nodes(self, query: str, label_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """Global search across node names, aliases, IDs, and labels."""
        results = []
        q = str(query).strip().lower()

        # If Neo4j is active, execute direct parameterized Cypher search
        if self.is_neo4j_active():
            try:
                with self.neo4j_driver.session(database=NEO4J_DATABASE) as session:
                    if label_filter and label_filter.lower() != "all":
                        cypher = f"""
                        MATCH (n:`{label_filter}`)
                        WHERE toLower(n.name) CONTAINS $q OR toLower(n.id) CONTAINS $q OR toLower(n.alias) CONTAINS $q
                        RETURN n, labels(n) AS labels LIMIT 100
                        """
                    else:
                        cypher = """
                        MATCH (n)
                        WHERE toLower(n.name) CONTAINS $q OR toLower(n.id) CONTAINS $q OR toLower(n.alias) CONTAINS $q
                        RETURN n, labels(n) AS labels LIMIT 100
                        """
                    records = session.run(cypher, q=q)
                    for rec in records:
                        node_props = dict(rec["n"])
                        node_props["label"] = rec["labels"][0] if rec["labels"] else "Entity"
                        results.append(node_props)
                if results:
                    return results
            except Exception as e:
                print(f"[GraphManager] Neo4j search error ({e}), falling back to local search.")

        # Local search fallback
        for nid, data in self.nx_graph.nodes(data=True):
            node_label = data.get("label", "Entity")
            if label_filter and label_filter.lower() != "all" and node_label.lower() != label_filter.lower():
                continue

            name = str(data.get("name", "")).lower()
            alias = str(data.get("alias", "")).lower()
            node_id = str(nid).lower()

            if not q or q in name or q in alias or q in node_id or q in node_label.lower():
                res_dict = dict(data)
                res_dict["id"] = nid
                results.append(res_dict)

        return results

    def get_1_hop_subgraph(self, center_node_id: str) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Retrieves 1-hop ego network: center node + direct neighbors and all connecting edges.
        Returns (nodes, edges).
        """
        if not self.nx_graph.has_node(center_node_id):
            # Check by name
            for nid, data in self.nx_graph.nodes(data=True):
                if str(data.get("name", "")).lower() == str(center_node_id).lower():
                    center_node_id = nid
                    break
            else:
                return [], []

        neighbors = set(self.nx_graph.predecessors(center_node_id)) | set(self.nx_graph.successors(center_node_id))
        sub_nodes_ids = {center_node_id} | neighbors

        nodes = []
        for nid in sub_nodes_ids:
            ndata = dict(self.nx_graph.nodes[nid])
            ndata["id"] = nid
            nodes.append(ndata)

        edges = []
        for u, v, k, edata in self.nx_graph.edges(keys=True, data=True):
            if u in sub_nodes_ids and v in sub_nodes_ids:
                e_entry = dict(edata)
                e_entry["source"] = u
                e_entry["target"] = v
                e_entry["type"] = k
                edges.append(e_entry)

        return nodes, edges

    def get_2_hop_subgraph(self, center_node_id: str) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Retrieves 2-hop ego network: center node + 1st & 2nd degree neighbors.
        Returns (nodes, edges).
        """
        if not self.nx_graph.has_node(center_node_id):
            for nid, data in self.nx_graph.nodes(data=True):
                if str(data.get("name", "")).lower() == str(center_node_id).lower():
                    center_node_id = nid
                    break
            else:
                return [], []

        # 1-Hop
        hop1 = set(self.nx_graph.predecessors(center_node_id)) | set(self.nx_graph.successors(center_node_id))
        
        # 2-Hop
        hop2 = set()
        for n1 in hop1:
            hop2 |= set(self.nx_graph.predecessors(n1)) | set(self.nx_graph.successors(n1))

        all_sub_ids = {center_node_id} | hop1 | hop2

        nodes = []
        for nid in all_sub_ids:
            ndata = dict(self.nx_graph.nodes[nid])
            ndata["id"] = nid
            nodes.append(ndata)

        edges = []
        for u, v, k, edata in self.nx_graph.edges(keys=True, data=True):
            if u in all_sub_ids and v in all_sub_ids:
                e_entry = dict(edata)
                e_entry["source"] = u
                e_entry["target"] = v
                e_entry["type"] = k
                edges.append(e_entry)

        return nodes, edges

    def get_connected_entities_for_person(self, person_id: str) -> Dict[str, List[str]]:
        """Retrieves structured lists of connected phones, vehicles, associates, locations for a person."""
        connections = {
            "phones": [],
            "vehicles": [],
            "associates": [],
            "organizations": [],
            "locations": [],
            "incidents": []
        }

        nodes, _ = self.get_1_hop_subgraph(person_id)
        for n in nodes:
            nid = n.get("id")
            if nid == person_id:
                continue

            lbl = n.get("label", "")
            name = n.get("name", nid)

            if lbl == "Phone":
                connections["phones"].append(name)
            elif lbl == "Vehicle":
                connections["vehicles"].append(name)
            elif lbl == "Person":
                connections["associates"].append(name)
            elif lbl == "Organization":
                connections["organizations"].append(name)
            elif lbl == "Location":
                connections["locations"].append(name)
            elif lbl == "Incident":
                connections["incidents"].append(name)

        return connections

    def get_graph_statistics(self) -> Dict[str, Any]:
        """Calculates live entity counts, relationship counts, and label distribution."""
        # If Neo4j is active, run live Cypher aggregation
        if self.is_neo4j_active():
            try:
                with self.neo4j_driver.session(database=NEO4J_DATABASE) as session:
                    n_count = session.run("MATCH (n) RETURN count(n) AS c").single()["c"]
                    r_count = session.run("MATCH ()-[r]->() RETURN count(r) AS c").single()["c"]
                    
                    label_counts = {}
                    for rec in session.run("MATCH (n) RETURN labels(n)[0] AS lbl, count(n) AS c"):
                        if rec["lbl"]:
                            label_counts[rec["lbl"]] = rec["c"]

                    type_counts = {}
                    for rec in session.run("MATCH ()-[r]->() RETURN type(r) AS t, count(r) AS c"):
                        if rec["t"]:
                            type_counts[rec["t"]] = rec["c"]

                    return {
                        "total_nodes": n_count,
                        "total_edges": r_count,
                        "node_counts": label_counts,
                        "edge_counts": type_counts,
                        "density": round(r_count / (n_count * (n_count - 1)) if n_count > 1 else 0.0, 5),
                        "backend": "neo4j"
                    }
            except Exception as e:
                print(f"[GraphManager] Neo4j stats query error ({e}), falling back to local stats.")

        # Local NetworkX stats
        node_counts: Dict[str, int] = {}
        for _, data in self.nx_graph.nodes(data=True):
            lbl = data.get("label", "Unknown")
            node_counts[lbl] = node_counts.get(lbl, 0) + 1

        edge_counts: Dict[str, int] = {}
        for _, _, k in self.nx_graph.edges(keys=True):
            edge_counts[k] = edge_counts.get(k, 0) + 1

        num_nodes = self.nx_graph.number_of_nodes()
        num_edges = self.nx_graph.number_of_edges()

        return {
            "total_nodes": num_nodes,
            "total_edges": num_edges,
            "node_counts": node_counts,
            "edge_counts": edge_counts,
            "density": round(nx.density(self.nx_graph), 5) if num_nodes > 1 else 0.0,
            "backend": "local"
        }

    # -------------------------------------------------------------
    # Batch Population from Loaded Datasets
    # -------------------------------------------------------------
    def build_from_datasets(self, datasets: Dict[str, Any]):
        """Populates graph from DataFrames and unstructured reports."""
        print(f"[GraphManager] Populating graph from loaded datasets using '{self.active_backend}' engine...")
        self.nx_graph.clear()
        self.node_lookup.clear()

        # 1. Add Persons
        persons_df = datasets.get("persons", pd.DataFrame())
        if not persons_df.empty:
            for _, row in persons_df.iterrows():
                p_id = str(row["person_id"])
                self.add_node(p_id, "Person", {
                    "name": str(row.get("name", p_id)),
                    "alias": str(row.get("alias", "None")),
                    "syndicate": str(row.get("syndicate", "Unaffiliated")),
                    "role": str(row.get("role", "Associate")),
                    "city": str(row.get("city", "Unknown")),
                    "primary_phone": str(row.get("primary_phone", "")),
                    "primary_vehicle": str(row.get("primary_vehicle", "")),
                    "status": str(row.get("status", "Normal")),
                    "is_suspect": bool(row.get("is_suspect", False))
                })

        # 2. Add Phones
        phones_df = datasets.get("phones", pd.DataFrame())
        if not phones_df.empty:
            for _, row in phones_df.iterrows():
                phone_num = str(row.get("phone_number", ""))
                if phone_num:
                    self.add_node(f"PH_{phone_num}", "Phone", {
                        "name": phone_num,
                        "carrier": str(row.get("carrier", "Unknown")),
                        "imei": str(row.get("imei", "")),
                        "is_burner": bool(row.get("is_burner", False)),
                        "status": str(row.get("status", "Active"))
                    })

        # 3. Add Vehicles
        vehicles_df = datasets.get("vehicles", pd.DataFrame())
        if not vehicles_df.empty:
            for _, row in vehicles_df.iterrows():
                plate = str(row.get("plate_number", ""))
                if plate:
                    self.add_node(f"VEH_{plate}", "Vehicle", {
                        "name": plate,
                        "model": str(row.get("model", "Unknown")),
                        "color": str(row.get("color", "Unknown")),
                        "vehicle_type": str(row.get("vehicle_type", "Automobile")),
                        "status": str(row.get("status", "Normal"))
                    })

        # 4. Add Locations
        loc_df = datasets.get("locations", pd.DataFrame())
        if not loc_df.empty:
            for _, row in loc_df.iterrows():
                loc_name = str(row.get("name", ""))
                if loc_name:
                    self.add_node(f"LOC_{loc_name.replace(' ', '_')}", "Location", {
                        "name": loc_name,
                        "city": str(row.get("city", "Unknown")),
                        "lat": float(row.get("lat", 0.0)),
                        "lon": float(row.get("lon", 0.0)),
                        "type": str(row.get("type", "Commercial"))
                    })

        # 5. Add Organizations
        org_df = datasets.get("organizations", pd.DataFrame())
        if not org_df.empty:
            for _, row in org_df.iterrows():
                org_name = str(row.get("name", ""))
                if org_name:
                    self.add_node(f"ORG_{org_name.replace(' ', '_')}", "Organization", {
                        "name": org_name,
                        "type": str(row.get("type", "Entity")),
                        "city": str(row.get("city", "Unknown"))
                    })

        # 6. Add Incidents
        inc_df = datasets.get("incidents", pd.DataFrame())
        if not inc_df.empty:
            for _, row in inc_df.iterrows():
                inc_id = str(row["incident_id"])
                self.add_node(inc_id, "Incident", {
                    "name": str(row.get("title", inc_id)),
                    "incident_type": str(row.get("incident_type", "Crime")),
                    "severity": str(row.get("severity", "Medium")),
                    "city": str(row.get("city", "")),
                    "timestamp": str(row.get("timestamp", ""))
                })

        # 7. Add Reports
        reports_list = datasets.get("reports", [])
        for rep in reports_list:
            r_id = rep.get("report_id", "REP-000")
            self.add_node(r_id, "Report", {
                "name": rep.get("filename", r_id),
                "filepath": rep.get("filepath", ""),
                "size_bytes": rep.get("size_bytes", 0)
            })

        # 8. Extract and add all structured relationships
        struct_rels = self.relationship_extractor.extract_structured_relationships(datasets)
        for rel in struct_rels:
            self.add_edge(
                source_id=rel["source_id"],
                target_id=rel["target_id"],
                rel_type=rel["relationship_type"],
                properties=rel.get("properties", {})
            )

        # 9. Extract and add unstructured text report links
        for rep in reports_list:
            rep_rels = self.relationship_extractor.extract_text_report_relationships(rep)
            for rel in rep_rels:
                self.add_edge(
                    source_id=rel["source_id"],
                    target_id=rel["target_id"],
                    rel_type=rel["relationship_type"],
                    properties=rel.get("properties", {})
                )

        # Save local copy to persistent disk
        self.save_to_disk()

        stats = self.get_graph_statistics()
        print(f"[GraphManager] Graph build complete: {stats['total_nodes']} nodes, {stats['total_edges']} edges.")
