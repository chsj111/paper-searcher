from .llm_client import LLMClient

SYSTEM_PROMPT = """你是一位学术论文分析助手。你需要阅读论文的标题和摘要，根据用户的研究需求进行分析总结。
请用中文回复，保持专业且简洁。"""


def summarize_papers(papers: list[dict], query: str,
                     llm: LLMClient, batch_size: int = 5) -> str:
    if not papers:
        return f"# 筛选报告：{query}\n\n未找到匹配的论文。"

    # 分批生成单篇摘要
    batches = [papers[i:i + batch_size] for i in range(0, len(papers), batch_size)]
    all_summaries = []

    for batch in batches:
        prompt = _build_batch_prompt(batch, query)
        resp = llm.call(prompt, system=SYSTEM_PROMPT)
        if resp:
            all_summaries.append(resp.content)

    # 生成综合报告
    combined = "\n\n".join(all_summaries) if all_summaries else "（LLM 调用失败）"
    overview_prompt = _build_overview_prompt(papers, query, combined)
    overview_resp = llm.call(overview_prompt, system=SYSTEM_PROMPT)
    overview = overview_resp.content if overview_resp else "（综合分析生成失败）"

    return _assemble_report(papers, query, combined, overview)


def _build_batch_prompt(papers: list[dict], query: str) -> str:
    paper_blocks = []
    for i, p in enumerate(papers, 1):
        paper_blocks.append(
            f"论文{i}:\n"
            f"  标题: {p['title']}\n"
            f"  摘要: {p['abstract'][:500]}\n"
            f"  链接: {p.get('arxiv_url', '')}"
        )

    return f"""用户研究需求：{query}

以下是筛选出的相关论文，请对每篇论文：
1. 用一句话总结核心贡献
2. 评估与用户需求的相关度（高/中/低）
3. 指出关键方法或发现

{chr(10).join(paper_blocks)}

请逐篇分析，格式如下：
### 论文N: [标题]
- **核心贡献**: ...
- **相关度**: 高/中/低
- **关键点**: ...
"""


def _build_overview_prompt(papers: list[dict], query: str,
                           summaries: str) -> str:
    return f"""基于以下 {len(papers)} 篇与"{query}"相关的论文分析：

{summaries}

请生成一个综合分析报告，包含：
1. **领域趋势**: 这些论文反映了哪些研究趋势
2. **关键发现**: 最值得关注的 3-5 个发现
3. **推荐阅读**: 最值得深入阅读的 2-3 篇论文及原因
4. **研究空白**: 可能的研究机会或未充分探索的方向

请用中文回复，保持专业简洁。"""


def _assemble_report(papers: list[dict], query: str,
                     summaries: str, overview: str) -> str:
    lines = [
        f"# 论文筛选报告：{query}",
        f"\n共筛选出 **{len(papers)}** 篇相关论文。\n",
        "---",
        "\n## 综合分析\n",
        overview,
        "\n---",
        "\n## 逐篇分析\n",
        summaries,
        "\n---",
        "\n## 论文列表\n",
    ]
    for i, p in enumerate(papers, 1):
        authors = ", ".join(p.get("authors", [])[:3])
        if len(p.get("authors", [])) > 3:
            authors += " et al."
        lines.append(f"{i}. **{p['title']}** - {authors} [链接]({p.get('arxiv_url', '')})")

    return "\n".join(lines)
