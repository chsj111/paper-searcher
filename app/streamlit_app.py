import sys
from pathlib import Path
from datetime import date

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import streamlit as st
from paper_searcher.config import load_config
from paper_searcher.fetcher import fetch_papers
from paper_searcher.classifier import classify_papers
from paper_searcher.filter import filter_papers
from paper_searcher.llm_client import LLMClient
from paper_searcher.summarizer import summarize_papers
from paper_searcher.report import generate_daily_report
from paper_searcher.storage import Storage

st.set_page_config(page_title="Paper Searcher", page_icon="📄", layout="wide")
cfg = load_config()
storage = Storage(cfg.storage.data_path)

# === 侧边栏 ===
st.sidebar.title("Paper Searcher")
available_dates = storage.list_dates()
if available_dates:
    selected_date = st.sidebar.selectbox("选择日期", available_dates,
                                          format_func=lambda d: d.isoformat())
else:
    selected_date = date.today()
    st.sidebar.info("暂无数据，请先抓取论文。")

categories_input = st.sidebar.text_input("arXiv 类别（逗号分隔）",
                                          value=", ".join(cfg.arxiv.categories))
categories = [c.strip() for c in categories_input.split(",") if c.strip()]

if st.sidebar.button("🔄 抓取今日论文"):
    with st.spinner("正在从 arXiv 抓取论文..."):
        papers = fetch_papers(categories, date.today(), cfg.arxiv.max_results_per_query)
        storage.save_papers(papers, date.today())
        stats = classify_papers(papers)
        storage.save_stats(stats, date.today())
        report = generate_daily_report(papers, stats, categories, date.today())
        storage.save_report(report, "daily_overview", date.today())
    st.sidebar.success(f"抓取完成！共 {len(papers)} 篇论文。")
    st.rerun()

# === 主页面 ===
papers = storage.load_papers(selected_date)
stats = storage.load_stats(selected_date)

tab_overview, tab_papers, tab_search, tab_history = st.tabs(
    ["📊 总览", "📋 论文列表", "🔍 智能筛选", "📁 历史报告"])

with tab_overview:
    if not stats:
        st.warning(f"{selected_date} 暂无数据。")
    else:
        col1, col2 = st.columns(2)
        col1.metric("论文总数", stats.get("total", 0))
        col2.metric("类别数", len(stats.get("by_primary_category", {})))

        by_cat = stats.get("by_primary_category", {})
        if by_cat:
            import pandas as pd
            df = pd.DataFrame([
                {"类别": cat, "数量": info["count"]}
                for cat, info in by_cat.items()
            ]).sort_values("数量", ascending=False)
            st.bar_chart(df.set_index("类别"))

with tab_papers:
    if not papers:
        st.warning("暂无论文数据。")
    else:
        cat_filter = st.selectbox("按类别筛选", ["全部"] + list(
            stats.get("by_primary_category", {}).keys()))
        display = papers if cat_filter == "全部" else [
            p for p in papers if p.get("primary_category") == cat_filter]

        for p in display:
            with st.expander(f"**{p['title']}** [{p.get('primary_category', '')}]"):
                st.write(f"**作者**: {', '.join(p.get('authors', [])[:5])}")
                st.write(f"**摘要**: {p.get('abstract', '')[:500]}...")
                st.write(f"[PDF]({p.get('pdf_url', '')}) | [arXiv]({p.get('arxiv_url', '')})")

with tab_search:
    query = st.text_input("输入研究需求（如：微调、数字孪生、reinforcement learning）")
    if query and st.button("开始筛选与总结"):
        filtered = filter_papers(papers, query)
        st.info(f"匹配 {len(filtered)}/{len(papers)} 篇论文")

        if not filtered:
            st.warning("没有匹配的论文。")
        elif not cfg.llm.api_key:
            st.error("未配置 LLM API Key。请设置环境变量 PAPER_SEARCHER_LLM_API_KEY。")
            for p in filtered:
                st.write(f"- {p['title']}")
        else:
            llm = LLMClient(
                api_url=cfg.llm.api_url, api_key=cfg.llm.api_key,
                model=cfg.llm.model, temperature=cfg.llm.temperature,
                max_workers=cfg.llm.max_workers, retries=cfg.llm.retries,
                timeout=cfg.llm.timeout,
            )
            with st.spinner("LLM 正在分析论文..."):
                report = summarize_papers(filtered, query, llm, cfg.llm.batch_size)
                storage.save_report(report, query, selected_date)
            st.markdown(report)

with tab_history:
    reports = storage.list_reports(selected_date)
    if not reports:
        st.info("暂无历史报告。")
    else:
        selected_report = st.selectbox("选择报告", reports)
        content = storage.load_report(selected_report, selected_date)
        if content:
            st.markdown(content)
