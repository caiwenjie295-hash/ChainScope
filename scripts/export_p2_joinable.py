"""Merge data/p2 into frontend snapshot; map RankItem.company_id → companies[].id via ticker.

Single source of truth: this script ALWAYS overwrites
  frontend/public/data/snapshot.json
and writes the same bytes as backup to
  artifacts/frontend/snapshot.p2.joinable.json
Legacy P1 editorial lives only under artifacts/frontend/snapshot.round2.p1.json
(export_frontend.py) and must never replace public.
"""
from __future__ import annotations
import copy, hashlib, json
from datetime import datetime, timezone, timedelta
from pathlib import Path

from p2_empty_copy import ensure_board_empty_zh, filter_concept_feeds, scrub_customer_facing_snapshot

ROOT = Path(__file__).resolve().parents[1]
HK = timezone(timedelta(hours=8))


def ticker_map(companies):
    m = {}
    for c in companies:
        tid = (c.get("ticker") or "").upper().strip()
        if not tid:
            continue
        m[tid] = c["id"]
        if "." in tid:
            m[tid.split(".")[0]] = c["id"]
    return m


def map_item(it, tmap):
    it = copy.deepcopy(it)
    ths = (it.get("thscode") or "").upper().strip()
    bare = ths.split(".")[0] if ths else ""
    deep = tmap.get(ths) or tmap.get(bare)
    it["ticker"] = ths or it.get("ticker")
    if deep:
        it["company_id"] = deep
        it["deep_company_id"] = deep
        it["deep_linked"] = True
        it.pop("market_id", None)
    else:
        it["company_id"] = None
        it["deep_company_id"] = None
        it["deep_linked"] = False
        it["market_id"] = f"mkt.{ths.lower().replace('.', '_')}" if ths else None
    return it


def map_board(board, tmap):
    if not isinstance(board, dict):
        return board
    b = copy.deepcopy(board)
    b["items"] = [map_item(it, tmap) for it in (b.get("items") or [])]
    return b


