# P2 四硬指标深核覆盖盘点

> **群报版本**：`meta.research_version=2026-10-22.p2.deep.b1h.p1` — 盲测 P1 契约（feeds 产业过滤 + 权重/feeds 空态人话）；**非新深核**；深核盘点仍以 B1h 为准。

## B1h.p1 盲测契约（2026-10-22 Asia/Hong_Kong）— 算法侧 P1

> 版本：`meta.research_version=2026-10-22.p2.deep.b1h.p1`  
> 约束：走 snapshot 契约；禁假数/假深核；不 push；不改前端视觉组件。

### 本轮动作

1. **feeds**：过滤到产业/概念相关（`industry_concept_only`）；时政灌屏剔除；空则 `concept_feeds_meta[id].empty_reason_zh`。
2. **权重榜空态人话**：`rank_by_concept_weight.empty_reason_zh`（「权重数据暂不可用」）；机读码仍在 `missing_reason`，勿裸露。
3. 先改 `FRONTEND_FIELDS_P2.md` 再灌 public snapshot；validate 绿。

### UIUX 建议新键

| 键 | 用途 |
|---|---|
| `concepts[].rank_by_concept_weight.empty_reason_zh` | 权重空态人话 |
| `concept_feeds_meta[concept_id].empty_reason_zh` | feeds 空态人话 |
| `concept_feeds`（已过滤数组） | 仅产业/概念相关；可空 |

---


## B1h 执行结果（2026-10-21 Asia/Hong_Kong）— 可演示四硬收口

> 版本：`meta.research_version=2026-10-21.p2.deep.b1h`  
> 约束遵守：禁假 A；**无假 pair**；金额只来自披露；不 push；不改前端视觉；**不开 Pro**；**不喊 P2 完成**。  
> 本轮目标：第 1 档「可演示四硬」收口（非铺满 38 席仅市值）。

### 本轮动作

1. **本批无新增深核**：盘点双榜仅市值席后，无明显可引年报/同环节 pair 新对象；不灌假、不刷 pair。
2. **审计已 deep 9 slug**（+ 非市值 `envicool` / 海外池 `lite`）的 C①–C④ 可点开性与空态。
3. **写出可演示清单**（下表）；C③ 无把握继续 `missing_reason`。

### 可演示清单（点开四硬位）

| slug | C① 归属 | C② grade | C③ pair | C④ event | 演示结论 |
|---|---|---|---|---|---|
| `fii` | 多概念成分 + 年报源 | 窄 **B** | **有** `fii_smci` | **有** `fii_ai_server_cloud` | **四硬齐可演示** |
| `eoptolink` | 同上 | 窄 **B** | **有** `eoptolink_cohr` | **有** `eoptolink_high_speed_optics` | **四硬齐可演示** |
| `innolight` | 同上 | 窄 **B** | **有** `innolight_cohr` | **有** `optics_high_speed_shipments` | **四硬齐可演示** |
| `envicool` | 研究库深核（**非**市值 top10） | 窄 **B** | **有** `envicool_vrt` | **有** `blackwell_ultra` | **四硬齐**；入口非市值主榜 |
| `tfc` | 成分 + 年报 | 窄 **B** | **空态** missing | **有** `tfc_optical_interconnect_components` | 三硬可演示；C③ 诚实空 |
| `luxshare` | 成分 + 年报 | 窄 **B** | **空态** missing | **有** `luxshare_datacenter_interconnect` | 三硬可演示；C③ 诚实空 |
| `shengyi` | 成分 + 年报 | 窄 **B** | **空态** missing | **有** `shengyi_ccl_pcb_ai_server` | 三硬可演示；C③ 诚实空 |
| `cambricon` | 成分 + 年报 | 窄 **B** | **空态** missing | **有** `cambricon_cloud_ai_accelerator` | 三硬可演示；C③ 诚实空 |
| `hygon` | 成分 + 年报 | 窄 **B** | **空态** missing | **有** `hygon_high_end_processor_ai` | 三硬可演示；C③ 诚实空 |
| `sanhua` | 低置信（在板≠液冷专项） | **E** + missing_reason | **无** | **无** | **诚实 E / 空态示范** |
| `lite` | 业绩+10-K（海外池） | 窄 **B** / 宽 A | **无**（禁假 `tfc_lite`） | 无专用 | 对标池可点；不为凑 pair |

### 缺啥写清（不为凑齐降门槛）

- **C③**：`tfc`/`luxshare`/`shengyi`/`cambricon`/`hygon` 仍缺合格**同环节**海外深核对标 → 保持 missing；禁止 `tfc_lite` 等跨层假 pair。
- **窄口径 A**：九席均无 AI/DCU/液冷专项可拆金额 → 禁假 A（宽口径 A 仅在研究库，snapshot 展示窄 B）。
- **权重双榜**：仍空（`weight_api_unavailable`）。
- **概念板 `source_ids`**：成分/目录源已挂；不谎称 P2 完成。

### 剩余仅市值名单（38 席，本批不深核）

噪声/无专项保持仅市值行（示例，完整见各概念 `rank_by_mkt_cap` 且 `deep_linked=false`）：

- 已列噪声策略：`000333` 美的、`000725` 京东方、`002352` 顺丰、`601872`、`300059` 东方财富、`300760` 迈瑞等。
- 其他高频仅市值：海康威视 `002415`、澜起 `688008`、以及各板 top10 中未映射席。
- **不**对本批名单灌深核或假 grade。

### 席位粗算（相对 B1g 不变）

deep_linked **32** / 仅市值行 **38**（7×10）；去重映射 slug **9**（含 `sanhua` E）；另 `envicool`/`lite` 可演示但不计入市值映射主位。

### 验收

