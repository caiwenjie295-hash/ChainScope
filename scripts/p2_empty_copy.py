"""P2 blind-test P1: human empty-state copy + industry/concept feed filter.

No fabricated ranks/feeds. Machine codes stay on missing_reason; UI reads empty_reason_zh.
"""
from __future__ import annotations

import re
from typing import Any

EMPTY_WEIGHT_ZH = "权重数据暂不可用"
EMPTY_FEEDS_ZH = "本轮暂无与该概念直接相关的产业资讯"
EMPTY_MKT_ZH = "暂无可用市值排序数据"

# machine missing_reason → human copy
MISSING_REASON_ZH: dict[str, str] = {
    "weight_api_unavailable": EMPTY_WEIGHT_ZH,
    "constituents_empty_or_no_float_market_cap": EMPTY_MKT_ZH,
    "legacy_empty_array": "本榜暂不可用",
}

# Allowlist: industry / concept / AI supply-chain signals (case-insensitive for latin).
_INDUSTRY_PATTERNS = [
    r"AI",
    r"A\.?I\.?",
    r"人工智能",
    r"算力",
    r"大模型",
    r"芯片",
    r"半导体",
    r"GPU",
    r"CPU",
    r"DCU",
    r"光模块",
    r"光通信",
    r"光互连",
    r"光互联",
    r"CPO",
    r"共封装",
    r"液冷",
    r"数据中心",
    r"AIDC",
    r"服务器",
    r"超算",
    r"超微",
    r"英伟达",
    r"NVIDIA",
    r"DeepSeek",
    r"寒武纪",
    r"海光",
    r"PCB",
    r"覆铜板",
    r"CCL",
    r"互连",
    r"液冷服务器",
    r"供配电",
    r"UPS",
    r"机柜",
    r"交换机",
    r"以太网",
    r"HBM",
    r"先进封装",
    r"晶圆",
    r"代工",
    r"云(?:计算|服务|厂商)?",
    r"智算",
    r"推理",
    r"训练集群",
    r"Blackwell",
    r"GB200",
    r"NVLink",
    r"光器件",
    r"硅光",
    r"铜缆",
    r"高速互联",
    r"产业创新",
    r"科技创新",
]

_INDUSTRY_RE = re.compile("|".join(f"(?:{p})" for p in _INDUSTRY_PATTERNS), re.IGNORECASE)

# Hard reject: politics / geopolitics flood (even if somehow matched)
_POLITICS_RE = re.compile(
    r"外长|总统|军演|宵禁|弹道导弹|霍尔木兹|胡塞|俄美乌|三方会谈|农相|丑闻|珊瑚白化|"
    r"进博会|香蕉|外交部|联合军演|夜禁|袭船|伊朗|也门|秘鲁",
)


def is_industry_concept_feed(title: str | None) -> bool:
    t = (title or "").strip()
    if not t:
        return False
    if _POLITICS_RE.search(t):
        return False
    return bool(_INDUSTRY_RE.search(t))


def empty_reason_zh_for(missing_reason: str | None, *, metric: str | None = None) -> str:
    if missing_reason and missing_reason in MISSING_REASON_ZH:
        return MISSING_REASON_ZH[missing_reason]
    if metric == "concept_weight":
        return EMPTY_WEIGHT_ZH
    if metric == "mkt_cap":
        return EMPTY_MKT_ZH
    return "本榜暂不可用"


def ensure_board_empty_zh(board: Any) -> Any:
    """Attach empty_reason_zh on RankBoard; keep missing_reason as machine code."""
    if not isinstance(board, dict):
        return board
    items = board.get("items") or []
    if items:
        board["empty_reason_zh"] = None
        if board.get("missing_reason") in ("",):
            board["missing_reason"] = None
        return board
    mr = board.get("missing_reason")
    if not mr:
        # keep honest: empty board must explain
        metric = board.get("metric")
        board["missing_reason"] = (
            "weight_api_unavailable" if metric == "concept_weight" else "board_empty"
        )
        mr = board["missing_reason"]
    board["empty_reason_zh"] = empty_reason_zh_for(mr, metric=board.get("metric"))
    return board


