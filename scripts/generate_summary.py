#!/usr/bin/env python3
"""
Generate structured summary.md files for arXiv papers using new template.
Processes abstract.md and paper_content.txt, uses Claude API to enhance with missing fields.

New template includes:
- YAML Front Matter (title, arXiv ID, authors, year, source, venue, tags, difficulty, importance, read_status)
- Detailed method breakdown (Pipeline, core modules, tech+physics fusion)
- Math & Physics modeling (optimization objective, loss function, key PDEs)
- Experiment details (datasets, evaluation metrics, comparison methods, core conclusions)
- Strengths/Weaknesses analysis
- Research inspiration (directly reusable modules, transferable insights)
- Idea extensions (2-3 deep expansion directions)
- BibTeX citation format
"""

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from anthropic import Anthropic
except ImportError:
    print("Error: anthropic package not installed. Install with: uv add anthropic")
    sys.exit(1)


def get_api_key() -> str:
    """Get API key from environment or arguments."""
    # Check common environment variable names
    for env_var in ["ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN"]:
        api_key = os.environ.get(env_var, "")
        if api_key:
            return api_key

    # Check common .env locations
    env_locations = [
        Path.home() / ".env",
        Path.home() / ".claude" / "projects" / ".env",
        Path.home() / ".claude" / ".env",
        Path(__file__).parent.parent / ".env",
    ]

    for env_path in env_locations:
        if env_path.exists():
            with open(env_path) as f:
                for line in f:
                    if line.startswith("ANTHROPIC_API_KEY=") or line.startswith("ANTHROPIC_AUTH_TOKEN="):
                        return line.split("=", 1)[1].strip()

    return ""


# Paper list - same as generate_abstracts.py
PAPER_LIST = [
    ("2025", "2507_06479v1"),
    ("2023", "2308_11814v1"),
    ("2025", "2508_03315v1"),
    ("2022", "2206_01599v1"),
    ("2025", "2503_19160v1"),
    ("2025", "2501_08430v1"),
    ("2022", "2212_03656v2"),
    ("2021", "2109_08017v1"),
    ("2025", "2510_15284v1"),
    ("2025", "2511_06041v1"),
    ("2021", "2105_05363v1"),
    ("2022", "2205_13410v1"),
    ("2024", "2406_07680v1"),
    ("2019", "1906_06722v2"),
    ("2025", "2505_10894v1"),
    ("2021", "2105_02939v1"),
    ("2021", "2106_08747v1"),
    ("2023", "2308_09956v1"),
    ("2025", "2510_17756v1"),
    ("2025", "2507_08834v1"),
    ("2025", "2511_05629v1"),
    ("2026", "2603_05560v2"),
    ("2022", "2212_12086v2"),
    ("2017", "1707_01146v4"),
    ("2020", "2010_00399v2"),
    ("2024", "2410_16605v1"),
    ("2024", "2409_19518v1"),
    ("2026", "2603_14115v1"),
    ("2023", "2309_05317v3"),
    ("2022", "2206_13659v1"),
    ("2025", "2507_08749v1"),
    ("2023", "2310_00813v2"),
    ("2023", "2305_11913v2"),
    ("2023", "2310_02691v2"),
    ("2024", "2404_05768v2"),
    ("2023", "2311_12902v2"),
    ("2025", "2510_09792v1"),
    ("2026", "2601_01813v1"),
    ("2021", "2110_07100v1"),
    ("2022", "2202_09967v1"),
    ("2023", "2305_09468v1"),
    ("2024", "2409_05369v1"),
    ("2024", "2412_03413v2"),
    ("2025", "2510_25563v1"),
    ("2024", "2408_12632v1"),
    ("2020", "2005_01090v1"),
    ("2022", "2206_12746v1"),
    ("2023", "2310_04540v1"),
    ("2024", "2404_14757v3"),
    ("2026", "2601_01864v1"),
    ("2024", "2408_06262v1"),
    ("2019", "1909_08573v2"),
    ("2025", "2505_10191v1"),
    ("2025", "2511_18732v2"),
    ("2025", "2505_24429v2"),
    ("2025", "2512_22152v1"),
    ("2025", "2506_23900v1"),
    ("2026", "2603_06153v1"),
    ("2023", "2308_03152v2"),
    ("2025", "2511_17427v1"),
    ("2020", "2009_01554v1"),
    ("2025", "2512_11525v1"),
    ("2023", "2307_00734v1"),
    ("2026", "2601_12775v1"),
    ("2022", "2202_08956v2"),
    ("2021", "2107_09483v1"),
    ("2024", "2410_11807v2"),
    ("2023", "2304_05872v2"),
    ("2025", "2512_11545v1"),
    ("2021", "2105_12903v1"),
    ("2023", "2312_05068v1"),
    ("2022", "2211_05904v1"),
    ("2023", "2304_03832v1"),
    ("2022", "2209_11371v3"),
    ("2012", "1204_3547v2"),
    ("2011", "1108_0168v1"),
    ("2013", "1302_3876v2"),
]