- `validate.py` / `validate_frontend.py` 本轮 **绿**。
- **不喊 P2 完成**；第 1 档可演示：至少 3 家市值映射席四硬齐 + 多席三硬/E 空态可对照。

---

## B1g 执行结果（2026-10-21 Asia/Hong_Kong）

> 版本：`meta.research_version=2026-10-21.p2.deep.b1g`  
> 约束遵守：禁假 A；无专项收入不评窄口径 A；**无假 pair**；无无 fact 的财务传导；金额只来自披露；不 push；不改前端视觉；**不开 Pro 全量**。

### 本轮动作

1. **优先海光等仅市值席**：归档海光信息 FY2025 巨潮年报 PDF（query API 仍空 → 直链 `1225083088.PDF`）。  
2. **`hygon` 深核**：分产品「高端处理器」**143.62 亿元**可引；研究库宽口径 **A** / snapshot 窄「AI芯片」**B**（CPU+DCU 未拆）；挂 C① membership + C④ `hygon_high_end_processor_ai`；**不挂** C③（禁假 pair）。  
3. **`tfc`/`luxshare`/`shengyi`/`cambricon` C③**：同环节边界仍不清 → **继续 missing_reason**，不降门槛。  
4. **弱证据**：`sanhua` 维持诚实 E；噪声名（美的/海康/东方财富等）仍仅市值行。

### 总览

| slug | 窄口径 grade | C③ pair | C④ event 传导 | 备注 |
|---|---|---|---|---|
| `fii` | B | 已挂 `fii_smci` | 已挂 | 维持 |
| `tfc` | B | **未挂**（missing_reason） | 已挂 | 禁假 `tfc_lite` |
| `eoptolink` | B | 已挂 `eoptolink_cohr` | 已挂 | 维持 |
| `innolight` | B | 维持 | 维持 | — |
| `luxshare` | B | **未挂**（missing_reason） | 已挂 | 维持 |
| `shengyi` | B | **未挂** | 已挂 | 维持 B1f |
| `cambricon` | B | **未挂** | 已挂 | 维持 B1f |
| `hygon` | **B**（新） | **未挂** | **已挂** `hygon_high_end_processor_ai` | 高端处理器宽 A / 窄 B |
| `sanhua` | E | 无 | 无 | 无液冷专项；`missing_reason` |
| `lite` | 窄 B / 宽 A | 无（不为凑 tfc） | — | 维持 |
| `envicool` | B | 维持 | 维持 | 非市值 top10 |

### 各家 C①–C④（本轮新增/关键）

| slug | C① 归属 | C② A–E | C③ pairs | C④ events |
|---|---|---|---|---|
| `hygon` | membership **年报+成分** medium | 窄 B；宽高端处理器 A | **缺** | **有** |
| `tfc`/`luxshare`/`shengyi`/`cambricon` | 维持 | 窄 B | **仍缺** | 维持 |

### 仍未齐（不喊 P2 完成）

- `tfc`/`luxshare`/`shengyi`/`cambricon`/`hygon` C③ 仍缺合格同环节海外对标（禁假 pair）。
- 窄口径均无 AI/DCU 专项可拆金额 → 禁假 A。
- `sanhua` 诚实 E；噪声名仍仅市值行。
- 权重双榜仍空（`weight_api_unavailable`）。
- `validate.py` / `validate_frontend.py` 本轮 **绿**。

### 挂载表（市值 deep_linked 并集，B1g）

| 概念 | deep_linked slugs（示例） |
|---|---|
| `concept.ai` | `fii`, `cambricon`, `hygon` |
| `concept.ai_chip` | `fii`, `innolight`, `cambricon`, `hygon`, `eoptolink`, `luxshare`, `shengyi` |
| `concept.ai_server` | `fii`, `innolight`, `cambricon`, `eoptolink`, `luxshare`, `tfc` |
| `concept.ai_optics` | `fii`, `innolight`, `eoptolink`, `luxshare`, `shengyi`, `tfc` |
| `concept.ai_cooling` | `fii`, `innolight`, `luxshare`, `sanhua`(E) |
| `concept.ai_power` | `fii`, `innolight`, `cambricon`, `eoptolink`, `luxshare`, `tfc` |
| `concept.ai_software` | （shallow，0） |

席位粗算：deep_linked **32** / 仅市值行 **38**（7×10）；去重映射 slug 增至 **9**（+`hygon`；`sanhua` 为 E）。

---

## B1f 执行结果（2026-10-21 Asia/Hong_Kong）

> 版本：`meta.research_version=2026-10-21.p2.deep.b1f`  
> 约束遵守：禁假 A；无专项收入不评窄口径 A；**无假 pair**；无无 fact 的财务传导；金额只来自披露；不 push；不改前端视觉；**不开 Pro 全量**。

### 本轮动作

1. **优先可引年报映射席**：归档生益科技、寒武纪、三花智控 FY2025 巨潮年报 PDF（query API 仍空 → 直链归档）。  
2. **`shengyi` 深核**：覆铜板+PCB 相关收入 **269.18 亿元**可引；研究库宽口径 **A** / snapshot 窄 AI 材料 **B**；挂 C① membership + C④ `shengyi_ccl_pcb_ai_server`；**不挂** C③（缺同环节海外 CCL/PCB 材料深核）。  
3. **`cambricon` 深核**：云端产品线 **64.77 亿元**可引；研究库宽口径「云端产品线」**A** / snapshot 窄「AI芯片」**B**（含整机未拆纯芯片）；挂 C① + C④ `cambricon_cloud_ai_accelerator`；**不挂** C③（NVDA 仍广度 E / 生态边界，禁假 pair）。  
4. **`sanhua` 诚实 E**：制冷空调/汽车零部件有数，但**无数据中心液冷专项** → grade **E** + `missing_reason`；C③/C④ 不挂。  
5. **`tfc`/`luxshare` C③**：同环节边界仍不清 → **继续 missing_reason**，不降门槛。  
6. **海光等**：本轮仍仅市值行（未强行灌深核）。