def filter_concept_feeds(
    feeds: dict[str, list],
    *,
    concept_ids: list[str] | None = None,
) -> tuple[dict[str, list], dict[str, dict]]:
    """Filter to industry/concept-related items; build concept_feeds_meta."""
    ids = concept_ids or list(feeds.keys())
    out: dict[str, list] = {}
    meta: dict[str, dict] = {}
    for cid in ids:
        raw = list(feeds.get(cid) or [])
        kept = [f for f in raw if is_industry_concept_feed(f.get("title") if isinstance(f, dict) else None)]
        # dedupe by id preserving order
        seen = set()
        uniq = []
        for f in kept:
            fid = f.get("id") if isinstance(f, dict) else None
            if fid and fid in seen:
                continue
            if fid:
                seen.add(fid)
            uniq.append(f)
        out[cid] = uniq[:20]
        meta[cid] = {
            "empty_reason_zh": None if out[cid] else EMPTY_FEEDS_ZH,
            "source_policy": "industry_concept_only",
            "filtered": True,
            "raw_count": len(raw),
            "kept_count": len(out[cid]),
        }
    # also keep any extra keys from feeds not in ids? already covered if ids from feeds
    for cid, raw in feeds.items():
        if cid in out:
            continue
        kept = [f for f in (raw or []) if is_industry_concept_feed(f.get("title") if isinstance(f, dict) else None)]
        out[cid] = kept[:20]
        meta[cid] = {
            "empty_reason_zh": None if out[cid] else EMPTY_FEEDS_ZH,
            "source_policy": "industry_concept_only",
            "filtered": True,
            "raw_count": len(raw or []),
            "kept_count": len(out[cid]),
        }
    return out, meta


# --- customer-facing scrub (blind 0.3.21) ---
_MACHINE_MR = frozenset(MISSING_REASON_ZH) | {"board_empty", "legacy_empty_array"}


def _human_source_title(title: str | None) -> str | None:
    if not title:
        return title
    t = title
    t = t.replace("（P2 raw）", "").replace("(P2 raw)", "")
    t = t.replace("P2 raw", "")
    t = re.sub(r"\s{2,}", " ", t).strip(" /")
    return t or title


def _human_source_locator(locator: str | None) -> str | None:
    if not locator:
        return locator
    loc = locator.strip()
    if "response.data" in loc or re.search(r"item\[\*\]\.thscode", loc):
        return "概念板块成分代码列表"
    m = re.match(r"^thscode\s*=\s*([0-9A-Za-z.]+)\s*;\s*item_count\s*=\s*(\d+)\s*$", loc)
    if m:
        return f"成分约 {m.group(2)} 只"
    if loc.startswith("thscode=") or "thscode=" in loc:
        # drop keyname; keep trailing human bits if any
        loc2 = re.sub(r"thscode\s*=\s*[0-9A-Za-z.]+;?\s*", "", loc)
        loc2 = re.sub(r"item_count\s*=\s*(\d+)", r"成分约 \1 只", loc2)
        loc2 = re.sub(r"\s{2,}", " ", loc2).strip(" ;")
        return loc2 or "成分列表"
    return locator


def _ensure_metric_empty_zh(obj: Any) -> None:
    if not isinstance(obj, dict):
        return
    mr = obj.get("missing_reason")
    if not mr or obj.get("empty_reason_zh"):
        return
    if isinstance(mr, str) and mr in _MACHINE_MR:
        obj["empty_reason_zh"] = empty_reason_zh_for(mr)
    elif isinstance(mr, str) and not re.fullmatch(r"[a-z0-9_]+", mr):
        # already human sentence wrongly parked on missing_reason — mirror for UI
        obj["empty_reason_zh"] = mr


def scrub_customer_facing_snapshot(snap: dict[str, Any]) -> dict[str, Any]:
    """Rewrite customer-visible strings; keep machine keys for join.

    Shell still must not render key names: thscode / missing_reason / pair id.
    """
    sources = snap.get("sources")
    if isinstance(sources, dict):
        for _sid, src in sources.items():
            if not isinstance(src, dict):
                continue
            if "title" in src:
                src["title"] = _human_source_title(src.get("title"))
            if "locator" in src:
                src["locator"] = _human_source_locator(src.get("locator"))

    for co in snap.get("companies") or []:
        if not isinstance(co, dict):
            continue
        for met in co.get("metrics") or []:
            _ensure_metric_empty_zh(met)
        for k in (
            "relevant_revenue_share",
            "revenue_yoy",
            "gross_margin",
            "net_profit_yoy",
            "gross_margin_change_pp",
        ):
            _ensure_metric_empty_zh(co.get(k))
        for seg in co.get("business_composition") or []:
            _ensure_metric_empty_zh(seg)

    for board_parent in snap.get("concepts") or []:
        if not isinstance(board_parent, dict):
            continue
        for bk in ("rank_by_mkt_cap", "rank_by_concept_weight"):
            ensure_board_empty_zh(board_parent.get(bk))

    meta = snap.setdefault("meta", {})
    # customer footer must not need these; keep for validate but mark policy
    meta["customer_copy"] = "empty_reason_zh_primary"
    return snap

