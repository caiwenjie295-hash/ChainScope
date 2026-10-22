# ChainScope 产业透镜

面向个人投资者的 AI 产业链研究 Web 原型：从 AI 概念进入产业结构，选择公司查看基础信息、财务指标、已有 AI 总结、概念证据、中外比较和事件路径。

界面版本 **0.3.22**；研究版本 **2026-10-22.p2.deep.b1h.p1.c**；数据截至 **2026-10-21**。本说明依据 2026-10-22 的源码、快照、构建和公网浏览器验证更新。

## 1. 源代码与访问入口

- 公开源码仓库：[caiwenjie295-hash/ChainScope](https://github.com/caiwenjie295-hash/ChainScope)。
- 当前公开仓库是本地项目的发布快照。原始开发基线为本地提交 `1cb9e86`、标签 `v0.3.22`；本仓库的提交历史从公开发布开始，原始本地历史保留在原源码包中。
- 本地入口：[http://127.0.0.1:5173/](http://127.0.0.1:5173/)，需要先按下文启动服务。
- 公网产品 URL：[打开 ChainScope](https://emberscrolls.top/ChainScope-0.3.22/dist/)。2026-10-22 已从外网浏览器验证公司总结、研究数据加载及研究流程导航。
- [60 秒流程演示视频](https://github.com/caiwenjie295-hash/ChainScope/blob/main/demo/ChainScope_60秒流程演示_无旁白.mp4) · [AI 使用与验证记录](https://github.com/caiwenjie295-hash/ChainScope/blob/main/submission/03_AI使用与验证记录.md) · [测试说明](https://github.com/caiwenjie295-hash/ChainScope/blob/main/submission/04_测试说明.md)。
- [子目录部署说明](https://github.com/caiwenjie295-hash/ChainScope/blob/main/deployment/子目录部署说明.md) · [提交总览](https://github.com/caiwenjie295-hash/ChainScope/blob/main/submission/00_提交说明.md) · [要求核对](https://github.com/caiwenjie295-hash/ChainScope/blob/main/submission/05_提交要求逐项核对.md) · [溯源索引](https://github.com/caiwenjie295-hash/ChainScope/blob/main/submission/06_关键数字与结论溯源索引.md)。

公开源码中保留研究结果、来源 ID、定位与已公开材料，受限接口和片段的原始摘录已从来源索引的公开副本移除；原始接口响应、财报缓存、凭证和逐次模型轨迹没有上传。因此本包支持前端运行和快照规则校验，不承诺完整研究离线重放。缺件及公开副本差异见 [发布记录](https://github.com/caiwenjie295-hash/ChainScope/blob/main/PUBLIC_RELEASE.md)。

## 2. 产品选择与范围

选择“AI 产业链跨市场公司研究”，是为了把分散的公司业务与财务信息整理为可追溯的研究入口，帮助用户判断公司与概念的关联是否有证据、财务数据能否比较，以及哪些结论只是推断。

当前前端仅开放 AI；白酒、智能驾驶等入口标注为 Demo。主流程为：勾选 AI → 开始分析 → 产业结构 → 环节公司列表 → 公司基础信息 → AI智能总结。市值榜、证据等级说明和研究流程页用于辅助理解。

产业结构图采用项目定义的技术功能分类：主题 → 产业分支 → 具体环节；公司归属按主营业务证据说明，部分分类边为推断。`concepts[]` 另记录数据商概念板的层级与成分，两者并非同一套分类体系。板块成分命中不等于主营业务归属，也不等于已确认专项收入。

当前发布快照共 **27 家公司**，其中 **17 家 reviewed、10 家 candidate**；有 **116 条来源、6 组中外对照、9 个事件、40 个图谱节点**。reviewed 表示已有经整理的研究内容，不代表所有公司均完成相同深度研究。早期第二轮只有 8 家公司，不能用该阶段数字描述当前覆盖。

## 3. 前端启动

本次验证环境：macOS、Node.js 22.22.2、npm 10.9.7。前端使用 React 18、TypeScript 与 Vite；依赖按 `package-lock.json` 安装。

在本仓库根目录执行：

```sh
cd frontend
npm ci
npm run dev -- --host 127.0.0.1 --port 5173 --strictPort
```

访问 [本地研究页面](http://127.0.0.1:5173/)。无需登录，也无需填写 API Key。关闭服务后本地地址失效。

生产构建与本地预览：

```sh
npm run build
npm run preview -- --host 127.0.0.1 --port 4173 --strictPort
```

产物位于 `frontend/dist/`。静态部署时发布其中的全部内容，可放在域名根目录或子目录；页面资源、研究数据和导航使用相对路径。子目录 URL 以 `/` 结尾或明确指定 `index.html`。多页入口包括 `index.html`、`agent_architecture.html`、`cost_performance.html`、`prod_loop.html`，应一并保留。

## 4. 环境变量和外部配置

前端运行不需要环境变量；所有研究凭证只供研究脚本使用，不写入前端。

| 变量 | 用途 | 前端是否需要 |
| --- | --- | --- |
| `DEEPSEEK_API_KEY` | 在线研究模型调用；环境变量优先于本地凭证文件 | 否 |
| `IFIND_API_KEY` | iFinD MCP Authorization | 否 |
| `FUYAO_API_KEY` | 扶摇金融数据请求 | 否 |
| `CHAINSCOPE_MODEL_PROFILE` | 第二轮适配器的模型配置；默认 `deepseek`，可选择配置中的 `deepseek-pro` | 否 |

`.env.example` 仅列出前三个凭证变量。脚本**不会自动加载 `.env`**，运行前需在终端或运行环境中设置变量。模型端点、模型名和凭证解析规则见 `config/model_registry.json`、`scripts/model_adapter.py`。

注意：当前 iFinD 客户端仍需项目父目录 `API及接口/iFinD MCP.txt` 中的 `mcpServers` 配置来读取服务 URL 和服务名称；仅设置 `IFIND_API_KEY` 不足以启动这条通路。扶摇可通过 `FUYAO_API_KEY` 取密钥，也保留父目录 `扶摇APIkey.txt` 回退；模型密钥保留对应文件回退。这些私人配置未随包提供。`probe.py` 的主入口还会直接读取扶摇密钥文件，不能把它当成纯环境变量即可重建的通用安装方式。

不要将真实密钥写入仓库、页面或截图。当前 `.gitignore` 排除 `.env`、`artifacts/`、本地环境和构建目录。

## 5. AI 的角色与研究流程

开发记录记载前端由用户指定的 `gpt-6-luna`、`max` 实现；Codex 主代理参与数据适配、验收与版本记录。研究模型的发布基线为 `deepseek-flash`。

第二轮使用 PydanticAI 2.59.0 编排固定阶段：业务证据、财务质量、跨市场比较、独立反证、研究编辑、事件传导。阶段内可选择工具，输出经过结构、引用和口径闸门检查，并保留人工/代理抽核修正。它不是任意主题的全自主规划系统。

AI 用于基于给定证据整理摘要与解释；财务数值、口径、分级和可比边界由代码约束并保留审查责任。两处约 3 秒“分析”进度是本地交互演示，读取已发布内容，**不触发新的模型或金融数据请求**。

DeepSeek Pro 的历史替换模型自检仍未完整通过，详见 `docs/P2_AGENT_SELFCHECK.md`；不得把它描述成通过验收的发布模型。开源设计借鉴与使用范围见 `THIRD_PARTY_NOTES.md`。

## 6. 数据来源与核验口径

- 扶摇 / iFinD 的金融数据、公司概况、概念与公告线索。
- 公司公开年报、业绩披露和产品材料；配置与来源 ID 分别位于 `config/`、`data/sources.json`、`data/round2/sources.json`。
- 前端唯一发布数据入口：`frontend/public/data/snapshot.json`。来源元数据、公开 URL 与访问边界随快照提供；受限来源不在浏览器中暴露接口原始响应或摘录。
- 财务基线包括 FY2025，部分公司补齐 H12026；按具体指标标注报告期。页面截至日期不等于所有财务项目都是该日期最新数据。
- AI 专项收入未披露或未核实则保留 null 和原因；不能以集团、母类别或相关业务收入替代。
- 概念 A–E 是特定主题的证据等级，不是公司整体评级、信用评级或投资建议。浪潮自建投运证据保守列 C；Vertiv 的 B 级限定综合基础设施，不扩展为液冷单品收入证明。
- 不同币种与期间不能机械比较绝对金额；经营现金流减资本开支仅作分析代理，事实、推断和情景分开标识。

来源主张和原件引用表明历史取数方式，但本次没有重新联网核对全部披露原文，不能宣称完成全量事实审计。金融数据对外展示许可仍待确认。

## 7. 验证、依赖与复现边界

只检查当前前端快照：Python 标准库即可运行，在项目根目录执行：

```sh
python3 scripts/validate_frontend.py
```

本次结果为 **1516 项通过**，验证结构、引用、空值、口径和数据指纹；不代表事实准确率。

研究脚本以 Python 3.12+ 为目标；本次使用 Python 3.12.14 运行基础测试。安装研究依赖的现有入口为：

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-agent.txt
```

Windows 激活方式为 `.venv\Scripts\Activate.ps1`。`requirements-agent.txt` 包含基础依赖、PydanticAI 与 EdgarTools。源码还直接导入 `bs4`，但依赖文件未显式声明 `beautifulsoup4`；本次基础运行环境缺少它，完整依赖安装后的状态尚未验证。如需运行相应脚本，应在隔离环境补齐该依赖并固定版本。

执行已有测试：

```sh
python -m unittest discover -s tests -v
```

**本次全套未通过**：当前基础验证环境发现 26 项（含模块加载错误占位），20 通过、2 失败、4 错误。原因包括缺少 `artifacts/` 原件、缺少研究依赖，以及旧用例将公司数写死为 9 而当前值为 17。模块加载失败使部分用例未执行；不能据此声称全套测试通过。

`data/` 与前端快照已提供，因此浏览器演示和快照校验可独立运行；但公开源码及原始 ZIP 未附研究原件目录 `artifacts/raw/`、`artifacts/public/`、`artifacts/round2/runs/` 和 `reports/`，原 README 指向的两份研究报告亦无法打开。缺少原始接口响应、财报和模型轨迹，完整研究链路目前无法离线重放。历史 README 中“无需网络可重放”的前提是原本已有完整缓存，本包不满足这一前提。

不要为查看前端而重跑在线研究。补齐缓存、许可、依赖和凭证后，才能逐段复现 `collect.py` / `fetch_public.py` → 整理研究 → 模型编排 → 校验 → 发布。在线流程会产生真实请求与费用，部分披露如 Eaton 的人工事实转录也不能自动重建。

`export_frontend.py` 仅生成旧 P1 编辑备份；当前 P2 发布入口为 `export_p2_joinable.py`，带 `--sync-public` 时才同步前端。更新数据后需重新运行校验和 `refresh_research_validation.py` 并构建；本次未重导出研究数据，修正子目录资源和导航路径时保持快照字节不变。

## 8. 已知边界与未做事项

- 公网产品和公开源码仓库已发布；尚未实现自动部署。
- 未接入真实用户点击触发研究、实时行情、定时刷新或全市场自动审计。
- 未实现账户、多租户、用户 Key、计费和队列调度。
- 部分公司缺少同口径中外对照、专项收入或完整四项研究块；不能补造 pair 或数字。
- Pro 替换模型全量复验未通过；P2 不能宣称全部完成。
- 原始证据附件和部分报告缺失，完整研究重放受阻。
- 全套测试未通过；尚未完成完整实体移动设备兼容、负载或安全专项测试。
- 未提供收益预测、交易执行或买卖建议。

## 9. 目录导航

| 路径 | 内容 |
| --- | --- |
| `frontend/src/` | React 界面、状态、来源展示、快照适配与页面说明 |
| `frontend/public/data/snapshot.json` | 当前发布研究快照 |
| `scripts/` | 取数、研究、模型适配、导出和校验 |
| `data/` | 结构化研究、来源、财务计算和历史评估 |
| `config/`、`schemas/` | 数据任务配置、模型配置和契约 |
| `tests/` | 口径、引用、空值、假 A 和影响方向闸门测试 |
| `docs/` | 产品方向、数据契约、历史验收与版本记录 |

交付文档和检查记录位于 `submission/`，视频位于 `demo/`，部署材料位于 `deployment/`。当前提交说明已统一到公网发布状态；原始验证日志保留其执行时的结果，未把旧日志改写为新测试结果。


### 2026-10-22 子目录部署修正

生产构建改用相对资源、数据和导航路径，四个页面支持同级静态部署到域名根目录或子文件夹。保留原主站时，可将 dist 内全部内容放入网站根目录下的 ChainScope/，通过 /ChainScope/ 访问。完整说明见 deployment/子目录部署说明.md（公开仓库）；修正包的构建校验与原研究测试结果应分开看待。