# Application tags for ocean/DA research
OCEAN_TAGS = ["ocean-modeling", "data-assimilation", "ocean-forecasting", "marine-science"]
METHOD_TAGS = ["graph-neural-network", "transformer", "neural-operator", "physics-informed", "deep-learning"]


def extract_from_content(content: str) -> dict:
    """Extract metadata from paper_content.txt using regex patterns."""
    info = {}

    # Extract title (usually first non-empty lines before authors)
    lines = content.split('\n')
    title_lines = []
    for i, line in enumerate(lines[:10]):
        line = line.strip()
        if not line or line.startswith('manuscript submitted to'):
            continue
        # Stop if we hit authors section
        if re.match(r'^[A-Z][a-z]+.*,\s*\d+,?\s*(and)?|E-mail:|Email:', line, re.I):
            break
        title_lines.append(line)
        if i > 0 and len(title_lines) >= 3:
            next_line = lines[i+1].strip() if i+1 < len(lines) else ""
            if not next_line or re.match(r'^[A-Z][a-z]+.*,', next_line):
                break

    info['title'] = ' '.join(title_lines).replace('arXiv:', '').strip()
    if not info['title']:
        info['title'] = "Untitled Paper"

    # Extract authors - look for patterns like "Name Name1, Name Name2"
    author_patterns = [
        r'([A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+\d)?(?:,\s*[A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+\d)?)*)',
        r'((?:[A-Z][a-z]+\s+){2,}\d+)',
    ]
    for pattern in author_patterns[:1]:
        match = re.search(pattern, content[:500])
        if match:
            authors_raw = match.group(1)
            # Clean up - remove numbers and split by "and" or ","
            authors_clean = re.sub(r'\s+\d+', '', authors_raw)
            authors_clean = re.sub(r',\s*and\s+', '; ', authors_clean)
            authors_clean = re.sub(r',\s*', '; ', authors_clean)
            info['authors'] = authors_clean.strip('; ')
            break

    if 'authors' not in info:
        info['authors'] = "Authors not extracted"

    # Extract arXiv ID from content
    arxiv_match = re.search(r'arXiv:(\d{4}\.\d{4,5})v\d+', content)
    if arxiv_match:
        info['arxiv_id'] = arxiv_match.group(1)
    else:
        info['arxiv_id'] = "unknown"

    # Extract year from content (look for patterns like "2024" or "24")
    year_match = re.search(r'(?:arXiv:|submitted.*)(20\d{2})', content)
    if year_match:
        info['year'] = year_match.group(1)
    else:
        # Try to extract from first 4 digits
        year_match2 = re.search(r'^(20\d{2})', content.strip())
        if year_match2:
            info['year'] = year_match2.group(1)
        else:
            info['year'] = "unknown"

    return info


def extract_from_abstract(abstract_md: str) -> dict:
    """Extract information from existing abstract.md."""
    info = {}

    if not abstract_md:
        return info

    # Extract sections using markdown headers
    sections = {}
    current_header = None
    current_content = []

    for line in abstract_md.split('\n'):
        if line.startswith('## '):
            if current_header:
                sections[current_header] = '\n'.join(current_content).strip()
            current_header = line[3:].strip()
            current_content = []
        elif current_header:
            current_content.append(line)

    if current_header:
        sections[current_header] = '\n'.join(current_content).strip()

    info['sections'] = sections

    # Extract method info
    if 'Method' in sections:
        info['method'] = sections['Method']

    if 'TL;DR' in sections:
        info['tldr'] = sections['TL;DR']

    if 'Research Question' in sections:
        info['research_question'] = sections['Research Question']

    if 'Main Contributions' in sections:
        contributions = sections['Main Contributions']
        # Extract bullet points
        info['contributions'] = re.findall(r'^\d+\.\s*(.+)$', contributions, re.MULTILINE)

    if 'Core Results' in sections:
        results = sections['Core Results']
        info['results'] = re.findall(r'^- (.+)$', results, re.MULTILINE)

    if 'Datasets' in sections:
        datasets = sections['Datasets']
        info['datasets'] = re.findall(r'^- (.+)$', datasets, re.MULTILINE)

    if 'Limitations' in sections:
        limitations = sections['Limitations']
        info['limitations'] = re.findall(r'^- (.+)$', limitations, re.MULTILINE)

    if 'Research Gaps' in sections:
        gaps = sections['Research Gaps']
        info['research_gaps'] = re.findall(r'^- (.+)$', gaps, re.MULTILINE)

    return info


