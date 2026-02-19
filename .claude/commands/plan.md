---
description: "Create step-by-step implementation plan. WAIT for user confirmation before writing code."
arguments:
  - name: "task"
    description: "What needs to be built or implemented"
    required: false
---

# /plan - Implementation Planning

Create a comprehensive implementation plan before writing any code. MUST receive user approval before proceeding.

## What This Command Does

1. **Restate Requirements** - Clarify what needs to be built
2. **Identify Risks** - Surface potential issues and blockers
3. **Create Step Plan** - Break down implementation into phases
4. **Wait for Confirmation** - MUST receive explicit user approval

## Workflow

1. **Analyze the request** and restate requirements clearly
2. **Break down into phases** with specific, actionable steps
3. **Identify dependencies** between components
4. **Assess risks** and potential blockers
5. **Estimate complexity** (High / Medium / Low)
6. **Present the plan** and WAIT for explicit confirmation

## Plan Structure

```
# Implementation Plan: {Title}

## Requirements Restatement
- Clear bullet points of what will be built

## Implementation Phases
### Phase 1: {Name}
- Step-by-step actions
### Phase 2: {Name}
- Step-by-step actions

## Dependencies
- External services, libraries, accounts needed

## Risks
- HIGH / MEDIUM / LOW with descriptions

## Estimated Complexity
- Per-phase estimates and total
```

## CRITICAL

The planner will NOT write any code until you explicitly confirm with "yes", "proceed", or similar.

To modify, respond with:
- "modify: [your changes]"
- "different approach: [alternative]"
- "skip phase X and do phase Y first"

## Integration

After planning:
- Use `/tdd` to implement with test-driven development
- Use `/code-review` to review completed implementation
- Use `/commit` to commit changes
