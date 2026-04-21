# Knowledge Base MCP

A Model Context Protocol (MCP) server for storing and retrieving personal knowledge, notes, contacts, and context.

## Quick Start

### 1. Run the Server

**Local (OpenCode/CLI):**
```bash
cd ~/Desktop/github/knowledge-mcp
source venv/bin/activate
python server.py --mode stdio
```

**HTTP (Remote access):**
```bash
python http_server.py
# Server runs at http://localhost:8000/mcp
```

### 2. Connect to OpenCode

```bash
opencode mcp add
# Name: base
# Type: Local  
# Command: /home/arslan/Desktop/github/knowledge-mcp/venv/bin/python /home/arslan/Desktop/github/knowledge-mcp/server.py
```

### 3. Add Your First Data

```bash
# Via CLI
cd ~/Desktop/github/knowledge-mcp
source venv/bin/activate
python cli.py add "My WiFi" "Password: mypass123" --category network --tags wifi,home
python cli.py add "Friend - John" "Phone: 555-1234" --category contacts --tags friend
python cli.py add "Project Notes" "Key decisions..." --category work --tags project
```

### 4. Search Your Data

In OpenCode, just ask:
- "What's my WiFi password?"
- "Tell me about John"
- "What project notes do I have?"

---

## Data Organization

### Categories

Organize your entries by category:

| Category | Use For |
|----------|---------|
| `contacts` | Friends, family, colleagues |
| `work` | Projects, meetings, notes |
| `personal` | Passwords, subscriptions |
| `reference` | Commands, documentation |
| `learn` | Study notes, resources |
| `finance` | Budgets, accounts |

### Tags

Add tags for flexible searching:
- `friend`, `work`, `urgent`
- `password`, `wifi`, `api`
- `project-x`, `meeting-notes`

### Examples

```bash
# Add a contact
python cli.py add "Friend - Ouwen" "Phone: xxx, Notes: teacher of Diddy" --category contacts --tags friend,ouwen

# Add work notes
python cli.py add "Sprint Planning" "Features: 1. Auth, 2. Dashboard" --category work --tags sprint,planning

# Add password
python cli.py add "Gmail Password" "myemail@gmail.com / password123" --category personal --tags password,email
```

---

## Access Methods

### 1. OpenCode (Local)

```bash
opencode mcp add base
# Use "base" MCP for knowledge search
```

### 2. HTTP Server (Remote)

```bash
# Start server
python http_server.py

# Access via:
# http://localhost:8000/mcp
```

### 3. CLI (Direct)

```bash
python cli.py list
python cli.py add "Title" "Content"
python cli.py search
python cli.py categories
```

---

## MCP Tools

| Tool | Description |
|------|-------------|
| `search_knowledge` | Search by query, category, tags |
| `add_entry_kb` | Add new entry |
| `list_kb_categories` | List all categories |

---

## Multi-User Support

Each user has their own database:
- `data/default.db` - default user
- `data/arslan.db` - user "arslan"
- `data/username.db` - any username

```bash
# CLI for specific user
python cli.py --user arslan add "Note" "Content"
```

---

## Project Structure

```
knowledge-mcp/
├── server.py       # MCP server (stdio mode)
├── http_server.py  # MCP server (HTTP mode)
├── cli.py          # CLI tool
├── data/           # SQLite databases (per user)
│   └── default.db
├── README.md
└── venv/           # Python environment
```

---

## Troubleshooting

### MCP not connecting
```bash
opencode mcp list
# Check if "base" shows ✓ connected
```

### HTTP server won't start
```bash
# Check port is free
lsof -i :8000

# Kill if needed
kill $(lsof -t -i:8000)
```

### No data shows up
```bash
# Check what's in database
python cli.py list
```

---

## Next Steps

- [ ] Add more sample data
- [ ] Set up HTTP server for remote access
- [ ] Connect to other clients (Claude Desktop, Cursor)
- [ ] Add document ingestion (PDF, URLs)
