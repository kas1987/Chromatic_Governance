#!/usr/bin/env python3
"""
taxonomy_sync.py — Synchronize skill and provider taxonomy to SQLite database

Reads skill/provider metadata from workspace and builds a queryable taxonomy graph.
Output: taxonomy.db (SQLite) with nodes (11) and edges (5) documented in schema.

Usage:
    python taxonomy_sync.py
    python taxonomy_sync.py --export json
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

# Configuration
WORKSPACE_ROOT = Path(__file__).parent
DB_PATH = WORKSPACE_ROOT / "taxonomy.db"

# Taxonomy schema: skills and providers form a directed graph
TAXONOMY_NODES = [
    # Skills (11 total)
    {"id": "skill-orchestration", "type": "skill", "name": "Orchestration", "tier": "T2"},
    {"id": "skill-validation", "type": "skill", "name": "Validation", "tier": "T1"},
    {"id": "skill-routing", "type": "skill", "name": "Provider Routing", "tier": "T1"},
    {"id": "skill-dispatch", "type": "skill", "name": "Dispatch", "tier": "T2"},
    {"id": "skill-governance", "type": "skill", "name": "Governance", "tier": "T3"},
    {"id": "skill-safety", "type": "skill", "name": "Multi-Session Safety", "tier": "T2"},
    {"id": "skill-audit", "type": "skill", "name": "Audit", "tier": "T1"},
    {"id": "provider-ollama", "type": "provider", "name": "Ollama (T0)", "tier": "T0"},
    {"id": "provider-featherless", "type": "provider", "name": "Featherless (T1)", "tier": "T1"},
    {"id": "provider-gemini", "type": "provider", "name": "Gemini (T3)", "tier": "T3"},
    {"id": "provider-anthropic", "type": "provider", "name": "Anthropic (T4)", "tier": "T4"},
]

# Edges define relationships: depends_on, routes_to, uses, implements
TAXONOMY_EDGES = [
    # Skills depend on providers
    {"source": "skill-routing", "target": "provider-ollama", "relation": "routes_to"},
    {"source": "skill-routing", "target": "provider-featherless", "relation": "routes_to"},
    {"source": "skill-routing", "target": "provider-gemini", "relation": "routes_to"},
    # Orchestration uses dispatch
    {"source": "skill-orchestration", "target": "skill-dispatch", "relation": "uses"},
    # Safety depends on audit
    {"source": "skill-safety", "target": "skill-audit", "relation": "depends_on"},
]

def init_database() -> sqlite3.Connection:
    """Initialize SQLite database with taxonomy schema."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Nodes table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS nodes (
            id TEXT PRIMARY KEY,
            type TEXT NOT NULL,
            name TEXT NOT NULL,
            tier TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Edges table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS edges (
            source TEXT NOT NULL,
            target TEXT NOT NULL,
            relation TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (source, target, relation),
            FOREIGN KEY (source) REFERENCES nodes(id),
            FOREIGN KEY (target) REFERENCES nodes(id)
        )
    """)
    
    # Metadata table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS metadata (
            key TEXT PRIMARY KEY,
            value TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    return conn

def sync_nodes(conn: sqlite3.Connection) -> int:
    """Insert or update taxonomy nodes."""
    cursor = conn.cursor()
    count = 0
    
    for node in TAXONOMY_NODES:
        cursor.execute("""
            INSERT OR REPLACE INTO nodes (id, type, name, tier)
            VALUES (?, ?, ?, ?)
        """, (node["id"], node["type"], node["name"], node.get("tier")))
        count += 1
    
    conn.commit()
    return count

def sync_edges(conn: sqlite3.Connection) -> int:
    """Insert or update taxonomy edges."""
    cursor = conn.cursor()
    count = 0
    
    for edge in TAXONOMY_EDGES:
        cursor.execute("""
            INSERT OR REPLACE INTO edges (source, target, relation)
            VALUES (?, ?, ?)
        """, (edge["source"], edge["target"], edge["relation"]))
        count += 1
    
    conn.commit()
    return count

def update_metadata(conn: sqlite3.Connection):
    """Record sync timestamp and statistics."""
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM nodes")
    node_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM edges")
    edge_count = cursor.fetchone()[0]
    
    cursor.execute("""
        INSERT OR REPLACE INTO metadata (key, value)
        VALUES (?, ?)
    """, ("last_sync", datetime.now().isoformat()))
    
    cursor.execute("""
        INSERT OR REPLACE INTO metadata (key, value)
        VALUES (?, ?)
    """, ("node_count", str(node_count)))
    
    cursor.execute("""
        INSERT OR REPLACE INTO metadata (key, value)
        VALUES (?, ?)
    """, ("edge_count", str(edge_count)))
    
    conn.commit()

def export_json(conn: sqlite3.Connection) -> Dict:
    """Export taxonomy as JSON for CI/documentation."""
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, type, name, tier FROM nodes")
    nodes = [{"id": row[0], "type": row[1], "name": row[2], "tier": row[3]} 
             for row in cursor.fetchall()]
    
    cursor.execute("SELECT source, target, relation FROM edges")
    edges = [{"source": row[0], "target": row[1], "relation": row[2]} 
             for row in cursor.fetchall()]
    
    return {
        "nodes": nodes,
        "edges": edges,
        "metadata": {
            "node_count": len(nodes),
            "edge_count": len(edges),
            "synced_at": datetime.now().isoformat()
        }
    }

def main():
    """Run taxonomy synchronization."""
    print(f"Initializing taxonomy database: {DB_PATH}")
    conn = init_database()
    
    print(f"Syncing {len(TAXONOMY_NODES)} nodes...")
    node_count = sync_nodes(conn)
    print(f"  [+] {node_count} nodes synced")
    
    print(f"Syncing {len(TAXONOMY_EDGES)} edges...")
    edge_count = sync_edges(conn)
    print(f"  [+] {edge_count} edges synced")
    
    print("Updating metadata...")
    update_metadata(conn)
    
    # Export JSON summary
    summary = export_json(conn)
    json_path = WORKSPACE_ROOT / "taxonomy.json"
    with open(json_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"  [+] JSON export: {json_path}")
    
    conn.close()
    
    print(f"\n[OK] Taxonomy sync complete!")
    print(f"   Database: {DB_PATH}")
    print(f"   Nodes: {node_count} | Edges: {edge_count}")

if __name__ == "__main__":
    main()
