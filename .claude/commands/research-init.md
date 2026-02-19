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

通过 Bash 运行 pyzotero 脚本创建集合结构：

```bash
python3 -c "
from pyzotero import zotero
import os
zot = zotero.Zotero(os.environ['ZOTERO_LIBRARY_ID'], 'user', os.environ['ZOTERO_API_KEY'])
# Create main collection
resp = zot.create_collections([{'name': 'Research-{Topic}-{YYYY-MM}'}])
main_key = list(resp['successful'].values())[0]['data']['key']
# Create sub-collections
subs = ['Core Papers', 'Methods', 'Applications', 'Baselines', 'To-Read']
zot.create_collections([{'name': s, 'parentCollection': main_key} for s in subs])
print(f'Created: {main_key}')
"
```

Record all `collection_key` values for import in Step 2.

### Step 2: Literature Search and Import

1. Use WebSearch to find papers related to "$topic"
   - Search strategy: topic + variant key term combinations
   - Target sources: arXiv, Google Scholar, conference proceedings
   - Time range: focused = last 3 years, broad = last 5 years
   - Target count: 20-50 (focused) / 50-100 (broad)
2. Extract DOIs from search results
3. Pre-import deduplication:
   - Call `mcp__zotero__zotero_search_items` with DOI or title to find existing matches
   - Use `mcp__zotero__zotero_semantic_search` for fuzzy deduplication
4. Import new papers via Bash + pyzotero (write operations):
   - `zot.create_items()` with metadata from CrossRef/Semantic Scholar API
   - Classify into sub-collections during import
5. Use `mcp__zotero__zotero_batch_update_tags` to tag imported papers by category

### Step 3: Paper Analysis

1. Call `mcp__zotero__zotero_get_collection_items` to list imported papers
2. Call `mcp__zotero__zotero_get_item_metadata` for detailed metadata (BibTeX supported)
3. Call `mcp__zotero__zotero_get_item_fulltext` for papers with PDFs
4. Call `mcp__zotero__zotero_get_annotations` for existing PDF annotations
5. For each paper, extract: research question, core methodology, key findings, limitations

### Step 4: Gap Analysis and Synthesis

1. Analyze research trends, methodological gaps, unexplored domains, contradictions
2. Identify 2-3 concrete research gaps
3. Formulate potential research questions
4. Use `mcp__zotero__zotero_create_note` to save analysis notes back to Zotero

### Step 5: Generate Outputs

Based on output_type "$output_type":
- `literature-review.md` - Structured literature review with Zotero citations
- `research-proposal.md` - Research proposal (if "proposal" or "both")
- `references.bib` - BibTeX references (use `zotero_get_item_metadata` with bibtex format)

## Error Handling

- pyzotero 创建集合失败：记录错误，手动在 Zotero 中创建
- `zotero_get_item_fulltext` fails: use `WebFetch` on DOI URL, fall back to abstractNote
- `zotero_semantic_search` fails: fall back to `zotero_search_items` keyword search
- Single paper fails: log error, skip, continue
- API rate limit: wait 5 seconds, retry up to 3 times

## Completion Checklist

- [ ] Zotero collection created with sub-collections
- [ ] Papers imported and organized (target count met)
- [ ] Full-text analysis completed for core papers
- [ ] Gap analysis identifies 2-3 research gaps
- [ ] Output files generated with real Zotero citations
