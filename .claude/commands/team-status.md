---
description: "Check research team status and agent progress"
---

# /team-status - Team Status Dashboard

Check the current status of the research team, including active agents and task progress.

## What This Command Does

1. Read team status from `team/status.md` (if exists)
2. Check active tasks and their completion state
3. Review agent outputs in `team/outputs/`
4. Generate a status summary

## Workflow

### Step 1: Scan Team Workspace

Check for the team workspace structure:
```
team/
├── tasks/          # Task assignments
├── outputs/        # Collected outputs
└── status.md       # Status dashboard
```

If the workspace does not exist, report that no team has been spawned yet and suggest using `/spawn-team`.

### Step 2: Check Task Status

For each task file in `team/tasks/`:
- Read the task description
- Check if corresponding output exists in `team/outputs/`
- Determine status: Pending / In Progress / Completed / Blocked

### Step 3: Check Agent Memory Files

Look for agent memory or state files that track recent work:
- Check `.claude/` for any agent-specific memory files
- Review recent file modifications in the project directory

### Step 4: Generate Status Report

Output a formatted status report:

```
# Team Status Report

## Active Agents
| Agent | Task | Status | Last Updated |
|-------|------|--------|-------------|
| ... | ... | ... | ... |

## Completed Deliverables
- [list of completed outputs]

## Blocked / Pending
- [list of blocked or waiting tasks]

## Next Actions
- [recommended next steps]
```

## Notes

- Run this command periodically to stay informed about team progress
- Use output to decide which agents need attention or additional tasks
- Pair with `/spawn-team` to add new agents as needed
