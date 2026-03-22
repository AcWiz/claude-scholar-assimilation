#!/usr/bin/env python3
"""
Migration script: claude-scholar-assimilation → ai-data-assimilation-papers

Migrates papers with:
- Renames paper_content.txt → arxiv_content.txt
- Creates abstract.md with YAML frontmatter + detailed notes
- Copies summary.md as-is
- Merges papers.json index
"""

import json
import os
import re
import shutil
from pathlib import Path
from typing import Dict, Set, Tuple, Optional, List

# Paths
SOURCE_ROOT = Path("/sharefiles1/fenglonghan/projects/claude-scholar-assimilation")
TARGET_ROOT = Path("/home/fenglonghan/projects/ai-data-assimilation-papers")
SOURCE_PAPERS_JSON = SOURCE_ROOT / "_data" / "papers.json"
TARGET_PAPERS_JSON = TARGET_ROOT / "_data" / "papers.json"
SOURCE_PAPERS_DIR = SOURCE_ROOT / "papers"
TARGET_PAPERS_DIR = TARGET_ROOT / "papers"


def extract_arxiv_id(arxiv_str: str) -> Optional[str]:
    """Extract arXiv ID without version (e.g., '2507.06479' from '2507.06479v1')."""
    if not arxiv_str:
        return None
    # Remove version suffix like v1, v2, etc.
    match = re.match(r'(\d{4}[._]\d{5})', arxiv_str.replace('_', '.'))
    if match:
        return match.group(1).replace('_', '.')
    # Try pure digit format
    match = re.match(r'(\d{4}\.\d{5})', arxiv_str)
    if match:
        return match.group(1)
    return None


def normalize_arxiv_for_comparison(arxiv_str: str) -> str:
    """Normalize arXiv ID for comparison (remove dots, version)."""
    base = extract_arxiv_id(arxiv_str)
    if base:
        return base.replace('.', '')
    return arxiv_str.replace('.', '').split('v')[0]


def read_yaml_frontmatter(file_path: Path) -> Tuple[Dict, str]:
    """Read YAML frontmatter from a markdown file."""
    content = file_path.read_text()
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            yaml_content = parts[1].strip()
            body = parts[2].strip()
            # Simple YAML parsing for our known fields
            data = {}
            current_key = None
            current_list = []

            for line in yaml_content.split('\n'):
                stripped = line.strip()
                if not stripped:
                    continue

                if stripped.startswith('- ') and current_key:
                    # List item
                    current_list.append(stripped[2:].strip("'\""))
                elif ':' in stripped and not stripped.startswith('-'):
                    # Save previous list if exists
                    if current_key and current_list:
                        data[current_key] = current_list
                        current_list = []

                    key, val = stripped.split(':', 1)
                    key = key.strip()
                    val = val.strip().strip("'\"")

                    if val.startswith('['):
                        # Inline list
                        items = [i.strip().strip("'\"") for i in val[1:-1].split(',')]
                        data[key] = items
                    elif val == '':
                        # Start of list
                        current_key = key
                        current_list = []
                    else:
                        data[key] = val
                        current_key = None

            # Save final list
            if current_key and current_list:
                data[current_key] = current_list

            return data, body
    return {}, content


def create_abstract_md(frontmatter: Dict, notes_content: str, paper_info: Dict = None) -> str:
    """Create new abstract.md with YAML frontmatter and notes content."""
    # Build YAML frontmatter for target
    yaml_lines = ["---"]

    # Map fields from source summary.md frontmatter to target YAML
    field_mapping = {
        'title': 'title',
        'arXiv': 'arXiv',
        'authors': 'authors',
        'year': 'year',
        'source': 'source',
        'venue': 'venue',
        'difficulty': 'difficulty',
        'importance': 'importance',
        'read_status': 'read_status',
    }

    for src_key, tgt_key in field_mapping.items():
        if src_key in frontmatter:
            val = frontmatter[src_key]
            if isinstance(val, list):
                yaml_lines.append(f"{tgt_key}:")
                for item in val:
                    yaml_lines.append(f"- {item}")
            else:
                # Normalize arXiv ID to use dots instead of underscores
                if tgt_key == 'arXiv' and isinstance(val, str):
                    val = val.replace('_', '.')
                yaml_lines.append(f"{tgt_key}: {val}")

    # Add method_tags and application_tags if present
    if 'method_tags' in frontmatter:
        val = frontmatter['method_tags']
        if isinstance(val, list):
            yaml_lines.append("method_tags:")
            for item in val:
                yaml_lines.append(f"- {item}")
        else:
            yaml_lines.append(f"method_tags: {val}")

    if 'application_tags' in frontmatter:
        val = frontmatter['application_tags']
        if isinstance(val, list):
            yaml_lines.append("application_tags:")
            for item in val:
                yaml_lines.append(f"- {item}")
        else:
            yaml_lines.append(f"application_tags: {val}")

    # Add new fields (empty)
    yaml_lines.append("ocean_vars: Unknown")
    yaml_lines.append("spatiotemporal_res: Unknown")

    yaml_lines.append("---")
    yaml_lines.append("")

    # Combine with notes content
    return "\n".join(yaml_lines) + notes_content


