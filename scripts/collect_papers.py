#!/usr/bin/env python3
"""
arXiv Paper Collector

从 arXiv API 收集数据同化与海洋 AI 交叉领域论文，建立论文索引。
"""

import argparse
import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

import requests

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# 搜索查询配置
SEARCH_QUERIES = [
    'all:"data assimilation" AND all:"deep learning" AND all:"ocean"',
    'all:"data assimilation" AND all:"neural network" AND all:"ocean"',
    'all:"ocean" AND all:"state estimation" AND (all:"neural" OR all:"learning")',
    'all:"PINN" AND all:"ocean"',
    'all:"physics-informed" AND all:"neural network" AND all:"ocean"',
    'all:"Koopman" AND all:"ocean"',
    'all:"Koopman" AND all:"data assimilation"',
    'all:"neural operator" AND all:"ocean"',
    'all:"Fourier neural operator" AND all:"ocean"',
    'all:"FNO" AND all:"ocean"',
    'all:"sea surface temperature" AND all:"deep learning"',
    'all:"sea surface height" AND all:"neural network"',
    'all:"SST" AND all:"forecast" AND all:"learning"',
    'all:"ocean forecast" AND all:"deep learning"',
    'all:"ocean prediction" AND all:"neural"',
    'all:"ocean modeling" AND all:"machine learning"',
    'all:"graph neural network" AND all:"ocean"',
    'all:"GNN" AND all:"ocean"',
    'all:"ocean data assimilation" AND all:"neural"',
    'all:"ensemble Kalman" AND all:"ocean"',
    'all:"4D-Var" AND all:"ocean"',
    'all:"ENSO" AND all:"deep learning"',
    'all:"El Nino" AND all:"neural network"',
    'all:"deep ocean" AND all:"neural"',
    'all:"subsurface" AND all:"data assimilation" AND all:"learning"',
    'all:"ocean model" AND all:"learning"',
    'all:"numerical ocean" AND all:"neural network"',
]

ARXIV_API_URL = "http://export.arxiv.org/api/query"


def fetch_arxiv_papers(query: str, max_results: int = 10) -> list:
    """从 arXiv API 获取论文"""
    params = {
        "search_query": query,
        "start": 0,
        "max_results": max_results,
        "sortBy": "relevance",
        "sortOrder": "descending",
    }

    try:
        response = requests.get(ARXIV_API_URL, params=params, timeout=60)
        response.raise_for_status()
        return parse_arxiv_response(response.text)
    except requests.RequestException as e:
        logger.error(f"API 请求失败: {query}, 错误: {e}")
        return []


def parse_arxiv_response(xml_text: str) -> list:
    """解析 arXiv API 返回的 XML 响应"""
    import re

    papers = []
    # 简单的 XML 解析 - 提取 entry 块
    entries = re.findall(r"<entry>(.*?)</entry>", xml_text, re.DOTALL)

    for entry in entries:
        paper = {}

        # 提取 arXiv ID
        id_match = re.search(r"<id>(.*?)</id>", entry)
        if id_match:
            url = id_match.group(1)
            paper["arxiv_id"] = url.split("/")[-1]
            paper["arxiv_url"] = url

        # 标题
        title_match = re.search(r"<title>(.*?)</title>", entry, re.DOTALL)
        if title_match:
            paper["title"] = re.sub(r"\s+", " ", title_match.group(1)).strip()

        # 摘要
        summary_match = re.search(r"<summary>(.*?)</summary>", entry, re.DOTALL)
        if summary_match:
            paper["abstract"] = re.sub(r"\s+", " ", summary_match.group(1)).strip()

        # 作者
        authors = re.findall(r"<name>(.*?)</name>", entry)
        paper["authors"] = authors

        # 发布日期
        published_match = re.search(r"<published>(.*?)</published>", entry)
        if published_match:
            paper["published"] = published_match.group(1)[:10]  # YYYY-MM-DD
            paper["year"] = int(paper["published"][:4])

        # 分类
        categories = re.findall(r"<category term=\"([^\"]+)\"", entry)
        paper["categories"] = categories

        # DOI
        doi_match = re.search(r"<arxiv:doi>(.*?)</arxiv:doi>", entry)
        if doi_match:
            paper["doi"] = doi_match.group(1)

        # 评论/期刊引用信息
        comment_match = re.search(r"<arxiv:comment>(.*?)</arxiv:comment>", entry, re.DOTALL)
        if comment_match:
            paper["comment"] = re.sub(r"\s+", " ", comment_match.group(1)).strip()

        if paper.get("arxiv_id"):
            papers.append(paper)

    return papers