### 总览

| slug | 窄口径 grade | C③ pair | C④ event 传导 | 备注 |
|---|---|---|---|---|
| `fii` | B | 已挂 `fii_smci` | 已挂 | 维持 |
| `tfc` | B | **未挂**（missing_reason） | 已挂 | 禁假 `tfc_lite` |
| `eoptolink` | B | 已挂 `eoptolink_cohr` | 已挂 | 维持 |
| `innolight` | B | 维持 | 维持 | — |
| `luxshare` | B | **未挂**（missing_reason） | 已挂 | 维持 B1e |
| `shengyi` | **B**（新） | **未挂** | **已挂** `shengyi_ccl_pcb_ai_server` | CCL+PCB 宽 A / 窄 B |
| `cambricon` | **B**（新） | **未挂** | **已挂** `cambricon_cloud_ai_accelerator` | 云端产品线宽 A / 窄 B |
| `sanhua` | **E**（新） | 无 | 无 | 无液冷专项；`missing_reason` |
| `lite` | 窄 B / 宽 A | 无（不为凑 tfc） | — | 维持 |
| `envicool` | B | 维持 | 维持 | 非市值 top10 |

### 各家 C①–C④（本轮新增/关键）

| slug | C① 归属 | C② A–E | C③ pairs | C④ events |
|---|---|---|---|---|
| `shengyi` | membership **年报+成分** medium | 窄 B；宽覆铜板+PCB A | **缺** | **有** |
| `cambricon` | membership **年报+成分** medium | 窄 B；宽云端产品线 A | **缺** | **有** |
| `sanhua` | membership **低置信**（在板≠液冷专项） | **E** + missing_reason | 无 | 无 |
| `tfc`/`luxshare` | 维持 B1e | 窄 B | **仍缺** | 维持 |

### 仍未齐（不喊 P2 完成）

- `tfc`/`luxshare`/`shengyi`/`cambricon` C③ 仍缺合格同环节海外对标（禁假 pair）。
- 窄口径均无 AI 专项（或纯芯片）可拆金额 → 禁假 A。
- `sanhua` 诚实 E；海光及其他噪声名仍仅市值行。
- 权重双榜仍空（`weight_api_unavailable`）。
- `validate.py` / `validate_frontend.py` 本轮 **绿**。

### 挂载表（市值 deep_linked 并集，B1f）

| 概念 | deep_linked slugs（示例） |
|---|---|
| `concept.ai` | `fii`, `cambricon` |
| `concept.ai_chip` | `fii`, `innolight`, `cambricon`, `eoptolink`, `luxshare`, `shengyi` |
| `concept.ai_server` | `fii`, `innolight`, `cambricon`, `eoptolink`, `luxshare`, `tfc` |
| `concept.ai_optics` | `fii`, `innolight`, `eoptolink`, `luxshare`, `shengyi`, `tfc` |
| `concept.ai_cooling` | `fii`, `innolight`, `luxshare`, `sanhua`(E) |
| `concept.ai_power` | `fii`, `innolight`, `cambricon`, `eoptolink`, `luxshare`, `tfc` |
| `concept.ai_software` | （shallow，0） |

席位粗算：deep_linked **30** / 仅市值行 **40**（7×10）；去重映射 slug 增至 **8**（+`shengyi`/`cambricon`/`sanhua`；`sanhua` 为 E）。

---

## B1e 执行结果（2026-10-21 Asia/Hong_Kong）

> 版本：`meta.research_version=2026-10-21.p2.deep.b1e`  
> 约束遵守：禁假 A；无专项收入不评窄口径 A；**无假 pair**；无无 fact 的财务传导；金额只来自披露；不 push；不改前端视觉；**不开 Pro 全量**。

### 本轮动作

1. **补齐 B1d 未入 public 的 `lite` 深核**：Lumentum FY2025 业绩+10-K 源写入 snapshot；窄口径 **B**；**仍不挂** `tfc_lite`（跨模块层）。  
2. **B2 高频未映射席优先有年报**：归档立讯精密 FY2025 年报 PDF；新 slug `luxshare` 深核；宽口径「通讯及数据中心」研究库 **A** / 窄 AI 相关 snapshot **B**；挂事件 `luxshare_datacenter_interconnect`；**不挂**中外 pair。  
3. **C①**：`fii`/`tfc`/`eoptolink`/`lite`/`luxshare` membership 升年报/披露源（confidence medium）。  
4. **诚实纠偏**：`fii`/`tfc`/`eoptolink` uncertainties 与已挂 pair/event 对齐；`tfc` C③ 继续 `missing_reason`。

### 总览

| slug | 窄口径 grade | C③ pair | C④ event 传导 | 备注 |
|---|---|---|---|---|
| `fii` | **B** | **已挂** `fii_smci` | **已挂** `fii_ai_server_cloud` | C① 升年报源 |
| `tfc` | **B** | **未挂**（`missing_reason`） | **已挂** `tfc_optical_interconnect_components` | lite 已入 public 仍跨模块 → 诚实不挂 |
| `eoptolink` | **B** | **已挂** `eoptolink_cohr` | **已挂** `eoptolink_high_speed_optics` | C① 升年报源 |
| `innolight` | B | 维持 `innolight_cohr` | 维持 `optics_high_speed_shipments` | — |
| `luxshare` | **B**（新） | **未挂**（`missing_reason`） | **已挂** `luxshare_datacenter_interconnect` | 通讯及数据中心 245.68 亿元可引；禁假 A；消费电子仍主体 |
| `lite`（海外对标池） | 窄 **B** / 宽 Cloud&Networking **A** | **无**（不为凑 tfc 假挂） | — | **已入 public**；非市值 top10 映射叙事主位 |
| `envicool` | B | 维持 `envicool_vrt` | 维持 `blackwell_ultra` | — |

