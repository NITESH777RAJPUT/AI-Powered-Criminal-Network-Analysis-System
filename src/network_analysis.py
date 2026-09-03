"""
Network Analytics Engine
Computes graph centrality metrics (Degree, Betweenness, Closeness, PageRank, Eigenvector),
community detection clustering (Louvain / Greedy Modularity), and bridge node identification.
"""

import networkx as nx
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple

class NetworkAnalysisEngine:
    def __init__(self, nx_graph: nx.MultiDiGraph):
        self.raw_graph = nx_graph
        # Convert to simple undirected graph for community detection & normalized algorithms
        self.undirected_graph = nx.Graph()
        self._build_undirected_representation()

    def _build_undirected_representation(self):
        """Builds an undirected simplified graph with edge weights representing connection frequency."""
        for u, v, data in self.raw_graph.edges(data=True):
            if self.undirected_graph.has_edge(u, v):
                self.undirected_graph[u][v]["weight"] += 1.0
            else:
                self.undirected_graph.add_edge(u, v, weight=1.0)

        # Ensure all isolated nodes are also included
        for n, data in self.raw_graph.nodes(data=True):
            if not self.undirected_graph.has_node(n):
                self.undirected_graph.add_node(n, **data)

    def calculate_centralities(self) -> Dict[str, Dict[str, float]]:
        """
        Calculates all standard centrality metrics for all nodes in the network:
        - Degree Centrality
        - Betweenness Centrality
        - PageRank
        - Closeness Centrality
        - Eigenvector Centrality
        """
        if len(self.raw_graph) == 0:
            return {}

        # 1. Degree Centrality
        deg_centrality = nx.degree_centrality(self.raw_graph)

        # 2. Betweenness Centrality (identifies brokers / bridges)
        try:
            between_centrality = nx.betweenness_centrality(self.raw_graph, normalized=True)
        except Exception:
            between_centrality = {n: 0.0 for n in self.raw_graph.nodes()}

        # 3. PageRank (influential orchestrators)
        try:
            pagerank_centrality = nx.pagerank(self.raw_graph, alpha=0.85, max_iter=200)
        except Exception:
            pagerank_centrality = {n: 1.0 / len(self.raw_graph) for n in self.raw_graph.nodes()}

        # 4. Closeness Centrality
        try:
            closeness_centrality = nx.closeness_centrality(self.raw_graph)
        except Exception:
            closeness_centrality = {n: 0.0 for n in self.raw_graph.nodes()}

        # 5. Eigenvector Centrality
        try:
            eigen_centrality = nx.eigenvector_centrality(self.undirected_graph, max_iter=300)
        except Exception:
            eigen_centrality = {n: 0.0 for n in self.raw_graph.nodes()}

        # Combine into unified dictionary
        centrality_map = {}
        for node_id in self.raw_graph.nodes():
            centrality_map[node_id] = {
                "degree": deg_centrality.get(node_id, 0.0),
                "betweenness": between_centrality.get(node_id, 0.0),
                "pagerank": pagerank_centrality.get(node_id, 0.0),
                "closeness": closeness_centrality.get(node_id, 0.0),
                "eigenvector": eigen_centrality.get(node_id, 0.0),
                "raw_degree": self.raw_graph.degree(node_id)
            }

        return centrality_map

    def detect_communities(self) -> Dict[str, int]:
        """
        Detects distinct sub-clusters / criminal syndicates using Modularity / Louvain community partitioning.
        Returns a mapping of node_id -> community_id (int).
        """
        if len(self.undirected_graph) == 0:
            return {}

        community_map = {}
        try:
            import networkx.algorithms.community as nx_comm
            # Greedy modularity optimization for robust community clustering
            communities = nx_comm.greedy_modularity_communities(self.undirected_graph)
            for comm_id, member_set in enumerate(communities):
                for node_id in member_set:
                    community_map[node_id] = comm_id + 1
        except Exception as e:
            print(f"[NetworkAnalysisEngine] Community detection fallback: {e}")
            # Fallback: connected components
            for comm_id, comp in enumerate(nx.connected_components(self.undirected_graph)):
                for node_id in comp:
                    community_map[node_id] = comm_id + 1

        return community_map

    def find_bridge_nodes(self) -> List[str]:
        """Identifies articulation points (critical single points of failure / brokers)."""
        if len(self.undirected_graph) < 3:
            return []
        try:
            return list(nx.articulation_points(self.undirected_graph))
        except Exception:
            return []

    def get_influential_persons_leaderboard(self, top_n: int = 25) -> pd.DataFrame:
        """
        Generates a ranked leaderboard of individuals based on network importance metrics.
        Filters for Person nodes and calculates composite network rank.
        """
        centralities = self.calculate_centralities()
        communities = self.detect_communities()
        bridge_nodes = set(self.find_bridge_nodes())

        records = []
        for nid, data in self.raw_graph.nodes(data=True):
            label = data.get("label", "")
            if label.lower() == "person" or str(nid).startswith("PER"):
                c = centralities.get(nid, {})
                comm_id = communities.get(nid, 0)
                is_bridge = nid in bridge_nodes

                records.append({
                    "person_id": nid,
                    "name": data.get("name", nid),
                    "alias": data.get("alias", "None"),
                    "syndicate": data.get("syndicate", "Unaffiliated"),
                    "role": data.get("role", "Associate"),
                    "raw_degree": c.get("raw_degree", 0),
                    "degree_centrality": round(c.get("degree", 0.0), 4),
                    "betweenness_centrality": round(c.get("betweenness", 0.0), 4),
                    "pagerank": round(c.get("pagerank", 0.0), 4),
                    "closeness": round(c.get("closeness", 0.0), 4),
                    "community_id": f"Cluster {comm_id}",
                    "is_bridge": is_bridge
                })

        if not records:
            return pd.DataFrame()

        df = pd.DataFrame(records)
        # Sort by composite centrality (Betweenness + PageRank + Degree)
        df["composite_influence"] = (
            df["betweenness_centrality"] * 0.45 +
            df["pagerank"] * 0.35 +
            df["degree_centrality"] * 0.20
        )
        df = df.sort_values(by="composite_influence", ascending=False).reset_index(drop=True)
        df.insert(0, "Rank", df.index + 1)
        return df.head(top_n)

