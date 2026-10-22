# 第二轮研究的开源借鉴记录

本轮以阅读固定版本源码、借鉴设计并重新实现的方式使用开源项目。未执行这些仓库的研究流水线，也没有把其源码片段复制为ChainScope运行代码。参考源码和许可证保存在 `artifacts/references/`，便于复核。

| 项目及固定提交 | 实际阅读的文件 | 借鉴后落实的位置 |
|---|---|---|
| [FinRobot](https://github.com/AI4Finance-Foundation/FinRobot/tree/2717499b8e30f242640af08c4ad9afd1113c2d45)，Apache-2.0 | `equity_research.py`、`validators.py`、`currency_caliber.py`、`ttm_period.py`、`earnings.py` | `prepare_round2.py`以代码计算现金转化与现金流减资本开支代理；检查币种、期间、空值；`round2_agents.py`将取数、解释与审查分为明确阶段 |
| [TradingAgents](https://github.com/TauricResearch/TradingAgents/tree/e8f5503e9b86d5c2710b0c76b1f686703968c9df)，Apache-2.0 | `fundamentals_analyst.py`、`bear_researcher.py` | 独立反证角色重新检索原文，寻找归因、业务口径及收入确认问题；不沿用交易指令或股票买卖目标 |
| [EdgarTools](https://github.com/dgunning/edgartools/tree/73abc6747c8b786f2108060a516d74f590d9e932)，MIT | `edgar/financials.py` | 阅读期间分类与财务报表处理方式；实际安装5.62.0并调用 `edgar.documents.parse_html` 解析本地、公司托管的Vertiv正式10-K |

PydanticAI是本轮实际使用的编排框架，安装版本为 `pydantic-ai-slim==2.59.0`。所有真实模型请求通过显式配置的DeepSeek官方域名发送，模型为 `deepseek-flash`。当前是固定阶段DAG、阶段内自主选工具、有限补证，不是完全自主规划系统。

参考上游仓库的提交版本与PyPI安装版本不是同一个概念；EdgarTools安装包版本固定在依赖文件中。未承诺复制上游全部能力，也没有把上游报告质量作为本项目研究正确性的保证。
