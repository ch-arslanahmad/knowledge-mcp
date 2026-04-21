#!/usr/bin/env python3
"""Knowledge Base MCP Server."""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from pydantic import AnyUrl

DB_PATH = Path(__file__).parent / "knowledge.db"


def init_db():
    """Initialize the database."""
    conn = sqlite3.connect(DB_PATH)
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
    search: str = None, category: str = None, limit: int = 50
) -> list[dict]:
    """Get entries from database."""
    conn = sqlite3.connect(DB_PATH)
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

    query += " ORDER BY updated_at DESC LIMIT ?"
    params.append(limit)

    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def add_entry(
    title: str, content: str, category: str = "general", tags: str = ""
) -> dict:
    """Add a new entry."""
    now = datetime.now().isoformat()
    conn = sqlite3.connect(DB_PATH)
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
    entry_id: int,
    title: str = None,
    content: str = None,
    category: str = None,
    tags: str = None,
) -> dict:
    """Update an entry."""
    conn = sqlite3.connect(DB_PATH)
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


def delete_entry(entry_id: int) -> dict:
    """Delete an entry."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DELETE FROM entries WHERE id = ?", (entry_id,))
    deleted = cur.rowcount > 0
    conn.commit()
    conn.close()
    return {"deleted": deleted}


app = Server("knowledge-mcp")

init_db()


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
                    "entry_id": {"type": "integer", "description": "Entry ID to delete"}
                },
                "required": ["entry_id"],
            },
        ),
        Tool(
            name="list_categories",
            description="List all categories in knowledge base",
            inputSchema={"type": "object", "properties": {}},
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    if name == "search_knowledge":
        results = get_entries(
            search=arguments.get("search"),
            category=arguments.get("category"),
            limit=arguments.get("limit", 50),
        )
        return [TextContent(type="text", text=str(results))]

    elif name == "add_entry":
        result = add_entry(
            title=arguments["title"],
            content=arguments["content"],
            category=arguments.get("category", "general"),
            tags=arguments.get("tags", ""),
        )
        return [TextContent(type="text", text=str(result))]

    elif name == "update_entry":
        result = update_entry(
            entry_id=arguments["entry_id"],
            title=arguments.get("title"),
            content=arguments.get("content"),
            category=arguments.get("category"),
            tags=arguments.get("tags"),
        )
        return [TextContent(type="text", text=str(result))]

    elif name == "delete_entry":
        result = delete_entry(arguments["entry_id"])
        return [TextContent(type="text", text=str(result))]

    elif name == "list_categories":
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT category FROM entries ORDER BY category")
        cats = [row[0] for row in cur.fetchall()]
        conn.close()
        return [TextContent(type="text", text=str(cats))]

    return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
