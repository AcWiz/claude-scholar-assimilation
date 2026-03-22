#!/usr/bin/env python3
"""
Regenerate Paper Abstracts using MiniMax API

使用 MiniMax-Text-01 模型根据论文全文生成高质量的新模板内容。
"""

import argparse
import json
import logging
import os
import time
from pathlib import Path
from typing import Optional

import requests

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# MiniMax API 配置
MINIMAX_API_URL = "https://api.minimax.chat/v1/text/chatcompletion_pro"
MINIMAX_MODEL = "MiniMax-Text-01"

# 新模板格式
NEW_TEMPLATE_FORMAT = """## 标题
{title}

## TL;DR
{tl_dr}

## 研究问题
{research_question}

## 主要贡献
1. {contribution_1}
2. {contribution_2}
3. {contribution_3}

## 方法
{method}

## 数据集
{datasets}

## 核心结果
{core_results}

## 局限性
{limitations}

## 研究空白 (Gap)
{research_gap}
"""


def load_papers_index() -> list:
    """加载论文索引"""
    index_path = Path(__file__).parent.parent / "_data" / "papers.json"
    if not index_path.exists():
        logger.error(f"索引文件不存在: {index_path}")
        return []

    with open(index_path, "r", encoding="utf-8") as f:
        index = json.load(f)
    return index.get("papers", [])


def get_paper_dir(paper: dict, base_dir: Path) -> Path:
    """获取论文目录路径"""
    year = paper.get("year", "unknown")
    safe_id = paper["arxiv_id"].replace(".", "_").replace("/", "_") if paper.get("arxiv_id") else paper.get("title", "unknown")[:50]
    return base_dir / str(year) / safe_id


def load_paper_content(paper_dir: Path) -> Optional[str]:
    """加载论文内容（优先全文，其次摘要）"""
    # 优先使用 PDF 提取的全文
    text_path = paper_dir / "paper_content.txt"
    if text_path.exists():
        with open(text_path, "r", encoding="utf-8") as f:
            content = f.read()
        if len(content) > 5000:  # 有效全文
            return content

    # 回退到 abstract.md
    abstract_path = paper_dir / "abstract.md"
    if abstract_path.exists():
        with open(abstract_path, "r", encoding="utf-8") as f:
            return f.read()

    return None


def generate_with_minimax(
    title: str,
    full_text: str,
    api_key: str,
) -> Optional[str]:
    """调用 MiniMax API 生成新模板内容"""

    prompt = f"""你是一个海洋科学和机器学习交叉领域的研究助手。请根据以下论文全文，按照新模板格式生成论文分析。

## 标题
{title}

## 全文（限于前 15000 字符）
{full_text[:15000]}

## 新模板格式要求
请严格按照以下格式生成，每个 section 必须有实质性内容：

1. **TL;DR**: 一句话总结论文贡献，不超过 100 字符
2. **研究问题**: 论文要解决的核心科学或技术问题
3. **主要贡献**: 列出 3 条主要贡献
4. **方法**: 论文采用的核心方法和技术路线
5. **数据集**: 使用的数据集或实验环境
6. **核心结果**: 主要实验结果或理论结果（包含具体数值）
7. **局限性**: 论文的局限性或不足之处
8. **研究空白 (Gap)**: 与你的研究方向（海洋数据同化+AI）相关的潜在研究机会

注意：
- 如果某些信息在全文中未提供，使用"未提供"或基于上下文合理推断
- 保持学术严谨性，不要编造具体数值
- 中文回答
"""

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": MINIMAX_MODEL,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "bot_setting": [
            {
                "bot_name": "paper_assistant",
                "content": "你是一个海洋科学和机器学习交叉领域的研究助手，擅长分析论文并生成结构化的论文分析模板。"
            }
        ],
        "temperature": 0.3,
        "max_tokens": 2000,
    }

    try:
        response = requests.post(
            MINIMAX_API_URL,
            headers=headers,
            json=payload,
            timeout=120,
        )
        response.raise_for_status()
        result = response.json()

        # 解析响应
        if result is None:
            logger.warning(f"API 响应为空")
            return None

        # 检查错误响应
        base_resp = result.get("base_resp", {})
        if base_resp.get("status_code") != 0:
            status_msg = base_resp.get("status_msg", "未知错误")
            logger.warning(f"API 错误: {status_msg}")
            return None

        # 优先使用 reply 字段（MiniMax 格式）
        if result.get("reply"):
            return result["reply"]

        # 回退到 choices 格式（OpenAI 兼容格式）
        choices = result.get("choices")
        if choices and len(choices) > 0:
            return choices[0].get("message", {}).get("content")

        logger.warning(f"API 响应格式异常: {result}")
        return None

    except requests.RequestException as e:
        logger.error(f"API 请求失败: {e}")
        return None
    except Exception as e:
        logger.error(f"未知错误: {e}")
        return None


