# CONCEPT_GRADES 对外权威对照与修订建议

> 作者：算法｜日期：2026-10-21（Asia/Hong_Kong）  
> 依据：Finance 要求联网检索后对照 `CONCEPT_GRADES.md`；**禁编造引用**  
> 状态：**已冻结**（Finance 2026-10-21）；revision `align-cas14-wind`

---

## 0. 先说结论

| 问题 | 结论 |
|---|---|
| 有没有国际/监管「概念归属 A–E」国标？ | **没有。** 标普信用等级、CEBM 临床证据等级、财报 forensic A–D **不是**同一事物。 |
| 我们该不该废弃自拟 A–E？ | **不建议废弃字母**；应在文档与 C 区注明「产品证据阶梯」，并**对齐**公开的「披露/证据优先序」。 |
| 什么能对齐公开标准？ | **A 的收入门槛**（分部/分产品已披露金额）← IFRS 8 / ASC 280 / 证监会年报分项收入要求。 |
| 什么必须自拟并写清边界？ | **B/C/D/E 对「业务交付 vs 进展 vs 表态 vs 未核验」的产品切分**；「概念板/主题」本身不是会计科目。 |

---

## 1. 检索到的可引用类比（真实链接）

### 1.1 分部/分产品收入披露（支撑「A = 有可核验专项收入」）

| 来源 | 要点 | 链接 |
|---|---|---|
| **IFRS 8 Operating Segments** | 按管理层审阅的经营分部披露收入等；定量门槛等规则规范「可报告分部」披露 | https://www.ifrs.org/content/dam/ifrs/publications/html-standards/english/2026/issued/ifrs8.html |
| **US GAAP ASC 280**（Deloitte Roadmap 综述） | 分部利润/收入等信息按 CODM 审阅口径披露 | https://dart.deloitte.com/USDART/home/codification/presentation/asc280-10/roadmap-segment-reporting |
| **中国证监会《年报内容与格式准则第2号》** | 要求按行业/产品/地区等披露营收构成；对占收入或利润 **10% 以上**的分项列示收入、成本、毛利率等（检索摘要；以证监会正式文本为准） | 检索入口例：https://www.shanghaiinvest.com/cn/viewfile.php?id=20747 ；上交所转载 PDF：https://www.sse.com.cn/lawandrules/regulations/csrcannoun/c/10751828/files/d317e9b945c049139531169b328abca7.pdf |

**对齐含义**：公开准则要求「能拆开的收入要拆开披露」。我们把 **A** 定义为「该*概念口径*已有可核验收入数字且非集团总收入冒充」——与「分部/分产品披露优先于合并总额」同向；**不是**照搬 IFRS 8 的 10% 定量门槛（概念板往往窄于报告分部）。

### 1.2 证据等级思想（支撑「来源强弱排序」，不照搬字母）

| 来源 | 要点 | 链接 |
|---|---|---|
| **Oxford CEBM Levels of Evidence (2011)** | 按问题类型排「更可能可靠的证据」；强调判断，不是万能打分器 | https://www.cebm.ox.ac.uk/resources/levels-of-evidence/ocebm-levels-of-evidence ；导读 https://www.cebm.ox.ac.uk/resources/levels-of-evidence/levels-of-evidence-introductory-document |
| **投研证据阶梯（实践向）** | 监管申报/公司归因披露 > 可核验经营披露 > 二手综合 > 新闻表态（作线索不作规模证明） | 例：市场研究证据模型 https://cdn.jsdelivr.net/npm/pi-scientific-skills@1.1.0/skills/market-research-reports/references/evidence_model.md ；Evidence Ladder E0–E3 https://www.runcheyresearch.com/concepts/evidence-ladder |

**对齐含义**：我们闸门「claims 必须 `source_ids`、新闻/订单不能证 A」与「主源优先、表态降级」一致。**不对齐**：CEBM 是临床医学问题类型；E0–E3 是单条 claim 可验证度——可作对照表，不宜直接改名替换 A–E。

### 1.3 易混淆、明确**不对齐**的标准

| 名称 | 为何不对齐 | 边界声明（产品须写清） |
|---|---|---|
| 信用评级（如 S&P/Moody's 字母） | 偿债能力，不是概念归属 | UI 禁止写成「信用 A」 |
| 财报 forensic A–D（应计/造假红旗） | 整份报表可信度，不是「是否属于 AI 液冷」 | 可另轨展示，勿与概念 grade 混用 |
| 同花顺/券商「概念纯正度」营销分 | 无统一公开方法学，多为成分/业务关键词启发式 | 我们**不以**第三方概念评分代替年报证据 |

---

## 2. 对照现行 `CONCEPT_GRADES.md`

| 级 | 现行定义（摘要） | 可对齐公开标准的部分 | 必须保留的产品自拟 |
|---|---|---|---|
| **A** | 概念口径可核验收入；禁 consolidated_total | ✓ 对齐分部/分产品披露精神（IFRS 8 / ASC 280 / 证监会分项收入） | 「概念」常窄于报告分部；无单列时**不得**用集团收入升 A（产品硬规则） |
| **B** | 有商业交付，窄口径收入未知 | ✓ 对齐「主源披露有业务、无专项金额」 | 「交付」操作定义（年报产品线/客户案例等）自拟 |
| **C** | 发布/订单/进展，未核实交付 | ✓ 对齐证据阶梯中「进展≠收入」 | 订单→不升 B/A 的闸门自拟 |
| **D** | 仅战略表态 | ✓ 对齐「专家/表态 = 弱证据」 | 本轮可 0 条；预留 |
| **E** | 未核验/证据不足 | ✓ 对齐 abstain / 缺源不下强结论 | E ≠「公司没这业务」（产品文案） |

---

## 3. 修订建议（请 Finance 勾选）

### 建议采纳（文档层，不改字母）

1. 在 `CONCEPT_GRADES.md` 文首增加 **「非信用评级；非财报造假等级」** 免责与对照表（链到本文件 §1）。  
2. **A 级释义**显式写：优先引用年报/附注**分行业、分产品、分部**收入；与证监会分项披露及 IFRS 8/ASC 280「可分开报告的收入」同向。  
3. C 区 UI 增加一行「本产品证据阶梯」+ 链到短释义（@UIUX 只展示，不改逻辑）。  
4. 可选：每条 assessment 增加 `evidence_ladder_note`（如 `aligned: segment_disclosure` / `product_heuristic`），便于盲测解释。

### 建议暂缓

1. 改名为 CEBM Level 1–5 或 E0–E3——认知迁移成本高，且问题类型不匹配。  
2. 引入「概念纯正度」第三方分数当 grade——方法不透明，易假精确。  
3. 把 IFRS 8「10% 门槛」写进 A 的必要条件——过严且与窄概念冲突。

### 建议拒绝

1. 用集团合并收入证明窄概念 A。  
2. 用新闻稿/订单金额冒充已核实专项收入。

---

## 4. 拍板记录

- [x] 名称继续 A–E，不改名（2026-10-21 Finance）  
- [x] 修订 `CONCEPT_GRADES.md`：证据阶梯 + CAS14 + 分部禁假 A + Wind≥30% 对照  
- [x] §4：采纳 §3「建议采纳」；暂缓改名与纯正度；拒绝合并收入/新闻冒充 A；IFRS 10% 不写进 A 必要条件（2026-10-21 Finance）  
- [x] Finance 确认冻结文案（2026-10-21）  
- [ ] @UIUX C 区展开「本产品定义 / 外部对照」（已授权开工）

闸门代码未改。`evidence_ladder_note` 按拍板可选后做。
