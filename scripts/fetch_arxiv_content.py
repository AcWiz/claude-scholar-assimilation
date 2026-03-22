#!/usr/bin/env python3
"""
arXiv Paper Content Fetcher

下载 arXiv 论文 PDF 并提取全文文本，或获取 Abstract + Introduction。
"""

import argparse
import io
import json
import logging
import time
from pathlib import Path
from typing import Optional

import requests

try:
    import PyPDF2
    HAS_PYPDF2 = True
except ImportError:
    HAS_PYPDF2 = False
    print("警告: PyPDF2 未安装，PDF 解析将不可用。请运行: pip install PyPDF2")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

ARXIV_API_URL = "http://export.arxiv.org/api/query"
PDF_BASE_URL = "https://arxiv.org/pdf"


def load_papers_index() -> list:
    """加载论文索引"""
    index_path = Path(__file__).parent.parent / "_data" / "papers.json"
    if not index_path.exists():
        logger.error(f"索引文件不存在: {index_path}")
        return []

    with open(index_path, "r", encoding="utf-8") as f:
        index = json.load(f)
    return index.get("papers", [])


def fetch_pdf(arxiv_id: str) -> Optional[bytes]:
    """下载 arXiv PDF"""
    # 清理 ID（移除版本号）
    clean_id = arxiv_id.split("v")[0] if "v" in arxiv_id else arxiv_id
    url = f"{PDF_BASE_URL}/{clean_id}.pdf"

    try:
        response = requests.get(url, timeout=120)
        response.raise_for_status()
        return response.content
    except requests.RequestException as e:
        logger.warning(f"PDF 下载失败: {arxiv_id}, 错误: {e}")
        return None


def extract_text_from_pdf(pdf_bytes: bytes) -> Optional[str]:
    """从 PDF 提取全文文本"""
    if not HAS_PYPDF2:
        logger.error("PyPDF2 未安装，无法解析 PDF")
        return None

    try:
        pdf_file = io.BytesIO(pdf_bytes)
        reader = PyPDF2.PdfReader(pdf_file)
        text = ""

        for i, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

        return text if text.strip() else None
    except Exception as e:
        logger.warning(f"PDF 解析失败: {e}")
        return None


def fetch_abstract_intro(arxiv_id: str) -> Optional[str]:
    """通过 arXiv API 获取 Abstract 和 Introduction"""
    params = {"id_list": arxiv_id.split("v")[0]}

    try:
        response = requests.get(ARXIV_API_URL, params=params, timeout=30)
        response.raise_for_status()

        import re
        content = response.text

        # 提取摘要
        summary_match = re.search(r"<summary>(.*?)</summary>", content, re.DOTALL)
        abstract = ""
        if summary_match:
            abstract = re.sub(r"\s+", " ", summary_match.group(1)).strip()

        # 提取 Introduction（通常在摘要之后的第一节）
        # 注：arXiv API 只返回摘要，不返回全文
        # 这里我们尝试从 PDF 中获取
        return abstract

    except requests.RequestException as e:
        logger.warning(f"API 请求失败: {arxiv_id}, 错误: {e}")
        return None


def get_paper_dir(paper: dict, base_dir: Path) -> Path:
    """获取论文目录路径"""
    year = paper.get("year", "unknown")
    # 使用安全的文件夹名
    safe_id = paper["arxiv_id"].replace(".", "_").replace("/", "_")
    paper_dir = base_dir / str(year) / safe_id
    paper_dir.mkdir(parents=True, exist_ok=True)
    return paper_dir


def process_paper(paper: dict, base_dir: Path, mode: str = "pdf") -> dict:
    """处理单篇论文"""
    arxiv_id = paper["arxiv_id"]
    paper_dir = get_paper_dir(paper, base_dir)

    result = {
        "arxiv_id": arxiv_id,
        "dir": str(paper_dir),
        "pdf_downloaded": False,
        "pdf_extracted": False,
        "abstract_intro_saved": False,
    }

    if mode == "pdf":
        # 尝试下载并解析 PDF
        pdf_path = paper_dir / "paper.pdf"

        if pdf_path.exists():
            logger.info(f"PDF 已存在: {arxiv_id}")
            result["pdf_downloaded"] = True
        else:
            logger.info(f"下载 PDF: {arxiv_id}")
            pdf_bytes = fetch_pdf(arxiv_id)
            if pdf_bytes:
                with open(pdf_path, "wb") as f:
                    f.write(pdf_bytes)
                result["pdf_downloaded"] = True
                time.sleep(2)  # 避免请求过快

        # 提取文本
        if result["pdf_downloaded"]:
            text_path = paper_dir / "paper_content.txt"

            if text_path.exists():
                logger.info(f"文本已提取: {arxiv_id}")
                result["pdf_extracted"] = True
            else:
                logger.info(f"提取文本: {arxiv_id}")
                with open(pdf_path, "rb") as f:
                    pdf_bytes = f.read()

                text = extract_text_from_pdf(pdf_bytes)
                if text:
                    with open(text_path, "w", encoding="utf-8") as f:
                        f.write(text)
                    result["pdf_extracted"] = True
                else:
                    logger.warning(f"文本提取失败: {arxiv_id}")

    elif mode == "abstract":
        # 获取 Abstract + Introduction（回退方案）
        abstract_path = paper_dir / "abstract.md"

        if abstract_path.exists():
            logger.info(f"摘要已存在: {arxiv_id}")
            result["abstract_intro_saved"] = True
        else:
            logger.info(f"获取摘要: {arxiv_id}")
            abstract = fetch_abstract_intro(arxiv_id)
            if abstract:
                with open(abstract_path, "w", encoding="utf-8") as f:
                    f.write(f"# {paper.get('title', arxiv_id)}\n\n")
                    f.write(f"**arXiv ID**: {arxiv_id}\n\n")
                    f.write(f"**作者**: {', '.join(paper.get('authors', []))}\n\n")
                    f.write(f"**发布日期**: {paper.get('published', 'N/A')}\n\n")
                    f.write(f"**分类**: {', '.join(paper.get('categories', []))}\n\n")
                    f.write("## Abstract\n\n")
                    f.write(abstract)
                result["abstract_intro_saved"] = True
                time.sleep(1.5)

    return result


