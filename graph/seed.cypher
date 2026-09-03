// ================================================================
// AI-POWERED CRIMINAL NETWORK ANALYSIS SYSTEM — NEO4J SEED SCRIPT
// Core Synthetic Syndicates and Key Nodes Initialization
// ================================================================

// 1. Create Core Persons
MERGE (p1:Person {id: 'PER-001', name: 'Rahul Verma', alias: 'Hawk', syndicate: 'Northside Logistics Syndicate', role: 'Kingpin / Orchestrator', city: 'Pune', status: 'High Priority Suspect'});
MERGE (p2:Person {id: 'PER-002', name: 'Amit Deshmukh', alias: 'Shadow', syndicate: 'Northside Logistics Syndicate', role: 'Logistics Coordinator', city: 'Pune', status: 'High Priority Suspect'});
MERGE (p3:Person {id: 'PER-003', name: 'Vikram Malhotra', alias: 'Slick', syndicate: 'Northside Logistics Syndicate', role: 'Field Enforcer', city: 'Mumbai', status: 'High Priority Suspect'});
MERGE (p4:Person {id: 'PER-004', name: 'Suresh Singhania', alias: 'Banker', syndicate: 'Apex Global Financial Ring', role: 'Financial Broker', city: 'Mumbai', status: 'High Priority Suspect'});
MERGE (p5:Person {id: 'PER-005', name: 'Pooja Mehta', alias: 'Accountant', syndicate: 'Apex Global Financial Ring', role: 'Financial Broker', city: 'Delhi', status: 'High Priority Suspect'});
MERGE (p6:Person {id: 'PER-006', name: 'Rohan Kapoor', alias: 'Broker', syndicate: 'Apex Global Financial Ring', role: 'Front Businessman', city: 'Mumbai', status: 'High Priority Suspect'});
MERGE (p7:Person {id: 'PER-007', name: "Karan D'Souza", alias: 'Captain', syndicate: 'Coastal Freight & Smuggling Cell', role: 'Kingpin / Orchestrator', city: 'Goa', status: 'High Priority Suspect'});
MERGE (p8:Person {id: 'PER-008', name: 'Devendra Patel', alias: 'Fixer', syndicate: 'Independent Syndicate Operative', role: 'Bridge Broker', city: 'Ahmedabad', status: 'High Priority Suspect'});

// 2. Create Shared Identifiers & Devices
MERGE (ph1:Phone {id: 'PH_9800000001', name: '9800000001', carrier: 'Airtel', is_burner: true, status: 'Active'});
MERGE (ph2:Phone {id: 'PH_9700000002', name: '9700000002', carrier: 'Satellite Encrypted', is_burner: true, status: 'Active'});
MERGE (v1:Vehicle {id: 'VEH_MH02AA1173', name: 'MH02AA1173', model: 'Mahindra Scorpio', color: 'Black', status: 'Flagged'});
MERGE (v2:Vehicle {id: 'VEH_DL03BA1346', name: 'DL03BA1346', model: 'Toyota Fortuner', color: 'Silver', status: 'Flagged'});

// 3. Create Locations & Organizations
MERGE (loc1:Location {id: 'LOC_Pune_Railway_Station_Cargo_Hub', name: 'Pune Railway Station Cargo Hub', city: 'Pune', lat: 18.5284, lon: 73.8743});
MERGE (loc2:Location {id: 'LOC_Nhava_Sheva_Container_Terminal', name: 'Nhava Sheva Container Terminal', city: 'Mumbai', lat: 18.9496, lon: 72.9515});
MERGE (org1:Organization {id: 'ORG_Northside_Logistics_Syndicate', name: 'Northside Logistics Syndicate', type: 'Criminal Syndicate', city: 'Pune'});
MERGE (org2:Organization {id: 'ORG_Apex_Global_Financial_Ring', name: 'Apex Global Financial Ring', type: 'Money Laundering Front', city: 'Mumbai'});

// 4. Create Relationships
MERGE (p1)-[:USES {role: 'Primary Contact'}]->(ph1);
MERGE (p2)-[:USES {role: 'Shared Burner'}]->(ph1);
MERGE (p1)-[:USES {role: 'Getaway Vehicle'}]->(v1);
MERGE (p3)-[:USES {role: 'Secondary User'}]->(v1);

MERGE (p1)-[:ASSOCIATED_WITH {role: 'Leader'}]->(org1);
MERGE (p4)-[:ASSOCIATED_WITH {role: 'Financial Controller'}]->(org2);

MERGE (p8)-[:KNOWS {context: 'Broker Channel'}]->(p1);
MERGE (p8)-[:KNOWS {context: 'Hawala Settlement'}]->(p4);
MERGE (p8)-[:KNOWS {context: 'Maritime Logistics'}]->(p7);

MERGE (p4)-[:TRANSFERRED {transaction_id: 'TX-SMURF-001', amount: 49500.0, channel: 'Structured Wire', is_suspicious: true}]->(p1);
MERGE (p8)-[:TRANSFERRED {transaction_id: 'TX-HAWALA-001', amount: 2500000.0, channel: 'Offshore Token', is_suspicious: true}]->(p4);

