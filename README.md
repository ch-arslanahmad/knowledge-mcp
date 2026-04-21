# Knowledge Base MCP

A Model Context Protocol (MCP) server for storing and retrieving personal knowledge, notes, contacts, and context.

## What is this?

This MCP server provides a knowledge base that can be connected to AI tools like OpenCode. It allows:
- **Storage**: Store contacts, notes, documentation, conversations
- **Retrieval**: Search and query your data via MCP tools
- **Management**: Add, update, delete entries via CLI or MCP

## Setup

### 1. Create Virtual Environment

```bash
cd ~/Desktop/github/knowledge-mcp
python3 -m venv venv
source venv/bin/activate
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org mcp sqlite-utils
```

### 2. Test the Server

```bash
# Test MCP server directly
echo '{"jsonrpc":"2.0","id":"1","method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}' | python3 server.py
```

### 3. Connect to OpenCode

```bash
opencode mcp add
# Enter: base / Local / /home/arslan/Desktop/github/knowledge-mcp/venv/bin/python /home/arslan/Desktop/github/knowledge-mcp/server.py
```

Or add to `~/.config/opencode/opencode.json`:

```json
{
  "mcp": {
    "base": {
      "type": "local",
      "command": [
        "/home/arslan/Desktop/github/knowledge-mcp/venv/bin/python",
        "/home/arslan/Desktop/github/knowledge-mcp/server.py"
      ]
    }
  }
}
```

### 4. Add System Prompt (Optional)

Add to `~/.config/opencode/opencode.json` to auto-check knowledge base:

```json
{
  "mode": {
    "build": {
      "prompt": "You have a knowledge base MCP called 'base' connected. Before answering questions about personal info (friends, family, contacts, passwords), work info (projects, meetings), or any question where the answer might be in the user's data, ALWAYS use the MCP tools first: base_search_knowledge, base_add_entry, base_update_entry."
    }
  }
}
```

## Usage

### Via OpenCode (Recommended)

Just ask questions:
- "What's my WiFi password?"
- "Tell me about my friend"
- "What meetings do I have scheduled?"

The MCP will automatically search and retrieve relevant info.

### Via CLI

```bash
cd ~/Desktop/github/knowledge-mcp
source venv/bin/activate

# List all entries
python cli.py list

# Search entries
python cli.py search

# Add entry
python cli.py add "Title" "Content" --category work --tags tag1,tag2

# Update entry
python cli.py update 1 --title "New Title"

# Delete entry
python cli.py delete 1

# List categories
python cli.py categories
```

## MCP Tools

| Tool | Description |
|------|-------------|
| `search_knowledge` | Search entries by query and/or category |
| `add_entry` | Add new entry (title, content, category, tags) |
| `update_entry` | Update existing entry |
| `delete_entry` | Delete entry by ID |
| `list_categories` | List all categories |

## Database Schema

```sql
CREATE TABLE entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    category TEXT DEFAULT 'general',
    tags TEXT DEFAULT '',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
```

## Troubleshooting

### MCP not connecting

1. Check status: `opencode mcp list`
2. Check logs: `cat ~/.local/share/opencode/log/2026-*.log | grep -i mcp`
3. Test server manually: Run the command and check for errors

### Module not found errors

Make sure you're using the venv Python, not system Python:
```
/home/arslan/Desktop/github/knowledge-mcp/venv/bin/python
```

## Future Enhancements

- [ ] Cloud hosting (for multi-device access)
- [ ] Web UI (n8n integration)
- [ ] Document ingestion (PDF, TXT)
- [ ] Multiple workspaces
- [ ] Sync with other MCP clients (Cursor, Cline)
