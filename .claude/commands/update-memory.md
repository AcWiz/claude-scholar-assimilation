---
description: "Check and update CLAUDE.md memory based on recent changes to skills, commands, and agents"
---

# /update-memory - Update Agent Memory

Check and update the CLAUDE.md global memory file, ensuring it stays in sync with skills, commands, agents, and hooks source files.

## What Gets Tracked

CLAUDE.md is a summary memory file containing:
- Skill directory structure (from `skills/`)
- Command list (from `commands/`)
- Agent configurations (from `agents/`)
- Hook definitions (from `hooks/`)

## Workflow

### Step 1: Scan Source Files

Scan modification times of:
- `.claude/commands/**/*.md`
- `.claude/agents/**/*.md`
- `.claude/skills/**/skill.md` (if exists)
- `.claude/hooks/**/*.{js,json}` (if exists)

### Step 2: Compare with CLAUDE.md

- If any source file is newer than CLAUDE.md, it needs updating
- Record which sections need updates

### Step 3: Generate Report

```
Source File Status:
- Commands: X files (latest modified: {name})
- Agents: Y files (latest modified: {name})
- Skills: Z files
- Hooks: W files

Time Comparison:
- CLAUDE.md last updated: {timestamp}
- Source files last modified: {timestamp}

Sections needing update:
- [ ] Command list (N commands changed)
- [ ] Agent configurations (no changes)
```

### Step 4: Confirm and Update

Ask the user:
- `yes` - Execute update
- `no` - Cancel
- `diff` - Show detailed differences

### Step 5: Execute Update

- Preserve user-edited sections (e.g., "User Background", "Tech Stack Preferences")
- Only update AUTO-GENERATED sections
- Update timestamp

## Usage

```bash
/update-memory          # Check and prompt for update
```

## Notes

- Run periodically, especially after adding new commands or agents
- Preserves all manually written sections in CLAUDE.md
- Only auto-generated sections are overwritten