def migrate_paper(src_dir: Path, tgt_dir: Path, dry_run: bool = False) -> Tuple[str, str, Optional[Dict]]:
    """
    Migrate a single paper directory.
    Returns (status, arxiv_id, paper_info_for_json)
    """
    # Get arXiv ID from directory name
    dir_name = src_dir.name
    arxiv_id = None

    # Try various formats
    for pattern in [
        # New format: 4 digits + . + 5 digits (e.g., 2308.11814)
        r'(\d{4}_\d{5})v?\d*',
        r'(\d{4}\.\d{5})v?\d*',
        # Old format: 4 digits + . + 4 digits (e.g., 1108.0168)
        r'(\d{4}_\d{4})v?\d*',
        r'(\d{4}\.\d{4})v?\d*',
    ]:
        match = re.match(pattern, dir_name)
        if match:
            raw = match.group(1)
            arxiv_id = raw.replace('_', '.')
            break

    if not arxiv_id:
        print(f"  WARNING: Could not extract arXiv ID from {dir_name}")
        arxiv_id = dir_name

    # Read source files
    abstract_src = src_dir / "abstract.md"
    summary_src = src_dir / "summary.md"
    content_src = src_dir / "paper_content.txt"

    if not abstract_src.exists():
        print(f"  SKIP: No abstract.md in {src_dir}")
        return 'skipped', arxiv_id, None

    # Read source abstract.md content (no YAML frontmatter expected)
    notes_content = abstract_src.read_text()

    # Read source summary.md for YAML frontmatter
    frontmatter = {}
    if summary_src.exists():
        fm, _ = read_yaml_frontmatter(summary_src)
        frontmatter = fm

    if dry_run:
        print(f"  Would migrate: {arxiv_id}")
        return 'migrated', arxiv_id, None

    # Create target directory
    tgt_dir.mkdir(parents=True, exist_ok=True)

    # Copy and rename paper_content.txt -> arxiv_content.txt
    if content_src.exists():
        shutil.copy2(content_src, tgt_dir / "arxiv_content.txt")

    # Create new abstract.md with YAML frontmatter
    new_abstract = create_abstract_md(frontmatter, notes_content)
    (tgt_dir / "abstract.md").write_text(new_abstract)

    # Copy summary.md as-is
    if summary_src.exists():
        shutil.copy2(summary_src, tgt_dir / "summary.md")

    # Build paper info for JSON
    paper_info = {
        'path': f"papers/{tgt_dir.parent.name}/{arxiv_id}",
        'year': int(tgt_dir.parent.name),
        'title': frontmatter.get('title', ''),
        'arxiv': arxiv_id,
        'authors': frontmatter.get('authors', []),
        'source': frontmatter.get('source', 'arXiv'),
        'venue': frontmatter.get('venue', ''),
        'method_tags': frontmatter.get('method_tags', []),
        'application_tags': frontmatter.get('application_tags', []),
        'date_collected': '2026-03-22',
        'paper_url': '',
        'abstract_preview': notes_content[:200] + '...' if len(notes_content) > 200 else notes_content,
    }

    return 'migrated', arxiv_id, paper_info


def load_papers_json(path: Path) -> Dict:
    """Load papers.json."""
    if path.exists():
        return json.loads(path.read_text())
    return {"papers": []}


