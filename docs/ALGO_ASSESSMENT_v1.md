# ChainScope 离线研究 Agent — 算法评估 v1

> 作者：算法｜负责人：Finance｜日期：2026-10-21（Asia/Hong_Kong）  
> 范围：评估与方案，**本阶段不大改代码**；不改前端视觉。  
> 依据：仓库 README / 两轮报告 / `scripts/*` / `schemas/` / `data*` / `artifacts/connectivity/` / `THIRD_PARTY_NOTES.md` / UX freeze 与 IA 线框。  
> 密钥未写入本文。

---

## 1. 现状评分

| 维度 | 分（/10） | 一句话 |
|---|---:|---|
| 编排与闸门 | **7.5** | 固定阶段 DAG + 阶段内选工具 + 独立反证/有限修复已实跑；非全自主规划，边界写得清楚 |
| 证据可追溯 | **8.0** | source_id / metric_id / SHA-256 / 失败留痕齐全；确定性校验通过 ≠ 事实审计 |
| A–E 概念分级 | **7.0** | Schema+校验强约束 A 级；宽/窄口径双轨已落地；D 级几乎未用，AI 窄口径普遍缺 A |
| 中外可比边界 | **7.5** | 四组可比/不可比说明完整；仅英维克–Vertiv 对齐同自然年半年量化 |
| 事件→环节→业务→财务 | **6.0** | 有 1 个 Blackwell Ultra 传导案例且 fact/inference 分离；未产品化为可复用模板 |
| 数据通路（扶摇/iFinD/公开披露） | **6.5** | 连通实测 OK；海外财年错配、官网直连失败、MCP 片段边界仍在 |
| 喂前端可靠性 | **6.5** | `export_frontend` 有闸门与 E 级候选保护；星图 `impact` 本轮全 `unclear`，红绿语义未上线 |
| 交付验收完备度 | **5.5** | 本地 Web+文档+校验齐；公开仓库、演示视频、受控对比实验、再分发合规未齐 |

**综合：约 6.8 / 10** — 作为「可复现的离线研究辅助」已过线；距「可信产业结论流水线」差在：窄口径收入补证、impact 核验、事件传导模板化、前端字段闸门硬化。

---

## 2. 现有 Agent 框架与编排

### 2.1 流水线地图

**首轮（契约 + 采集 + 单轮 Flash）**

`probe → collect / fetch_public → build_research → run_agent → finalize → validate`

**第二轮（PydanticAI DAG）**

```
研究对象 → 业务证据×8 → 财务质量×8 → 跨市场比较×4
         → 独立反证×4 →（有预算补证/修复）→ 研究编辑×4
         → 事件传导×1 → 确定性验证 + 语义抽核 → JSON/报告
```

实现主文件：`scripts/round2_agents.py`（`VERSION=round2.agents.v4`），复现：`prepare_round2 → round2_agents [--offline] → repair_round2 → publish_round2`。

### 2.2 已做对的设计

1. **数字与叙事分离**：财务由代码算（FinRobot 思路）；模型写机制与边界，正文禁写阿拉伯数字（技术型号例外）。
2. **独立反证角色**（TradingAgents 思路）：不把上游草稿当证据；反证本身也标注「不可默认全对」。
3. **硬闸门**：A 级必须绑定非 `consolidated_total` 且非空 `metric_id`；claim/assessment 必须挂 `source_ids`；失败 attempt 保留。
4. **事实分层**：`fact` / `inference` / `scenario`；quote 限单一来源连续短句。
5. **工具预算**：检索轮次与补证次数有上限；阶段名单由代码指定，避免「伪多 Agent 并发」。

### 2.3 缺口与风险

| ID | 风险 | 说明 |
|---|---|---|
| R1 | 校验≠审计 | 首轮 661、二轮 686 项「通过」只保证契约/引用/空值规则，不保证结论真 |
| R2 | 反证亦模型 | 资本开支 vs 经营现金流等归因仍可能错；仅靠再一轮模型不够 |
| R3 | D 级空洞 | Schema 有 D，实盘几乎不见；A–E 语义对客户不够产品化 |
| R4 | 事件传导单例 | 仅 Blackwell Ultra→液冷；缺通用「事件卡 → 环节 impact → 公司 claims」流水线 |
| R5 | 语义抽核人工 | `semantic_review` 依赖研究者；无可回归的抽核集 |
| R6 | 前端红绿未接 | snapshot 节点 `impact` 全 `unclear`；图例已诚实，但产品语义未闭环 |
| R7 | 许可与再分发 | 金融接口原始响应本地可用；公开发布前缺许可审查 |

---

## 3. 数据通路问题

### 3.1 连通性（`artifacts/connectivity/`）

| 通路 | 状态 | 备注 |
|---|---|---|
| iFinD MCP（综合/A股/海外/资讯） | HTTP 200，工具可发现 | 工具数含跨服务重复 |
| DeepSeek `deepseek-flash` | chat 200 | 模型固定；用量进 evaluation |
| 扶摇 | key_present | 首轮合并利润表取数成功 |

