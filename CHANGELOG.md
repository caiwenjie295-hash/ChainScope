# 0.3.22 — 2026-10-22

- **前端** `chainscope-frontend@0.3.22` 调整为“选择 AI → 开始分析 → 查看产业结构 → 选择公司查看基础信息 → AI智能总结”的研究流程；两处本地演示均保留约 3 秒步骤进度，复用已发布研究结果，不新增 Agent 或金融 API 调用。
- 新增常见概念演示入口、独立 AI 概念市值榜与 A–E 评级说明；改善公司财务指标报告期、来源说明、窄屏定位、键盘操作和用户可见文案。不改研究快照。
- 保留“流程与证据”及“Deepseek Flash API调用成本核算”说明页；前端生产构建通过。
- 核对并区分当前研究覆盖与早期归档数字：研究流程页动态计算当前公司、来源、图谱、事实引用、财务数值、对照和事件；1516 项校验只在验证记录数据哈希匹配时显示。29 个阶段、686 项归档校验及成本页的115次请求明确标注为早期8家公司运行记录，不含后续补充研究及前端开发。

## 0.3.21 — 2026-10-22

- **前端** `chainscope-frontend@0.3.21` Finance 盲测 0.3.20 抽测不过项一次到位（禁止中间升版）：用户可见文案去机读键（加强 `humanize*`，禁裸 `thscode`/`missing_reason`/`response.data`/`pair` 等）；去对内旁白（ReleaseMeta 不再展示 data_hash/commit；「暂未开放分析」；去「块内状态/主题根/蒙层」技术腔）；分析中/追问结束对客一两句；`npm run build` 绿。**不改** `snapshot.json`。

## 0.3.19 — 2026-10-22

- **前端** `chainscope-frontend@0.3.19` 盲测 0.3.18 残留摩擦：散户文案清洗（归属块禁裸 `parent`/`thscode`/`pair`/`missing_reason` 等；复用并补全 `humanize*`）；换公司自动收起「同主题其他」；市值榜 `deep_linked===false` / 无深核行默认折入「暂无深核」；概念权重榜逻辑未改；`npm run build` 绿。不改 snapshot / 算法文档。

# 版本记录

## 0.3.12 — 2026-10-22

- **前端** `chainscope-frontend@0.3.12` 软档盲测：环节默认「本环节」；选司直开 C 四硬；传导按公司过滤；区徽章「概念/结构/公司」；A–E「证据阶梯，非信用评级」；空态优先 `empty_reason_zh` / `concept_feeds_meta`（禁裸 `weight_api_unavailable`）；`npm run build` 绿。
- 盲测 **P1 契约**（**非新深核**）：`research_version=2026-10-22.p2.deep.b1h.p1`（群报可用）。
- **feeds**：`industry_concept_only` 过滤；禁时政灌屏；过滤后空数组 + `concept_feeds_meta[].empty_reason_zh`（如「本轮暂无与该概念直接相关的产业资讯」）。
- **权重榜空态**：`rank_by_concept_weight` 保留机读 `missing_reason=weight_api_unavailable`，新增人话 **`empty_reason_zh=权重数据暂不可用`**（禁 UI 裸露机读码）。
- 契约：`docs/FRONTEND_FIELDS_P2.md` 先增补再灌数；`scripts/p2_empty_copy.py` + `p2_pull_fuyao` / `export_p2_joinable`。
- public 覆盖 `frontend/public/data/snapshot.json`；`validate.py` / `validate_frontend.py` 绿；不 push；不改前端视觉（UIUX 读新键）。

## 0.3.11 — 2026-10-21

- P2 深核 B1h（可演示四硬收口）：**本批无新增深核**；盘点已 deep 9 slug + `envicool`/`lite` 的 C①–C④ 可点开/空态/E；不刷假 pair；不喊 P2 完成；`research_version=2026-10-21.p2.deep.b1h`。
- 更新 `docs/P2_DEEP_COVERAGE.md`「可演示清单」；剩余 38 席仅市值行保持噪声/未映射。
- `validate.py` / `validate_frontend.py` 预期绿；不 push；不改前端视觉；不开 Pro。

## 0.3.10 — 2026-10-21

- P2 深核 B1g：归档海光信息 FY2025 巨潮年报；新进 `hygon` 深核（宽口径「高端处理器」研究库 **A** / 窄口径 AI芯片 snapshot **B**）；事件 `hygon_high_end_processor_ai`；**不挂** C③（CPU/DCU 未拆，禁假 pair）；`tfc`/`luxshare`/`shengyi`/`cambricon` C③ 仍诚实 missing；`research_version=2026-10-21.p2.deep.b1g`。
- 噪声名（美的/海康等）仍仅市值行；禁假 A；不开 Pro；不 push；不改前端视觉。
- `validate.py` / `validate_frontend.py` 预期绿。

## 0.3.9 — 2026-10-21

