# 前端字段表 P2（算法 → UIUX）

> 研究主题：`theme_mode=concept_board`｜种子见 `config/p2_concept_seed.json`  
> 状态：**双榜契约已定**（2026-10-21）；真数扶摇试拉中，壳子按下列键接（缺省安全默认已注明）

## A0 / A1 / A2

### `concepts[]`

| 键 | 类型 | 说明 |
|---|---|---|
| `id` | string | 如 `concept.ai_chip` |
| `name` | string | 展示名 |
| `parent_id` | string\|null | 根为 null 或指向 `concept.ai` |
| `level` | number | 0=根，1=子概念… |
| `company_ids` | string[] | 成分并集（可大于 10）；列表展示**勿**直接当排序源 |
| `company_count` | number | |
| `analysis_enabled` | boolean | **`true` 才可「开始分析」**；缺省视为 `false` |
| `shallow` | boolean | 可选；应用软件本轮 true |
| `description` | string | 可选 |
| `source_ids` | string[] | 可选 |
| `ths_code` | string | 可选；同花顺概念板代码，如 `885728.TI` |
| `rank_by_mkt_cap` | RankBoard\|null | **市值榜**（可分析方向必出；见下） |
| `rank_by_concept_weight` | RankBoard\|null | **概念权重榜**（可分析方向必出键；无源则空 items + `missing_reason` 机读码 + `empty_reason_zh` 人话） |

悬停置灰 CTA 文案（对客）：本板块暂不可分析（禁写 Demo/API Key 等对内词）

### `RankBoard`（双榜共用结构）

| 键 | 类型 | 说明 |
|---|---|---|
| `metric` | `"mkt_cap"` \| `"concept_weight"` | 与所在字段一致 |
| `metric_label` | string | 展示用：`市值` / `概念权重` |
| `as_of` | string\|null | 时点，ISO 或 `YYYY-MM-DD` |
| `unit` | string\|null | 如 `CNY`；权重可为 `pct` 或 `null` |
| `items` | RankItem[] | **默认展示前 10**；可多于 10 但 UI 默认截前 10 |
| `missing_reason` | string\|null | **机读码**；items 为空时必填（如 `weight_api_unavailable`）；有 items 时 null；**禁止直接展示给用户** |
| `empty_reason_zh` | string\|null | **人话空态**；items 为空时必填（如「权重数据暂不可用」）；有 items 时 null；**UI 空态优先读此键** |

### `RankItem`

| 键 | 类型 | 说明 |
|---|---|---|
| `rank` | number | 1-based |
| `company_id` | string | 与 `companies[].id` 对齐 |
| `name` | string | 展示名（可与 companies 重复，便于列表直读） |
| `thscode` | string\|null | 如 `300308.SZ` |
| `value` | number\|null | 市值金额或权重值；未知则 null，**禁止编造** |
| `value_display` | string\|null | 可选预格式化文案 |

### RankItem id 策略（`p2.joinable.2`）

| 键 | 规则 |
|---|---|
| `thscode` / `ticker` | **稳定市场键**，始终填写 |
| `company_id` | 能映射到 `companies[].id` 时用同一 slug（如 `fii`）；否则 **`null`**（禁止 `co.601138_sh` 伪 id） |
| `deep_company_id` | 与可映射时的 `company_id` 相同；未映射为 null |
| `deep_linked` | bool，便于前端分流 |
| `market_id` | 可选；仅未映射时调试用 `mkt.{thscode}` |

`concepts[].company_ids`：仅含已映射深核 slug（可进 C 过滤）；未深核市值行靠榜 `items` + `thscode` 展示。

## 对客文案（盲测 0.3.21 / research `b1h.p1.c`）

**算法保证（snapshot 正文）**

- `sources[].title` / `locator`：人话；禁止 `P2 raw`、`response.data…`、`thscode=` 机读定位串。
- 空态对客只认 **`empty_reason_zh`**（榜、feeds、指标/占比空）。`missing_reason` 仅机读（或历史中文人话镜像），**禁止当 UI 文案键展示**。
- `pairs[]` 对客用 `title` / `summary`；禁止裸露 `pairs[].id`（如 `inspur_smci`）。