def process_paper(
    paper: dict,
    base_dir: Path,
    api_key: str,
    dry_run: bool = False,
) -> dict:
    """处理单篇论文"""
    arxiv_id = paper.get("arxiv_id", "N/A")
    paper_dir = get_paper_dir(paper, base_dir)

    result = {
        "arxiv_id": arxiv_id,
        "title": paper.get("title", "N/A")[:80],
        "paper_dir": str(paper_dir),
        "content_loaded": False,
        "generated": False,
    }

    # 加载论文内容
    content = load_paper_content(paper_dir)
    if not content:
        logger.warning(f"未找到论文内容: {arxiv_id}")
        return result

    result["content_loaded"] = True
    result["content_length"] = len(content)

    if dry_run:
        result["dry_run"] = True
        return result

    # 调用 MiniMax API
    title = paper.get("title", "")
    generated = generate_with_minimax(title, content, api_key)

    if generated:
        # 保存生成的内容
        abstract_path = paper_dir / "abstract.md"
        with open(abstract_path, "w", encoding="utf-8") as f:
            f.write(f"# {title}\n\n")
            f.write(f"**arXiv ID**: {arxiv_id}\n\n")
            f.write(f"**作者**: {', '.join(paper.get('authors', []))}\n\n")
            f.write(f"**发布日期**: {paper.get('published', 'N/A')}\n\n")
            f.write(f"**分类**: {', '.join(paper.get('categories', []))}\n\n")
            f.write("---\n\n")
            f.write(generated)

        result["generated"] = True
        logger.info(f"生成完成: {arxiv_id}")
    else:
        logger.warning(f"生成失败: {arxiv_id}")

    return result


def process_all_papers(
    api_key: Optional[str] = None,
    dry_run: bool = False,
    limit: Optional[int] = None,
    batch_size: int = 10,
) -> dict:
    """处理所有论文"""
    # 获取 API Key
    if not api_key:
        api_key = os.environ.get("MINIMAX_API_KEY", "")
        if not api_key:
            logger.error("未提供 MINIMAX_API_KEY，请通过 --api-key 参数或环境变量设置")
            return {"processed": 0, "success": 0, "failed": 0, "results": []}

    papers = load_papers_index()
    if not papers:
        logger.error("没有找到论文索引")
        return {"processed": 0, "success": 0, "failed": 0, "results": []}

    base_dir = Path(__file__).parent.parent / "papers"

    # 只处理有内容的论文
    papers_to_process = []
    for paper in papers:
        paper_dir = get_paper_dir(paper, base_dir)
        if load_paper_content(paper_dir):
            papers_to_process.append(paper)

    if limit:
        papers_to_process = papers_to_process[:limit]

    logger.info(f"待处理论文数: {len(papers_to_process)}")

    results = []
    for i, paper in enumerate(papers_to_process):
        arxiv_id = paper.get("arxiv_id", "N/A")
        logger.info(f"[{i+1}/{len(papers_to_process)}] 处理: {arxiv_id}")

        result = process_paper(
            paper,
            base_dir,
            api_key,
            dry_run=dry_run,
        )
        results.append(result)

        # 批次处理后暂停
        if not dry_run and (i + 1) % batch_size == 0:
            logger.info(f"已完成 {(i+1)} 篇，暂停 {batch_size} 秒...")
            time.sleep(batch_size * 2)  # 每篇间隔 2 秒

        # 每篇之间暂停
        if not dry_run:
            time.sleep(2)

    success = sum(1 for r in results if r.get("generated"))
    failed = len(results) - success

    return {
        "processed": len(results),
        "success": success,
        "failed": failed,
        "results": results,
    }


def main():
    parser = argparse.ArgumentParser(description="使用 MiniMax 生成论文新模板")
    parser.add_argument(
        "--api-key",
        type=str,
        default=None,
        help="MiniMax API Key (也可通过 MINIMAX_API_KEY 环境变量设置)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="仅预览，不实际生成",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="限制处理数量",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=10,
        help="每批处理数量 (default: 10)",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="正式执行生成（不加此参数则默认为 dry-run）",
    )

    args = parser.parse_args()

    if not args.dry_run and not args.apply:
        logger.info("未指定 --apply，将以 dry-run 模式运行")
        args.dry_run = True

    result = process_all_papers(
        api_key=args.api_key,
        dry_run=args.dry_run,
        limit=args.limit,
        batch_size=args.batch_size,
    )

    logger.info(
        f"处理完成: {result['success']} 成功, {result['failed']} 失败, 共 {result['processed']} 篇"
    )


if __name__ == "__main__":
    main()
