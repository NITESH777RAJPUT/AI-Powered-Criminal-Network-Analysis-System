"""
Relationship Extractor Engine
Extracts semantic relationships between intelligence entities from structured tables
and co-occurrence graph extraction in unstructured text reports.
"""

import json
import pandas as pd
from typing import Dict, List, Any, Set, Tuple
from src.entity_extractor import EntityExtractor

class RelationshipExtractor:
    def __init__(self):
        self.entity_extractor = EntityExtractor()

    def extract_structured_relationships(self, datasets: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extracts verified relationships from structured datasets:
        - USES (Person -> Phone, Person -> Vehicle)
        - TRANSFERRED (Person -> Person)
        - ASSOCIATED_WITH (Person -> Organization)
        - INVOLVED_IN (Person -> Incident)
        - VISITED / LOCATED_AT (Incident/Person -> Location)
        - KNOWS (Person -> Person inferred from shared group/incident)
        """
        relationships = []

        # 1. Person -> Phone and Person -> Vehicle (USES)
        persons_df = datasets.get("persons", pd.DataFrame())
        if not persons_df.empty:
            for _, row in persons_df.iterrows():
                p_id = str(row["person_id"])
                p_name = str(row.get("name", p_id))

                # Primary Phone
                phone = str(row.get("primary_phone", ""))
                if phone and phone != "UNAVAILABLE":
                    relationships.append({
                        "source_id": p_id,
                        "source_name": p_name,
                        "source_type": "Person",
                        "target_id": f"PH_{phone}",
                        "target_name": phone,
                        "target_type": "Phone",
                        "relationship_type": "USES",
                        "properties": {"role": "Primary Contact", "status": "Active"}
                    })

                # Primary Vehicle
                veh = str(row.get("primary_vehicle", ""))
                if veh and veh != "UNKNOWN_PLATE":
                    relationships.append({
                        "source_id": p_id,
                        "source_name": p_name,
                        "source_type": "Person",
                        "target_id": f"VEH_{veh}",
                        "target_name": veh,
                        "target_type": "Vehicle",
                        "relationship_type": "USES",
                        "properties": {"role": "Primary Vehicle", "status": "Active"}
                    })

                # Syndicate / Organization affiliation
                synd = str(row.get("syndicate", ""))
                if synd and synd != "Unaffiliated" and synd != "Civilian / Unaffiliated":
                    relationships.append({
                        "source_id": p_id,
                        "source_name": p_name,
                        "source_type": "Person",
                        "target_id": f"ORG_{synd.replace(' ', '_')}",
                        "target_name": synd,
                        "target_type": "Organization",
                        "relationship_type": "ASSOCIATED_WITH",
                        "properties": {"role": str(row.get("role", "Member"))}
                    })

        # Direct Foreign Keys in Phones dataset (person_id)
        phones_df = datasets.get("phones", pd.DataFrame())
        if not phones_df.empty and "person_id" in phones_df.columns:
            for _, row in phones_df.iterrows():
                p_id = str(row["person_id"]).strip()
                phone = str(row.get("phone_number", "")).strip()
                if p_id and phone and phone != "UNAVAILABLE":
                    relationships.append({
                        "source_id": p_id,
                        "source_name": p_id,
                        "source_type": "Person",
                        "target_id": f"PH_{phone}",
                        "target_name": phone,
                        "target_type": "Phone",
                        "relationship_type": "USES",
                        "properties": {"role": "Assigned Terminal", "status": str(row.get("status", "Active"))}
                    })

        # Direct Foreign Keys in Vehicles dataset (person_id)
        vehicles_df = datasets.get("vehicles", pd.DataFrame())
        if not vehicles_df.empty and "person_id" in vehicles_df.columns:
            for _, row in vehicles_df.iterrows():
                p_id = str(row["person_id"]).strip()
                plate = str(row.get("plate_number", "")).strip()
                if p_id and plate and plate != "UNKNOWN_PLATE":
                    relationships.append({
                        "source_id": p_id,
                        "source_name": p_id,
                        "source_type": "Person",
                        "target_id": f"VEH_{plate}",
                        "target_name": plate,
                        "target_type": "Vehicle",
                        "relationship_type": "USES",
                        "properties": {"role": "Registered Owner", "status": str(row.get("status", "Normal"))}
                    })

        # 2. Financial Transactions (TRANSFERRED)
        tx_df = datasets.get("transactions", pd.DataFrame())
        if not tx_df.empty:
            for _, row in tx_df.iterrows():
                s_id = str(row["sender_id"])
                r_id = str(row["receiver_id"])
                s_name = str(row.get("sender_name", s_id))
                r_name = str(row.get("receiver_name", r_id))
                amt = float(row.get("amount", 0.0))
                time_val = str(row.get("timestamp", ""))
                flag = str(row.get("pattern_flag", "Normal"))

                relationships.append({
                    "source_id": s_id,
                    "source_name": s_name,
                    "source_type": "Person",
                    "target_id": r_id,
                    "target_name": r_name,
                    "target_type": "Person",
                    "relationship_type": "TRANSFERRED",
                    "properties": {
                        "transaction_id": str(row.get("transaction_id", "")),
                        "amount": amt,
                        "timestamp": time_val,
                        "channel": str(row.get("channel", "Wire")),
                        "pattern_flag": flag,
                        "is_suspicious": bool(row.get("is_suspicious", False))
                    }
                })

        # 3. Incidents (INVOLVED_IN & VISITED)
        inc_df = datasets.get("incidents", pd.DataFrame())
        if not inc_df.empty:
            for _, row in inc_df.iterrows():
                inc_id = str(row["incident_id"])
                inc_title = str(row.get("title", inc_id))
                loc_id = str(row.get("location_id", ""))
                loc_name = str(row.get("location_name", "Unknown Location"))
                sev = str(row.get("severity", "Medium"))

                # Location relationship
                if loc_name:
                    relationships.append({
                        "source_id": inc_id,
                        "source_name": inc_title,
                        "source_type": "Incident",
                        "target_id": f"LOC_{loc_name.replace(' ', '_')}",
                        "target_name": loc_name,
                        "target_type": "Location",
                        "relationship_type": "LOCATED_AT",
                        "properties": {"city": str(row.get("city", ""))}
                    })

                # Involved Persons
                raw_inv = row.get("involved_person_ids", "[]")
                inv_list = []
                if isinstance(raw_inv, str):
                    try:
                        inv_list = json.loads(raw_inv)
                    except Exception:
                        inv_list = [p.strip() for p in raw_inv.split(",") if p.strip()]
                elif isinstance(raw_inv, list):
                    inv_list = raw_inv

                for p_id in inv_list:
                    relationships.append({
                        "source_id": p_id,
                        "source_name": p_id,
                        "source_type": "Person",
                        "target_id": inc_id,
                        "target_name": inc_title,
                        "target_type": "Incident",
                        "relationship_type": "INVOLVED_IN",
                        "properties": {"severity": sev}
                    })

                # Inferred KNOWS among co-suspects in same incident
                if len(inv_list) > 1:
                    for i in range(len(inv_list)):
                        for j in range(i + 1, len(inv_list)):
                            relationships.append({
                                "source_id": inv_list[i],
                                "source_name": inv_list[i],
                                "source_type": "Person",
                                "target_id": inv_list[j],
                                "target_name": inv_list[j],
                                "target_type": "Person",
                                "relationship_type": "KNOWS",
                                "properties": {"context": f"Co-accused in {inc_title}"}
                            })

        return relationships

    def extract_text_report_relationships(self, report_item: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extracts semantic MENTIONED_IN and CONNECTED_TO links from a text report document.
        """
        relationships = []
        rep_id = report_item.get("report_id", "REP-UNKNOWN")
        rep_title = report_item.get("filename", "Intelligence Bulletin")
        content = report_item.get("content", "")

        extracted = self.entity_extractor.extract_entities_from_text(content)

        # 1. Connect all extracted entities to the Report node (MENTIONED_IN)
        for person_name in extracted.get("PERSON", []):
            relationships.append({
                "source_id": f"PER_NAME_{person_name.replace(' ', '_')}",
                "source_name": person_name,
                "source_type": "Person",
                "target_id": rep_id,
                "target_name": rep_title,
                "target_type": "Report",
                "relationship_type": "MENTIONED_IN",
                "properties": {"context": "Mentioned in intelligence report"}
            })

        for phone in extracted.get("PHONE", []):
            relationships.append({
                "source_id": f"PH_{phone}",
                "source_name": phone,
                "source_type": "Phone",
                "target_id": rep_id,
                "target_name": rep_title,
                "target_type": "Report",
                "relationship_type": "MENTIONED_IN",
                "properties": {"context": "Intercepted in bulletin"}
            })

        for veh in extracted.get("VEHICLE", []):
            relationships.append({
                "source_id": f"VEH_{veh}",
                "source_name": veh,
                "source_type": "Vehicle",
                "target_id": rep_id,
                "target_name": rep_title,
                "target_type": "Report",
                "relationship_type": "MENTIONED_IN",
                "properties": {"context": "Sighted in field report"}
            })

        for loc in extracted.get("LOCATION", []):
            relationships.append({
                "source_id": f"LOC_{loc.replace(' ', '_')}",
                "source_name": loc,
                "source_type": "Location",
                "target_id": rep_id,
                "target_name": rep_title,
                "target_type": "Report",
                "relationship_type": "MENTIONED_IN",
                "properties": {"context": "Operational site in report"}
            })

        # 2. Extract co-occurrence pairs between persons mentioned together in the same report
        persons = extracted.get("PERSON", [])
        if len(persons) > 1:
            for i in range(len(persons)):
                for j in range(i + 1, len(persons)):
                    relationships.append({
                        "source_id": f"PER_NAME_{persons[i].replace(' ', '_')}",
                        "source_name": persons[i],
                        "source_type": "Person",
                        "target_id": f"PER_NAME_{persons[j].replace(' ', '_')}",
                        "target_name": persons[j],
                        "target_type": "Person",
                        "relationship_type": "CONNECTED_TO",
                        "properties": {"context": f"Co-mentioned in {rep_title}"}
                    })

        return relationships

    def commit_nlp_extraction_to_graph(
        self,
        extracted: Dict[str, List[str]],
        report_title: str,
        graph_manager: Any
    ) -> Dict[str, Any]:
        """
        Commits extracted NLP entities and co-occurrences directly into the Graph Database.
        Creates Person, Phone, Vehicle, Location, Organization nodes, Report node,
        and links them via MENTIONED_IN, CONNECTED_TO, and USES edges.
        """
        nodes_before = graph_manager.nx_graph.number_of_nodes()
        edges_before = graph_manager.nx_graph.number_of_edges()

        # Create Report Node
        import hashlib
        rep_id = f"REP_{hashlib.md5(report_title.encode('utf-8')).hexdigest()[:8]}"
        graph_manager.add_node(rep_id, "Report", {
            "name": report_title,
            "entity_count": sum(len(v) for v in extracted.values())
        })

        # Add Persons
        person_node_ids = []
        for p in extracted.get("PERSON", []):
            p_id = f"PER_{p.replace(' ', '_')}"
            graph_manager.add_node(p_id, "Person", {
                "name": p,
                "alias": "Extracted Subject",
                "status": "Under Review"
            })
            graph_manager.add_edge(p_id, rep_id, "MENTIONED_IN", {"context": f"Mentioned in {report_title}"})
            person_node_ids.append(p_id)

        # Add Phones
        for ph in extracted.get("PHONE", []):
            ph_id = f"PH_{ph}"
            graph_manager.add_node(ph_id, "Phone", {"name": ph, "status": "Active"})
            graph_manager.add_edge(ph_id, rep_id, "MENTIONED_IN", {"context": "Intercepted number"})
            # Link to first person if available
            if person_node_ids:
                graph_manager.add_edge(person_node_ids[0], ph_id, "USES", {"context": "Associated in report"})

        # Add Vehicles
        for vh in extracted.get("VEHICLE", []):
            vh_id = f"VEH_{vh}"
            graph_manager.add_node(vh_id, "Vehicle", {"name": vh, "status": "Sighted"})
            graph_manager.add_edge(vh_id, rep_id, "MENTIONED_IN", {"context": "Spotted vehicle"})
            if person_node_ids:
                graph_manager.add_edge(person_node_ids[0], vh_id, "USES", {"context": "Driven/sighted with"})

        # Add Locations
        for loc in extracted.get("LOCATION", []):
            loc_id = f"LOC_{loc.replace(' ', '_')}"
            graph_manager.add_node(loc_id, "Location", {"name": loc})
            graph_manager.add_edge(loc_id, rep_id, "MENTIONED_IN", {"context": "Meeting/sighting location"})
            for p_id in person_node_ids:
                graph_manager.add_edge(p_id, loc_id, "VISITED", {"context": "Present at location"})

        # Add Organizations
        for org in extracted.get("ORGANIZATION", []):
            org_id = f"ORG_{org.replace(' ', '_')}"
            graph_manager.add_node(org_id, "Organization", {"name": org})
            graph_manager.add_edge(org_id, rep_id, "MENTIONED_IN", {})
            for p_id in person_node_ids:
                graph_manager.add_edge(p_id, org_id, "ASSOCIATED_WITH", {})

        # Co-occurrence links among persons
        if len(person_node_ids) > 1:
            for i in range(len(person_node_ids)):
                for j in range(i + 1, len(person_node_ids)):
                    graph_manager.add_edge(
                        person_node_ids[i],
                        person_node_ids[j],
                        "CONNECTED_TO",
                        {"context": f"Co-mentioned in {report_title}"}
                    )

        graph_manager.save_to_disk()

        nodes_created = graph_manager.nx_graph.number_of_nodes() - nodes_before
        edges_created = graph_manager.nx_graph.number_of_edges() - edges_before

        return {
            "report_id": rep_id,
            "nodes_created": nodes_created,
            "edges_created": edges_created,
            "total_nodes": graph_manager.nx_graph.number_of_nodes(),
            "total_edges": graph_manager.nx_graph.number_of_edges()
        }

