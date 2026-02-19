---
description: "Initialize a research project with Zotero-integrated literature review"
arguments:
  - name: "topic"
    description: "Research topic or keywords"
    required: true
  - name: "scope"
    description: "Review scope: focused (last 3 years, 20-50 papers) or broad (last 5 years, 50-100 papers)"
    required: false
  - name: "output_type"
    description: "Output type: review, proposal, or both"
    required: false
---

# /research-init - Zotero-Integrated Research Startup Workflow

Launch a complete literature survey workflow for the research topic "$topic", with scope "$scope" (default: focused) and output type "$output_type" (default: both).

## Workflow

### Step 1: Create Zotero Research Collection

1. Call `mcp__zotero__create_collection` to create the main collection named `Research-{Topic}-{YYYY-MM}`
2. Create sub-collections: `Core Papers`, `Methods`, `Applications`, `Baselines`, `To-Read`
3. Record all `collection_key` values for import in Step 2

### Step 2: Literature Search and Import

1. Use WebSearch to find papers related to "$topic"
   - Search strategy: topic + variant key term combinations
   - Target sources: arXiv, Google Scholar, conference proceedings
   - Time range: focused = last 3 years, broad = last 5 years
   - Target count: 20-50 (focused) / 50-100 (broad)
2. Extract DOIs from search results
3. Classify each paper into the appropriate sub-collection before import
4. Pre-import deduplication:
   - Call `mcp__zotero__search_library` with DOI to find matches
   - Call `mcp__zotero__get_items_details` to confirm exact DOI match
   - For papers without DOI: search by title using token overlap ratio > 0.8
5. Import with `mcp__zotero__add_items_by_doi` into the target sub-collection
6. Fallback for papers without DOI: use `mcp__zotero__add_web_item` with the paper URL
7. Call `mcp__zotero__find_and_attach_pdfs` for all imported item keys

### Step 3: Paper Analysis

1. Call `mcp__zotero__get_collection_items` to list imported papers
2. Call `mcp__zotero__get_items_details` with `include_abstract: true`
3. Call `mcp__zotero__get_item_fulltext` for papers with PDFs
4. For each paper, extract: research question, core methodology, key findings, limitations

### Step 4: Gap Analysis and Synthesis

1. Analyze research trends, methodological gaps, unexplored domains, contradictions
2. Identify 2-3 concrete research gaps
3. Formulate potential research questions

### Step 5: Generate Outputs

Based on output_type "$output_type":
- `literature-review.md` - Structured literature review with Zotero citations
- `research-proposal.md` - Research proposal (if "proposal" or "both")
- `references.bib` - BibTeX references (use Zotero REST API `?format=bibtex`)

## Error Handling

- `create_collection` fails: use Zotero REST API directly
- `add_items_by_doi` fails: fetch via CrossRef API + `add_web_item`
- `get_item_fulltext` fails: use `WebFetch` on DOI URL, fall back to abstractNote
- Single paper fails: log error, skip, continue
- API rate limit: wait 5 seconds, retry up to 3 times

## Completion Checklist

- [ ] Zotero collection created with sub-collections
- [ ] Papers imported and organized (target count met)
- [ ] PDFs attached for open-access papers
- [ ] Full-text analysis completed for core papers
- [ ] Gap analysis identifies 2-3 research gaps
- [ ] Output files generated with real Zotero citations
