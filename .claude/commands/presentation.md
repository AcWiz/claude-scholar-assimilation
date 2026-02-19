---
description: "Create conference presentation slides for accepted paper"
arguments:
  - name: "time_limit"
    description: "Presentation time in minutes (e.g., 15, 20, 30)"
    required: false
  - name: "format"
    description: "Output format: outline, beamer, or pptx-guide"
    required: false
---

# /presentation - Conference Presentation Creator

Create presentation slides for your accepted paper.

## What This Command Does

1. Guides you through presentation slide creation
2. Provides templates and design guidelines
3. Helps with time management and content structure

## Workflow

1. Ask about presentation time limit (default: 15 minutes)
2. Read the paper to extract key content
3. Suggest slide structure based on time:
   - 15 min: ~12 slides (1 title, 1 motivation, 2 method, 3 results, 1 conclusion, 1 Q&A)
   - 20 min: ~16 slides (add related work, more results)
   - 30 min: ~22 slides (full treatment of all sections)
4. Generate slide content for each slide
5. Provide design guidelines:
   - One key message per slide
   - Figures over text
   - Consistent color scheme
   - Large fonts (24pt minimum for body)

## Output

Generate a presentation outline with:
- Slide-by-slide content breakdown
- Speaker notes for each slide
- Key figures to include
- Timing suggestions per slide

## Tips

- Start preparing 2-3 weeks before the conference
- Practice your presentation multiple times
- Keep slides simple and visual
- Prepare backup PDF version
