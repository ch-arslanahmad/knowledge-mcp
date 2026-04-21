#!/usr/bin/env python3
"""Knowledge Base MCP Server - with HTTP support and multi-user."""

import argparse
import asyncio
import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.server.http import HttpServer
from mcp.types import Tool, TextContent

# Config
DEFAULT_PORT = 8000
DEFAULT_HOST = "0.0.0.0"
DB_DIR = Path(__file__).parent / "data"


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


def get_entries(
    db_path: Path,
    search: str = None,
    category: str = None,
    limit: int = 50,
    tags: str = None,
) -> list[dict]:
    """Get entries from database."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    query = "SELECT * FROM entries WHERE 1=1"
    params = []

    if search:
        query += " AND (title LIKE ? OR content LIKE ? OR tags LIKE ?)"
        s = f"%{search}%"
        params.extend([s, s, s])

    if category:
        query += " AND category = ?"
        params.append(category)

    if tags:
        query += " AND tags LIKE ?"
        params.append(f"%{tags}%")

    query += " ORDER BY updated_at DESC LIMIT ?"
    params.append(limit)

    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def add_entry(
    db_path: Path,
    title: str,
    content: str,
    category: str = "general",
    tags: str = "",
) -> dict:
    """Add a new entry."""
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
    return {
        "id": entry_id,
        "title": title,
        "content": content,
        "category": category,
        "tags": tags,
    }


def update_entry(
    db_path: Path,
    entry_id: int,
    title: str = None,
    content: str = None,
    category: str = None,
    tags: str = None,
) -> dict:
    """Update an entry."""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("SELECT * FROM entries WHERE id = ?", (entry_id,))
    existing = cur.fetchone()
    if not existing:
        conn.close()
        return {"error": "Entry not found"}

    updates = []
    params = []

    if title is not None:
        updates.append("title = ?")
        params.append(title)
    if content is not None:
        updates.append("content = ?")
        params.append(content)
    if category is not None:
        updates.append("category = ?")
        params.append(category)
    if tags is not None:
        updates.append("tags = ?")
        params.append(tags)

    if not updates:
        conn.close()
        return {"error": "No fields to update"}

    updates.append("updated_at = ?")
    params.append(datetime.now().isoformat())
    params.append(entry_id)

    query = f"UPDATE entries SET {', '.join(updates)} WHERE id = ?"
    cur.execute(query, params)
    conn.commit()

    cur.execute("SELECT * FROM entries WHERE id = ?", (entry_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else {"error": "Entry not found"}


def delete_entry(db_path: Path, entry_id: int) -> dict:
    """Delete an entry."""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("DELETE FROM entries WHERE id = ?", (entry_id,))
    deleted = cur.rowcount > 0
    conn.commit()
    conn.close()
    return {"deleted": deleted}


def get_categories(db_path: Path) -> list[str]:
    """Get all categories."""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT category FROM entries ORDER BY category")
    cats = [row[0] for row in cur.fetchall()]
    conn.close()
    return cats


def get_tags(db_path: Path) -> list[str]:
    """Get all unique tags."""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT tags FROM entries WHERE tags != ''")
    all_tags = []
    for row in cur.fetchall():
        if row[0]:
            all_tags.extend([t.strip() for t in row[0].split(",")])
    conn.close()
    return list(set(all_tags))


# MCP App
app = Server("knowledge-mcp")


@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="search_knowledge",
            description="Search knowledge base entries",
            inputSchema={
                "type": "object",
                "properties": {
                    "search": {"type": "string", "description": "Search query"},
                    "category": {"type": "string", "description": "Filter by category"},
                    "tags": {
                        "type": "string",
                        "description": "Filter by tags (comma-separated)",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Max results",
                        "default": 50,
                    },
                },
            },
        ),
        Tool(
            name="add_entry",
            description="Add a new entry to knowledge base",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Entry title"},
                    "content": {"type": "string", "description": "Entry content"},
                    "category": {
                        "type": "string",
                        "description": "Category",
                        "default": "general",
                    },
                    "tags": {
                        "type": "string",
                        "description": "Comma-separated tags",
                        "default": "",
                    },
                },
                "required": ["title", "content"],
            },
        ),
        Tool(
            name="update_entry",
            description="Update an existing entry",
            inputSchema={
                "type": "object",
                "properties": {
                    "entry_id": {
                        "type": "integer",
                        "description": "Entry ID to update",
                    },
                    "title": {"type": "string", "description": "New title"},
                    "content": {"type": "string", "description": "New content"},
                    "category": {"type": "string", "description": "New category"},
                    "tags": {"type": "string", "description": "New tags"},
                },
                "required": ["entry_id"],
            },
        ),
        Tool(
            name="delete_entry",
            description="Delete an entry",
            inputSchema={
                "type": "object",
                "properties": {
                    "entry_id": {
                        "type": "integer",
                        "description": "Entry ID to delete",
                    },
                },
                "required": ["entry_id"],
            },
        ),
        Tool(
            name="list_categories",
            description="List all categories",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="list_tags",
            description="List all unique tags",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="get_entry",
            description="Get a specific entry by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "entry_id": {"type": "integer", "description": "Entry ID"},
                },
                "required": ["entry_id"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    # Get user from headers or default
    user = os.environ.get("KB_USER", "default")
    db_path = get_db_path(user)
    init_db(db_path)

    try:
        if name == "search_knowledge":
            results = get_entries(
                db_path,
                search=arguments.get("search"),
                category=arguments.get("category"),
                tags=arguments.get("tags"),
                limit=arguments.get("limit", 50),
            )
            return [TextContent(type="text", text=str(results))]

        elif name == "add_entry":
            result = add_entry(
                db_path,
                title=arguments["title"],
                content=arguments["content"],
                category=arguments.get("category", "general"),
                tags=arguments.get("tags", ""),
            )
            return [TextContent(type="text", text=str(result))]

        elif name == "update_entry":
            result = update_entry(
                db_path,
                entry_id=arguments["entry_id"],
                title=arguments.get("title"),
                content=arguments.get("content"),
                category=arguments.get("category"),
                tags=arguments.get("tags"),
            )
            return [TextContent(type="text", text=str(result))]

        elif name == "delete_entry":
            result = delete_entry(db_path, arguments["entry_id"])
            return [TextContent(type="text", text=str(result))]

        elif name == "list_categories":
            cats = get_categories(db_path)
            return [TextContent(type="text", text=str(cats))]

        elif name == "list_tags":
            tags = get_tags(db_path)
            return [TextContent(type="text", text=str(tags))]

        elif name == "get_entry":
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute("SELECT * FROM entries WHERE id = ?", (arguments["entry_id"],))
            row = cur.fetchone()
            conn.close()
            if row:
                return [TextContent(type="text", text=str(dict(row)))]
            return [TextContent(type="text", text="Entry not found")]

        return [TextContent(type="text", text=f"Unknown tool: {name}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def run_stdio():
    """Run as stdio server (for local/IDE use)."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


async def run_http(host: str, port: int):
    """Run as HTTP server (for remote access)."""
    http_server = HttpServer(app)
    await http_server.run(host=host, port=port)


def main():
    parser = argparse.ArgumentParser(description="Knowledge Base MCP Server")
    parser.add_argument(
        "--mode", choices=["stdio", "http"], default="stdio", help="Server mode"
    )
    parser.add_argument("--host", default=DEFAULT_HOST, help="HTTP host")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="HTTP port")
    parser.add_argument(
        "--user", default="default", help="Default user (for stdio mode)"
    )
    parser.add_argument(
        "--db-dir", type=Path, default=DB_DIR, help="Database directory"
    )

    args = parser.parse_args()

    global DB_DIR
    if args.db_dir:
        DB_DIR = args.db_dir

    # Initialize default user's DB
    init_db(get_db_path(args.user))

    if args.mode == "http":
        print(f"Starting HTTP server on {args.host}:{args.port}")
        asyncio.run(run_http(args.host, args.port))
    else:
        print("Starting stdio server...")
        asyncio.run(run_stdio())


if __name__ == "__main__":
    main()
