# MCP Guide for Charm Crush

Model Context Protocol (MCP) servers extend Crush with external tools and resources.

## Overview

MCP servers are configured in `crush.json` under the `mcp` key. Once configured, their tools become available alongside Crush's builtin tools automatically.

## Configuration

### Basic Structure

```json
{
  "mcp": {
    "my_server": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path"]
    }
  }
}
```

### Connection Types

| Type | When to Use | Required Fields |
|------|-------------|----------------|
| `stdio` | Local Node.js/Python servers | `command`, `args` |
| `http` | Remote HTTP endpoints | `url` |
| `sse` | Server-Sent Events | `url` |

### Full Example

```json
{
  "mcp": {
    "filesystem": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/home/user/projects"]
    },
    "github": {
      "type": "http",
      "url": "https://api.githubcopilot.com/mcp/",
      "headers": {
        "Authorization": "Bearer $GH_PAT"
      }
    },
    "postgres": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres"],
      "env": {
        "DATABASE_URL": "postgresql://localhost/mydb"
      }
    }
  }
}
```

## All Options

| Option | Type | Description |
|--------|------|-------------|
| `type` | string | Required: `stdio`, `sse`, or `http` |
| `command` | string | Executable (stdio only) |
| `args` | array | Arguments (stdio only) |
| `url` | string | Endpoint URL (http/sse only) |
| `headers` | object | HTTP headers |
| `env` | object | Environment variables |
| `disabled` | boolean | Skip loading this server |
| `disabled_tools` | array | Tools to hide |
| `timeout` | number | Request timeout in seconds |

## Popular Servers

| Package | Purpose | Install |
|---------|---------|---------|
| `@modelcontextprotocol/server-filesystem` | File read/write | `npx -y ...` |
| `@modelcontextprotocol/server-postgres` | PostgreSQL queries | `npx -y ...` |
| `@modelcontextprotocol/server-sqlite` | SQLite queries | `npx -y ...` |
| `@modelcontextprotocol/server-github` | GitHub API | `npx -y ...` |

## Adding a New Server

1. Choose or build an MCP server
2. Add entry to `crush.json` → `mcp` section
3. Restart Crush
4. Verify with `crush_info`

## Config Priority

```
1. .crush.json     → Project-local (hidden)
2. crush.json     → Project-local
3. ~/.config/crush/crush.json → Global
```