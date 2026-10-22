# 前端字段表 P1（算法 → UIUX）

> 研究版本：`2026-10-21.round2.p1`｜snapshot 已更新｜视觉仍等你接

## 可接红绿

| 字段 | 位置 | 取值 | 说明 |
|---|---|---|---|
| `impact` | `graph.nodes[]` | `positive` / `negative` / `unclear` | **仅 8 个节点为 positive**（cooling/thermal、optics/transceiver + envicool/vrt/innolight/cohr）；其余 unclear。本轮无 negative |
| `impact_source_ids` | 同上 | string[] | positive/negative 必有 |
| `impact_rationale` | 同上 | string | 短说明 |

图例建议：有 positive 时可显示红=相关；无 negative 时不要假装有绿，或写「本轮无替代/受挤占核验」。

## 叙事焦点（14 家折叠用）

| 字段 | 位置 | 取值 |
|---|---|---|
| `demo_priority` | `companies[]` | `focus`（4）/ `deep`（其余深研 4）/ `candidate`（14） |
| `narrative_focus` | `companies[]` bool；`meta.narrative_focus` = `["cooling","optics"]` | |
| `overview.title` | 已改为「AI数据中心：液冷与高速光模块」 | |
| `overview.focus_company_ids` | 优先四家：envicool, vrt, innolight, cohr | |

## 双事件

| 字段 | 说明 |
|---|---|
| `event` | 主事件仍为 Blackwell→液冷（兼容旧 UI） |
| `events[]` | `[blackwell_ultra, optics_high_speed_shipments]`；第二件为光模块出货→光收发环节 |

## 可比性（P0 已有）

`pairs[]`：`aligned_period`、`amount_compare_allowed=false`、`ratio_compare_allowed`（仅 envicool_vrt 为 true）

## 预览

```bash
cd /workspace/chainscope/frontend && npm run dev -- --host 127.0.0.1 --port 5173 --strictPort
```