def build_prompt(title: str, arxiv_id: str, year: str, authors: str,
                 abstract_info: dict, paper_content: str) -> str:
    """Build the prompt for Claude API to generate summary.md content."""

    method = abstract_info.get('method', 'Not specified')
    tldr = abstract_info.get('tldr', 'Not specified')
    rq = abstract_info.get('research_question', 'Not specified')
    contributions = abstract_info.get('contributions', [])
    results = abstract_info.get('results', [])
    datasets = abstract_info.get('datasets', [])
    limitations = abstract_info.get('limitations', [])
    research_gaps = abstract_info.get('research_gaps', [])

    # Truncate paper content to first 8000 chars for API
    paper_sample = paper_content[:8000] if len(paper_content) > 8000 else paper_content

    prompt = f"""You are generating a structured summary for an academic paper. Generate a complete summary.md file with YAML front matter and detailed sections.

## Paper Information
- Title: {title}
- arXiv ID: {arxiv_id}
- Year: {year}
- Authors: {authors}

## Existing Abstract Info (from abstract.md)
- TL;DR: {tldr}
- Research Question: {rq}
- Method: {method}
- Contributions: {'; '.join(contributions) if contributions else 'Not specified'}
- Results: {'; '.join(results) if results else 'Not specified'}
- Datasets: {'; '.join(datasets) if datasets else 'Not specified'}
- Limitations: {'; '.join(limitations) if limitations else 'Not specified'}
- Research Gaps: {'; '.join(research_gaps) if research_gaps else 'Not specified'}

## Paper Content Sample (first 8000 chars)
{paper_sample}

## Required Output Format
Generate a complete summary.md file with this exact structure:

```markdown
---
title: "Paper Title Here"
arXiv: "XXXXX.XXXXXvN"
authors: "Author1; Author2; Author3"
year: "YYYY"
source: "arXiv"
venue: "arXiv" (or conference/journal name if identifiable)
tags:
  - method: [inferred method tags like "graph-neural-network", "transformer", etc.]
  - application: [inferred application tags like "ocean-modeling", "data-assimilation", etc.]
difficulty: "medium" (or "low", "medium", "high" based on paper complexity)
importance: "high" (or "low", "medium", "high" based on relevance to ocean/DA/forecasting)
read_status: "skim" (or "read", "priority-read")
---

## TL;DR
[2-3 sentence summary of the paper]

## Research Question
[What problem does this paper address?]

## Method Summary
[Brief overview of the approach]

### Pipeline
[Step-by-step pipeline description]

### Core Modules
[Key architectural components]

### Technical & Physics Fusion
[How does it combine ML with domain physics?]

## Math & Physics Modeling
### Optimization Objective
[Loss function / optimization target]

### Key Equations/Physics
[Any key PDEs, physical constraints, or mathematical formulations]

## Experiments
### Datasets
- [Dataset 1]
- [Dataset 2]

### Evaluation Metrics
- [Metric 1]
- [Metric 2]

### Comparison Methods
- [Baseline 1]
- [Baseline 2]

### Core Results
- [Key finding 1]
- [Key finding 2]
- [Key finding 3]

## Strengths
- [Strength 1]
- [Strength 2]

## Weaknesses
- [Weakness 1]
- [Weakness 2]

## Research Inspiration
### Directly Reusable Modules
- [Module/technique that can be directly reused]

### Transferable Insights
- [High-level insights transferable to other research]

## Idea Extensions
1. [Extension direction 1 with 1-2 sentence description]
2. [Extension direction 2 with 1-2 sentence description]
3. [Extension direction 3 with 1-2 sentence description]

## BibTeX
```bibtex
@article{{key{year},
  title={{{title}}},
  author={{{authors}}},
  year={{{year}}},
  eprint={{{arxiv_id}}},
  archivePrefix={{arXiv}},
  primaryClass={{cs}},
  note={{arXiv preprint}}
}}
```
```

Generate ONLY the summary.md content, no additional explanation.
"""

    return prompt


