#!/usr/bin/env python3
"""
Phase 2 Migration: Cleanup slugified directories in ai-data-assimilation-papers

This script:
1. Scans target papers directory for slugified directories
2. For directories with papers.json entries: use the arXiv ID from JSON
3. For orphaned directories: extract arXiv ID from abstract.md content
4. Renames directories to proper arXiv ID format
5. Copies summary.md from source if available
6. Updates papers.json with new paths
"""

import json
import os
import re
import shutil
from pathlib import Path
from typing import Dict, Optional, Tuple

# Paths
SOURCE_ROOT = Path("/sharefiles1/fenglonghan/projects/claude-scholar-assimilation")
TARGET_ROOT = Path("/home/fenglonghan/projects/ai-data-assimilation-papers")
TARGET_PAPERS_JSON = TARGET_ROOT / "_data" / "papers.json"
TARGET_PAPERS_DIR = TARGET_ROOT / "papers"


def extract_arxiv_id(arxiv_str: str) -> Optional[str]:
    """Extract and normalize arXiv ID (e.g., '2601.01501' from '2601.01501v1')."""
    if not arxiv_str:
        return None
    # Match patterns like 2601.01501, 2601_01501, 2601.01501v1, 2601_01501v1
    match = re.match(r'(\d{4}[._]\d{5})v?\d*', arxiv_str)
    if match:
        base = match.group(1)
        return base.replace('_', '.')
    return None


def normalize_arxiv_for_comparison(arxiv_str: str) -> str:
    """Normalize arXiv ID for comparison (remove dots, version)."""
    base = extract_arxiv_id(arxiv_str)
    if base:
        return base.replace('.', '')
    return arxiv_str.replace('.', '').split('v')[0]


def is_slugified_dir(dir_name: str) -> bool:
    """Check if directory name is slugified (not proper arXiv ID format)."""
    # Proper format: 4 digits + . + 5 digits (with optional version)
    # e.g., 2601.01501, 2601.01501v1
    if len(dir_name) >= 9:
        if dir_name[4] == '.':
            # Check digits
            if dir_name[:4].isdigit() and dir_name[5:].replace('.', '').replace('v', '').isdigit():
                return False
    return True


def extract_arxiv_from_abstract(abstract_path: Path) -> Optional[str]:
    """Try to extract arXiv ID from abstract.md content (including YAML frontmatter)."""
    if not abstract_path.exists():
        return None
    content = abstract_path.read_text()

    # First try YAML frontmatter
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 2:
            yaml_part = parts[1]
            # Look for arXiv: or arXiv ID pattern
            match = re.search(r'arXiv:\s*(\d{4}[._]\d{5})v?\d*', yaml_part)
            if match:
                arxiv = match.group(1).replace('_', '.')
                if '.' in arxiv:
                    return arxiv

    # Try content body - look for arXiv URL or ID pattern
    # Pattern: https://arxiv.org/abs/YYMM.NNNNN or bare YYMM.NNNNN
    match = re.search(r'(?:https?://arxiv\.org/abs/)?(\d{4}\.\d{5})', content)
    if match:
        return match.group(1)

    # Try format YYMM_NNNNN
    match = re.search(r'(\d{4}_\d{5})', content)
    if match:
        return match.group(1).replace('_', '.')

    return None


def find_source_paper(arxiv_id: str, year: str) -> Optional[Path]:
    """Find source paper in claude-scholar-assimilation by arxiv ID."""
    # Normalize arxiv_id for directory matching (source uses underscores)
    normalized = arxiv_id.replace('.', '_')

    # Try various version formats
    source_root = SOURCE_ROOT / "papers"
    if not source_root.exists():
        return None

    # First check the specified year
    year_dir = source_root / year
    if year_dir.exists():
        for d in year_dir.iterdir():
            if d.is_dir():
                # Check if directory name starts with the normalized arxiv
                if d.name.startswith(normalized) or d.name.startswith(arxiv_id.replace('.', '_')):
                    return d

    # Search all years if not found
    for year_dir in source_root.iterdir():
        if not year_dir.is_dir() or not year_dir.name.isdigit():
            continue
        for d in year_dir.iterdir():
            if d.is_dir():
                if d.name.startswith(normalized) or d.name.startswith(arxiv_id.replace('.', '_')):
                    return d

    return None


def load_papers_json(path: Path) -> Dict:
    """Load papers.json."""
    if path.exists():
        return json.loads(path.read_text())
    return {"papers": []}


def save_papers_json(path: Path, data: Dict):
    """Save papers.json."""
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False))


