# ChainScope 算法 P0 计划

> 作者：算法｜拍板：Finance｜日期：2026-10-21（Asia/Hong_Kong）  
> 依据：`ALGO_ASSESSMENT_v1.md` §6–§8 + 群拍板三问  
> 约束：先契约/脚本/测试，再离线重放；**不大改视觉**；不编造数字；密钥不入库。

---

## 0. 拍板摘要

| # | 决定 |
|---|---|
| 1 | P0 四条开干：A–E 产品化、export 闸门、可比性结构化、事件传导模板 |
| 2 | 窄口径：保留概念；允许永久 B/C + 解释；**禁止**集团收入冒充 AI 专项 A；缺数→「未披露/未核验」 |
| 3 | 14 家候选保持 E 占位，不深核；精力在 8 家 + P0 可信度 |

**成功标准（§8）**

1. 前端 C 区导出数据：**零未引用数字**（claims/headline 关联数字须有 source_ids 或 metric_ids）  
2. **impact**：有核验则写入；否则 unclear + 可统计报表（比例/节点列表）  
3. **≥1** 个负向测试：伪造 A 级（无 scoped revenue）必须被拒  

---

## 1. 任务拆分

### T1 — A–E 产品化

| 项 | 内容 |
|---|---|
| 做什么 | 钉死五级定义；export/校验引用同一份定义；窄口径允许 B/C，禁止假 A |
| 改哪些 | 新增 `docs/CONCEPT_GRADES.md`；`schemas/company_research.schema.json`（description/enum 注释对齐）；`scripts/validate.py` / `export_frontend.py` 读定义或内嵌常量 |
| 验收 | 文档含 A–E（含 D）；假 A 用例失败；现有 8 家深研等级不被本轮无故上调 |
| 产出 | `docs/CONCEPT_GRADES.md`；相关脚本小改；测试见 T5 |

**等级口径（写入 CONCEPT_GRADES，与现闸门一致）**

- **A**：对应概念口径有可核验收入数值（非集团 `consolidated_total`，非用母类代替 AI 专项）  
- **B**：有商业/交付业务证据，窄口径收入未知或未披露  
- **C**：产品发布、订单/进展证据，尚未核实销售交付  
- **D**：仅战略表态/合作意向，无产品与收入证据（预留，本轮可 0 条）  
- **E**：本轮证据不足或未核验（含 14 家候选占位）；**≠** 公司无该业务  

### T2 — export 闸门硬化

| 项 | 内容 |
|---|---|
| 做什么 | `export_frontend.py` 只放行已通过确定性校验、且（深研）经抽核策略允许的字段；候选 E 不导出未核验财务结论 |
| 改哪些 | `scripts/export_frontend.py`；必要时 `validate_frontend.py` |
| 验收 | 无 `source_ids` 的 claim 不得进 snapshot；故意插入未引用数字 → export/validate 失败；C 区字段仍只读快照、不调模型 |
| 产出 | 更新后的 `frontend/public/data/snapshot.json`（离线重放后）；闸门日志可选 `artifacts/frontend/export_gate.json` |

### T3 — 可比性结构化

| 项 | 内容 |
|---|---|
| 做什么 | 四组 peer 增加结构化可比/不可比与期间对齐标记 |
| 改哪些 | `schemas/`（company_research 或独立小 schema）；`data/company_research.json` 或 round2 编辑结果 → export 映射到 snapshot `pairs` |
| 验收 | 无 `aligned_period` 时导出侧标记 `amount_compare_allowed=false`（前端本轮可不改 UI，只带字段）；有对齐的英维克–Vertiv 为 true（比率/方向，金额仍分币种） |
| 产出 | 数据字段 + schema；测试断言 |

### T4 — 事件传导最小模板

| 项 | 内容 |
|---|---|
| 做什么 | 固定 `event_card`：fact 步骤 + mechanism(inference) + company_touchpoints + missing；无供应合同不得写收入弹性数字 |
| 改哪些 | 新增 `schemas/event_transmission.schema.json`（或并入现有）；`data/` 或 snapshot `event` 对齐；脚本校验 `kind` |
| 验收 | 现有 Blackwell 案例能通过 schema；故意加入无引用「收入+X%」→ 校验失败 |
| 产出 | schema + 校验钩子；现事件数据迁移/标注 |

### T5 — 测试与离线重放

