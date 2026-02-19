---
description: "Spawn the 9-agent research team for parallel work"
arguments:
  - name: "project"
    description: "Project name or research topic for the team"
    required: false
  - name: "agents"
    description: "Comma-separated agent names to spawn (or 'all' for full team)"
    required: false
---

# /spawn-team - Spawn Research Team

Spawn a multi-agent research team for parallel work on project "$project". Agents to spawn: "$agents" (default: all).

## The 9-Agent Research Team

| Agent | Role | Responsibility |
|-------|------|----------------|
| `literature-scout` | Literature Search | Zotero MCP（语义搜索、全文、标注）, paper analysis, literature review |
| `data-analyst` | Experiment Analysis | Statistical analysis, visualization specs, results drafts |
| `language-editor` | Writing & Translation | Translation, polishing, compression, expansion, de-AI |
| `figure-designer` | Figures & Tables | Chart recommendation, figure/table captions |
| `mock-reviewer` | Paper Review | Simulate harsh reviewer, find fatal flaws |
| `rebuttal-writer` | Review Response | Systematic rebuttal writing, tone optimization |
| `dev-planner` | Development Planning | Implementation plans, task breakdown |
| `code-reviewer` | Code Quality | Security review, quality checks |
| `tdd-guide` | Test-Driven Dev | TDD workflow guidance, coverage targets |

## Workflow

### Step 1: Create Team Structure

Create a team workspace directory:

```
team/
├── tasks/          # Task assignments for each agent
├── outputs/        # Collected outputs from agents
└── status.md       # Team status dashboard
```

### Step 2: Create Tasks

Use the Task tool to create tasks for each agent based on the project needs. Each task should include:
- Clear objective and deliverable
- Input data or references needed
- Output format expected
- Dependencies on other agents' work

### Step 3: Spawn Agents

For each agent in the team, use the Task tool to spawn a sub-agent:
- Assign the agent's specific role description
- Provide the task instructions
- Set up any required context (files, data paths)

### Step 4: Coordinate

- Monitor agent progress via team/status.md
- Resolve dependencies (e.g., literature-reviewer outputs feed into language-editor)
- Collect and merge outputs into team/outputs/

## Usage Examples

```bash
# Spawn full team for a new paper
/spawn-team "Cross-Subject EEG Classification" all

# Spawn only writing-related agents
/spawn-team "Paper Revision" language-editor,figure-designer,mock-reviewer

# Spawn analysis agents
/spawn-team "Experiment Analysis" data-analyst,figure-designer
```

## Notes

- Not all agents need to be spawned simultaneously; spawn based on current phase
- Agents work best when given focused, specific tasks
- Use `/team-status` to check progress
