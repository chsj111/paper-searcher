# Paper Searcher

每日 arXiv 论文自动抓取、分类展示与 LLM 智能总结工具。

## 功能

- **每日抓取**：自动从 arXiv 获取指定领域的最新论文
- **分类展示**：按类别统计，表格/图表展示
- **智能筛选**：根据自定义需求关键词筛选论文
- **LLM 总结**：调用大语言模型对筛选论文进行深度摘要，生成综合报告
- **双入口**：CLI 命令行 + Streamlit Web 界面
- **自动调度**：GitHub Actions 每日定时运行

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 配置 LLM API Key
export PAPER_SEARCHER_LLM_API_KEY="your-api-key"

# 抓取论文
python main.py fetch --categories cs.AI cs.LG

# 查看统计
python main.py stats

# 筛选 + LLM 总结
python main.py search --query "fine-tuning"

# 完整每日流程
python main.py daily

# 启动 Web 界面
streamlit run app/streamlit_app.py
```

## 配置

编辑 `config/default.yaml` 或通过环境变量覆盖：

| 环境变量 | 说明 |
|----------|------|
| `PAPER_SEARCHER_LLM_API_KEY` | LLM API 密钥 |
| `PAPER_SEARCHER_LLM_API_URL` | LLM API 地址 |
| `PAPER_SEARCHER_LLM_MODEL` | LLM 模型名称 |
| `PAPER_SEARCHER_DATA_DIR` | 数据存储目录 |

## 项目结构

```
├── main.py                  # CLI 入口
├── app/streamlit_app.py     # Web 前端
├── src/paper_searcher/      # 核心模块
│   ├── config.py            # 配置管理
│   ├── fetcher.py           # arXiv 抓取
│   ├── classifier.py        # 分类统计
│   ├── filter.py            # 关键词筛选
│   ├── llm_client.py        # LLM 调用
│   ├── summarizer.py        # 摘要生成
│   ├── report.py            # 报告生成
│   └── storage.py           # 数据存取
├── config/default.yaml      # 默认配置
├── data/                    # 运行数据
└── docs/                    # 开发文档
```

## GitHub Actions

仓库已配置每日 UTC 2:00（北京时间 10:00）自动运行。需要在仓库 Settings → Secrets 中添加 `LLM_API_KEY`。

也可手动触发：Actions → Daily Paper Fetch → Run workflow。