**壳必须藏（算法键仍在 JSON，壳藏不住会再漏）**

- 键名：`thscode`、`missing_reason`、`market_id`、`deep_company_id`、`pair` id、`data_hash`、commit/`p2_notes`。
- 榜行展示：`name` + `ticker`（或 `value_display`）；不要打印 `thscode=` 标签。
- 页脚：生产闭环短链可留；版本哈希/commit 默认折叠对内。




**列表规则（前端）**

- 页签切换读 `rank_by_mkt_cap` / `rank_by_concept_weight`；**默认市值**。
- 按 `items[].rank` 升序；缺整板时回退 `company_ids` 原序。
- 权重板 `items=[]`：页签可点；空态文案读 **`empty_reason_zh`**（如「权重数据暂不可用」）；**勿**把 `missing_reason` 机读码拼进 UI；勿假填。

### `concept_feeds`

`Record<concept_id, FeedItem[]>`（数组契约不变，便于兼容）

| 键 | 类型 | 说明 |
|---|---|---|
| `id` | string | |
| `title` | string | |
| `date` | string|null | ISO 或 YYYY-MM-DD |
| `url` | string|null | 外链；可空 |
| `kind` | `news`|`notice`|`filing`|`other` | |
| `source_id` | string | 进 `sources` |
| `publisher` | string | 可选 |

**过滤策略（盲测 P1）**：只保留产业/概念相关资讯；**禁止时政/国际政治灌屏**。过滤后无条 → 数组为 `[]`，并在 `concept_feeds_meta` 给诚实空态人话。

### `concept_feeds_meta`（空态人话，新增）

`Record<concept_id, FeedMeta>`

| 键 | 类型 | 说明 |
|---|---|---|
| `empty_reason_zh` | string|null | 该概念 feeds 为空时必填人话（如「本轮暂无与该概念直接相关的产业资讯」）；有条目时 null |
| `source_policy` | string | 如 `industry_concept_only` |
| `filtered` | boolean | 本轮是否做过产业相关过滤 |

A0：只渲染 `concepts`。A1：`concept_feeds[selectedId]`（建议最近 20 条）。A2：仅 `analysis_enabled===true` 启用 CTA。

## B / C（兼容）

沿用 P1：`graph.nodes.impact`、`companies`、`events[]`、`pairs.*` 可比闸门。  
**公司池**：每可分析方向双榜各 top10 进展示；深核按预算覆盖这些公司，证据不足诚实 B/C/E，**禁假 A**。  
分支名/主题名**只读数据**，禁止写死旧四分支；**勿写死全局 8 家**。

## `meta`

| 键 | 例 |
|---|---|
| `theme_mode` | `"concept_board"` |
| `research_version` | `"2026-10-22.p2.deep.b1h.p1"`（盲测 P1 契约增量；非新深核） |
| `feeds_window_days` | `30` |
| `rank_default` | `"mkt_cap"` |

## Mock 最小例

```json
{
  "concepts": [
    {
      "id": "concept.ai_chip",
      "name": "AI芯片",
      "parent_id": "concept.ai",
      "level": 1,
      "company_ids": ["co.a", "co.b"],
      "company_count": 2,
      "analysis_enabled": true,
      "ths_code": "885756.TI",
      "rank_by_mkt_cap": {
        "metric": "mkt_cap",
        "metric_label": "市值",
        "as_of": "2026-10-21",
        "unit": "CNY",
        "items": [
          {"rank": 1, "company_id": "co.a", "name": "示例甲", "thscode": "000001.SZ", "value": 1.2e11},
          {"rank": 2, "company_id": "co.b", "name": "示例乙", "thscode": "000002.SZ", "value": 9.0e10}
        ],
        "missing_reason": null
      },
      "rank_by_concept_weight": {
        "metric": "concept_weight",
        "metric_label": "概念权重",
        "as_of": null,
        "unit": null,
        "items": [],
        "missing_reason": "weight_api_unavailable",
        "empty_reason_zh": "权重数据暂不可用"
      }
    },
    {
      "id": "concept.other_demo_disabled",
      "name": "其他板块（Demo不可分析）",
      "parent_id": null,
      "level": 0,
      "company_ids": [],
      "company_count": 0,
      "analysis_enabled": false,
      "rank_by_mkt_cap": null,
      "rank_by_concept_weight": null
    }
  ],
  "concept_feeds": {
    "concept.ai_chip": [
      {"id": "feed.mock.1", "title": "示例公告", "date": "2026-10-01", "url": "https://example.com", "kind": "notice", "source_id": "src.mock.1"}
    ]
  },
  "concept_feeds_meta": {
    "concept.ai_chip": {"empty_reason_zh": null, "source_policy": "industry_concept_only", "filtered": true},
    "concept.other_demo_disabled": {"empty_reason_zh": "本轮暂无与该概念直接相关的产业资讯", "source_policy": "industry_concept_only", "filtered": true}
  }
}
```