def process_slugified_dir(
    slug_dir: Path,
    target_arxiv: Optional[str] = None,
    dry_run: bool = False
) -> Tuple[str, Optional[str], Optional[Dict]]:
    """
    Process a single slugified directory.

    Args:
        slug_dir: Path to the slugified directory
        target_arxiv: arXiv ID from papers.json (if available)
        dry_run: If True, only show what would be done

    Returns: (status, new_arxiv_id, paper_info_for_json)
    """
    year = slug_dir.parent.name
    new_arxiv_id = None

    # Try to get arXiv ID from papers.json first, then from abstract.md
    if target_arxiv:
        new_arxiv_id = extract_arxiv_id(target_arxiv)

    if not new_arxiv_id:
        # Try to extract from abstract.md
        abstract_path = slug_dir / "abstract.md"
        new_arxiv_id = extract_arxiv_from_abstract(abstract_path)

    if not new_arxiv_id:
        print(f"  ERROR: Could not extract arXiv ID")
        return 'error', None, None

    new_dir = slug_dir.parent / new_arxiv_id

    if dry_run:
        print(f"  Would rename: {slug_dir.name} -> {new_arxiv_id}")
        if new_dir.exists():
            print(f"    (target already exists)")
        return 'renamed', new_arxiv_id, None

    # Check if source paper exists
    source_paper = find_source_paper(new_arxiv_id, year)
    source_has_summary = False
    if source_paper and (source_paper / "summary.md").exists():
        source_has_summary = True
        print(f"  Found source with summary.md: {source_paper.relative_to(SOURCE_ROOT)}")

    # Check if we already have summary.md in target
    target_has_summary = (slug_dir / "summary.md").exists()

    # Copy summary.md from source if available and target doesn't have it
    if source_has_summary and not target_has_summary:
        shutil.copy2(source_paper / "summary.md", slug_dir / "summary.md")
        print(f"  Copied summary.md from source")

    # Copy paper_content.txt if it exists in source but not in target
    if source_paper:
        source_content = source_paper / "paper_content.txt"
        target_content = slug_dir / "arxiv_content.txt"
        if source_content.exists() and not target_content.exists():
            shutil.copy2(source_content, target_content)
            print(f"  Copied paper_content.txt -> arxiv_content.txt")

    # Rename directory
    if new_dir.exists():
        print(f"  Target already exists: {new_dir.relative_to(TARGET_ROOT)}")
        return 'exists', new_arxiv_id, None

    shutil.move(str(slug_dir), str(new_dir))
    print(f"  Renamed: {slug_dir.name} -> {new_arxiv_id}")

    return 'renamed', new_arxiv_id, None


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Cleanup slugified paper directories')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done')
    args = parser.parse_args()

    print("=" * 70)
    print("Phase 2: Cleanup slugified directories in ai-data-assimilation-papers")
    print("=" * 70)

    # Load papers.json
    data = load_papers_json(TARGET_PAPERS_JSON)
    papers_list = data.get('papers', [])
    print(f"\nTotal papers in papers.json: {len(papers_list)}")

    # Build mapping from slugified path -> paper entry
    slugified_entries = {}  # dir_name -> paper_entry
    proper_entries = {}     # dir_name -> paper_entry
    all_entries_by_arxiv_norm = {}  # normalized_arxiv -> paper_entry (for matching)

    for p in papers_list:
        path = p.get('path', '')
        if path and '/' in path:
            dir_name = path.split('/')[-1]
            arxiv = p.get('arxiv', '')
            norm = normalize_arxiv_for_comparison(arxiv)

            if is_slugified_dir(dir_name):
                slugified_entries[dir_name] = p
                all_entries_by_arxiv_norm[norm] = p
            else:
                proper_entries[dir_name] = p
                all_entries_by_arxiv_norm[norm] = p

    print(f"Proper arXiv ID entries: {len(proper_entries)}")
    print(f"Slugified entries in JSON: {len(slugified_entries)}")

    # Find slugified directories in target filesystem
    slugified_dirs = []
    for year_dir in sorted(TARGET_PAPERS_DIR.iterdir()):
        if not year_dir.is_dir() or not year_dir.name.isdigit():
            continue
        for paper_dir in sorted(year_dir.iterdir()):
            if paper_dir.is_dir() and is_slugified_dir(paper_dir.name):
                slugified_dirs.append((year_dir.name, paper_dir))

    print(f"\nSlugified directories found in filesystem: {len(slugified_dirs)}")

    # Process each slugified directory
    renamed_count = 0
    error_count = 0
    skipped_count = 0
    entries_to_update = []

    for year, dir_name in slugified_dirs:
        print(f"\n[{year}] {dir_name}")

        slug_dir = TARGET_PAPERS_DIR / year / dir_name

        # Try to find matching entry in papers.json
        target_arxiv = None
        paper_entry = None

        if dir_name in slugified_entries:
            # Direct match by directory name
            paper_entry = slugified_entries[dir_name]
            target_arxiv = paper_entry.get('arxiv', '')
            print(f"  Found in papers.json: arXiv={target_arxiv}")
        else:
            # Try to find by extracting arXiv from abstract and matching
            abstract_path = slug_dir / "abstract.md"
            extracted_arxiv = extract_arxiv_from_abstract(abstract_path)
            if extracted_arxiv:
                norm = normalize_arxiv_for_comparison(extracted_arxiv)
                if norm in all_entries_by_arxiv_norm:
                    paper_entry = all_entries_by_arxiv_norm[norm]
                    target_arxiv = paper_entry.get('arxiv', '')
                    print(f"  Matched via abstract extraction: arXiv={target_arxiv}")
                else:
                    print(f"  Extracted arXiv={extracted_arxiv} but no JSON entry")
            else:
                print(f"  No papers.json entry and cannot extract arXiv from abstract")

        if not target_arxiv and not extracted_arxiv:
            print(f"  SKIP: No arXiv ID available")
            error_count += 1
            continue

        status, new_arxiv_id, _ = process_slugified_dir(
            slug_dir, target_arxiv or extracted_arxiv, dry_run=args.dry_run
        )

        if status == 'renamed' and paper_entry:
            renamed_count += 1
            # Update papers.json entry
            paper_entry['path'] = f"papers/{year}/{new_arxiv_id}"
            paper_entry['arxiv'] = new_arxiv_id
            entries_to_update.append(paper_entry)
        elif status == 'exists' and paper_entry:
            # Directory already exists, update papers.json
            paper_entry['path'] = f"papers/{year}/{new_arxiv_id}"
            paper_entry['arxiv'] = new_arxiv_id
            entries_to_update.append(paper_entry)
        elif status == 'renamed' and not paper_entry:
            # No JSON entry, but directory was renamed
            renamed_count += 1
        elif status == 'error':
            error_count += 1

    print(f"\n{'=' * 70}")
    print(f"Summary (dry_run={args.dry_run}):")
    print(f"  Renamed directories: {renamed_count}")
    print(f"  Errors: {error_count}")
    print(f"  Skipped: {skipped_count}")
    print(f"  Papers.json entries to update: {len(entries_to_update)}")

    if not args.dry_run and entries_to_update:
        print(f"\nUpdating papers.json...")

        # Build set of updated arxiv IDs
        updated_arxiv_norms = {normalize_arxiv_for_comparison(p['arxiv']) for p in entries_to_update}

        # Update papers list: replace entries that were updated
        updated_papers = []
        processed_norms = set()

        for p in papers_list:
            arxiv = p.get('arxiv', '')
            norm = normalize_arxiv_for_comparison(arxiv)

            # Check if this entry was updated
            if norm in updated_arxiv_norms and norm not in processed_norms:
                # Find the updated version
                for up in entries_to_update:
                    if normalize_arxiv_for_comparison(up['arxiv']) == norm:
                        updated_papers.append(up)
                        processed_norms.add(norm)
                        break
            else:
                updated_papers.append(p)

        # Sort by year descending, then by title
        updated_papers.sort(key=lambda x: (-x.get('year', 0), x.get('title', '')))

        # Update statistics
        by_year = {}
        by_method = {}
        by_application = {}
        for p in updated_papers:
            year = str(p.get('year', ''))
            by_year[year] = by_year.get(year, 0) + 1
            for tag in p.get('method_tags', []):
                by_method[tag] = by_method.get(tag, 0) + 1
            for tag in p.get('application_tags', []):
                by_application[tag] = by_application.get(tag, 0) + 1

        data['papers'] = updated_papers
        data['statistics'] = {
            'total': len(updated_papers),
            'by_year': by_year,
            'by_method': by_method,
            'by_application': by_application,
        }
        data['last_updated'] = '2026-03-22T00:00:00.000000'

        save_papers_json(TARGET_PAPERS_JSON, data)
        print(f"  Updated papers.json with {len(updated_papers)} total papers")

    # Verify final state
    print(f"\n{'=' * 70}")
    print("Verification:")

    remaining_slugified = []
    for year_dir in sorted(TARGET_PAPERS_DIR.iterdir()):
        if not year_dir.is_dir() or not year_dir.name.isdigit():
            continue
        for paper_dir in sorted(year_dir.iterdir()):
            if paper_dir.is_dir() and is_slugified_dir(paper_dir.name):
                remaining_slugified.append(f"{year_dir.name}/{paper_dir.name}")

    print(f"  Remaining slugified directories: {len(remaining_slugified)}")
    if remaining_slugified:
        for d in remaining_slugified[:10]:
            print(f"    - {d}")
        if len(remaining_slugified) > 10:
            print(f"    ... and {len(remaining_slugified) - 10} more")

    print(f"\n{'=' * 70}")
    print("Done!")


if __name__ == '__main__':
    main()