def save_papers_json(path: Path, data: Dict):
    """Save papers.json."""
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False))


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Migrate papers from source to target')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without making changes')
    args = parser.parse_args()

    print("=" * 60)
    print("Paper Migration: claude-scholar-assimilation → ai-data-assimilation-papers")
    print("=" * 60)

    # Load source papers.json
    source_data = load_papers_json(SOURCE_PAPERS_JSON)
    source_papers = source_data.get('papers', [])
    print(f"\nSource papers.json: {len(source_papers)} papers")

    # Load target papers.json
    target_data = load_papers_json(TARGET_PAPERS_JSON)
    target_papers_list = target_data.get('papers', [])
    print(f"Target papers.json: {len(target_papers_list)} papers")

    # Build dict of existing target papers by normalized arxiv
    target_papers_by_arxiv = {}
    for p in target_papers_list:
        arxiv = p.get('arxiv', '')
        norm = normalize_arxiv_for_comparison(arxiv)
        target_papers_by_arxiv[norm] = p

    print(f"Target unique arXiv IDs: {len(target_papers_by_arxiv)}")

    # Migrate papers directory by directory
    migrated_count = 0
    updated_count = 0
    skipped_count = 0

    new_paper_entries = []  # List of (normalized_arxiv, entry)

    for year_dir in sorted(SOURCE_PAPERS_DIR.iterdir()):
        if not year_dir.is_dir():
            continue
        year = year_dir.name
        if not year.isdigit():
            continue

        for paper_dir in sorted(year_dir.iterdir()):
            if not paper_dir.is_dir():
                continue

            print(f"\n[{year}] {paper_dir.name}")

            # Determine arXiv ID
            dir_name = paper_dir.name
            arxiv_id = None
            for pattern in [
                # New format: 4 digits + . + 5 digits (e.g., 2308.11814)
                r'(\d{4}_\d{5})v?\d*',
                r'(\d{4}\.\d{5})v?\d*',
                # Old format: 4 digits + . + 4 digits (e.g., 1108.0168)
                r'(\d{4}_\d{4})v?\d*',
                r'(\d{4}\.\d{4})v?\d*',
            ]:
                match = re.match(pattern, dir_name)
                if match:
                    raw = match.group(1)
                    arxiv_id = raw.replace('_', '.')
                    break

            if not arxiv_id:
                print(f"  WARNING: Could not extract arXiv ID, using dir name")
                arxiv_id = dir_name

            norm_arxiv = normalize_arxiv_for_comparison(arxiv_id)
            target_dir = TARGET_PAPERS_DIR / year / arxiv_id

            # Check if already exists
            if norm_arxiv in target_papers_by_arxiv:
                print(f"  -> Already exists (will update): {target_dir.relative_to(TARGET_ROOT)}")
                status = 'updated'
                updated_count += 1
            else:
                print(f"  -> New: {target_dir.relative_to(TARGET_ROOT)}")
                status = 'new'
                migrated_count += 1

            result, migrated_arxiv, paper_info = migrate_paper(
                paper_dir, target_dir, dry_run=args.dry_run
            )

            if paper_info:
                new_paper_entries.append((norm_arxiv, paper_info))

    print(f"\n{'=' * 60}")
    print(f"Migration Summary (dry_run={args.dry_run}):")
    print(f"  New papers: {migrated_count}")
    print(f"  Updated papers: {updated_count}")
    print(f"  Skipped: {skipped_count}")

    if not args.dry_run and new_paper_entries:
        # Merge papers.json
        print(f"\nMerging papers.json...")

        # Build updated target papers list
        updated_target_papers = []
        entries_by_arxiv = {arxiv: entry for arxiv, entry in new_paper_entries}

        # Add existing papers that are NOT being updated
        for p in target_papers_list:
            p_arxiv_norm = normalize_arxiv_for_comparison(p.get('arxiv', ''))
            if p_arxiv_norm not in entries_by_arxiv:
                updated_target_papers.append(p)

        # Add new/updated entries
        for arxiv_norm, entry in entries_by_arxiv.items():
            updated_target_papers.append(entry)

        # Sort by year descending, then by title
        updated_target_papers.sort(key=lambda x: (-x.get('year', 0), x.get('title', '')))

        # Update statistics
        by_year = {}
        by_method = {}
        by_application = {}
        for p in updated_target_papers:
            year = str(p.get('year', ''))
            by_year[year] = by_year.get(year, 0) + 1
            for tag in p.get('method_tags', []):
                by_method[tag] = by_method.get(tag, 0) + 1
            for tag in p.get('application_tags', []):
                by_application[tag] = by_application.get(tag, 0) + 1

        target_data['papers'] = updated_target_papers
        target_data['statistics'] = {
            'total': len(updated_target_papers),
            'by_year': by_year,
            'by_method': by_method,
            'by_application': by_application,
        }
        target_data['last_updated'] = '2026-03-22T00:00:00.000000'

        save_papers_json(TARGET_PAPERS_JSON, target_data)
        print(f"  Updated papers.json with {len(updated_target_papers)} total papers")

    print(f"\n{'=' * 60}")
    print("Migration complete!")


if __name__ == '__main__':
    main()
