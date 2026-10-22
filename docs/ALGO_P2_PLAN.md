# ChainScope 算法 P2 计划（AI 概念板）

> 作者：算法｜拍板依据：`P2_BRIEF.md`｜日期：2026-10-21（Asia/Hong_Kong）  
> **状态：已拍板，开跑中**（双榜 + 每方向 top10；废全局深研 8）  
> 约束：复用 P0/P1 闸门；不编造；不改 UX 视觉规范；密钥不入库。

---

## 0. 一句话

把研究主题从「手搓液冷+光模块切片」切到 **扶摇/iFinD AI 概念板 taxonomy**；snapshot 增加 `concepts[]` + `concept_feeds`，供 A0/A1；graph/companies/pairs/events/impact 继续可动态驱动 B/C。

---


## 0.1 产品定调（Finance · 算法主责）

主责是 **通用 Agent 编排与开发**：阶段 DAG、工具预算、闸门、证据/分级/可比/传导契约可复现。  
主题（如 AI 概念板）与模型（DeepSeek 等）**可替换**：换 API / 换概念板应少改编排、多改配置与 registry。  
P2 拉数服务硬指标，但代码形态按通用框架收敛——供应商调用进 adapter/config，禁止散落业务脚本写死路径。

## 1. 数据源

| 用途 | 源 | 用法 |
|---|---|---|
| 概念层级 / 成分股 | **iFinD MCP**（`search_stocks` / `get_security_indicators` / 综合 MCP 自然语言指标）+ 必要时扶摇板块/成分接口 | 拉取「AI」相关概念板列表与成分；落 `artifacts/raw/` + 规范化 `data/p2/concepts.json` |
| 公司概况 / 财务 | 扶摇 A 股财报 API（已有路径模式）+ iFinD `get_stock_financials` / `get_stock_info` | 深研子集；空值保留 missing_reason |
| 新闻 / 公告 feeds | iFinD `search_news` / `search_notice` / `search_trending_news` | 按 concept 关键词+成分代码检索；只存标题/日期/url/kind/source_id |
| 海外对标 | iFinD global stock + 公开 IR/SEC（EdgarTools 模式，本地原文） | 每概念最多 1–2 组中外 pair |
| 模型 | `deepseek-flash` + 现有 round2 DAG（阶段名单换概念池） | 离线可重放；在线仅补缺 |

**探测顺序（开跑后）**：`probe` → 概念列表试拉 → 单概念成分试拉 → 单概念 news/notice 试拉 → 再批量。失败保留 raw，不静默填空。

**已知风险**：MCP 工具以自然语言为主，概念板「官方树」可能需人工钉一版 `config/p2_concept_seed.json`（id/name/query）再自动扩成分；计划里允许 **种子表 + 自动成分**，禁止前端写死。

---

## 2. 公司池与深研范围（已纠正）

| 层 | 规模（目标） | 规则 |
|---|---|---|
| 概念板覆盖 | 种子根 AI + 可分析子概念 | `analysis_enabled`；应用软件 shallow |
| 成分全量 | 每方向扶摇/iFinD 成分 | 落 raw；`company_ids` 可 >10 |
| **双榜展示** | 每可分析方向各 **top10** | 同时导出 `rank_by_mkt_cap` + `rank_by_concept_weight`（含 rank/value/as_of）；默认前端看市值 |
| 深核 | 覆盖各方向双榜并集（预算内） | 证据不足诚实 B/C/E；**禁假 A**；**废全局硬顶 8 家** |
| 叙事焦点 | 有核验证据者优先 | impact 只标有源节点 |

权重源：优先 iFinD/扶摇概念权重；当前扶摇「指数权重」标注敬请期待 → 权重榜可空 items + `missing_reason=weight_api_unavailable`，市值榜仍必须尽量实数。  
P1 证据可迁移；**graph 以新 taxonomy 为准**，不硬编码旧四分支。

---

## 3. Snapshot 契约（新增）

### 3.1 `concepts[]`

```json
{
  "id": "concept.ai_chip",
  "name": "AI芯片",
  "parent_id": "concept.ai_root",
  "level": 1,
  "company_ids": ["..."],
  "company_count": 12,
  "description": "可选一句",
  "source_ids": ["src.ifind.concept..."]
}
```

- A0 只渲染本数组（树/chip）；`parent_id=null` 为根。  
- **禁止**前端写死名称；缺数据则空态。

### 3.2 `concept_feeds`

```json
{
  "concept.ai_chip": [
    {
      "id": "feed....",
      "title": "...",
      "date": "2026-10-18",
      "url": "https://...",
      "kind": "news|notice|filing|other",
      "source_id": "src....",
      "publisher": "可选"
    }
  ]
}
```

- A1：选中 `concept_id` 后只展示 `concept_feeds[id]`（可截断最近 N=20）。  
- 无 url 时仍可展示标题+日期，标明本地摘录边界。  
- 校验：每条要么有可点 url，要么有 source_id 进 `sources`。

