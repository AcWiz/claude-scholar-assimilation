---
description: "Analyze experimental results with statistical analysis for paper writing"
arguments:
  - name: "data_path"
    description: "Path to experimental results (CSV, JSON, or directory)"
    required: false
  - name: "analysis_type"
    description: "Type of analysis: full, comparison, ablation, or visualization"
    required: false
---

# /analyze-results - Experiment Results Analysis

Analyze experimental results at "$data_path" with analysis type "$analysis_type" (default: full).

If no data_path is provided, enter interactive mode and ask the user for data location.

## Analysis Types

| Type | Description | Output |
|------|-------------|--------|
| `full` | Complete analysis (default) | Statistics + visualization + Results draft |
| `comparison` | Model comparison | Performance comparison + significance tests |
| `ablation` | Ablation study | Component contribution analysis |
| `visualization` | Visualization only | Paper-quality figure specifications |

## Workflow

### Step 1: Data Location and Validation
- Find experiment result files
- Check data completeness and format
- Identify columns, units, metric directions

### Step 2: Statistical Analysis
- Descriptive statistics (mean, std, confidence intervals)
- Pre-tests (normality, homogeneity of variance)
- Hypothesis tests: t-test, ANOVA, Wilcoxon as appropriate
- Effect sizes: Cohen's d, eta-squared

### Step 3: Generate Report
- Create `analysis-output/analysis-report.md` with statistical summary and key findings
- Create `analysis-output/results-draft.md` with paper-ready Results section draft
- Create `analysis-output/visualization-specs.md` with figure specifications

### Step 4: Visualization Specifications
- Recommend chart types using the chart-recommend methodology
- Provide detailed specs: axes, scales, error bars, color schemes

## Output Files

```
analysis-output/
├── analysis-report.md
├── results-draft.md
└── visualization-specs.md
```

## Notes

- Ensure results include complete statistical info (multiple runs, random seeds)
- Data format should clearly label columns, units, and metric direction
- Generated Results drafts require human review and adjustment