def call_claude_api(prompt: str, api_key: str) -> Optional[str]:
    """Call Claude API to generate summary content."""
    # Check for custom base URL and model
    base_url = os.environ.get("ANTHROPIC_BASE_URL", "")
    model = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")

    if base_url:
        client = Anthropic(api_key=api_key, base_url=base_url)
    else:
        client = Anthropic(api_key=api_key)

    try:
        response = client.messages.create(
            model=model,
            max_tokens=4096,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        # Handle different response block types
        for block in response.content:
            if hasattr(block, 'text') and block.text:
                return block.text

        # Fallback if no text found
        return None

    except Exception as e:
        print(f"  [API ERROR] {e}")
        return None


def process_paper(year: str, paper_id: str, base_dir: Path, api_key: str) -> bool:
    """Process a single paper and generate summary.md."""
    paper_dir = base_dir / year / paper_id
    abstract_path = paper_dir / "abstract.md"
    content_path = paper_dir / "paper_content.txt"

    # Check if required files exist
    if not content_path.exists():
        print(f"  [SKIP] No paper_content.txt: {year}/{paper_id}")
        return False

    if not abstract_path.exists():
        print(f"  [SKIP] No abstract.md: {year}/{paper_id}")
        return False

    try:
        # Read files
        with open(content_path, 'r', encoding='utf-8') as f:
            paper_content = f.read()

        with open(abstract_path, 'r', encoding='utf-8') as f:
            abstract_md = f.read()

        if len(paper_content.strip()) < 100:
            print(f"  [SKIP] Content too short: {year}/{paper_id}")
            return False

        # Extract information
        content_info = extract_from_content(paper_content)
        abstract_info = extract_from_abstract(abstract_md)

        title = content_info.get('title', 'Untitled')
        arxiv_id = content_info.get('arxiv_id', paper_id.replace('v', 'v'))
        extracted_year = content_info.get('year', year)
        authors = content_info.get('authors', 'Authors not specified')

        print(f"  Processing: {title[:60]}...")

        # Build prompt and call API
        prompt = build_prompt(
            title=title,
            arxiv_id=arxiv_id,
            year=extracted_year,
            authors=authors,
            abstract_info=abstract_info,
            paper_content=paper_content
        )

        summary_content = call_claude_api(prompt, api_key)

        if not summary_content:
            print(f"  [FAILED] API call failed: {year}/{paper_id}")
            return False

        # Clean up markdown code block markers if present
        cleaned_content = summary_content.strip()
        if cleaned_content.startswith("```markdown"):
            cleaned_content = cleaned_content[len("```markdown"):].strip()
        if cleaned_content.endswith("```"):
            cleaned_content = cleaned_content[:-3].strip()

        # Write output
        output_path = paper_dir / "summary.md"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(cleaned_content)

        print(f"  [OK] Generated: {year}/{paper_id}")
        return True

    except Exception as e:
        print(f"  [ERROR] {year}/{paper_id}: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    parser = argparse.ArgumentParser(description="Generate summary.md files for arXiv papers")
    parser.add_argument("--api-key", type=str, default=None, help="Anthropic API key (or set ANTHROPIC_API_KEY env var)")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of papers to process")
    parser.add_argument("--dry-run", action="store_true", help="Test mode - show what would be processed")
    args = parser.parse_args()

    # Get API key
    api_key = args.api_key if args.api_key else get_api_key()
    if not api_key:
        print("Error: ANTHROPIC_API_KEY not found")
        print("Set it with: export ANTHROPIC_API_KEY=sk-ant-...")
        print("Or pass --api-key argument")
        sys.exit(1)

    base_dir = Path("/sharefiles1/fenglonghan/projects/claude-scholar-assimilation/papers")

    # Determine which papers to process
    papers_to_process = PAPER_LIST[:args.limit] if args.limit else PAPER_LIST

    print(f"Processing {len(papers_to_process)} papers...")
    print("=" * 60)

    if args.dry_run:
        print("\nDry run - papers that would be processed:")
        for year, paper_id in papers_to_process:
            print(f"  {year}/{paper_id}")
        return

    success = 0
    failed = 0
    skipped = 0

    # Process papers with rate limiting
    for i, (year, paper_id) in enumerate(papers_to_process):
        print(f"\n[{i+1}/{len(papers_to_process)}] ", end="", flush=True)

        result = process_paper(year, paper_id, base_dir, api_key)

        if result is True:
            success += 1
        elif result is False:
            failed += 1
        else:
            skipped += 1

        # Rate limiting - sleep between API calls to avoid rate limits
        if i < len(papers_to_process) - 1:
            time.sleep(1)  # 1 second between calls

    print("\n" + "=" * 60)
    print(f"Done: {success} succeeded, {failed} failed, {skipped} skipped")


if __name__ == "__main__":
    main()
