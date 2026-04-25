# Architecture Clarification

## Original Idea vs RAG

### What User Asked For (Original Request)

User wanted:
- "a MCP in which there is all the context and it is connected to all major LLM providers"
- "MCPIn which there is all the contexts" 
- "main context data db like a knowledge base"
- "database that can be added and removed"
- Store: documents (if needed), conversations, important stuff
- Flexible - "how the user wants and how the conversation the user wants"
- Access via web or TUI with MCP

**This is a knowledge base MCP - NOT RAG.**

---

### What We Built

A **knowledge base MCP server** with:
- SQLite database
- Basic search (substring matching with LIKE queries)
- CRUD operations (add, update, delete entries)
- Categories and tags
- CLI for direct access
- Connected to OpenCode as "base" MCP

**This is what was asked for** - simple knowledge base with basic search.

---

### What RAG Is (Different Project)

**RAG** = Retrieval-Augmented Generation

Requires:
- Embeddings (vector representations of text)
- Semantic similarity search (cosine similarity)
- Chunked documents with overlap
- Vector database (LanceDB, Qdrant, pgvector)
- Understanding conceptual meaning, not just keywords

**This is NOT what was originally asked for.**

---

### Why The Confusion

The user explored RAG via the explore agent, but the original request was simpler:
- Store context, notes, conversations
- Basic search
- MCP-accessible

RAG would be a future enhancement, not the original scope.

---

### Can Both Exist?

Yes, future hybrid approach:

1. **Keep SQLite** for structured data (contexts, passwords, notes)
2. **Add vector DB** for semantic search on documents
3. Use **both** depending on query type

---

## Summary

| | Knowledge Base | RAG |
|-|----------------|-----|
| **Search** | Substring match | Semantic similarity |
| **Storage** | SQLite | Vector DB |
| **Documents** | Manual entry | Auto-chunked |
| **Understanding** | Keyword based | Conceptual |
| **Status** | ✅ Built | Future option |

**Original scope:** Knowledge base MCP (done)
**Future:** RAG enhancement (different project)
