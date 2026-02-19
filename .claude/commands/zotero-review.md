---
description: "Read and analyze papers from a Zotero collection, generate literature review"
arguments:
  - name: "collection"
    description: "Zotero collection name or keyword to search"
    required: true
  - name: "depth"
    description: "Analysis depth: quick (abstract only) or deep (full text)"
    required: false
---

# /zotero-review - Zotero Collection Literature Analysis

Read and analyze papers in the Zotero collection "$collection", with analysis depth "$depth" (default: deep).

## Workflow

### Step 1: Locate Collection

1. Call `mcp__zotero__zotero_get_collections` to list all collections
2. Find the collection matching "$collection" (fuzzy match supported)
3. Call `mcp__zotero__zotero_get_collection_items` to get all items

### Step 2: Read Papers

For each paper:
1. Call `mcp__zotero__zotero_get_item_metadata` to get metadata (with BibTeX if needed)
2. Call `mcp__zotero__zotero_get_item_fulltext` to read full text (if PDF available)
3. Call `mcp__zotero__zotero_get_annotations` to read PDF highlights and comments
4. Quick depth: analyze abstract and introduction only
5. Deep depth: analyze complete paper content + annotations

### Step 3: Generate Notes

Create structured notes for each paper:
- **Research Question**: What problem does this paper address?
- **Core Method**: What method/approach is proposed?
- **Key Findings**: What are the main results?
- **Limitations**: What are the limitations?
- **Relevance**: How does it relate to our research?

Deep mode: create individual `paper-notes/{paper-title}.md` files.
Optionally write notes back to Zotero via `mcp__zotero__zotero_create_note`.

### Step 4: Synthesis

1. Group papers by theme/method
2. Identify common patterns and divergences
3. Generate comparison matrix
4. Create or update `literature-review.md`

## Error Handling

- `zotero_get_item_fulltext` fails: use `WebFetch` on DOI URL, fall back to abstractNote
- `zotero_get_collection_items` fails: use `zotero_search_items` with keywords, filter results
- Single paper fails: log error, skip, continue
- API rate limit: wait 5 seconds, retry up to 3 times

## Output Files

```
{project_dir}/
├── literature-review.md
└── paper-notes/           (deep mode)
    ├── {paper1-title}.md
    └── {paper2-title}.md
```

## Completion Checklist

- [ ] All papers in collection read (or flagged if no PDF)
- [ ] Structured notes generated for each paper
- [ ] Individual paper-notes files created (deep mode)
- [ ] literature-review.md generated with thematic grouping and comparison matrix