### 各家 C①–C④

| slug | C① 归属 | C② A–E | C③ pairs | C④ events |
|---|---|---|---|---|
| `fii` | membership **年报+成分** | 窄 B；宽云计算 A | **有** `fii_smci` | **有** |
| `tfc` | membership **年报+成分** | 窄 B；宽光互连 A | **缺**（missing_reason） | **有** |
| `eoptolink` | membership **年报+成分** | 窄 B；宽光互联 A | **有** `eoptolink_cohr` | **有** |
| `innolight` | 维持 | B | 有 | 有 |
| `luxshare` | membership **年报+多板成分** | 窄 B；宽通讯及数据中心 A | **缺**（本轮不编造） | **有** |
| `lite` | membership **业绩+10-K** | 窄 B；宽 A | 无（对 tfc 禁挂） | — |

### 仍未齐（不喊 P2 完成）

- `tfc` C③ 仍缺同环节海外器件层深核对标（不得降门槛假挂）。
- `luxshare` C③ 本轮未挂（缺已核验同环节海外对标）。
- 窄口径均无 AI 专项收入 → 禁假 A。
- 市值 top10 其余未映射席（寒武纪/海光/生益/三花等）保持仅市值行或待 B2 续；**无证据不进假 A**。
- 权重双榜仍空（`weight_api_unavailable`）。
- `validate.py` / `validate_frontend.py` 本轮 **绿**。

---

## B1d 执行结果（2026-10-21 Asia/Hong_Kong）

> 版本：`meta.research_version=2026-10-21.p2.deep.b1d`  
> 约束遵守：禁假 A；无专项收入不评窄口径 A；**无假 pair**；无无 fact 的财务传导；金额只来自披露；不 push；不改前端视觉；**不盖入 Pro 残稿**。

### 本轮动作

1. **优先 tfc 同环节海外器件层**：归档 Lumentum FY2025 业绩稿（IR）+ 10-K（SEC 直链本环境 403 → 公开镜像归档并交叉核对标题）；升 `lite` 深核。  
2. **有把握才挂 pair → 本轮仍不挂**：10-K 明示 Cloud & Networking = chips / components / modules / subsystems；业绩稿并列「组件（EML 等）+ 800G modules」。相对天孚「光互连元器件/光引擎（模块上游）」同环节边界仍不清 → **保持 missing_reason**，禁假 `tfc_lite`。  
3. **双榜已映射席扫描**（权重板全空 `weight_api_unavailable`，实质=市值 deep_linked 并集）：`fii`/`innolight`/`eoptolink` 的 C③/C④ 已齐；**仅 `tfc` 缺 C③**（C④ 已有 `tfc_optical_interconnect_components`）。无证据不新挂、不假 A。

### 总览

| slug | 窄口径 grade | C③ pair | C④ event 传导 | 备注 |
|---|---|---|---|---|
| `fii` | **B** | **已挂** `fii_smci` | **已挂** `fii_ai_server_cloud` | 维持 B1c |
| `tfc` | **B** | **未挂**（`missing_reason` 已用 Lumentum 主源刷新） | **已挂** `tfc_optical_interconnect_components` | Lumentum 已深核仍跨模块层 → 诚实不挂 |
| `eoptolink` | **B** | **已挂** `eoptolink_cohr` | **已挂** `eoptolink_high_speed_optics` | 维持 |
| `innolight` | B | 维持 `innolight_cohr` | 维持 `optics_high_speed_shipments` | — |
| `envicool` | B | 维持 `envicool_vrt` | 维持 `blackwell_ultra` | — |
| `lite`（海外对标池） | 窄 **B** / 宽 Cloud&Networking **A** | **无**（不为凑 tfc 假挂） | — | 新深核；非市值 top10 映射席 |

### 各家 C①–C④

| slug | C① 归属 | C② A–E | C③ pairs | C④ events |
|---|---|---|---|---|
| `fii` | 概念板源已齐 | 窄 B；宽云计算 A | **有** `fii_smci` | **有** |
| `tfc` | 同上 | 窄 B；宽光互连 A | **缺**（missing_reason 已写） | **有** |
| `eoptolink` | 同上 | 窄 B；宽光互联 A | **有** `eoptolink_cohr` | **有** |
| `innolight` | 已补概念源 | B | 有 | 有 |
| `envicool` | P1 强；非市值 top10 | B | 有 | 有 |

### 仍未齐（不喊 P2 完成）

- `tfc` C③ 仍缺**同环节**海外器件层深核对标（Lumentum/Coherent 均跨模块或更宽，不得降门槛假挂）。
- 窄口径均无 AI 专项收入 → 禁假 A。
- 市值 top10 仅市值行 52 席未深核（B2）；权重双榜仍空。
- `validate.py` / `validate_frontend.py` 本轮应绿。

---

## B1c 执行结果（2026-10-21 Asia/Hong_Kong）归档

> 版本：`meta.research_version=2026-10-21.p2.deep.b1c`  
> 约束遵守：禁假 A；无专项收入不评窄口径 A；无假 pair；无无 fact 的财务传导；金额只来自披露；不 push；不改前端视觉。

### 总览

