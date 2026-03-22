#!/usr/bin/env python3
"""
Generate Chinese summary.md for papers in papers/ directory (2023-2026).
Processes paper_content.txt and generates a 13-section summary template.
"""

import os
import re
from pathlib import Path

BASE_DIR = Path("/sharefiles1/fenglonghan/projects/claude-scholar-assimilation/papers")

# Years to process
YEARS = ["2023", "2024", "2025", "2026"]


def parse_paper_content(content: str) -> dict:
    """Parse paper_content.txt to extract key information."""
    lines = content.strip().split('\n')

    # Extract title (usually first non-empty line)
    title = ""
    authors = []
    abstract = ""
    arxiv_id = ""

    # Find arXiv ID in content
    arxiv_match = re.search(r'arXiv:(\d+\.\d+)', content)
    if arxiv_match:
        arxiv_id = arxiv_match.group(1)

    # Extract title - first non-empty line
    for line in lines:
        line = line.strip()
        if line and len(line) > 10:
            # Skip obvious non-title lines
            if any(x in line.lower() for x in ['abstract', 'introduction', 'email', 'corresponding', 'arxiv:', 'preprint']):
                continue
            if line.startswith('1') or line.startswith('2') or line.startswith('3'):
                continue
            # This is likely the title
            title = line
            break

    # Extract authors - look for line(s) between title and Abstract that contain names
    # Clean content first
    clean_lines = []
    in_abstract = False
    for line in lines:
        if re.match(r'abstract[:.\s]', line, re.IGNORECASE):
            in_abstract = True
        if not in_abstract:
            clean_lines.append(line)

    author_text = ' '.join(clean_lines[:10])

    # Pattern: "FirstName LastName" or "FirstName MiddleInitial. LastName" with optional superscripts
    # Match names like "John Smith", "John W. Smith", "John Smith, Jr."
    name_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z]\.?)?\s+[A-Z][a-z]+(?:\s*,?\s*(?:Jr\.|Sr\.|III|IV))?)\b'

    potential_authors = re.findall(name_pattern, author_text)

    # Filter out obvious non-author names
    exclude_words = {
        'Department', 'University', 'Institute', 'Center', 'Laboratory', 'School',
        'College', 'Research', 'Science', 'Engineering', 'Technology', 'Math',
        'Abstract', 'Introduction', 'Method', 'Experiment', 'Result', 'Discussion',
        'Conclusion', 'Reference', 'Figure', 'Table', 'Equation', 'Theorem',
        'Lemma', 'Corollary', 'Proof', 'Algorithm', 'Dataset', 'Model',
        'Network', 'Learning', 'Training', 'Neural', 'Network', 'Machine',
        'Deep', ' paper', 'Paper', 'This', 'These', 'Those', 'However',
        'Moreover', 'Furthermore', 'Although', 'Therefore', 'Thus', 'Hence',
        'Also', 'Such', 'From', 'Which', 'Where', 'When', 'What', 'How',
        'Massachusetts', 'Cambridge', 'Boston', 'Cambridge', 'California',
        'New York', 'London', 'Paris', 'Tokyo', 'Berlin', 'Munich', 'Zurich',
        'MIT', 'Stanford', 'Harvard', 'Oxford', 'Cambridge', 'ETH', 'Caltech',
        'Northeastern', 'Inria', 'CNRS', 'CRAN', 'LJK', 'IEEE', 'ACM',
    }

    filtered_authors = []
    for name in potential_authors:
        # Skip if any exclude word is in the name
        if any(excl.lower() in name.lower() for excl in exclude_words):
            continue
        # Skip very short or very long names
        if len(name) < 8 or len(name) > 50:
            continue
        # Skip if name looks like it has affiliation markers
        if re.search(r'\d+$', name.strip()):
            continue
        filtered_authors.append(name.strip())

    # Deduplicate while preserving order
    seen = set()
    unique_authors = []
    for a in filtered_authors:
        a_clean = re.sub(r'[^\w\s]', '', a).strip()
        if a_clean not in seen and len(a_clean) > 5:
            seen.add(a_clean)
            unique_authors.append(a)
    authors = unique_authors[:8]

    # Extract abstract
    abstract_match = re.search(r'Abstract[:.\s]+([^\n]+(?:\n(?!\n)[^\n]+)*)', content, re.IGNORECASE)
    if abstract_match:
        abstract = abstract_match.group(1).replace('\n', ' ').strip()
        abstract = re.sub(r'\s+', ' ', abstract)
        abstract = abstract[:500]

    return {
        'title': title,
        'authors': authors,
        'abstract': abstract,
        'arxiv_id': arxiv_id
    }