### 3.2 质量问题清单

1. **财年错配**：海外 MCP 曾未按要求对齐财年 → 整份财务隔离，改官网披露（首轮已记录）。
2. **空值诚实但覆盖不均**：海外相关业务收入多 `null`；AI 窄口径几乎全缺 → 无法给 AI 概念 A。
3. **期间对齐稀缺**：仅英维克/Vertiv 补齐同自然年 H1；其余组不可做同口径现金转化排名。
4. **访问边界**：MCP 片段 / `excerpt_only` 不得当全文；Eaton 官网超时+SEC 拒 → 人工事实转录，自动重建失败。
5. **旧标的碰撞**：`VRT-1.N` vs `VRT.N` 已隔离，规则需固化进采集。
6. **语料规模**：二轮 corpus ~1292 chunks；引用/指标用到的 distinct 子集更小——检索召回质量未单独评测。
7. **成本统计不完整**：最终采用阶段可估算；早期调试用量有缺失，禁止宣称总费用或节省百分比。

### 3.3 当前研究快照画像（不编造）

- 公司：22（深研 8 + 候选 14）；图谱：35 节点 / 35 边（theme1 / branch4 / segment8 / company22）。
- 首轮 assessment 等级分布（可多概念）：A:4，B:5，C:3，E:14（E 多为广度候选）。
- snapshot 公司 grade：B:7，C:1，E:14；**impact 全 unclear**。
- claim kinds：fact 与 inference 各 22（成对出现，需防「看起来很满」的错觉）。

---

## 4. 对照原题验收

### 4.1 主链路：产业链分类 / 归属证据 / A–E

| 要求 | 现状 | 差距 |
|---|---|---|
| 分类口径与层级 | 人工 taxonomy；theme→branch→segment→company | 层级规则未版本化为可测规范；公司归属边证据强度不一 |
| 公司归属证据 | assessments + claims + source_ids | 候选 14 家 E 级仅保护位，未定向核验 |
| A–E | A=对应口径收入；B=商业证据无窄收入；C=产品/订单进展；E=证据不足；D 预留 | 需在 schema/产品文案钉死五级定义表；窄口径 A 几乎不可达 |

### 4.2 中外可比 + 传导路径

| 要求 | 现状 | 差距 |
|---|---|---|
| 为何可比/不可比 | 四组文字边界完整（准则/币种/财年/业务宽度） | 缺结构化 `comparability` 对象喂前端 |
| 外部变化→环节→业务→财务 | 单事件案例；fact/inference/scenario 分离 | 未进 DAG 常驻阶段；无环节 impact 打分与核验闸门 |

### 4.3 交付侧 — 算法负责产出的 artifact

| Artifact | 路径/形态 | 算法责任 |
|---|---|---|
| 五类 Schema | `schemas/*.schema.json` | 契约演进与兼容 |
| 研究数据 | `data/`、`data/round2/` | 可离线重放、版本号 |
| 原始响应与披露 | `artifacts/raw/`、`artifacts/public/` | 哈希、失败留痕 |
| Agent 轨迹 | `artifacts/agent/`、round2 traces | attempt/accepted 可审计 |
| 连通与校验 | `artifacts/connectivity/`、`validation_report.json` | 每次发布附带 |
| 运行评估 | `data/agent_evaluation.json`、`data/round2/evaluation.json` | 用量/失败类型 |
| 语义抽核 | `data/round2/semantic_review.json` | 纠偏清单 |
| 开源借鉴记录 | `THIRD_PARTY_NOTES.md` + `artifacts/references/` | 固定 commit |
| 研究报告 | `reports/*.md` | 人读结论 |
| 前端快照 | `frontend/public/data/snapshot.json`（经 `export_frontend.py`） | **只导出已闸门数据** |
| 本评估 | `docs/ALGO_ASSESSMENT_v1.md` | 本文件 |
| （待补）演示视频脚本/AI 验证记录模板 | `docs/` 或 `artifacts/qa/` | 算法列清单，不拍片 |
| （待补）异常与合规测试集 | `tests/` 扩展 | 负向用例可回归 |

**非算法本轮**：公网部署、账户系统、实时刷新、买卖建议。

---

## 5. 开源对标（已借鉴 + 可再补）

仓库已固定 commit 借鉴（见 `THIRD_PARTY_NOTES.md`），**未**跑上游流水线、未复制源码进运行时。

| 项目 | 已落实 | 可落地下一刀 |
|---|---|---|
| **FinRobot** | 代码算现金转化等；币种/期间/空值检查；取数/解释/审查分阶段 | 把「口径校验器」抽成独立 pytest 模块，对每张 metric 表强制跑 |
| **TradingAgents** | 独立反证 + 编辑处理意见 | 反证输出结构化「违规类型枚举」，编辑必须逐条 resolve/reject |
| **EdgarTools** | 本地 10-K HTML 解析（Vertiv） | 固化「海外主源=公司 IR/本地 filing，MCP 仅补证」路由策略 |
| **建议补：LangGraph / 自研状态机**（不必引入重框架） | 现 DAG 已近似 | 用显式状态对象（stage, budget, repairs_left）替代隐式脚本顺序，便于测试 |
| **建议补：OpenBB / 披露抓取类工具的「原文优先」模式** | 已有 fetch_public | 统一「主源失败 → 降级标签」枚举，禁止静默换源 |

