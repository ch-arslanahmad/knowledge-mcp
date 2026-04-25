#!/usr/bin/env python3
"""Knowledge Base MCP Server - HTTP version for remote access."""

import sqlite3
from datetime import datetime
from pathlib import Path

from fastmcp import FastMCP

# Config
DB_DIR = Path(__file__).parent / "data"
DEFAULT_PORT = 8000


def get_db_path(user: str = "default") -> Path:
    """Get database path for user."""
    DB_DIR.mkdir(exist_ok=True)
    return DB_DIR / f"{user}.db"


def init_db(db_path: Path):
    """Initialize database."""
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            category TEXT DEFAULT 'general',
            tags TEXT DEFAULT '',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_category ON entries(category)")
    conn.commit()
    conn.close()


def search_entries(user: str, query: str = None, category: str = None, limit: int = 50):
    """Search entries."""
    db_path = get_db_path(user)
    init_db(db_path)

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    sql = "SELECT * FROM entries WHERE 1=1"
    params = []

    if query:
        sql += " AND (title LIKE ? OR content LIKE ? OR tags LIKE ?)"
        s = f"%{query}%"
        params.extend([s, s, s])

    if category:
        sql += " AND category = ?"
        params.append(category)

    sql += " ORDER BY updated_at DESC LIMIT ?"
    params.append(limit)

    cur.execute(sql, params)
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_entry(
    user: str, title: str, content: str, category: str = "general", tags: str = ""
):
    """Add entry."""
    db_path = get_db_path(user)
    init_db(db_path)
    now = datetime.now().isoformat()

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO entries (title, content, category, tags, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
        (title, content, category, tags, now, now),
    )
    entry_id = cur.lastrowid
    conn.commit()
    conn.close()
    return {"id": entry_id, "title": title}


# MCP Server
mcp = FastMCP("knowledge-base")


@mcp.tool()
def search_knowledge(
    query: str = None,
    category: str = None,
    limit: int = 50,
    user: str = "default",
):
    """Search knowledge base."""
    results = search_entries(user, query, category, limit)
    return {"results": results, "count": len(results)}


@mcp.tool()
def add_entry_kb(
    title: str,
    content: str,
    category: str = "general",
    tags: str = "",
    user: str = "default",
):
    """Add new entry."""
    return add_entry(user, title, content, category, tags)


@mcp.tool()
def list_kb_categories(user: str = "default"):
    """List all categories."""
    db_path = get_db_path(user)
    init_db(db_path)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT category FROM entries ORDER BY category")
    cats = [r[0] for r in cur.fetchall()]
    conn.close()
    return {"categories": cats}


if __name__ == "__main__":
    import os

    os.environ.setdefault("FASTMCP_JSON_RESPONSE", "true")

    print(f"Starting MCP server on http://0.0.0.0:{DEFAULT_PORT}")
    mcp.run(transport="http", host="0.0.0.0", port=DEFAULT_PORT)