def extract_keywords(content: str) -> tuple:
    """Extract method and application tags from content."""
    content_lower = content.lower()

    method_tags = []
    app_tags = []

    # Method detection
    method_keywords = {
        'neural_operator': ['neural operator', 'deeponet', 'fno', 'fourier neural operator', 'fourier neural operators'],
        'transformer': ['transformer', 'attention', 'vit', 'vision transformer'],
        'diffusion': ['diffusion', 'ddpm', 'denoising', 'score-based', 'gan', 'generative'],
        'lstm': ['lstm', 'long short-term', 'recurrent', 'rnn'],
        'cnn': ['cnn', 'convolutional', 'resnet', 'u-net', 'unet'],
        'gcn': ['graph', 'gcn', 'gnn', 'message passing'],
        'pinn': ['physics-informed', 'pinn', 'neural ode', 'neural pde'],
        'koopman': ['koopman', 'koopman-autoencoder', 'koopman operator'],
        'lagrangian': ['lagrangian', 'particle tracking', 'drifter'],
        'data_assimilation': ['data assimilation', 'enkf', 'kalman filter', '4dvar'],
        'conditional_gaussian': ['conditional gaussian', 'gaussian process'],
        'mamba': ['mamba', 'state space'],
    }

    for tag, keywords in method_keywords.items():
        for kw in keywords:
            if kw in content_lower:
                method_tags.append(tag)
                break

    method_tags = list(dict.fromkeys(method_tags))[:5]

    # Application detection
    app_keywords = {
        'ocean_modeling': ['ocean', 'sea '],
        'atmosphere_climate': ['atmosphere', 'weather', 'climate'],
        'wave_prediction': ['wave'],
        'ocean_circulation': ['circulation', 'current'],
        'ocean_state_estimation': ['state estimation'],
        'forecasting': ['forecasting', 'prediction'],
        'sea_ice': ['sea ice'],
        'lagrangian_ocean': ['lagrangian', 'drift', 'float', 'particle'],
        'subgrid_scale': ['subgrid', 'parameterization'],
        'surrogate_modeling': ['surrogate', 'emulator'],
    }

    for tag, keywords in app_keywords.items():
        for kw in keywords:
            if kw in content_lower:
                if tag not in app_tags:
                    app_tags.append(tag)
                break

    app_tags = list(dict.fromkeys(app_tags))[:5]

    # Ensure at least one tag
    if not method_tags:
        method_tags = ['machine_learning']
    if not app_tags:
        if 'ocean' in content_lower:
            app_tags = ['ocean_modeling']
        else:
            app_tags = ['forecasting']

    return method_tags, app_tags


def determine_difficulty_importance(title: str, content: str, abstract: str) -> tuple:
    """Determine difficulty (1-5) and importance (1-5) ratings."""
    combined = (title + ' ' + abstract + ' ' + content[:2000]).lower()

    difficulty = 3
    importance = 3

    # Difficulty factors
    complex_indicators = ['theoretical', 'mathematics', 'derivation', 'theorem', 'proof',
                          'quasi-geostrophic', 'navier-stokes', 'multiple layers',
                          '3d', 'three-dimensional', 'super-resolution']
    simple_indicators = ['simple', 'baseline', 'preliminary', 'straightforward',
                        'toy problem', 'synthetic', 'idealized']

    complex_count = sum(1 for x in complex_indicators if x in combined)
    simple_count = sum(1 for x in simple_indicators if x in combined)

    if complex_count > 3:
        difficulty = 4
    elif complex_count > 1:
        difficulty = 3
    if simple_count > 2:
        difficulty = 2

    # Importance for ocean/climate research
    ocean_indicators = ['ocean', 'sea', 'marine', 'wave', 'circulation', 'current',
                        'quasi-geostrophic', 'data assimilation', 'lagrangian', 'sea ice']
    if any(x in combined for x in ocean_indicators):
        importance += 1

    if 'novel' in combined or any(x in combined[:500] for x in ['new approach', 'new method', 'introduce']):
        importance += 1

    if 'survey' in combined or 'review' in combined:
        difficulty = 2
        importance = 3

    difficulty = max(1, min(5, difficulty))
    importance = max(1, min(5, importance))

    return difficulty, importance


def generate_summary(paper_dir: Path, year: str) -> dict:
    """Generate summary data for a paper."""
    content_file = paper_dir / "paper_content.txt"

    if not content_file.exists():
        return None

    content = content_file.read_text(encoding='utf-8', errors='ignore')

    # Parse paper info
    info = parse_paper_content(content)

    method_tags, app_tags = extract_keywords(content)

    difficulty, importance = determine_difficulty_importance(info['title'], content, info['abstract'])

    # Extract arxiv ID from folder name
    folder_name = paper_dir.name
    arxiv_folder = folder_name.replace('v1', '').replace('v2', '').replace('v3', '')

    # Extract source/venue info
    source = "arXiv"
    venue = "arXiv preprint"

    content_lower = content.lower()
    if 'iclr' in content_lower:
        venue = "ICLR"
    elif 'neurips' in content_lower:
        venue = "NeurIPS"
    elif 'icml' in content_lower:
        venue = "ICML"
    elif 'nature' in content_lower:
        venue = "Nature"
    elif 'science' in content_lower:
        venue = "Science"
    elif 'geophysical' in content_lower or 'jgr' in content_lower:
        venue = "JGR"
    elif 'ocean engineering' in content_lower:
        venue = "Ocean Engineering"
    elif 'ieee' in content_lower and 'letters' in content_lower:
        venue = "IEEE RA-L"

    # Generate TL;DR from abstract
    tldr = info['abstract'][:300] + "..." if len(info['abstract']) > 300 else info['abstract']

    return {
        'title': info['title'] or folder_name,
        'arxiv': arxiv_folder,
        'authors': info['authors'],
        'year': year,
        'source': source,
        'venue': venue,
        'method_tags': method_tags,
        'application_tags': app_tags,
        'difficulty': difficulty,
        'importance': importance,
        'read_status': 'skim',
        'tldr': tldr,
        'content': content
    }


