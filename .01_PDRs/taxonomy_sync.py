"""Sync ARTIFACT_TAXONOMY.json + TAXONOMY_EDGES.json -> taxonomy.db

Computes derived fields (priority_score, is_blocked) and writes all
nodes and edges to SQLite. JSON files are the source of truth; the DB
is never edited directly.

Usage:
    python taxonomy_sync.py           # sync and print top-5 priority
    python taxonomy_sync.py --report  # full priority report
    python taxonomy_sync.py --query "SELECT ..." # run a raw query
"""

import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).parent
TAXONOMY_PATH = BASE / "ARTIFACT_TAXONOMY.json"
EDGES_PATH = BASE / "TAXONOMY_EDGES.json"
DB_PATH = BASE / "taxonomy.db"

STAGE_WEIGHTS = {
    "Pre-flight": 40,
    "Backlog": 30,
    "In-Process": 20,
    "Completed": 10,
    "Reviewed": 0,
    "Archived": 0,
}

MISSION_WEIGHTS = {"M4": 30, "M3": 20, "M2": 10, "M1": 5}

DUPLICATE_MULTIPLIERS = {
    "unique": 1.0,
    "possible_redundant": 0.7,
    "redundant": 0.3,
    "duplicate": 0.1,
    "unknown": 1.0,
}

TERMINAL_STAGES = {"Completed", "Reviewed", "Archived"}


def _age_bonus(registered_at):
    try:
        reg = datetime.fromisoformat(registered_at.replace("Z", "+00:00"))
        weeks = (datetime.now(timezone.utc) - reg).days / 7
        return min(10.0, max(0.0, weeks))
    except Exception:
        return 0.0


def _compute(node, stage_by_id, dep_targets):
    stage = node.get("stage", "")
    if stage in TERMINAL_STAGES:
        return 0.0, False

    is_blocked = any(
        stage_by_id.get(t, "") not in TERMINAL_STAGES
        for t in dep_targets
    )

    if not dep_targets:
        dep_bonus = 20.0
    elif is_blocked:
        dep_bonus = 0.0
    elif all(stage_by_id.get(t, "") in TERMINAL_STAGES for t in dep_targets):
        dep_bonus = 20.0
    else:
        dep_bonus = 10.0

    base = (
        STAGE_WEIGHTS.get(stage, 0)
        + MISSION_WEIGHTS.get(node.get("mission_level"), 0)
        + dep_bonus
        + _age_bonus(node.get("registered_at", ""))
    )
    dup_mult = DUPLICATE_MULTIPLIERS.get(node.get("duplicate_status", "unique"), 1.0)
    blocked_mult = 0.2 if is_blocked else 1.0
    return round(base * dup_mult * blocked_mult, 2), is_blocked


def _create_schema(cur):
    cur.executescript("""
        CREATE TABLE IF NOT EXISTS nodes (
            seq                  INTEGER,
            id                   TEXT PRIMARY KEY,
            type                 TEXT,
            title                TEXT,
            description          TEXT,
            version              TEXT,
            stage                TEXT,
            mission_level        TEXT,
            source               TEXT,
            owner                TEXT,
            assigned_agent_family TEXT,
            registered_at        TEXT,
            updated_at           TEXT,
            last_activity_at     TEXT,
            priority_score       REAL,
            is_blocked           INTEGER,
            duplicate_status     TEXT,
            duplicate_confidence INTEGER,
            implementation_signal TEXT,
            related_prs          TEXT,
            related_issues       TEXT,
            tags                 TEXT,
            file_path            TEXT,
            extracted_path       TEXT,
            extraction_status    TEXT,
            artifact_type        TEXT,
            zip_path             TEXT,
            completion_percentage INTEGER,
            acceptance_criteria  TEXT,
            target_quarter       TEXT,
            notes                TEXT
        );
        CREATE TABLE IF NOT EXISTS edges (
            id         TEXT PRIMARY KEY,
            from_id    TEXT,
            to_id      TEXT,
            type       TEXT,
            created_at TEXT,
            notes      TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_nodes_stage    ON nodes(stage);
        CREATE INDEX IF NOT EXISTS idx_nodes_type     ON nodes(type);
        CREATE INDEX IF NOT EXISTS idx_nodes_mission  ON nodes(mission_level);
        CREATE INDEX IF NOT EXISTS idx_nodes_priority ON nodes(priority_score DESC);
        CREATE INDEX IF NOT EXISTS idx_edges_from     ON edges(from_id);
        CREATE INDEX IF NOT EXISTS idx_edges_to       ON edges(to_id);
        CREATE INDEX IF NOT EXISTS idx_edges_type     ON edges(type);
    """)