### 3.2b 双榜（挂在 `concepts[]` 项上）

- `rank_by_mkt_cap` / `rank_by_concept_weight`：见 `FRONTEND_FIELDS_P2.md` 的 `RankBoard`。
- 非可分析概念两字段均为 `null`。
- 全局「深研 8」作废；列表排序只认 `rank`，勿写死 8。

### 3.3 兼容字段（继续）

| 字段 | 用途 |
|---|---|
| `graph` / `impact*` | B 星图；数据驱动分层，不假定四固定分支名 |
| `companies` + `demo_priority` | 列表/折叠 |
| `pairs` + 可比闸门 | C 对比 |
| `event` + `events[]` | 可挂在「已选概念分析后」；A0 不默认铺 |
| `overview` | 随选中概念或分析后更新；首屏可极简 |

`meta.research_version` → `2026-10-21.p2`（开跑后打戳）。  
`meta.theme_mode` → `"concept_board"`。

完整字段表开跑后写：`docs/FRONTEND_FIELDS_P2.md`。

---

## 4. 编排与闸门（复用）

1. 构建 `data/p2/`：concepts、constituents、feeds、registry。  
2. `build_research` / round2 DAG：公司名单改读 P2 registry；提示词改为概念板归属。  
3. **原样复用**：CONCEPT_GRADES、假 A、export 引用闸门、可比字段、impact 注解（无源 unclear）、事件 fact/inference/scenario。  
4. `export_frontend.py`：写出 `concepts` + `concept_feeds`；A 区所需最小 overview。  
5. 测试：新增 `tests/test_concept_feeds.py`（无概念不得空喂新闻；feed 缺源拒绝）。

---

## 5. 任务拆分与工期

| ID | 任务 | 估时 | 产出 |
|---|---|---|---|
| T0 | Finance 过本计划 | — | 拍板/改种子概念列表 |
| T1 | 种子表 `config/p2_concept_seed.json` + 连通试拉 | 0.5h | raw 探针结果 |
| T2 | 拉概念成分 → `data/p2/concepts.json` | 1–2h | concepts+constituents |
| T3 | 按概念拉 feeds（news/notice） | 1h | concept_feeds |
| T4 | 各可分析方向双榜 top10 深核 + 迁移/重跑（offline 优先） | 2–4h | company_research / round2 |
| T5 | export + 闸门 + FRONTEND_FIELDS_P2 | 1h | snapshot + 字段表 |
| T6 | 与 UIUX 联调 A0/A1/A2 | 0.5h | 修缺字段 |

并行：UIUX 用 mock `concepts` 做壳；真数以 T5 字段表为准。

---

## 6. 验收（对齐 BRIEF §6）

| # | 标准 |
|---|---|
| 1 | A0 仅 concepts，无默认新闻墙 |
| 2 | 点概念 → feeds 列表；未选不可「开始分析」（前端） |
| 3 | B graph 来自新 snapshot；换数据不改前端常量主题 |
| 4 | 无假 A / 假绿；数字可追溯 |
| 5 | `validate.py` + `validate_frontend` 绿 |
| 6 | C 区四块硬指标全部主位可验（§8） |

---


## 8. P2 硬指标验收（Finance · 缺一不算完成）

| # | 指标 | 算法交付 | 前端主位 |
|---|---|---|---|
| 1 | 产业链分类口径+层级+归属证据 | `concepts` + graph 归属边 + `source_ids` | C① |
| 2 | 概念 A–E（禁假 A） | grade 闸门 + 窄口径 missing_reason | C② |
| 3 | 中外可比/不可比边界 | `pairs` 金额/比率闸门 + 文案 | C③ |
| 4 | 事件→环节→业务→财务传导 | `events[]` fact/inference 分离 | C④ |

细节字段见 `FRONTEND_FIELDS_P2.md`「C 区四块硬指标」。双榜/feeds 是入口能力；**上述四块是 Agent 输出硬验收**。

## 7. 拍板记录（已确认）

1. 种子：根 AI + 芯片/服务器/光模块/液冷/供配电/应用软件（应用浅覆盖）✅  
2. ~~全局深研 8~~ → **每可分析方向双榜各 top10** ✅  
3. feeds 窗 30 天 ✅  
4. 授权在线试拉（费用走现有密钥，raw 留痕）✅  
5. 仅 AI demo `analysis_enabled=true` 可进 B/C ✅  

开跑中：扶摇概念 catalog + 成分；市值榜实拉；权重榜无 API 则诚实空态。

## 9. Agent 自跑验收（Finance 拍板）

主链路（DeepSeek 基线）跑通后，算法必须用**本助手模型**再**完整跑同一编排**（同 DAG/闸门/registry/种子，仅换模型配置），对照基线验：

- **稳定性**：可复现、不崩、闸门行为一致  
- **准确性**：禁假 A、四硬指标可追溯、不编造  

产出 **差异报告** `docs/P2_AGENT_SELFCHECK.md`（非口头“配置能通”），再喊验收/盲测。