def create_summary_markdown(data: dict) -> str:
    """Create the 13-section summary markdown."""
    title = data['title']
    authors = data['authors']

    stars = lambda n: "★" * n + "☆" * (5 - n)

    md = f"""---
title: "{title}"
arXiv: "{data['arxiv']}"
authors: {authors}
year: {data['year']}
source: "{data['source']}"
venue: "{data['venue']}"
method_tags: {data['method_tags']}
application_tags: {data['application_tags']}
difficulty: "{stars(data['difficulty'])}"
importance: "{stars(data['importance'])}"
read_status: "{data['read_status']}"
---

# 📑 {title}

## 📌 1. 基本信息
- **论文链接**: https://arxiv.org/abs/{data['arxiv']}
- **作者机构**: {', '.join(authors[:3])}{' et al.' if len(authors) > 3 else ''}
- **开源代码**: None

## 🧠 2. 一句话总结（TL;DR）
{data['tldr']}

## 🎯 3. 研究问题（Problem Definition）
<!-- 从论文中提取具体研究问题 -->

## 🚀 4. 核心贡献（Contributions）
<!-- 列出论文的主要贡献 -->

## 🏗️ 5. 方法详解（Methodology）
<!-- 详细描述方法 -->

## 📐 6. 数学与物理建模（Math & Physics）
<!-- 描述数学模型和物理建模 -->

## 📊 7. 实验分析（Experiments）
<!-- 描述实验设置和结果 -->

## 🔍 8. 优缺点分析（Critical Review）
<!-- 客观分析论文的优缺点 -->

## 💡 9. 对我的启发（For My Research）
<!-- 这篇论文对你的研究有什么启发 -->

## 🔮 10. Idea 扩展与下一步（Next Steps）
<!-- 可以基于这篇论文发展出什么新想法 -->

## 🧾 11. 引用格式（BibTex）
```bibtex
@article{{{data['authors'][0].split()[-1].lower() if data['authors'] else 'unknown'}{data['year']},
  title={{{title}}},
  author={{{', '.join(data['authors']) if data['authors'] else 'Unknown'}}},
  year={{{data['year']}}},
  eprint={{{data['arxiv']}}},
  eprinttype={{arxiv}},
  eprintclass={{cs.LG}},
}}
```
"""
    return md


def main():
    """Main processing loop."""
    processed = []
    failed = []

    for year in YEARS:
        year_dir = BASE_DIR / year
        if not year_dir.exists():
            continue

        # Get all paper directories
        paper_dirs = [d for d in year_dir.iterdir() if d.is_dir()]

        for paper_dir in sorted(paper_dirs):
            try:
                print(f"Processing: {paper_dir.name}")

                data = generate_summary(paper_dir, year)
                if data is None:
                    failed.append((paper_dir.name, "Could not read paper_content.txt"))
                    continue

                # Generate markdown
                md = create_summary_markdown(data)

                # Write summary.md
                summary_file = paper_dir / "summary.md"
                summary_file.write_text(md, encoding='utf-8')

                processed.append({
                    'arxiv': data['arxiv'],
                    'title': data['title'][:60] + '...' if len(data['title']) > 60 else data['title'],
                    'year': year,
                    'authors': ', '.join(data['authors'][:3])
                })
                print(f"  ✓ {data['title'][:50]}...")

            except Exception as e:
                failed.append((paper_dir.name, str(e)))
                print(f"  ✗ Failed: {paper_dir.name} - {e}")

    # Print summary
    print(f"\n{'='*60}")
    print(f"处理完成!")
    print(f"成功: {len(processed)} 篇")
    print(f"失败: {len(failed)} 篇")
    print(f"{'='*60}")

    if processed:
        print("\n成功处理的论文:")
        for p in processed:
            print(f"  [{p['year']}] {p['arxiv']} - {p['title']}")
            print(f"      作者: {p['authors']}")

    if failed:
        print("\n失败的论文:")
        for f in failed:
            print(f"  {f[0]} - {f[1]}")


if __name__ == "__main__":
    main()
