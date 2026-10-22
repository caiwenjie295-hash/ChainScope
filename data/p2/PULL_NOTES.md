# P2 拉数笔记

> 2026-10-22 盲测 P1（`b1h.p1`，非重拉深核）：对既有 `concept_feeds` 做 `industry_concept_only` 过滤；权重板补 `empty_reason_zh`；见 `FRONTEND_FIELDS_P2.md`。


- 时点：`2026-10-21`（Asia/Hong_Kong）
- 源：扶摇 REST；市值用 `auction/snapshot.float_market_cap`（`prices/snapshot` 无市值字段，已探针留痕）
- 权重：文档「敬请期待」，探针 404 → `missing_reason=weight_api_unavailable`，未假填

## 成分与市值榜
- `concept.ai`（885728.TI）：成分 1085；市值榜 10 条
- `concept.ai_chip`（885756.TI）：成分 932；市值榜 10 条
- `concept.ai_server`（885887.TI）：成分 663；市值榜 10 条
- `concept.ai_optics`（886033.TI）：成分 228；市值榜 10 条
- `concept.ai_cooling`（886044.TI）：成分 240；市值榜 10 条
- `concept.ai_power`（885887.TI）：成分 663；市值榜 10 条
- `concept.ai_software`（886108.TI）：成分 550；市值榜 10 条
- `concept.other_demo_disabled`：不可分析占位，双榜 null

## feeds
- flash/timeline 最小试拉：{"flash": {"ok": true, "n": 20}, "timeline": {"ok": true, "thscode": "601138.SH", "transport": {"http_status": 200, "elapsed_seconds": 2.958}}, "note": "minimal probe for联调"}
- 条数：{"concept.ai": 20, "concept.ai_chip": 0, "concept.ai_server": 0, "concept.ai_optics": 0, "concept.ai_cooling": 0, "concept.ai_power": 0, "concept.ai_software": 0, "concept.other_demo_disabled": 0}

## 边界
- 光模块→CPO（886033.TI）代理
- 算力服务器与 AIDC供配电共用 885887.TI
- AI应用软件 shallow=true

## 关键路径
- data/p2/concepts.json
- data/p2/concept_feeds.json
- data/p2/companies_registry.json
- data/p2/PULL_NOTES.md
- artifacts/raw/p2_constituents_*.json / p2_mktcap_*.json / p2_weight_probe.json

- 复用市值 raw：p2_mktcap_concept_ai.json: +1085 (file resolved=1085)

## B1b deep filings (2026-10-21 Asia/Hong_Kong)

- PDF via `scripts/fetch_public.py` + `config/public_focused_b1b*.json` (cninfo static URLs).
- cninfo hisAnnouncement/query returned 0 in this environment; MCP search_notice unavailable (URLError).
- Fuyao income statements: `config/p2_deep_b1b_fuyao.json` via `scripts/collect.py`.
- Grades: snapshot narrow B for fii/tfc/eoptolink; company_research wide A + narrow B.

## B1c pair/event (2026-10-21 Asia/Hong_Kong)

- Pairs hung: `fii_smci`, `eoptolink_cohr` (amount_compare_allowed=false; aligned_period=null).
- `tfc`: no pair — missing_reason (component vs module segment boundary; LITE breadth-only).
- Events: `fii_ai_server_cloud`, `eoptolink_high_speed_optics`, `tfc_optical_interconnect_components`.
- research_version=`2026-10-21.p2.deep.b1c`; validate green; no push.