def load_existing_index(index_path: Path) -> dict:
    """加载现有索引"""
    if index_path.exists():
        with open(index_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"papers": [], "metadata": {"last_updated": None}}


def save_index(index_path: Path, index: dict) -> None:
    """保存索引"""
    index["metadata"]["last_updated"] = datetime.now().isoformat()
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)


def collect_papers(
    max_results_per_query: int = 10,
    dry_run: bool = False,
    start_query: int = 0,
) -> dict:
    """收集论文主函数"""
    index_path = Path(__file__).parent.parent / "_data" / "papers.json"
    index_path.parent.mkdir(parents=True, exist_ok=True)

    # 加载现有索引
    index = load_existing_index(index_path)
    existing_ids = {p["arxiv_id"] for p in index["papers"]}

    logger.info(f"现有索引中论文数: {len(existing_ids)}")

    all_new_papers = []

    # 执行搜索查询
    queries_to_run = SEARCH_QUERIES[start_query:]

    for i, query in enumerate(queries_to_run):
        logger.info(f"查询 {i + start_query + 1}/{len(SEARCH_QUERIES)}: {query[:60]}...")

        if dry_run:
            # dry_run 模式下只打印查询信息
            logger.info(f"  [DRY RUN] 将获取最多 {max_results_per_query} 篇论文")
            time.sleep(0.5)
            continue

        papers = fetch_arxiv_papers(query, max_results_per_query)
        new_papers = [p for p in papers if p["arxiv_id"] not in existing_ids]

        if new_papers:
            all_new_papers.extend(new_papers)
            existing_ids.update(p["arxiv_id"] for p in new_papers)
            logger.info(f"  获取 {len(papers)} 篇, 新论文 {len(new_papers)} 篇")
        else:
            logger.info(f"  获取 {len(papers)} 篇, 无新论文")

        # 避免请求过快
        time.sleep(1.5)

    if dry_run:
        logger.info(f"[DRY RUN] 将会收集 {len(all_new_papers)} 篇新论文")
        return index

    # 添加新论文到索引
    index["papers"].extend(all_new_papers)
    save_index(index_path, index)

    logger.info(f"收集完成: {len(all_new_papers)} 篇新论文, 总计 {len(index['papers'])} 篇")

    return index


def main():
    parser = argparse.ArgumentParser(description="arXiv 论文收集器")
    parser.add_argument(
        "--max-results",
        type=int,
        default=10,
        help="每个查询返回的最大结果数 (default: 10)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="仅打印将要执行的操作，不实际收集",
    )
    parser.add_argument(
        "--start-query",
        type=int,
        default=0,
        help="从第几个查询开始 (0-indexed, default: 0)",
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="显示当前索引状态",
    )

    args = parser.parse_args()

    if args.status:
        index_path = Path(__file__).parent.parent / "_data" / "papers.json"
        index = load_existing_index(index_path)
        papers = index["papers"]

        # 按年份统计
        year_counts = {}
        for p in papers:
            year = p.get("year", "unknown")
            year_counts[year] = year_counts.get(year, 0) + 1

        print(f"索引状态:")
        print(f"  总论文数: {len(papers)}")
        print(f"  最后更新: {index['metadata'].get('last_updated', '从未更新')}")
        print(f"  年份分布: {dict(sorted(year_counts.items(), reverse=True))}")

        return

    collect_papers(
        max_results_per_query=args.max_results,
        dry_run=args.dry_run,
        start_query=args.start_query,
    )


if __name__ == "__main__":
    main()