| slug | 窄口径 grade | C③ pair | C④ event 传导 | 备注 |
|---|---|---|---|---|
| `fii` | **B** | **已挂** `fii_smci` | **已挂** `fii_ai_server_cloud` | 云计算分部 6,026.79 亿元可引；AI 服务器仅同比增速，无绝对专项收入；EMS/ODM vs 品牌整机边界已写清；`amount_compare_allowed=false` |
| `tfc` | **B** | **未挂**（`missing_reason`） | **已挂** `tfc_optical_interconnect_components` | 光互连元器件 vs Coherent 光模块/数通收发 **同环节边界不清**；Lumentum 仅广度 profile → 诚实不编造 pair |
| `eoptolink` | **B** | **已挂** `eoptolink_cohr` | **已挂** `eoptolink_high_speed_optics` | 结构复用 `innolight_cohr`；光互联 247.71 亿元与 800G/1.6T 产品线有年报 PDF 源；禁裸比金额 |
| `innolight` | B | 维持 `innolight_cohr` | 维持 `optics_high_speed_shipments` | — |
| `envicool` | B | 维持 `envicool_vrt` | 维持 `blackwell_ultra` | — |

### 各家 C①–C④

| slug | C① 归属 | C② A–E | C③ pairs | C④ events |
|---|---|---|---|---|
| `fii` | 概念板源已齐 | 窄 B；宽云计算 A | **有** `fii_smci` | **有** |
| `tfc` | 同上 | 窄 B；宽光互连 A | **缺**（missing_reason 已写） | **有** |
| `eoptolink` | 同上 | 窄 B；宽光互联 A | **有** `eoptolink_cohr` | **有** |
| `innolight` | 已补概念源 | B | 有 | 有 |
| `envicool` | P1 强；非市值 top10 | B | 有 | 有 |

### 仍未齐（不喊 P2 完成）

- `tfc` C③ 仍缺可用同环节海外深核对标（需器件层对标或补 Lumentum 等深核后再议）。
- 窄口径均无 AI 专项收入 → 禁假 A。
- 市值 top10 仅市值行 52 席未深核（B2）。
- `validate.py` / `validate_frontend.py` 本轮 **绿**。

---

## B1b 执行结果（2026-10-21 Asia/Hong_Kong）归档

> 已被 B1c 覆盖；C③/C④ 当时仍缺。完整 B1b 记录见下。


> 版本：`meta.research_version=2026-10-21.p2.deep.b1b`  
> 约束遵守：禁假 A；无专项收入不评窄口径 A；无假 pair；无无 fact 的财务传导；不 push；不改前端视觉。

### 拉取尝试（诚实记录）

| 通道 | 结果 |
|---|---|
| 巨潮 `hisAnnouncement/query` | HTTP 200 但 **0 条**（601138/300394/300502；对照 000977 亦空）→ 本环境 query 接口不可用 |
| 公开索引 + `static.cninfo.com.cn` 直链 | **成功**：三家 FY2025 年报 PDF 已下至 `artifacts/public/`，经 `scripts/fetch_public.py` |
| iFinD MCP `search_notice` | **失败**：`initialize` → URLError；`config/p2_deep_b1b_jobs.json` 未产出新摘录 |
| 扶摇利润表 | **成功**：经 `scripts/collect.py` + `config/p2_deep_b1b_fuyao.json` |

### 总览

| slug | 新 grade（snapshot 窄口径） | 研究库双轨 | 新增 pair | 新增 event 传导 | 备注 |
|---|---|---|---|---|---|
| `fii` | **B**（由 E） | 云计算 **A** / AI服务器 **B** | 否 | 否 | 年报 PDF p14–18；云计算分部 6,026.79 亿元；AI 服务器仅同比增速，无绝对专项收入 |
| `tfc` | **B**（由 E） | 光互连元器件 **A** / AI相关光器件 **B** | 否 | 否 | 年报 PDF；光互连 50.82 亿元；有源/无源分产品已披露 |
| `eoptolink` | **B**（维持；证据升级 PDF） | 光互联产品 **A** / AI专用高速光模块 **B** | 否 | 否 | 由公告摘录升级为本地年报 PDF 全文；光互联 247.71 亿元 |
| `innolight` | B（维持） | 维持 | 否 | 否 | — |
| `envicool` | B（维持） | 维持 | 否 | 否 | — |

### 各家 C①–C④ 仍缺什么

| slug | C① 归属 | C② A–E | C③ pairs | C④ events |
|---|---|---|---|---|
| `fii` | 概念板源已齐；membership 可升（年报业务证据） | 窄 B；宽云计算 A（非 AI 概念名） | **缺** | **缺** |
| `tfc` | 同上 | 窄 B；宽光互连 A | **缺** | **缺** |
| `eoptolink` | 同上；PDF 全文已齐 | 窄 B；宽光互联 A | **缺** | **缺** |
| `innolight` | 已补概念源 | B 维持 | 有 | 有 |
| `envicool` | P1 强；非市值 top10 | B 维持 | 有 | 有 |

### 仍未齐（不喊 P2 完成）

- 映射并集：fii/tfc/eoptolink 的 **C③–C④** 仍缺；窄口径均无 AI 专项收入。
- 市值 top10 仅市值行 52 席未深核（B2）。
- `validate.py` / `validate_frontend.py` 本轮应绿。

---

## B1 执行结果（2026-10-21 Asia/Hong_Kong）归档

> 已被 B1b 覆盖；保留对照。版本曾为 `p2.deep.b1`。eoptolink 当时仅公告摘录→B；fii/tfc 为 E。

## 0. 结论（未齐，不喊 P2 完成）

| 项 | 现状 |
|---|---|
| 市值 top10 席位 | 7 个可分析概念 × 10 = **70**；其中 **deep_linked 23 席 / 仅市值行 47 席**（B1e 后；含 `luxshare`） |
| 已映射深核 slug（去重） | **5**：`fii`、`innolight`、`eoptolink`、`tfc`、`luxshare` |
| 四硬指标铺满 | **未齐**（见 §3）；仅 `innolight` 在 A–E / pairs / events 上接近可验，其余映射公司多为 E + 无可比 + 无传导 |
| P1 可迁移但未进市值 top10 | `envicool` / `kehua` / `inspur` 等有深核证据，**当前概念市值榜未 deep_link**（市值未进前 10，非漏映射） |