def main():
    snap_path = ROOT / "frontend/public/data/snapshot.json"
    bak = ROOT / "frontend/public/data/snapshot.round2.p1.json"
    snap = json.loads(snap_path.read_text(encoding="utf-8"))
    if not bak.exists():
        bak.write_text(json.dumps(snap, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    tmap = ticker_map(snap.get("companies") or [])
    concepts_raw = json.loads((ROOT / "data/p2/concepts.json").read_text(encoding="utf-8"))
    concepts = concepts_raw if isinstance(concepts_raw, list) else concepts_raw.get("concepts", [])
    feeds_wrap = json.loads((ROOT / "data/p2/concept_feeds.json").read_text(encoding="utf-8"))
    feeds = feeds_wrap.get("concept_feeds", feeds_wrap) if isinstance(feeds_wrap, dict) else {}

    slim = []
    for c in concepts:
        c2 = copy.deepcopy(c)
        if c2.get("analysis_enabled"):
            c2["rank_by_mkt_cap"] = ensure_board_empty_zh(map_board(c2.get("rank_by_mkt_cap"), tmap))
            c2["rank_by_concept_weight"] = ensure_board_empty_zh(
                map_board(c2.get("rank_by_concept_weight"), tmap)
            )
            m_items = (c2.get("rank_by_mkt_cap") or {}).get("items") or []
            c2["company_ids"] = list(
                dict.fromkeys(it["company_id"] for it in m_items if it.get("deep_linked") and it.get("company_id"))
            )
        if c2.get("id") == "concept.ai":
            c2["parent_id"] = None
            c2["level"] = 0
        slim.append(c2)

    # Blind-test P1: industry/concept feeds only + human empty meta (no politics flood)
    feeds, feeds_meta = filter_concept_feeds(feeds, concept_ids=[c["id"] for c in slim])

    # persist remapped concepts (keep meta wrapper when present)
    out_concepts = slim
    if isinstance(concepts_raw, dict):
        wrapped = copy.deepcopy(concepts_raw)
        wrapped["concepts"] = slim
        meta_c = wrapped.setdefault("meta", {})
        meta_c["research_version"] = "2026-10-22.p2.deep.b1h.p1.c"
        meta_c["c1_hierarchy_note"] = (
            "C① 层级以 concepts[] 为准；legacy industry_graph 仍为 B 星图兼容（P1 树），本轮未切概念板 graph。"
        )
        out_concepts = wrapped
    (ROOT / "data/p2/concepts.json").write_text(
        json.dumps(out_concepts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    # persist filtered feeds + meta back to data/p2 (source of truth for next export)
    feeds_path = ROOT / "data/p2/concept_feeds.json"
    feeds_wrap_out = copy.deepcopy(feeds_wrap) if isinstance(feeds_wrap, dict) else {"concept_feeds": {}}
    feeds_wrap_out["concept_feeds"] = feeds
    feeds_wrap_out["concept_feeds_meta"] = feeds_meta
    meta_f = feeds_wrap_out.setdefault("meta", {})
    meta_f["source_policy"] = "industry_concept_only"
    meta_f["blind_p1"] = "b1h.p1"
    feeds_path.write_text(json.dumps(feeds_wrap_out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    snap["concepts"] = slim
    snap["concept_feeds"] = feeds
    snap["concept_feeds_meta"] = feeds_meta
    meta = snap.setdefault("meta", {})
    meta.update(
        {
            "theme_mode": "concept_board",
            "research_version": "2026-10-22.p2.deep.b1h.p1.c",
            "feeds_window_days": 30,
            "rank_default": "mkt_cap",
            "generated_at": datetime.now(HK).isoformat(),
            "p2_joinable": True,
            "id_policy": "RankItem.company_id == companies[].id when ticker maps; else null + thscode",
            "p2_notes": (
                "盲测P1契约 b1h.p1（非新深核）：feeds=industry_concept_only（禁时政灌屏）；"
                "权重空板带 empty_reason_zh=权重数据暂不可用（勿裸露 missing_reason 机读码）；"
                "市值 top10；id 已对齐；四硬指标深核未齐。"
                "C① 层级以 concepts[]（parent_id/level/source_ids）为准；"
                "legacy industry_graph 仍为 B 星图兼容（P1 theme/branch/segment 树），本轮不谎称已切概念板 graph。"
                "B1h可演示收口仍有效：四硬齐 fii/eoptolink/innolight(+envicool)；tfc/luxshare/shengyi/cambricon/hygon 三硬+C③空态；sanhua 诚实E；禁假A/假pair；不喊P2完成。"
            ),
            "c1_hierarchy": "concepts_array",
            "industry_graph_role": "legacy_star_map_p1_compat",
            "c_zone_blocks": [
                {"id": "taxonomy_membership", "title": "产业链分类与归属证据", "primary_paths": ["concepts", "graph"]},
                {"id": "concept_grades", "title": "概念可信度 A–E", "primary_paths": ["companies.assessment", "claims"]},
                {"id": "comparability", "title": "中外可比边界", "primary_paths": ["pairs"]},
                {"id": "transmission", "title": "事件传导路径", "primary_paths": ["events"]},
            ],
        }
    )
    scrub_customer_facing_snapshot(snap)

    # fingerprint must match validate_frontend (exclude generated_at + data_hash)
    content = {**snap, "meta": {k: v for k, v in snap["meta"].items() if k not in ("generated_at", "data_hash")}}
    snap["meta"]["data_hash"] = hashlib.sha256(
        json.dumps(content, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    text = json.dumps(snap, ensure_ascii=False, indent=2) + "\n"
    snap_path.write_text(text, encoding="utf-8")
    (ROOT / "artifacts/frontend/snapshot.p2.joinable.json").write_text(text, encoding="utf-8")
    print(snap_path, "sha256", hashlib.sha256(text.encode()).hexdigest()[:16])



def sync_joinable_to_public():
    """Copy artifacts joinable snapshot onto public when public lagged or was overwritten."""
    src = ROOT / "artifacts/frontend/snapshot.p2.joinable.json"
    dst = ROOT / "frontend/public/data/snapshot.json"
    if not src.is_file():
        raise FileNotFoundError(src)
    text = src.read_text(encoding="utf-8")
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(text, encoding="utf-8")
    print(dst, "synced from joinable sha256", hashlib.sha256(text.encode()).hexdigest()[:16])
    return dst


if __name__ == "__main__":
    import sys
    if "--sync-public" in sys.argv:
        sync_joinable_to_public()
    else:
        main()
