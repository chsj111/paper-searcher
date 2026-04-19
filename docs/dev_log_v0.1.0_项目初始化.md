# 开发文档 v0.1.0 - 项目初始化

**日期**: 2026-04-19

## 变更概要

完成 Paper Searcher 项目的初始搭建，实现全部核心模块。

## 涉及文件

### 新增文件
- `pyproject.toml` - 项目元数据与依赖
- `requirements.txt` - pip 依赖清单
- `.gitignore` - Git 忽略规则
- `config/default.yaml` - 默认配置文件
- `src/paper_searcher/__init__.py` - 包初始化
- `src/paper_searcher/config.py` - 配置加载（YAML + 环境变量覆盖）
- `src/paper_searcher/fetcher.py` - arXiv 论文抓取（使用 `arxiv` 库）
- `src/paper_searcher/classifier.py` - 论文分类统计
- `src/paper_searcher/filter.py` - 关键词筛选（支持 AND/OR）
- `src/paper_searcher/llm_client.py` - LLM API 调用（OpenAI 兼容 REST）
- `src/paper_searcher/summarizer.py` - LLM 论文摘要生成
- `src/paper_searcher/report.py` - Markdown 报告生成
- `src/paper_searcher/storage.py` - JSON 文件存取（按日期目录）
- `main.py` - CLI 命令行入口（fetch/stats/search/daily）
- `app/streamlit_app.py` - Streamlit Web 前端（总览/列表/筛选/历史）
- `.github/workflows/daily_fetch.yml` - GitHub Actions 每日定时任务
- `README.md` - 项目说明文档

## 设计决策

1. **LLM 调用方式**：直接使用 `requests.post` + OpenAI 兼容格式，而非引入 openai SDK，保持轻量且兼容各种第三方接口（DeepSeek/通义/CursorAI 等）
2. **存储方案**：本地 JSON 文件按日期目录组织，简单直接，GitHub Actions 可直接将报告 commit 入仓
3. **筛选逻辑**：基于关键词匹配（标题+摘要），支持 AND/OR 组合，预留 embedding 语义筛选扩展点
4. **双入口设计**：CLI 用于自动化/CI，Streamlit 用于交互浏览

## 待办/已知问题

- [ ] arXiv `submittedDate` 过滤在实际 API 中可能不精确，需测试验证
- [ ] LLM 并发调用的 token 消耗统计尚未在报告中展示
- [ ] Streamlit 前端未做分页，论文量大时可能卡顿
- [ ] 尚未添加单元测试
- [ ] 需要实际配置 GitHub 仓库并测试 Actions workflow