**喊完成条件（缺一不可）**：各可分析方向（shallow 除外）对 deep_linked 并集，C①–C④ 主位可点开证据；新进 top10 未深核者诚实 E，不进假 A。

---

## 1. 市值 top10：deep_linked vs 仅市值行

数据源：`frontend/public/data/snapshot.json` → `concepts[].rank_by_mkt_cap.items`  
规则：`deep_linked=true` 且 `company_id` 为 slug（与 `companies[].id` 对齐）；否则 `company_id=null`，仅 `thscode` 展示。

### 1.1 总表（可分析概念）

| 概念 | 市值 top10 | deep_linked（slug） | 仅市值行（thscode） | `company_ids` |
|---|---:|---|---|---|
| `concept.ai` | 10 | 1：`fii` | 9 | `fii` |
| `concept.ai_chip` | 10 | 3：`fii`,`innolight`,`eoptolink` | 7 | 同上三 |
| `concept.ai_server` | 10 | 4：`fii`,`innolight`,`eoptolink`,`tfc` | 6 | 同上四 |
| `concept.ai_optics` | 10 | 4：`fii`,`innolight`,`eoptolink`,`tfc` | 6 | 同上四 |
| `concept.ai_cooling` | 10 | 2：`fii`,`innolight` | 8 | 同上二 |
| `concept.ai_power` | 10 | 4：`fii`,`innolight`,`eoptolink`,`tfc` | 6 | 同上四 |
| `concept.ai_software` | 10 | **0**（shallow） | 10 | `[]` |
| **合计席位** | **70** | **23** | **47** | 去重 slug **5**（B1e） |

`concept.other_demo_disabled`：`analysis_enabled=false`，双榜 null，不计入。

### 1.2 分概念明细

#### `concept.ai`（人工智能）

| rank | 名称 | thscode | deep? | slug |
|---:|---|---|---|---|
| 1 | 工业富联 | 601138.SH | Y | `fii` |
| 2–10 | 寒武纪 / 海光信息 / 海康威视 / 东方财富 / 澜起科技 / 京东方Ａ / 顺丰控股 / 招商轮船 / 中国联通 | … | N | — |

#### `concept.ai_chip`

| rank | 名称 | thscode | deep? | slug |
|---:|---|---|---|---|
| 1 | 工业富联 | 601138.SH | Y | `fii` |
| 2 | 中际旭创 | 300308.SZ | Y | `innolight` |
| 7 | 新易盛 | 300502.SZ | Y | `eoptolink` |
| 其余 | 美的集团 / 寒武纪 / 海光信息 / 北方华创 / 立讯精密 / 海康威视 / 生益科技 | … | N | — |

#### `concept.ai_server` / `concept.ai_power`（共用 885887.TI 成分代理）

| rank | 名称 | thscode | deep? | slug |
|---:|---|---|---|---|
| 1 | 工业富联 | 601138.SH | Y | `fii` |
| 2 | 中际旭创 | 300308.SZ | Y | `innolight` |
| 6 | 新易盛 | 300502.SZ | Y | `eoptolink` |
| 9 | 天孚通信 | 300394.SZ | Y | `tfc` |
| 其余 | 美的 / 寒武纪 / 中国电信 / 立讯 / 比亚迪 / 沪电 | … | N | — |

#### `concept.ai_optics`（CPO 板代理）

| rank | 名称 | thscode | deep? | slug |
|---:|---|---|---|---|
| 1 | 工业富联 | 601138.SH | Y | `fii` |
| 2 | 中际旭创 | 300308.SZ | Y | `innolight` |
| 3 | 新易盛 | 300502.SZ | Y | `eoptolink` |
| 6 | 天孚通信 | 300394.SZ | Y | `tfc` |
| 其余 | 立讯 / 生益 / 三环 / 京东方 / 鹏鼎 / 东山 | … | N | — |

#### `concept.ai_cooling`

| rank | 名称 | thscode | deep? | slug |
|---:|---|---|---|---|
| 1 | 工业富联 | 601138.SH | Y | `fii` |
| 2 | 中际旭创 | 300308.SZ | Y | `innolight` |
| 其余 | 美的 / 立讯 / 格力 / 蓝思 / 亨通 / 海尔 / 三花 / 汇川 | … | N | — |

> 注意：P1 液冷焦点 `envicool`（002837.SZ）**不在**本板市值 top10 → 不 deep_link；证据仍在 `companies`/`pairs`/`events`，叙事可引用，但 **不计入「top10 深核铺满」席位**，除非后续权重榜或业务筛选榜替换排序源。

#### `concept.ai_software`（shallow=true）

全部 10 行为仅市值行；本轮不要求深核铺满，验收按浅覆盖。

### 1.3 未映射 top10 高频（跨板出现次数）

| thscode | 名称 | 出现板数 | 建议 |
|---|---|---:|---|
| 002475.SZ | 立讯精密 | 5 | 新进候选 → **E**，不进假 A |
| 688256.SH | 寒武纪 | 4 | 同上 |
| 000333.SZ | 美的集团 | 4 | 同上（宽口径噪声高） |
| 002415.SZ | 海康威视 | 3 | 同上 |
| 000725.SZ | 京东方Ａ | 3 | 同上 |
| 601728.SH | 中国电信 | 3 | 同上 |
| 其余 23 个 thscode | （见 raw 榜） | 1–2 | 占位 E / 仅市值行 |

---

## 2. 已映射 slug × 四硬指标对照