def _upsert_node(cur, node):
    cur.execute("""
        INSERT OR REPLACE INTO nodes VALUES (
            :seq, :id, :type, :title, :description, :version,
            :stage, :mission_level, :source, :owner, :assigned_agent_family,
            :registered_at, :updated_at, :last_activity_at,
            :priority_score, :is_blocked,
            :duplicate_status, :duplicate_confidence, :implementation_signal,
            :related_prs, :related_issues, :tags,
            :file_path, :extracted_path, :extraction_status,
            :artifact_type, :zip_path,
            :completion_percentage, :acceptance_criteria,
            :target_quarter, :notes
        )
    """, {
        "seq": node.get("seq"),
        "id": node.get("id"),
        "type": node.get("type"),
        "title": node.get("title"),
        "description": node.get("description"),
        "version": node.get("version"),
        "stage": node.get("stage"),
        "mission_level": node.get("mission_level"),
        "source": node.get("source"),
        "owner": node.get("owner"),
        "assigned_agent_family": node.get("assigned_agent_family"),
        "registered_at": node.get("registered_at"),
        "updated_at": node.get("updated_at"),
        "last_activity_at": node.get("last_activity_at"),
        "priority_score": node.get("priority_score", 0.0),
        "is_blocked": 1 if node.get("is_blocked") else 0,
        "duplicate_status": node.get("duplicate_status"),
        "duplicate_confidence": node.get("duplicate_confidence"),
        "implementation_signal": node.get("implementation_signal"),
        "related_prs": json.dumps(node.get("related_prs", [])),
        "related_issues": json.dumps(node.get("related_issues", [])),
        "tags": json.dumps(node.get("tags", [])),
        "file_path": node.get("file_path"),
        "extracted_path": node.get("extracted_path"),
        "extraction_status": node.get("extraction_status"),
        "artifact_type": node.get("artifact_type"),
        "zip_path": node.get("zip_path"),
        "completion_percentage": node.get("completion_percentage"),
        "acceptance_criteria": json.dumps(node.get("acceptance_criteria", [])),
        "target_quarter": node.get("target_quarter"),
        "notes": node.get("notes"),
    })


def sync(report=False, raw_query=None):
    try:
        with open(TAXONOMY_PATH) as f:
            taxonomy = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"ERROR reading {TAXONOMY_PATH}: {e}")
        sys.exit(1)

    try:
        with open(EDGES_PATH) as f:
            edges_data = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"ERROR reading {EDGES_PATH}: {e}")
        sys.exit(1)

    nodes = taxonomy["nodes"]
    edges = edges_data["edges"]

    # Build dependency map (depends_on edges only)
    depends_on_map = {}
    for e in edges:
        if e["type"] == "depends_on":
            depends_on_map.setdefault(e["from_id"], []).append(e["to_id"])

    stage_by_id = {n["id"]: n.get("stage", "") for n in nodes}

    # Compute derived fields
    for node in nodes:
        deps = depends_on_map.get(node["id"], [])
        score, blocked = _compute(node, stage_by_id, deps)
        node["priority_score"] = score
        node["is_blocked"] = blocked

    # Write computed fields back to taxonomy JSON
    taxonomy["last_updated"] = datetime.now(timezone.utc).isoformat()
    with open(TAXONOMY_PATH, "w") as f:
        json.dump(taxonomy, f, indent=2)

    # Sync to SQLite
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    _create_schema(cur)

    for node in nodes:
        _upsert_node(cur, node)

    for edge in edges:
        cur.execute(
            "INSERT OR REPLACE INTO edges VALUES (:id, :from_id, :to_id, :type, :created_at, :notes)",
            edge,
        )

    con.commit()

    print(f"Synced {len(nodes)} nodes, {len(edges)} edges -> {DB_PATH.name}")

    if raw_query:
        print(f"\nQuery: {raw_query}")
        for row in con.execute(raw_query):
            print(" ", row)
        con.close()
        return

    if report:
        print("\n--- Full Priority Report ---")
        rows = con.execute(
            "SELECT id, type, stage, mission_level, priority_score, is_blocked "
            "FROM nodes ORDER BY priority_score DESC"
        ).fetchall()
        for r in rows:
            blocked = " [BLOCKED]" if r[5] else ""
            print(f"  {r[4]:6.1f}  {r[0]:<50} {r[2]:<12} {r[3] or 'null'}{blocked}")
    else:
        print("\nTop 5 by priority:")
        rows = con.execute(
            "SELECT id, stage, mission_level, priority_score, is_blocked "
            "FROM nodes ORDER BY priority_score DESC LIMIT 5"
        ).fetchall()
        for r in rows:
            blocked = " [BLOCKED]" if r[4] else ""
            print(f"  {r[3]:6.1f}  {r[0]}  ({r[1]}, {r[2]}){blocked}")

    con.close()


if __name__ == "__main__":
    args = sys.argv[1:]
    if "--query" in args:
        idx = args.index("--query")
        sync(raw_query=args[idx + 1])
    elif "--report" in args:
        sync(report=True)
    else:
        sync()