def process_all_papers(mode: str = "pdf", dry_run: bool = False, limit: Optional[int] = None) -> dict:
    """处理所有论文"""
    papers = load_papers_index()

    if not papers:
        logger.error("没有找到论文索引，请先运行 collect_papers.py")
        return {"processed": 0, "failed": 0, "results": []}

    # 筛选有 arXiv ID 的论文
    papers_with_arxiv = [p for p in papers if p.get("arxiv_id")]

    if mode == "pdf":
        papers_to_process = papers_with_arxiv
    else:
        papers_to_process = papers  # 包括无 arXiv ID 的论文

    if limit:
        papers_to_process = papers_to_process[:limit]

    logger.info(f"待处理论文数: {len(papers_to_process)} (模式: {mode})")

    base_dir = Path(__file__).parent.parent / "papers"

    results = []
    for i, paper in enumerate(papers_to_process):
        logger.info(f"[{i+1}/{len(papers_to_process)}] 处理: {paper.get('arxiv_id', 'N/A')}")

        if dry_run:
            result = {
                "arxiv_id": paper.get("arxiv_id", "N/A"),
                "dir": str(get_paper_dir(paper, base_dir)),
                "dry_run": True,
            }
        else:
            result = process_paper(paper, base_dir, mode)

        results.append(result)

    success = sum(1 for r in results if r.get("pdf_extracted") or r.get("abstract_intro_saved"))
    failed = len(results) - success

    return {"processed": len(results), "success": success, "failed": failed, "results": results}


def show_status() -> None:
    """显示下载状态"""
    papers = load_papers_index()
    base_dir = Path(__file__).parent.parent / "papers"

    stats = {
        "total": len(papers),
        "with_arxiv": sum(1 for p in papers if p.get("arxiv_id")),
        "without_arxiv": sum(1 for p in papers if not p.get("arxiv_id")),
        "papers_downloaded": 0,
        "text_extracted": 0,
        "abstract_saved": 0,
    }

    for paper in papers:
        paper_dir = get_paper_dir(paper, base_dir)
        if (paper_dir / "paper_content.txt").exists():
            stats["text_extracted"] += 1
        elif (paper_dir / "paper.pdf").exists():
            stats["papers_downloaded"] += 1
        elif (paper_dir / "abstract.md").exists():
            stats["abstract_saved"] += 1

    print("论文下载状态:")
    print(f"  总论文数: {stats['total']}")
    print(f"  有 arXiv ID: {stats['with_arxiv']}")
    print(f"  无 arXiv ID: {stats['without_arxiv']}")
    print(f"  PDF 已下载: {stats['papers_downloaded']}")
    print(f"  文本已提取: {stats['text_extracted']}")
    print(f"  摘要已保存: {stats['abstract_saved']}")


def main():
    parser = argparse.ArgumentParser(description="arXiv 论文内容获取器")
    parser.add_argument(
        "--mode",
        choices=["pdf", "abstract"],
        default="pdf",
        help="获取模式: pdf=下载PDF并提取全文, abstract=获取摘要+简介 (默认: pdf)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="仅预览，不实际下载",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="限制处理数量",
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="显示当前下载状态",
    )

    args = parser.parse_args()

    if args.status:
        show_status()
        return

    result = process_all_papers(
        mode=args.mode,
        dry_run=args.dry_run,
        limit=args.limit,
    )

    if args.dry_run:
        logger.info(f"[DRY RUN] 将处理 {result['processed']} 篇论文")
    else:
        logger.info(
            f"处理完成: {result['success']} 成功, {result['failed']} 失败, 共 {result['processed']} 篇"
        )


if __name__ == "__main__":
    main()
