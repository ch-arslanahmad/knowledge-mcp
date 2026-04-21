# Skills Guide for Charm Crush

Skills extend Crush's capabilities through structured instruction files.

## Skill Location Paths

### The `crush://` Prefix

The `crush://` prefix is a **virtual protocol** — not a filesystem path or URL. It tells the View tool to load a skill directly from Crush's built-in skill definitions.

```
crush://skills/crush-config/SKILL.md
    ↑ This is NOT a URL
    ↓ This is a virtual identifier
```

When you pass `crush://skills/crush-config/SKILL.md` to the View tool, Crush:
1. Recognizes the `crush://` prefix
2. Looks up the skill definition by name (`crush-config`)
3. Returns the skill's `SKILL.md` content directly

**It does not** make HTTP requests or read filesystem paths.

### Skill Discovery

Skills are discovered from:

| Location | Type | Description |
|----------|------|-------------|
| `crush://skills/<name>/SKILL.md` | Builtin | Core skills bundled with Crush |
| `./.crush/skills/` | Local | Project-local skills |
| `./.claude/skills/` | Local | Claude-compatible |
| `./.cursor/skills/` | Local | Cursor-compatible |
| `./.agents/skills/` | Local | Agents-format skills |
| Custom paths | User | Via `options.skills_paths` |

### Default Auto-Loaded Paths

These paths are **automatically scanned** — no config needed:

- `.crush/skills/`
- `.claude/skills/`
- `.cursor/skills/`
- `.agents/skills/`

## Skill File Format

Each skill is a markdown file with YAML frontmatter:

```markdown
---
name: my-skill
description: What this skill does and when to use it
location: crush://skills/my-skill/SKILL.md
type: builtin
---

# Skill Title

Instructions for the AI...
```

### Frontmatter Fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Unique skill identifier |
| `description` | Yes | When to activate this skill |
| `location` | Yes | Path to the SKILL.md file |
| `type` | Yes | `builtin` or `local` |

## How to Add a Custom Skill

### Step 1: Create the Skill File

Create a directory and SKILL.md:

```bash
mkdir -p .crush/skills/my-custom-skill
```

```markdown
---
name: my-custom-skill
description: Add a custom skill
location: .crush/skills/my-custom-skill/SKILL.md
type: local
---

# My Custom Skill

Instructions here...
```

### Step 2: Add to Skills Path (if not in default location)

If using a non-standard location, add to `crush.json`:

```json
{
  "options": {
    "skills_paths": ["./custom-skills", "./vendor/skills"]
  }
}
```

### Step 3: Restart or Reload

Skills are loaded at startup. Restart Crush or trigger config reload.

## Finding Skills Persistently

### Where Builtin Skills Live

Builtin skills are **compiled into Crush** — they don't exist as filesystem files. The `crush://skills/<name>/SKILL.md` prefix is an internal registry lookup, not a file path.

To find builtin skills persistently:

1. **Check the documentation** — Search online for "Charm Crush skills" or check Crush's official docs
2. **Ask Crush directly** — Run a prompt asking what skills are available
3. **Check `crush_info`** — The output shows loaded skills under the `[skills]` section

### Local Skills

Local skills persist in your project or home directory:

| Location | Persists | Notes |
|----------|----------|-------|
| `.crush/skills/` | Yes (git) | Create and commit to repo |
| `.claude/skills/` | Yes (git) | Claude-compatible |
| Custom path | Yes | Via `options.skills_paths` |

To persist a skill **permanently**, create it in one of these directories — it will survive Crush updates.

### The `crush://` Path Is Not a File

```
crush://skills/crush-config/SKILL.md
```

This is a **runtime lookup only** — Crush resolves it from its internal skill registry at startup. The content doesn't exist as a `.md` file you can browse.

To make a skill **truly persistent**:
1. Create it in `.crush/skills/<name>/SKILL.md`
2. Add the path to `options.skills_paths` if not auto-loaded
3. Commit to git

### Finding Available Skills

| Method | How |
|--------|-----|
| `crush_info` | Shows loaded skills |
| `crush://` prefix | View tool loads skill content |
| Project files | Check `.crush/skills/` directory |
| Online docs | Charm Crush documentation |

## Disabling Skills

```json
{
  "options": {
    "disabled_skills": ["crush-config"]
  }
}
```

## Config File Priority

```
1. .crush.json     → Project-local (hidden)
2. crush.json     → Project-local
3. ~/.config/crush/crush.json → Global
```