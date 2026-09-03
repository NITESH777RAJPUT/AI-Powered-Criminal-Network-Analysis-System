// ================================================================
// AI-POWERED CRIMINAL NETWORK ANALYSIS SYSTEM — NEO4J GRAPH SCHEMA
// Constraints, Indexes, and Node/Relationship Definitions
// ================================================================

// 1. UNIQUE NODE CONSTRAINTS
CREATE CONSTRAINT person_id_unique IF NOT EXISTS
FOR (p:Person) REQUIRE p.id IS UNIQUE;

CREATE CONSTRAINT phone_id_unique IF NOT EXISTS
FOR (ph:Phone) REQUIRE ph.id IS UNIQUE;

CREATE CONSTRAINT vehicle_id_unique IF NOT EXISTS
FOR (v:Vehicle) REQUIRE v.id IS UNIQUE;

CREATE CONSTRAINT location_id_unique IF NOT EXISTS
FOR (l:Location) REQUIRE l.id IS UNIQUE;

CREATE CONSTRAINT organization_id_unique IF NOT EXISTS
FOR (o:Organization) REQUIRE o.id IS UNIQUE;

CREATE CONSTRAINT incident_id_unique IF NOT EXISTS
FOR (i:Incident) REQUIRE i.id IS UNIQUE;

CREATE CONSTRAINT report_id_unique IF NOT EXISTS
FOR (r:Report) REQUIRE r.id IS UNIQUE;

CREATE CONSTRAINT transaction_id_unique IF NOT EXISTS
FOR (t:Transaction) REQUIRE t.id IS UNIQUE;

// 2. SEARCH & TRAVERSAL INDEXES
CREATE INDEX person_name_idx IF NOT EXISTS
FOR (p:Person) ON (p.name);

CREATE INDEX person_alias_idx IF NOT EXISTS
FOR (p:Person) ON (p.alias);

CREATE INDEX phone_number_idx IF NOT EXISTS
FOR (ph:Phone) ON (ph.name);

CREATE INDEX vehicle_plate_idx IF NOT EXISTS
FOR (v:Vehicle) ON (v.name);

CREATE INDEX location_name_idx IF NOT EXISTS
FOR (l:Location) ON (l.name);

CREATE INDEX incident_timestamp_idx IF NOT EXISTS
FOR (i:Incident) ON (i.timestamp);

CREATE INDEX transaction_amount_idx IF NOT EXISTS
FOR ()-[r:TRANSFERRED]-() ON (r.amount);