| 项 | 内容 |
|---|---|
| 负向 | `tests/test_gate_fake_a.py`（或并入 `test_contract.py`）：无 scoped revenue 的 A → 失败 |
| 正向 | 现有 unittest 全绿；`validate.py` / `validate_frontend.py` 通过 |
| 重放 | 优先 `--offline`：`prepare_round2` 不强制；`export_frontend` + `validate_frontend`；若需 round2 离线则按 README |
| impact 报表 | 脚本或校验输出 `artifacts/frontend/impact_report.json`：`{unclear, positive, negative, ratio}` |

### 明确不做（本 P0）

- 改 UX 视觉 / 红绿上色（等有核验 impact 再喊 UIUX）  
- 14 家候选定向深核  
- 在线重新大跑模型（除非离线不够验证闸门）  
- 公网发布、许可审查全文  

---

## 2. 验收用例（可勾选）

| ID | 用例 | 期望 |
|---|---|---|
| AC1 | 构造 assessment grade=A 且 metric 为 null 或 scope=consolidated_total | `validate` 失败 |
| AC2 | 构造 claim 含数字但 source_ids 为空 | export 闸门拒绝 |
| AC3 | 候选公司（E）snapshot 无冒充已核验的 AI 专项收入 | `ai_specific_revenue` 保持 null + missing_reason |
| AC4 | 英维克–Vertiv pair：`aligned_period` 存在；跨币种 `amount_compare_allowed=false` 或等价 | 字段正确 |
| AC5 | 事件 steps 中 inference 不得充当唯一收入证据 | schema/校验 |
| AC6 | impact 全 unclear 时生成报表，ratio=1.0 | `impact_report.json` |
| AC7 | `npm`/`unittest`/validate 链路在离线重放后通过 | CI 级本地绿 |

---

## 3. 预计产出路径

```
docs/CONCEPT_GRADES.md
docs/ALGO_P0_PLAN.md          # 本文件
schemas/event_transmission.schema.json   # 若独立
schemas/company_research.schema.json     # 增补 description / comparability
scripts/export_frontend.py               # 闸门
scripts/validate.py                      # 假 A + 事件/可比钩子
scripts/export_impact_report.py          # 或并入 validate_frontend
tests/test_gate_fake_a.py                # 或 test_contract 增补
artifacts/frontend/impact_report.json
artifacts/frontend/export_gate.json      # 可选
frontend/public/data/snapshot.json       # 重放后更新（字段兼容，视觉不动）
data/company_research.json               # 仅结构化补字段，不改已核验数字
```

---

## 4. 执行顺序

1. T1 定义文档 + 校验常量  
2. T5 先写假 A 负向测试（红灯）→ 补闸门至绿灯  
3. T2 export 闸门 + C 区引用检查  
4. T3 可比性字段  
5. T4 事件模板 schema + 挂校验  
6. 离线 export + impact 报表 + 全量测试  
7. 群里汇报：完成项 / 路径 / 是否需 UIUX 对字段  

---

## 5. 风险与边界

- 抽核（semantic_review）不能自动化替代；P0 闸门以**确定性规则**为主，抽核结果作深研放行白名单（若接）。  
- 离线重放不声称「准确率提升%」。  
- 字段新增保持向后兼容：前端未读新字段也不崩（UIUX 旁听，变更再喊）。  


---

## 6. 执行状态（2026-10-21）

| 任务 | 状态 | 说明 |
|---|---|---|
| T1 CONCEPT_GRADES | 完成 | `docs/CONCEPT_GRADES.md`；`validate.py` 增加 AI 概念 A 禁母类收入 |
| T5 假 A 负向测试 | 完成 | `tests/test_gate_fake_a.py` 4/4 通过 |
| T2 export 闸门 | 完成 | `assert_claim_citations`；`artifacts/frontend/export_gate.json` |
| T3 可比性结构化 | 完成 | pairs 增 `aligned_period` / `amount_compare_allowed` / `ratio_compare_allowed` 等 |
| T4 事件模板 | 完成 | `schemas/event_transmission.schema.json`；前端校验禁无引用弹性% |
| impact 报表 | 完成 | `artifacts/frontend/impact_report.json`（本轮 unclear_ratio=1.0） |
| 离线 export + validate_frontend | 完成 | 979 checks passed |
| 全量 `test_contract` 含文件哈希 | 环境缺口 | `artifacts/public/*.pdf` 15 条路径缺失（gitignore artifacts；箱内仅有 txt/meta）。P0 闸门用 `verify_files=False` 路径已绿；补 PDF 后 `validate.py` 全量可再跑 |

成功标准对照：① C 区 claim 无空引用（闸门+测试）；② impact 报表已出；③ ≥1 假 A 负向测试（实际 3 类假 A + 1 未引用数字）。