原则：借鉴**编排与校验模式**，不追交易 Agent 的下单目标。

---

## 6. 优化路线图（P0 / P1）

### P0（下一轮实验前必须）

1. **A–E 定义表产品化**  
   - 改法：在 schema 或 `docs/CONCEPT_GRADES.md` 钉死 A–E（含 D）；export 时带 `grade_definition_id`。  
   - 验证：单元测试覆盖「无 scoped revenue 不得 A」「订单≠B」。  
   - 边界：不自动上调历史等级。

2. **前端喂数闸门硬化**  
   - 改法：`export_frontend` 仅放行 `semantic_review` 批准或确定性校验通过的 headline/claims；`impact` 无核验则强制 `unclear` + 图例文案（已有方向）。  
   - 验证：故意塞未批准 claim → build/export 失败。  
   - 边界：不现场调模型；C 区只读。

3. **可比性结构化**  
   - 改法：为四组 peer 增加 `comparable_on[]` / `not_comparable_on[]` / `aligned_period?`。  
   - 验证：无 `aligned_period` 时前端禁止金额并排「大小比较」。  
   - 边界：比率方向比较与金额比较分开展示。

4. **事件传导最小模板**  
   - 改法：固定输出 `event_card`（fact 步）+ `mechanism`（inference）+ `company_touchpoints`（缺证据则 missing）。  
   - 验证：无供应合同不得写收入弹性数字。  
   - 边界：本轮仍单主题，不扩行业。

### P1（增强可信度与覆盖）

5. 海外主源补齐：Eaton 原文件归档、Supermicro 审计年对照。  
6. 14 家候选的「是否进入深研」规则（触发条件 + 工作量上限）。  
7. 反证违规类型枚举 + 抽核集回归。  
8. 检索召回评测（关键词→应命中 source_id 金标小集）。  
9. 受控 baseline（同证据包、改提示/工具预算）——**有对照才许谈成本或质量提升**。

---

## 7. 如何喂给前端真实可靠结论

对齐 UX freeze：C 只读已验证摘要；空白诚实；红绿非涨跌。

| 前端区 | 推荐字段（已有或需补） | 闸门 |
|---|---|---|
| A 动机 | `overview.*` + `event.{title,date,summary,steps,limitations}` | steps 仅 fact；limitations 必展示 |
| B 星图 | `graph.nodes`（theme/branch/segment）+ `impact` / size | impact∈{positive,negative,unclear}；unclear→中性色；无体量→默认尺寸+「未披露」 |
| B 弹层列表 | company id/name/market + `assessment.grade` | 候选 E 不展示未核验财务结论 |
| C 摘要 | `headline`、`claims[]`（kind+source_ids）、`assessment`、`uncertainties` | 无 source_ids 不出；inference 视觉区分于 fact |
| C 对比 | `pairs` 优先，否则同 segment 前 N | 缺 metric 显示未披露；禁跨币种裸比金额 |
| 页脚 | research_version、data hash、as_of | 与 manifest 一致 |

**硬规则**：`null` 保留原因；不得用集团收入填 AI 专项；浏览器零密钥。

---

## 8. 下一轮实验设计（建议 Finance 拍板）

**目标**：在不扩公司名单的前提下，把「可展示的可信结论」密度提高一档。

| 项 | 建议 |
|---|---|
| 样本 | 维持 8 家深研；温控组作主样板；另选 1 组补「同期间」小实验（若数据可得） |
| 自变量 | （A）反证违规枚举+强制 resolve；（B）事件传导模板；（C）export 闸门 |
| 对照 | 同证据包离线重放；禁止与首轮混比「准确率%」 |
| 成功标准 | ① 前端 C 区零未引用数字；② impact 至少对 L2/L3 有核验或明确 unclear 比例报表；③ 新增 ≥1 个可复现负向测试（假 A 级被拒） |
| 非目标 | 全自主规划、实时行情、公网再分发、改 UX 视觉 |

**需 Finance 拍板**

1. P0 是否按上表四条进入下一轮开发（仍先方案评审再改代码）？  
2. 窄口径 AI 收入长期缺失时，产品是「永久 B/C + 解释」还是「隐藏窄概念只留宽口径 A」？  
3. 14 家候选是否本季度启动定向核验，还是保持 E 级占位？

---

## 9. 一页结论（给群）

二轮 DAG + 闸门已经能支撑「可审计的离线研究辅助」，最大风险是**把校验通过当成事实正确**、**红绿 impact 未核验**、以及**窄口径收入缺失却看似结论完整**。建议下一轮只做 P0：A–E 产品化、export 闸门、可比性结构化、事件传导模板——再考虑扩覆盖。