- P2 深核 B1f：归档生益科技/寒武纪/三花智控 FY2025 巨潮年报；新进 `shengyi`、`cambricon` 深核（宽口径研究库 A / 窄口径 snapshot B）；`sanhua` 诚实 **E**（无数据中心液冷专项，`missing_reason`）；事件 `shengyi_ccl_pcb_ai_server`、`cambricon_cloud_ai_accelerator`；`tfc`/`luxshare` C③ 仍诚实 missing（禁假 pair）；`research_version=2026-10-21.p2.deep.b1f`。
- 海光等其余未映射 top10 仍仅市值行；禁假 A；不开 Pro；不 push；不改前端视觉。
- `validate.py` / `validate_frontend.py` 预期绿。

## 0.3.8 — 2026-10-21

- P2 深核 B1e：`lite` 深核落入 public；新进 `luxshare`（002475）巨潮 FY2025 年报深核；映射席 C① membership 升年报源；`tfc` C③ 仍诚实 missing（禁假 pair）；窄口径仍 B、禁假 A；`research_version=2026-10-21.p2.deep.b1e`。
- 新增事件 `luxshare_datacenter_interconnect`；不挂 luxshare 中外 pair。
- `validate.py` / `validate_frontend.py` 绿；不 push；不改前端视觉；不开 Pro。

## 0.3.7 — 2026-10-21

- P2 深核 B1d：归档 Lumentum FY2025 业绩+10-K，升 `lite` 深核；`tfc` C③ 仍诚实 missing（Cloud & Networking 跨模块层，禁假 pair）；双榜已映射仅 tfc 缺 C③；`research_version=2026-10-21.p2.deep.b1d`。
- 不盖入 Pro 残稿；validate 绿；不 push；不改前端视觉。

## 0.3.6 — 2026-10-21

- P2 深核 B1c：`fii_smci`、`eoptolink_cohr` 可比 pair；`tfc` 诚实 missing_reason；新增三条 event 传导；`research_version=2026-10-21.p2.deep.b1c`。

## 0.3.5 — 2026-10-21

- P2 深核 B1b：`fii`/`tfc`/`eoptolink` 巨潮 FY2025 年报 PDF 归档至 `artifacts/public/`；`research_version=2026-10-21.p2.deep.b1b`。
- 研究库双轨：宽口径分部收入可 A（云计算 / 光互连 / 光互联产品）；窄口径 AI 概念维持 B，禁假 A；snapshot 展示窄口径 B。
- 拉取诚实记录：巨潮 query API 本环境空结果；iFinD MCP initialize 失败；扶摇利润表经 `collect.py` 成功。
- `validate.py` / `validate_frontend.py` 绿；不 push。

## 0.3.4 — 2026-10-21

- 概念榜联调：`RankItem.company_id`（如 `co.601138_sh`）与深核 `companies[].id`（如 `fii`）不对齐时，按 `thscode`↔`ticker`（忽略大小写）再按去交易所后缀数字码解析。
- SegmentSheet：当前概念有非空 RankBoard 时按方向级 top10 展示，**不再用 segment_id 滤掉整榜**；同 segment 标注「本环节」。
- 无深核上榜项仍显示 name / value_display / rank；点击提示「本轮研究快照未覆盖该公司深核」，不假装进入 C 区；匹配到 companies 的仍可进 C。
- 权重空板继续展示 `missing_reason` 空态；`resolveConcepts` 优先 `snapshot.concepts`，有真数时不被 DEV mock 覆盖。

## 0.3.3 — 2026-10-21

- C 区四块硬指标主位布局（对照 `docs/FRONTEND_FIELDS_P2.md`）：①归属（branch/segment + industry_membership 证据）→ ②A–E 概念可信度 → ③中外可比闸门（aligned_period / amount_compare_allowed / ratio_compare_allowed + 可比/不可比文案）→ ④传导（优先 events[]，fact/inference/scenario 分标签）。
- 论文式 headline 保留为导语；条形对比收进可比块；uncertainties / 传导边界作块内诚实状态；业务构成与指标条带退入次要折叠。
- 缺证据不美化：无 source 不声称已归属；窄口径无专项收入明示禁假 A；闸门关闭不静默比金额。

## 0.3.2 — 2026-10-21

- RankBoard 对象形对齐 `FRONTEND_FIELDS_P2`：`RankBoard` / `RankItem`；`ConceptNode.rank_by_mkt_cap` / `rank_by_concept_weight` 为板对象（运行时数组仍窄兼容为 items）。
- SegmentSheet：读 `board.items` 按 rank；展示 `metric_label` / `as_of` / `unit` / `value|value_display`；空 items+`missing_reason` 空态「权重暂不可用」或「本榜暂不可用（reason）」；整板 null 回退 `company_ids` 原序；默认市值页签、前 10。
- DEV mock：市值板有序 items；权重板演示空 items + `weight_api_unavailable`（子概念可带有序权重板）。
- C 区四块硬指标主位：已在 0.3.3 落地。

## 0.3.1 — 2026-10-21

- 公司列表双榜页签：SegmentSheet 增加「市值」|「概念权重」切换，默认市值；按当前概念的 `rank_by_mkt_cap` / `rank_by_concept_weight` 排序展示（前 10 可展开），可显示 entry `metric` / `as_of`。
- 类型：`ConceptRankEntry`；`ConceptNode` 可选双榜字段；公司级 `rank` / `rank_metric` / `rank_as_of` 仍作缺榜兜底。
- 缺榜降级：页签始终可见；榜为 `[]` 时空态「本榜本轮未导出」；字段缺失时短提示并回退现有 `compareCompanies` 排序。
- DEV mock：可分析概念挂两套不同顺序假榜（metric null），生产路径不注入。