对照 `FRONTEND_FIELDS_P2.md` C 区 + `CONCEPT_GRADES.md`。  
公司池：`data/company_research.json` + `snapshot.companies` + `pairs` + `events` + `industry_graph` membership。

| slug | 市值板出现 | C① 归属 source | C② grade / claims | C③ pairs | C④ events 传导 | 总评 |
|---|---|---|---|---|---|---|
| `innolight` | chip/server/optics/cooling/power | membership 边有 `source_ids`（P1 光模块口径）；**concepts[].source_ids 仍空** | snap **B**，claims×2；CR 宽 A / 窄 B | 有 `innolight_cohr`（金额闸关、边界文案齐） | 在 `optics_high_speed_shipments` | **最接近可验**；缺概念板归属源 |
| `fii` | ai+五子概念（除 software） | membership 有源但 **confidence=low**（广度 profile） | snap **E**，claims=0（CR 仅占位 claim） | **无** | **无** | 市值第一但深核空 → **优先迁/补** |
| `eoptolink` | chip/server/optics/power | 同上 low | **E** / 0 claims | **无** | **无** | 光模块第二梯队 → **优先补** |
| `tfc` | server/optics/power | 同上 low | **E** / 0 claims | **无** | **无** | 光器件 → **优先补** |

### 2.1 有 P1 深核、但未进当前市值 top10（迁移池）

| slug | P1 深度 | grade | pairs | events | 与当前概念板 |
|---|---|---|---|---|---|
| `envicool` | deep | B | `envicool_vrt`（aligned H12026，ratio 可、金额否） | `blackwell_ultra` 主链 | 液冷叙事核心；**市值未进 cooling top10** |
| `kehua` | deep | B | `kehua_etn` | 无专链 | 供配电；未进 power top10 |
| `inspur` | deep | C（窄 AI 服务器） | `inspur_smci` | 无专链 | 服务器；未进 server top10 |

海外对标 `smci`/`cohr`/`etn`/`vrt`：服务 pairs，不要求进 A 股市值榜。

### 2.2 图与概念板错位（C① 结构性缺口）

- `concepts[]`：有 `parent_id`/`level`/`ths_code`，但 **全部 `source_ids` 为空** → 不得声称「概念板归属已举证」。  
- `industry_graph`：仍为 P1 `theme.ai_dc` / `branch.*` / `segment.*` 树，**不是** `concept.*` taxonomy；membership 边对公司存在，但与概念板 id 未对齐。  
- `impact_annotations`：仅 cooling/optics 叙事节点有源；映射公司中仅 `innolight`（及池外 `envicool`）有公司级 impact。

---

## 3. 缺口清单（概念 × 公司 × 优先级）

优先级：P0 = 挡住「P2 完成」喊单；P1 = 下一批必做；P2 = 浅覆盖/噪声可延后。

### 3.1 按硬指标

| 硬指标 | 缺口 | 优先级 |
|---|---|---|
| **C① 归属+层级+证据** | 7 概念缺 `source_ids`；graph 未切到 concept_board；`fii`/`eoptolink`/`tfc` membership 仅低置信 profile | P0 |
| **C② A–E** | `fii`/`eoptolink`/`tfc` 为 E 且无实质 claims；窄口径若补数须走闸门，**禁假 A** | P0 |
| **C③ 可比边界** | 映射四家中仅 `innolight` 有 pair；`fii`/`eoptolink`/`tfc` 无中外可比文案 | P0 |
| **C④ 传导链** | 仅 optics→`innolight`、cooling→`envicool`（池外）；无 server/chip/power 映射公司传导 | P0 |
| 市值未映射 52 席 | 保持仅市值行；若拉入深核默认 **E** | P1（选高频）/ P2（噪声名） |
| software shallow | 不深核 | P2（维持浅） |

### 3.2 按「概念 × 公司」（deep_linked 席位）

| 概念 | 公司 | C① | C② | C③ | C④ | 动作优先级 |
|---|---|---|---|---|---|---|
| ai / chip / server / optics / cooling / power | `fii` | 弱 | E | 缺 | 缺 | **P0 迁/补** |
| chip / server / optics / cooling / power | `innolight` | 中（缺概念源） | B 可用 | 有 | 有 | **P1 补概念 source_ids** |
| chip / server / optics / power | `eoptolink` | 弱 | E | 缺 | 缺 | **P0 补** |
| server / optics / power | `tfc` | 弱 | E | 缺 | 缺 | **P0 补** |
| cooling（叙事） | `envicool` | 强（P1） | B | 有 | 有 | **P1 保留；榜外注明** |
| server（叙事） | `inspur` | 强 | C | 有 | 缺 | P1 可选迁 |
| power（叙事） | `kehua` | 强 | B | 有 | 缺 | P1 可选迁 |
| software top10 任一家 | — | — | — | — | — | 浅覆盖，标 E 即可 |

### 3.3 「缺」的判定口径（验收用）

1. **缺归属 source_ids**：`concepts[].source_ids` 空，或 membership 边无 `source_ids`，或仅有「广度 profile」且未点名该概念板。  
2. **缺 A–E**：`assessment.grade` 为 E 且 `claims` 无业务/边界实质条目；或 grade=A 但无 scoped revenue（校验应拒绝）。  
3. **缺可比边界**：该公司不在任何 `pairs[].company_ids`，或 pair 缺 `not_comparable_on` / 闸门字段。  
4. **缺传导链**：`events[].steps` 未覆盖该公司/环节，或无 `fact` 步却写成已证实财务影响。

---

## 4. 建议下一批（可复现）

配置清单：`config/p2_deep_coverage.json`（ticker→slug、批次、验收开关）。  
编排原则（`ALGO_P2_PLAN.md` §0.1）：**供应商调用进 adapter/config**；本文件只定覆盖与验收，**不写死扶摇 URL/密钥/散落脚本路径**。

