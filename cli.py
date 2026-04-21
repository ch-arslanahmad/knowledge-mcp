#!/usr/bin/env python3
"""Knowledge Base CLI."""

import argparse
import json
import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / "knowledge.db"


def init_db():
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
    conn.commit()
    conn.close()


def search(query=None, category=None, limit=50):
    conn = sqlite3.connect(DB_PATH)
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

    results = [dict(row) for row in rows]
    print(json.dumps(results, indent=2))
    return results


def add(title, content, category="general", tags=""):
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
    print(json.dumps({"id": entry_id, "title": title, "category": category}))


def update(entry_id, title=None, content=None, category=None, tags=None):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    updates = []
    params = []

    if title:
        updates.append("title = ?")
        params.append(title)
    if content:
        updates.append("content = ?")
        params.append(content)
    if category:
        updates.append("category = ?")
        params.append(category)
    if tags:
        updates.append("tags = ?")
        params.append(tags)

    if not updates:
        print(json.dumps({"error": "No fields to update"}))
        return

    updates.append("updated_at = ?")
    params.append(datetime.now().isoformat())
    params.append(entry_id)

    sql = f"UPDATE entries SET {', '.join(updates)} WHERE id = ?"
    cur.execute(sql, params)
    conn.commit()

    cur.execute("SELECT * FROM entries WHERE id = ?", (entry_id,))
    row = cur.fetchone()
    conn.close()

    if row:
        print(json.dumps(dict(row)))
    else:
        print(json.dumps({"error": "Entry not found"}))


def delete(entry_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DELETE FROM entries WHERE id = ?", (entry_id,))
    deleted = cur.rowcount > 0
    conn.commit()
    conn.close()
    print(json.dumps({"deleted": deleted}))


def list_categories():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT category FROM entries ORDER BY category")
    cats = [row[0] for row in cur.fetchall()]
    conn.close()
    print(json.dumps(cats))


def list_all(limit=100):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.execute(
        "SELECT * FROM entries ORDER BY updated_at DESC LIMIT ?", (limit,)
    )
    rows = cur.fetchall()
    conn.close()
    results = [dict(row) for row in rows]
    print(json.dumps(results, indent=2))


init_db()

parser = argparse.ArgumentParser(description="Knowledge Base CLI")
subparsers = parser.add_subparsers(dest="command", required=True)

subparsers.add_parser("search", help="Search entries")
subparsers.add_parser("categories", help="List categories")
subparsers.add_parser("list", help="List all entries")

add_parser = subparsers.add_parser("add", help="Add entry")
add_parser.add_argument("title", help="Entry title")
add_parser.add_argument("content", help="Entry content")
add_parser.add_argument("--category", default="general")
add_parser.add_argument("--tags", default="")

update_parser = subparsers.add_parser("update", help="Update entry")
update_parser.add_argument("id", type=int, help="Entry ID")
update_parser.add_argument("--title")
update_parser.add_argument("--content")
update_parser.add_argument("--category")
update_parser.add_argument("--tags")

delete_parser = subparsers.add_parser("delete", help="Delete entry")
delete_parser.add_argument("id", type=int, help="Entry ID")

args = parser.parse_args()

if args.command == "search":
    search()
elif args.command == "categories":
    list_categories()
elif args.command == "list":
    list_all()
elif args.command == "add":
    add(args.title, args.content, args.category, args.tags)
elif args.command == "update":
    update(args.id, args.title, args.content, args.category, args.tags)
elif args.command == "delete":
    delete(args.id)
