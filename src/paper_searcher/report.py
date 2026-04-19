from datetime import date


def generate_daily_report(papers: list[dict], stats: dict,
                          categories: list[str], day: date | None = None) -> str:
    d = day or date.today()
    lines = [
        f"# arXiv 每日论文报告 - {d.isoformat()}",
        f"\n监控领域：{', '.join(categories)}",
        f"\n## 统计概览\n",
        f"- 新增论文总数：**{stats.get('total', 0)}**",
    ]

    by_cat = stats.get("by_primary_category", {})
    if by_cat:
        lines.append("\n### 按主类别分布\n")
        lines.append("| 类别 | 数量 | 占比 |")
        lines.append("|------|------|------|")
        total = max(stats.get("total", 1), 1)
        for cat, info in sorted(by_cat.items(), key=lambda x: -x[1]["count"]):
            pct = info["count"] / total * 100
            lines.append(f"| {cat} | {info['count']} | {pct:.1f}% |")

    lines.append("\n## 论文列表\n")
    for cat, info in sorted(by_cat.items()):
        lines.append(f"\n### {cat} ({info['count']} 篇)\n")
        cat_papers = [p for p in papers if p.get("primary_category") == cat]
        for p in cat_papers:
            authors = ", ".join(p.get("authors", [])[:3])
            if len(p.get("authors", [])) > 3:
                authors += " et al."
            lines.append(f"- **{p['title']}** - {authors}")
            lines.append(f"  [PDF]({p.get('pdf_url', '')}) | [arXiv]({p.get('arxiv_url', '')})")

    return "\n".join(lines)