## 0.3.0 — 2026-10-21

- P2 A 区状态机：A0 概念分类 chip（来自 `concepts`，缺则 DEV mock / 生产图谱推导 / 空态）；A1 展示 `concept_feeds[id]`；A2「开始分析」仅当选中概念 `analysis_enabled===true`（缺省 false），禁用悬停文案固定 `demo对该板块暂无分析`。
- 动态概念：类型增补 `concepts` / `concept_feeds`（含 `company_ids`、`analysis_enabled`、feed `id`）；去掉 `BRANCH_LABELS` 四分支硬编码与产品叙事写死；overview/分支标签一律读 snapshot。
- B 星图灵动：确定性径向抖动、非均匀角距、二次贝塞尔连线；仍三层 theme→branch→segment；impact 红/绿/中性规则不变。
- 保留 P1 候选折叠与 SegmentSheet 行为。
- 公司列表：按可选 `rank` 升序；可展示 `rank_metric` / `rank_as_of`；缺 rank 时 focus/demo_priority/name 兜底；有 rank 时默认前 10 可展开。取消写死「8 家」。

## 0.2.4 — 2026-10-21

- P1 字段接入：`GraphNode.impact` / `impact_source_ids` / `impact_rationale`；星图 positive→红、negative→绿、unclear→中性；无 negative 时图例诚实写「本轮无替代/受挤占核验」。
- 候选折叠：默认隐藏 `demo_priority=candidate`（或 research_status candidate）；SegmentSheet「显示候选」开关（复用 `showCandidates`）；focus 公司优先排序。
- 双事件：A 区优先 `events[]`（含 `optics_high_speed_shipments`），否则回退 `event`；overview 标题走 snapshot 数据。
- pairs：尊重 `amount_compare_allowed` / `ratio_compare_allowed`，展示 `aligned_period`；Company / Snapshot meta 增加 `demo_priority`、`narrative_focus`。


## 0.2.3 — 2026-10-21

- A「主题补充」：日期与标题分行；日期 `nowrap`，标题用 `text-wrap: pretty` / `line-break: strict` 减轻末字孤行。
- B 星图外圈：短标签映射（如「服务器与整机」→「服务器」；长光侧截断+…），相邻 L3 径向内外错开；hover/`<title>` 出全称。
- 图例诚实：本轮 impact/direction 未核验时改为「本轮相关方向未核验，暂用中性色」，不再暗示红绿在用。
- 弹层底栏：打开 SegmentSheet 时隐藏星图图例，并提高 sheet/hint 层级与底栏分隔，避免与图例重叠。
- C：「清除正文」改为客户向「收起摘要」。

## 0.2.2

- 客户面去掉 A/C 区「不请求模型」等开发说明文案。


## 0.2.1 — 2026-10-21

- UX freeze v1：白底深蓝主色深红强调；纵向 A→B→C 阶段流；三层同心星图（不渲染公司节点）；C 区只读摘要与条形对比。
- 客户面去掉英文开发者小字；页脚 hash/commit 默认折叠；Loading/Error 中文客户向文案。
- Finance 确认：S1→S0「返回动机」；L2 四分支冻结文案；C 对比优先 pairs 否则同 segment reviewed。

## 0.2.0-mvp.2 — 2026-10-21

- 依照用户评审调整为产业投资研究终端：首页突出产业驱动、研究判断与公司经营数据，图谱辅助解释。
- 财务字段从现有缓存披露补齐，按同期间计算营收同比、集团毛利率和合并净利润同比；AI专项收入占比保留缺失。
- 母类别业务收入构成与AI专项占比分开展示；收入证据统计标明AI主题范围与核验分母，情景链不计为已验证传导闭环。
- 原图谱原型保存在 `bdd5665`，标签为 `checkpoint-ui-graph-20261021`，未标作验收版本。

## 0.2.0-mvp.1 — 2026-10-21

状态：原型检查点，信息架构经用户评审后由mvp.2取代，未正式验收。

- 新增本地交互前端：产业星图、市场与分支筛选、搜索和公司目录。
- 新增公司概览、证据、中外比较、事实与情景区分的事件路径。
- 新增研究流程与真实成本记录页面；标明已实现、规划和未测范围。
- 整理8家首批研究公司与14家待核验候选，输出独立前端快照与SHA-256。
- 使用用户指定的 `gpt-6-luna`、`max` 编写前端，研究模型保持 `deepseek-flash`。
- 保留研究快照、前端版本及构建Git提交，支持体验评审后的版本追溯。

## 0.1.0-research.20261021 — 2026-10-21

- 保存第二轮PydanticAI研究基线、计算表、Schema、来源和报告。
- Git基线提交：`07e0244`，标签：`v0.1.0-research.20261021`。
- 原始财报和接口产物保留在本地，不随源码提交。
