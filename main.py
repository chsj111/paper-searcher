import argparse
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from paper_searcher.config import load_config
from paper_searcher.fetcher import fetch_papers
from paper_searcher.classifier import classify_papers
from paper_searcher.filter import filter_papers
from paper_searcher.llm_client import LLMClient
from paper_searcher.summarizer import summarize_papers
from paper_searcher.report import generate_daily_report
from paper_searcher.storage import Storage


def cmd_fetch(args, cfg):
    categories = args.categories or cfg.arxiv.categories
    day = date.fromisoformat(args.date) if args.date else date.today()
    storage = Storage(cfg.storage.data_path)

    print(f"正在抓取 {day} 的 {', '.join(categories)} 领域论文...")
    papers = fetch_papers(categories, day, cfg.arxiv.max_results_per_query)
    storage.save_papers(papers, day)
    print(f"抓取完成，共 {len(papers)} 篇论文，已保存。")

    stats = classify_papers(papers)
    storage.save_stats(stats, day)
    print(f"分类统计已保存。")
    return papers, stats


def cmd_stats(args, cfg):
    day = date.fromisoformat(args.date) if args.date else date.today()
    storage = Storage(cfg.storage.data_path)
    stats = storage.load_stats(day)
    if not stats:
        print(f"未找到 {day} 的统计数据，请先运行 fetch。")
        return

    print(f"\n=== {day} 论文统计 ===")
    print(f"总数：{stats.get('total', 0)}")
    for cat, info in stats.get("by_primary_category", {}).items():
        print(f"  {cat}: {info['count']} 篇")


def cmd_search(args, cfg):
    day = date.fromisoformat(args.date) if args.date else date.today()
    storage = Storage(cfg.storage.data_path)
    papers = storage.load_papers(day)
    if not papers:
        print(f"未找到 {day} 的论文数据，请先运行 fetch。")
        return

    query = args.query
    filtered = filter_papers(papers, query)
    print(f"筛选 '{query}'：匹配 {len(filtered)}/{len(papers)} 篇")

    if not filtered:
        print("没有匹配的论文。")
        return

    if not cfg.llm.api_key:
        print("警告：未配置 LLM API Key，跳过摘要生成。")
        print("设置环境变量 PAPER_SEARCHER_LLM_API_KEY 或在 config/default.yaml 中配置。")
        for p in filtered:
            print(f"  - {p['title']}")
        return

    llm = LLMClient(
        api_url=cfg.llm.api_url, api_key=cfg.llm.api_key,
        model=cfg.llm.model, temperature=cfg.llm.temperature,
        max_workers=cfg.llm.max_workers, retries=cfg.llm.retries,
        timeout=cfg.llm.timeout,
    )
    print("正在调用 LLM 生成摘要报告...")
    report = summarize_papers(filtered, query, llm, cfg.llm.batch_size)
    storage.save_report(report, query, day)
    print(f"报告已保存。")
    print("\n" + report)


def cmd_daily(args, cfg):
    day = date.fromisoformat(args.date) if args.date else date.today()

    # 模拟带参数的 args
    class FetchArgs:
        categories = args.categories if hasattr(args, "categories") else None
        date = day.isoformat()
    papers, stats = cmd_fetch(FetchArgs(), cfg)

    categories = (args.categories if hasattr(args, "categories") else None) or cfg.arxiv.categories
    report = generate_daily_report(papers, stats, categories, day)
    storage = Storage(cfg.storage.data_path)
    storage.save_report(report, "daily_overview", day)
    print("\n每日报告已生成。")

    queries = cfg.filter.queries if hasattr(cfg.filter, "queries") else []
    if hasattr(args, "query") and args.query:
        queries = [args.query]

    for q in queries:
        class SearchArgs:
            query = q
            date = day.isoformat()
        cmd_search(SearchArgs(), cfg)


def main():
    parser = argparse.ArgumentParser(description="Paper Searcher - arXiv 论文搜索与 LLM 总结")
    parser.add_argument("--config", help="配置文件路径")
    sub = parser.add_subparsers(dest="command")

    p_fetch = sub.add_parser("fetch", help="抓取 arXiv 论文")
    p_fetch.add_argument("--categories", nargs="+", help="arXiv 类别")
    p_fetch.add_argument("--date", help="日期 (YYYY-MM-DD)")

    p_stats = sub.add_parser("stats", help="查看统计信息")
    p_stats.add_argument("--date", help="日期 (YYYY-MM-DD)")

    p_search = sub.add_parser("search", help="筛选论文并生成 LLM 摘要")
    p_search.add_argument("--query", required=True, help="筛选关键词")
    p_search.add_argument("--date", help="日期 (YYYY-MM-DD)")

    p_daily = sub.add_parser("daily", help="完整每日流程")
    p_daily.add_argument("--categories", nargs="+", help="arXiv 类别")
    p_daily.add_argument("--date", help="日期 (YYYY-MM-DD)")
    p_daily.add_argument("--query", help="额外筛选关键词")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    cfg = load_config(args.config)
    {"fetch": cmd_fetch, "stats": cmd_stats, "search": cmd_search, "daily": cmd_daily}[args.command](args, cfg)


if __name__ == "__main__":
    main()