## 盲测 P1 空态键（给 @UIUX）

> 契约增量：`p2.deep.b1h.p1`（非新深核）。算法已灌；**勿**再裸露机读码。

| 场景 | 优先读 | 勿展示 |
|---|---|---|
| 权重榜空 | `concepts[].rank_by_concept_weight.empty_reason_zh` | `missing_reason`（如 `weight_api_unavailable`） |
| 市值榜空 | `rank_by_mkt_cap.empty_reason_zh` | 同上 |
| 概念 feeds 空 | `concept_feeds_meta[concept_id].empty_reason_zh`（缺省可回退「本概念暂无资讯链接」） | 时政灌屏条目（算法侧已滤） |

## C 区四块硬指标（P2 必验 · 主位露出）

> Finance 拍板：缺一项不算 P2 完成；导出与 C 区摘要**优先露出**，禁止只埋附录。

| # | 硬指标 | Snapshot 主字段（前端主位） | 验收要点 |
|---|---|---|---|
| 1 | **产业链分类口径 + 层级 + 公司归属证据** | `concepts[]`（id/name/parent_id/level）+ `graph.nodes/edges`（含 `industry_membership`）+ 边/节点 `source_ids` → `sources` | 层级可见；归属边可点开证据；无 source 不得声称已归属 |
| 2 | **概念关系 A–E 可信度** | `companies[].assessment` / `claims[]` 的 `grade` + `rationale` + `source_ids`；窄口径 `ai_specific_revenue` / `missing_reason` | 有收入才可 A；窄口径禁假 A；B/C/D/E 文案诚实（见 `CONCEPT_GRADES.md`） |
| 3 | **中外可比：为何可比 / 哪些不可比** | `pairs[]`：`aligned_period`、`amount_compare_allowed`、`ratio_compare_allowed`、边界文案字段（summary / incomparability_notes） | 金额/比率闸门；不可比须明示，禁止静默比金额 |
| 4 | **外部变化→环节→业务→财务** | `events[]`（或主 `event`）：完整传导链；steps 分 `fact` / `inference` / `scenario` + `source_ids` | fact/inference 分离展示；无 fact 不得装成已证实财务影响 |

### C 区布局约定（给 @UIUX）

建议主位四块顺序固定为：**①归属与层级 → ②A–E → ③可比边界 → ④传导路径**；次要折叠只放 feeds/原始链接等。算法 export 将尽量提供 `c_zone_blocks` 摘要指针（可选，见下）；无该键时前端按上表字段拼。

### 可选 `meta.c_zone_priority` / `c_zone_blocks`

```json
{
  "c_zone_blocks": [
    {"id": "taxonomy_membership", "title": "产业链分类与归属证据", "primary_paths": ["concepts", "graph"]},
    {"id": "concept_grades", "title": "概念可信度 A–E", "primary_paths": ["companies.assessment", "claims"]},
    {"id": "comparability", "title": "中外可比边界", "primary_paths": ["pairs"]},
    {"id": "transmission", "title": "事件传导路径", "primary_paths": ["events"]}
  ]
}
```

## 生产闭环（说明）

见 [`PROD_LOOP.md`](./PROD_LOOP.md)。原型只读已发布 snapshot；不上真定时任务。
