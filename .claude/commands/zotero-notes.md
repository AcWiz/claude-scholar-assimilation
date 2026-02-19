---
description: "Batch generate structured reading notes from a Zotero collection"
arguments:
  - name: "collection"
    description: "Zotero collection name or keyword"
    required: true
  - name: "format"
    description: "Note format: summary, detailed, or comparison"
    required: false
---

# /zotero-notes - Zotero Batch Reading Notes Generator

Generate structured reading notes for papers in the Zotero collection "$collection", in "$format" format (default: detailed).

## Workflow

### Step 1: Load Papers

1. Call `mcp__zotero__get_collections` to find the matching collection
2. Call `mcp__zotero__get_collection_items` to list all papers
3. Call `mcp__zotero__get_items_details` to get metadata

### Step 2: Read and Annotate

For each paper with a PDF, call `mcp__zotero__get_item_fulltext` to read content.

**summary format:**
- One-paragraph summary per paper
- One-sentence core contribution

**detailed format (default):**
- One-sentence positioning
- Problem and motivation
- Method (core approach, key modules, differences from prior work)
- Experiments (datasets, metrics, performance, ablation findings)
- Limitations and questions
- Relationship to other works in the collection
- Value for my research

**comparison format:**
- Side-by-side comparison tables
- Method comparison matrix
- Performance comparison (if applicable)

**Content retrieval fallback chain:**
1. `get_item_fulltext` (primary)
2. `WebFetch(https://doi.org/{DOI})` (scrape abstract)
3. `abstractNote` + Claude domain knowledge

### Step 3: Output

1. Create `reading-notes-{collection}.md` containing all notes
2. If comparison format: additionally create a comparison table
3. List papers without PDFs for manual processing

### Step 4: Write Notes to Zotero (Optional)

If user requests, create child notes via Zotero REST API (no MCP `add_note` tool exists).

## Best Practices

- Validate the first paper through the full pipeline before batch processing
- Process 4-7 papers per batch with pauses for review
- Cross-reference papers using Zotero item keys in the "Relationship" section

## Output Files

```
{project_dir}/
├── reading-notes-{collection}.md
└── comparison-matrix.md          (comparison format only)
```

## Completion Checklist

- [ ] All papers processed (or flagged if no PDF)
- [ ] Reading notes generated in requested format
- [ ] Output files created
- [ ] Papers without PDFs listed for manual processing