### 批次 B1 — 迁移/加深「已有 P1 证据」与榜内空核（先做）

| 序 | slug | ticker | 动作 | 期望四指标 |
|---:|---|---|---|---|
| 1 | `innolight` | 300308.SZ | 保留深核；补概念板 `source_ids`；claims 对齐 `concept.ai_optics` 窄口径 | C①↑；C②–C④ 维持 |
| 2 | `fii` | 601138.SH | 从 breadth→深核：拉年报/公告业务证据；**无专项收入则 B/C/E，禁假 A**；补 membership 高置信源 | C①+C②；C③/C④ 有证据再挂 |
| 3 | `eoptolink` | 300502.SZ | 同上（光模块）；可对标路径参考 `innolight_cohr` 结构，**数字必须新核验** | C①+C②；条件具备再 pair |
| 4 | `tfc` | 300394.SZ | 同上（光器件）；窄口径默认 B/C/E | C①+C② |
| 5 | `envicool` | 002837.SZ | **迁移池**：不因未进 top10 丢弃；导出时保留 pairs/events；cooling 分析焦点可挂 | 维持 C②–C④；榜位诚实标注「非市值 top10」 |

可选同批：`inspur`、`kehua`（供 server/power 叙事补强，仍非市值 top10）。

### 批次 B2 — 新进 top10 未深核（标 E，不进假 A）

按跨板频次取前若干（默认见 config）：

1. `002475.SZ` 立讯精密  
2. `688256.SH` 寒武纪  
3. `688041.SH` 海光信息  
4. `600183.SH` 生益科技  
5. （冷却相关若业务筛选）`002050.SZ` 三花智控  

规则：

- registry / snapshot 若纳入：`research_status=candidate`，`grade=E`，`claims` 可空或仅「未核验」占位。  
- **禁止**用集团收入或订单新闻写成 A。  
- 美的 / 京东方 / 顺丰等宽噪声名：**保持仅市值行**，除非业务证据证明与该概念窄口径相关。

### 批次 B3 — 横切（概念级，非单公司）

1. 为每个 `analysis_enabled` 概念写入 `source_ids`（扶摇/iFinD 成分或板块目录 raw → `sources`）。  
2. graph：新增或映射 `concept.*` 节点/边，或明确 export 层用 `concepts[]` 承担 C① 层级、graph 仅作 B 星图兼容（二选一写进下一版 export 说明）。  
3. 权重榜仍空则保持 `missing_reason=weight_api_unavailable`，不假填。  
4. feeds：子概念多为 0 条 → 另轨补，不阻塞四硬指标，但 A1 体验需知情。

### 复现命令（示意，路径只指向仓库内脚本/配置）

```text
# 1) 读覆盖配置
config/p2_deep_coverage.json

# 2) 深核/迁移走既有 round2 / build_research DAG（公司名单读本配置 batch_b1）
#    供应商：adapter + p2_collection_jobs / 扶摇 pull 配置，禁止业务脚本写死 URL

# 3) 校验
python scripts/validate.py
# grade==A 必须有 scoped revenue（非 consolidated_total）

# 4) 导出 joinable（映射 ticker→slug）
python scripts/export_p2_joinable.py
# 验收：research_version 递增备注；四硬指标公司并集对照本文件 §2 表转绿
```

---

## 5. 通用编排约束（写进验收）

| 约束 | 要求 |
|---|---|
| 主题可替换 | 换概念种子 = 改 `config/p2_concept_seed.json` + 覆盖配置；不改前端常量主题名 |
| 供应商进 adapter | iFinD MCP / 扶摇 REST 只经 collection jobs + pull adapter；本盘点与 `p2_deep_coverage.json` **不**含密钥与散落 URL |
| 禁假 A | 窄口径无收入 → B/C/E + `missing_reason`；见 `CONCEPT_GRADES.md` |
| 禁编造市值/收入 | top10 `value` 以已拉 raw 为准；缺则 null |
| 不改前端视觉 | 只补数据/配置/文档；C 区主位字段按 `FRONTEND_FIELDS_P2.md` |
| 未齐不喊完成 | 本文件 §0 四指标转绿前，`meta.p2_notes` 保持「四硬指标深核未齐」类诚实表述 |

---

## 6. 验收清单（打勾用）

- [ ] 各非 shallow 可分析概念：deep_linked 并集在 C① 均有可点 `source_ids`（概念或 membership）  
- [ ] 同上并集：C② 均有诚实 grade + rationale/claims（E 须可解释为未核验，非「无业务」）  
- [ ] 每方向至少 1 组可用 pair **或** 明示「本轮无中外对标」挂在分析输出（映射公司尽量有）  
- [ ] 每方向至少 1 条 event 传导，steps 含 fact，且 inference/scenario 分离  
- [ ] 新进 top10 未深核者无 A  
- [ ] `validate.py` + frontend validate 绿；不 push 冒充完成  

---

## 7. 数据指纹（便于对照）

| 文件 | 用途 |
|---|---|
| `frontend/public/data/snapshot.json` | 联调真源；`p2.joinable.2` |
| `data/p2/concepts.json` / `PULL_NOTES.md` | 成分与市值榜 |
| `data/company_research.json` | 深核/广度 assessments |
| `data/industry_graph.json` | membership 边 |
| `data/impact_annotations.json` | 叙事 impact |
| `config/p2_deep_coverage.json` | 下一批可复现清单 |
| `config/p2_concept_seed.json` | 主题种子（可替换） |

---

*本盘点不包含任何编造的收入/市值数字；表中市值名次来自已落库扶摇 auction snapshot 榜，数值以 snapshot items 为准。*
