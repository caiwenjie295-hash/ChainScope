# ChainScope 算法 P1 计划（收窄做满）

> 作者：算法｜拍板：Finance｜日期：2026-10-21（Asia/Hong_Kong）  
> 前置：P0 已落地（`ALGO_P0_PLAN.md` / `CONCEPT_GRADES.md`）  
> 叙事默认：**液冷 + 光模块**；深研 8 家为主；14 家 E 仅搜索可见（前端折叠由 UIUX 后续接）  
> 约束：不编造；不大改视觉；impact 无证据保持 unclear；密钥不入库。

---

## 0. 目标与成功标准

| # | 目标 | 成功标准 |
|---|---|---|
| 1 | **有证据才写 impact** | 仅液冷/光相关 theme·branch·segment（及有披露触点的公司节点）可标 `positive`/`negative`；其余仍 `unclear`；`impact_report.json` 的 unclear_ratio **&lt; 1.0** 且附核验依据 source_ids |
| 2 | **`validate.py` 全绿** | 补齐缺失公开披露文件（优先 PDF）或等价可哈希原文，使 `check_bundle(..., verify_files=True)` 与 `unittest` 中文件哈希用例通过 |
| 3 | **再加 1 个可核验事件或第二对比组** | 优先：光模块侧第二事件（有公开事实源）；或补强一组同期间可比（若数据可得）。须 fact/inference/scenario 分离，无合同不写收入弹性 |

演示主线（说服力）：英维克–Vertiv H1 对齐 + Blackwell→液冷；中际旭创–Coherent 光互联（边界写清）+ 第二事件。

---

## 1. 任务拆分

### T1 — Impact 核验写入（仅有披露）

| 项 | 内容 |
|---|---|
| 范围 | 建议可核验正向：`branch.cooling` / `segment.thermal`（液冷需求与产品证据）；`branch.optics` / `segment.transceiver`（高速模块商业交付）。替代/受挤占（绿）本轮若无硬证据 → **不写 negative，保持 unclear** |
| 做法 | 新增 `data/impact_annotations.json`（node_id → impact, rationale, source_ids, reviewed_at）；`export_frontend.py` 合并注解，无注解强制 unclear；闸门：positive/negative 必须非空 source_ids |
| 验收 | impact_report 分项计数；故意无源标 positive → export/validate 失败 |
| 产出 | `data/impact_annotations.json`；更新 snapshot；测试 |

### T2 — 补公开披露，校验全绿

| 缺失文件（当前） | URL 来源（sources 已记） |
|---|---|
| `artifacts/public/inspur_annual_2025.pdf` | 新浪/巨潮镜像（sources） |
| `artifacts/public/innolight_annual_2025.pdf` | cninfo |
| `artifacts/public/kehua_annual_2025.pdf` | cninfo |
| `artifacts/public/envicool_annual_2025.pdf` | cninfo |
| `artifacts/public/coherent_fy2025_tables.pdf` | Coherent IR |

| 项 | 内容 |
|---|---|
| 做法 | 按 sources.url 重新拉取 PDF；核对 SHA-256 与 `data/sources.json`；若官方改链则更新 url+hash+txt 摘录并记入 CHANGELOG |
| 降级 | 仅当 PDF 永久不可得：把 `local_path` 改指向已有 `.txt` 并重算 hash（须标注 access 边界）——优先仍要 PDF |
| 验收 | `python scripts/validate.py` status=passed；`test_real_bundle` / `test_tampered_source_rejected` 绿 |
| 产出 | 5 个 PDF（或文档化降级）；更新 validation_report |

### T3 — 第二事件或第二对比组

| 选项 | 内容 | 选用条件 |
|---|---|---|
| **A（优先）** | 光模块事件卡：例如 1.6T/高速模块收入出货类**已有原文**的产品事实 → 传导至 `segment.transceiver`（机制=inference，无合同不写金额） | 本地 sources 已有可引用片段 |
| **B** | 第二对比组补「同期间」小样本（若能取得对齐财报） | 不拉长在线大跑；48h 内取不到则不做 |
| 本 P1 默认 | **先做 A**；B 作可选加分 | |

产出：扩展 snapshot `event` 为列表或 `events[]`（若前端仍读单 event，则主事件保持液冷，第二事件进 `overview.changes` 或 `events` 新字段并通知 UIUX）；schema 对齐 `event_transmission.schema.json`。

### T4 — 演示叙事与候选折叠（算法侧数据）

| 项 | 内容 |
|---|---|
| overview | 标题/动机侧重「液冷 + 光模块」；coverage 文案不夸大 14 家 |
| candidates | 保持 E；snapshot 可加 `demo_priority` 或 `narrative_focus` 供前端折叠（**字段表先出，UIUX 再接**） |
| 不做 | 14 家深核；编造 AI 专项收入；无证据上红绿 |

---

## 2. 验收用例

| ID | 用例 | 期望 |
|---|---|---|
| AC1 | thermal/transceiver（或计划内节点）impact=positive 且带 source_ids | 通过 |
| AC2 | 随机 theme 无注解却 positive | export 失败 |
| AC3 | 缺失 PDF 补齐后 validate.py | passed |
| AC4 | 篡改一字节 PDF | hash mismatch |
| AC5 | 第二事件 fact 步有源；含 % 弹性无源 | 拒 |
| AC6 | impact_report unclear_ratio &lt; 1.0 | 真 |

---

## 3. 产出路径

```
docs/ALGO_P1_PLAN.md
data/impact_annotations.json
artifacts/public/{inspur,innolight,kehua,envicool}_annual_2025.pdf
artifacts/public/coherent_fy2025_tables.pdf
artifacts/frontend/impact_report.json   # 更新
artifacts/validation_report.json      # 全绿
frontend/public/data/snapshot.json   # 重 export
schemas/event_transmission.schema.json  # 若 events[] 则小扩
tests/test_impact_gate.py            # 新增
```

---

## 4. 执行顺序

1. T2 拉 PDF / 对齐 hash（解锁全量校验）  
2. T1 impact 注解 + 闸门 + 测试  
3. T3 第二事件（光侧）  
4. 离线 export → validate_frontend → validate.py → unittest  
5. 群里交字段表（impact / events / demo_priority）喊 @UIUX  

---

## 5. 需 Finance 知晓的边界

- 绿（替代/受挤占）本轮大概率仍全 unclear：缺「被挤占」硬披露，不强行上色。  
- 第二对比组同期间若取数失败，不阻塞 T1/T2/事件 A。  
- 前端红绿与 14 家折叠：**等本 P1 export 后字段表**，不提前改视觉。


---

## 6. 执行状态（2026-10-21）

| 任务 | 状态 | 结果 |
|---|---|---|
| T2 补 PDF | 完成 | 5/5 拉取且 sha256 与 sources 一致；`validate.py` 687 项 passed |
| T1 impact | 完成 | 8 个 positive；unclear_ratio≈0.771；无 negative |
| T3 第二事件 | 完成 | `optics_high_speed_shipments` 入 `events[]` |
| 测试 | 完成 | impact/fake-A/frontend/contract 相关用例绿；validate_frontend 1068 |
| 字段表 | 完成 | `docs/FRONTEND_FIELDS_P1.md` |
