---
description: "Start systematic review response workflow for rebuttal writing"
arguments:
  - name: "review_file"
    description: "Path to file containing reviewer comments (optional)"
    required: false
---

# /rebuttal - Review Response Workflow

Start a systematic rebuttal writing workflow. If "$review_file" is provided, read the file. Otherwise, guide the user to paste or describe reviewer comments.

## Workflow

### Step 1: Obtain Reviewer Comments

If review_file provided: read file content, identify reviewer count and comment structure.
If not provided: guide user to paste or describe comments, confirm reviewer count.

### Step 2: Analyze and Classify

- Group comments by reviewer
- Classify as Major / Minor / Typo / Misunderstanding
- Identify priority order

### Step 3: Formulate Response Strategy

For each comment, select strategy:
- **Accept** - Accept and improve
- **Defend** - Politely defend with evidence
- **Clarify** - Clarify misunderstanding
- **Experiment** - Add supplementary experiments

### Step 4: Write Rebuttal

Generate structured responses:
- Response + Changes for each comment
- Include specific location references
- Provide evidence and reasoning

### Step 5: Tone Optimization

- Every response starts with thanks
- Avoid defensive or aggressive language
- Maintain professionalism and respect

### Step 6: Generate Output

Output files:
- `rebuttal.md` - Complete rebuttal document
- `review-analysis.md` - Comment analysis (optional)
- `experiment-plan.md` - Supplementary experiment plan (if needed)

## Key Principles

1. Analyze comments through natural language understanding, not automated scripts
2. Maintain professional, respectful, evidence-based tone throughout
3. Provide specific location references and evidence for every response
4. Verify all comments have been addressed before completing
