#!/usr/bin/env python3
"""
Update Papers Index

更新论文索引，添加缺失的元数据字段。
"""

import argparse
import json
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def load_index(index_path: Path) -> dict:
    """加载索引"""
    if index_path.exists():
        with open(index_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"papers": [], "metadata": {}}


def save_index(index_path: Path, index: dict) -> None:
    """保存索引"""
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)


def normalize_paper(paper: dict) -> dict:
    """规范化论文数据"""
    normalized = {}

    # 必填字段
    normalized["arxiv_id"] = paper.get("arxiv_id", "")
    normalized["title"] = paper.get("title", "Untitled")

    # 可选字段
    normalized["arxiv_url"] = paper.get("arxiv_url", "")
    normalized["authors"] = paper.get("authors", [])
    normalized["published"] = paper.get("published", "")
    normalized["year"] = paper.get("year", 2024)
    normalized["categories"] = paper.get("categories", [])
    normalized["abstract"] = paper.get("abstract", "")
    normalized["doi"] = paper.get("doi", "")
    normalized["comment"] = paper.get("comment", "")

    # 来源
    normalized["source"] = "arxiv" if normalized["arxiv_id"] else "other"

    return normalized


def update_index(verify_existence: bool = False) -> dict:
    """更新索引"""
    index_path = Path(__file__).parent.parent / "_data" / "papers.json"
    index = load_index(index_path)

    if not index["papers"]:
        logger.warning("索引为空")
        return index

    # 规范化所有论文
    normalized_papers = [normalize_paper(p) for p in index["papers"]]

    # 去除重复
    seen_ids = set()
    unique_papers = []
    for paper in normalized_papers:
        if paper["arxiv_id"] and paper["arxiv_id"] not in seen_ids:
            seen_ids.add(paper["arxiv_id"])
            unique_papers.append(paper)
        elif not paper["arxiv_id"]:
            # 无 arXiv ID 的论文也保留
            unique_papers.append(paper)

    index["papers"] = unique_papers

    # 统计
    year_counts = {}
    source_counts = {"arxiv": 0, "other": 0}

    for p in unique_papers:
        year = str(p.get("year", "unknown"))
        year_counts[year] = year_counts.get(year, 0) + 1
        source_counts[p.get("source", "other")] += 1

    logger.info(f"索引更新完成:")
    logger.info(f"  总论文数: {len(unique_papers)}")
    logger.info(f"  有 arXiv ID: {source_counts['arxiv']}")
    logger.info(f"  无 arXiv ID: {source_counts['other']}")
    logger.info(f"  年份分布: {dict(sorted(year_counts.items(), reverse=True))}")

    save_index(index_path, index)

    return index


def main():
    parser = argparse.ArgumentParser(description="更新论文索引")
    parser.add_argument(
        "--verify",
        action="store_true",
        help="验证论文文件是否存在",
    )

    args = parser.parse_args()

    update_index(verify_existence=args.verify)


if __name__ == "__main__":
    main()
