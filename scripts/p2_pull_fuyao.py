#!/usr/bin/env python3
"""P2 online pull via Fuyao REST. No fabricated numbers; raw traces with hashes."""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import time
from pathlib import Path
from urllib.parse import quote

from probe import CREDENTIALS, ROOT, now, request, save
from p2_empty_copy import EMPTY_WEIGHT_ZH, ensure_board_empty_zh, filter_concept_feeds, is_industry_concept_feed

BASE = "https://fuyao.aicubes.cn"
AS_OF = "2026-10-21"  # Asia/Hong_Kong calendar day of this run
FEEDS_WINDOW_DAYS = 30
AUCTION_BATCH = 80  # docs allow 100; keep margin
RANK_TOP_N = 10
WEIGHT_PROBE_PATHS = [
    "/api/a-share-index/constituents/weights?thscode={code}",
    "/api/a-share-index/weights?thscode={code}",
    "/api/a-share-index/overview/weights?thscode={code}",
    "/api/a-share-index/baseinfo/weights?thscode={code}",
]


def api_key() -> str:
    for p in (
        ROOT.parent / "chainscope-secrets" / "扶摇APIkey.txt",
        CREDENTIALS / "扶摇APIkey.txt",
    ):
        if p.exists():
            k = p.read_text(encoding="utf-8-sig").strip()
            if k:
                return k
    raise SystemExit("missing fuyao api key")


def headers(key: str) -> dict:
    return {"X-api-key": key, "Accept": "application/json"}


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def save_raw(name: str, payload: dict) -> dict:
    """Write JSON raw + sidecar hash meta. Returns meta."""
    path = ROOT / "artifacts" / "raw" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    raw = text.encode("utf-8")
    path.write_text(text, encoding="utf-8")
    meta = {
        "path": str(path.relative_to(ROOT)),
        "sha256": sha256_bytes(raw),
        "bytes": len(raw),
        "saved_at": now(),
    }
    meta_path = path.with_suffix(path.suffix + ".sha256")
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return meta


def company_id_from_thscode(thscode: str) -> str:
    return "co." + thscode.strip().lower().replace(".", "_")


def fmt_cny(v: float | None) -> str | None:
    if v is None:
        return None
    if abs(v) >= 1e12:
        return f"{v / 1e12:.2f}万亿"
    if abs(v) >= 1e8:
        return f"{v / 1e8:.2f}亿"
    if abs(v) >= 1e4:
        return f"{v / 1e4:.2f}万"
    return f"{v:.2f}"


def get_json(url: str, H: dict, timeout: int = 90):
    data, _, meta = request(url, headers=H, timeout=timeout)
    return data, meta


def load_seed() -> dict:
    return json.loads((ROOT / "config" / "p2_concept_seed.json").read_text(encoding="utf-8"))


def pull_constituents(concept_id: str, ths_code: str, H: dict) -> tuple[list[dict], dict]:
    url = f"{BASE}/api/a-share-index/constituents/ths-stock-list?thscode={quote(ths_code)}"
    data, meta = get_json(url, H)
    payload = {
        "id": f"p2_constituents_{concept_id}",
        "retrieved_at": now(),
        "request": {"method": "GET", "url": url, "thscode": ths_code, "concept_id": concept_id},
        "transport": meta,
        "response": data,
    }
    raw_meta = save_raw(f"p2_constituents_{concept_id}.json", payload)
    items = []
    if meta.get("http_status") == 200 and data.get("code") == 0:
        items = list((data.get("data") or {}).get("item") or [])
    return items, {"transport": meta, "raw": raw_meta, "biz_code": data.get("code"), "biz_message": data.get("message")}


def chunked(seq, n):
    for i in range(0, len(seq), n):
        yield seq[i : i + n]


def pull_auction_caps(thscodes: list[str], H: dict, tag: str) -> dict[str, dict]:
    """Return map thscode -> auction item (incl float_market_cap, name)."""
    out: dict[str, dict] = {}
    batch_raw = []
    unique = []
    seen = set()
    for c in thscodes:
        if c and c not in seen:
            seen.add(c)
            unique.append(c)
    for bi, batch in enumerate(chunked(unique, AUCTION_BATCH)):
        codes = ",".join(batch)
        url = f"{BASE}/api/a-share/auction/snapshot?thscodes={quote(codes, safe=',')}&stage=final"
        data, meta = get_json(url, H, timeout=120)
        batch_raw.append({"batch": bi, "url": url, "transport": meta, "response": data})
        if meta.get("http_status") == 200 and data.get("code") == 0:
            for it in (data.get("data") or {}).get("item") or []:
                tc = it.get("thscode")
                if tc:
                    out[tc] = it
        time.sleep(0.15)
    # also leave a prices/snapshot probe batch (no mkt cap field) for honesty/trace
    probe_codes = unique[: min(20, len(unique))]
    if probe_codes:
        url_p = f"{BASE}/api/a-share/prices/snapshot?thscodes={quote(','.join(probe_codes), safe=',')}"
        d_p, m_p = get_json(url_p, H, timeout=90)
        prices_probe = {"url": url_p, "transport": m_p, "response": d_p, "note": "prices/snapshot lacks float_market_cap; ranking uses auction/snapshot"}
    else:
        prices_probe = None
    raw_payload = {
        "id": f"p2_mktcap_{tag}",
        "retrieved_at": now(),
        "source_primary": "GET /api/a-share/auction/snapshot (float_market_cap)",
        "source_prices_probe": prices_probe,
        "batches": batch_raw,
        "resolved_count": len(out),
        "requested_count": len(unique),
    }
    save_raw(f"p2_mktcap_{tag}.json", raw_payload)
    return out


def probe_weights(ths_code: str, H: dict) -> dict:
    results = []
    available = False
    for tmpl in WEIGHT_PROBE_PATHS:
        path = tmpl.format(code=quote(ths_code))
        url = BASE + path
        data, meta = get_json(url, H, timeout=45)
        results.append({"url": url, "transport": meta, "biz_code": data.get("code"), "biz_message": data.get("message"), "has_items": bool(((data.get("data") or {}).get("item") or (data.get("data") or {}).get("items")))})
        if meta.get("http_status") == 200 and data.get("code") == 0 and results[-1]["has_items"]:
            available = True
        time.sleep(0.1)
    payload = {"id": "p2_weight_probe", "retrieved_at": now(), "ths_code": ths_code, "results": results, "available": available}
    save_raw("p2_weight_probe.json", payload)
    return payload


def empty_weight_board() -> dict:
    return ensure_board_empty_zh(
        {
            "metric": "concept_weight",
            "metric_label": "概念权重",
            "as_of": None,
            "unit": None,
            "items": [],
            "missing_reason": "weight_api_unavailable",
            "empty_reason_zh": EMPTY_WEIGHT_ZH,
        }
    )


def build_mkt_board(constituents: list[dict], caps: dict[str, dict], registry: dict) -> dict:
    rows = []
    for c in constituents:
        tc = c.get("thscode")
        if not tc:
            continue
        name = c.get("name") or (caps.get(tc) or {}).get("name") or tc
        cid = company_id_from_thscode(tc)
        registry.setdefault(cid, {"id": cid, "name": name, "thscode": tc})
        # prefer auction name if constituent name missing
        if registry[cid]["name"] in (None, "", tc) and (caps.get(tc) or {}).get("name"):
            registry[cid]["name"] = caps[tc]["name"]
        fmc = (caps.get(tc) or {}).get("float_market_cap")
        if isinstance(fmc, (int, float)):
            rows.append((cid, name, tc, float(fmc)))
    rows.sort(key=lambda x: x[3], reverse=True)
    # top10+ : keep at least 10 when available; also keep all with value for honesty of ranking source — task says top10+
    keep = rows[: max(RANK_TOP_N, min(15, len(rows)))]
    items = []
    for i, (cid, name, tc, val) in enumerate(keep, 1):
        items.append(
            {
                "rank": i,
                "company_id": cid,
                "name": name,
                "thscode": tc,
                "value": val,
                "value_display": fmt_cny(val),
            }
        )
    missing = None if items else "constituents_empty_or_no_float_market_cap"
    return ensure_board_empty_zh(
        {
            "metric": "mkt_cap",
            "metric_label": "市值",
            "as_of": AS_OF,
            "unit": "CNY",
            "items": items,
            "missing_reason": missing,
        }
    )


def ms_to_date(ms) -> str | None:
    if ms is None:
        return None
    try:
        # display in Asia/Hong_Kong
        tz = dt.timezone(dt.timedelta(hours=8))
        return dt.datetime.fromtimestamp(int(ms) / 1000, tz=tz).date().isoformat()
    except Exception:
        return None


def pull_feeds(concepts: list[dict], registry: dict, H: dict) -> tuple[dict, dict]:
    """Try flash + timelines for top names; 30d window. No fabricated links."""
    window_start = dt.datetime(2026, 9, 21, tzinfo=dt.timezone(dt.timedelta(hours=8)))
    window_start_ms = int(window_start.timestamp() * 1000)
    feeds: dict[str, list] = {}
    status = {"flash": None, "timelines": [], "missing": []}

    # flash general
    url_f = f"{BASE}/api/news/flash/list?tag_id=21103&seq=0"
    d_f, m_f = get_json(url_f, H, timeout=60)
    flash_items = []
    if m_f.get("http_status") == 200 and d_f.get("code") == 0:
        for it in (d_f.get("data") or {}).get("items") or []:
            cms = it.get("create_time_ms")
            if cms is not None and int(cms) < window_start_ms:
                continue
            flash_items.append(
                {
                    "id": f"feed.flash.{it.get('id')}",
                    "title": it.get("title") or "",
                    "date": ms_to_date(cms),
                    "url": it.get("encoded_url"),
                    "kind": "news",
                    "source_id": "src.fuyao.news.flash",
                    "publisher": None,
                }
            )
        status["flash"] = {"ok": True, "n": len(flash_items), "transport": m_f}
        save_raw("p2_feeds_flash.json", {"retrieved_at": now(), "request": url_f, "transport": m_f, "response": d_f})
    else:
        status["flash"] = {"ok": False, "transport": m_f, "biz": d_f.get("code")}
        status["missing"].append("news_flash")
        save_raw("p2_feeds_flash.json", {"retrieved_at": now(), "request": url_f, "transport": m_f, "response": d_f})

    # attach flash only to root concept if any — industry/concept filter (no politics flood)
    root_id = next((c["id"] for c in concepts if c.get("level") == 0 and c.get("analysis_enabled")), None)
    flash_industry = [f for f in flash_items if is_industry_concept_feed(f.get("title"))]

    for concept in concepts:
        cid = concept["id"]
        if not concept.get("analysis_enabled"):
            feeds[cid] = []
            continue
        collected = []
        if cid == root_id and flash_industry:
            collected.extend(flash_industry[:20])

        # timeline for top up to 5 by mkt board
        board = concept.get("rank_by_mkt_cap") or {}
        tops = (board.get("items") or [])[:5]
        for rank_item in tops:
            tc = rank_item.get("thscode")
            if not tc:
                continue
            url_t = f"{BASE}/api/news/stock/timeline-list?thscode={quote(tc)}&offset=first&size=20"
            d_t, m_t = get_json(url_t, H, timeout=60)
            status["timelines"].append({"concept_id": cid, "thscode": tc, "transport": m_t, "biz": d_t.get("code")})
            save_raw(
                f"p2_feeds_timeline_{cid}_{tc.replace('.', '_')}.json",
                {"retrieved_at": now(), "request": url_t, "transport": m_t, "response": d_t},
            )
            if m_t.get("http_status") == 200 and d_t.get("code") == 0:
                for it in (d_t.get("data") or {}).get("items") or []:
                    pms = it.get("publish_time_ms")
                    if pms is not None and int(pms) < window_start_ms:
                        continue
                    jump = it.get("jump_url")
                    # docs: jump_url 不保证可用；仍如实写入若非空
                    collected.append(
                        {
                            "id": f"feed.tl.{tc}.{it.get('id')}",
                            "title": it.get("title") or "",
                            "date": ms_to_date(pms),
                            "url": jump if jump else None,
                            "kind": "news",
                            "source_id": "src.fuyao.news.stock_timeline",
                            "publisher": it.get("source") or it.get("author"),
                        }
                    )
            time.sleep(0.12)

        # industry/concept filter (timeline may still carry noise), then dedupe / sort / cap 20
        collected = [f for f in collected if is_industry_concept_feed(f.get("title"))]
        seen = set()
        uniq = []
        for f in collected:
            if f["id"] in seen:
                continue
            seen.add(f["id"])
            uniq.append(f)
        uniq.sort(key=lambda x: x.get("date") or "", reverse=True)
        feeds[cid] = uniq[:20]
        if not feeds[cid]:
            status["missing"].append(f"feeds:{cid}")

    status["source_policy"] = "industry_concept_only"
    status["flash_industry_n"] = len(flash_industry)
    return feeds, status


def main():
    key = api_key()
    H = headers(key)
    seed = load_seed()
    (ROOT / "data" / "p2").mkdir(parents=True, exist_ok=True)

    # collect concept specs
    specs = []
    root = seed["root"]
    specs.append({**root, "parent_id": None, "level": 0, "shallow": False})
    for ch in seed["children"]:
        specs.append({**ch, "parent_id": root["id"], "level": 1})
    placeholder = seed["non_demo_placeholder"]

    # unique ths pulls
    code_to_items: dict[str, list] = {}
    pull_meta = {}
    for sp in specs:
        code = sp.get("ths_code")
        if not code:
            continue
        if code in code_to_items:
            # still write a concept-specific raw alias pointing to shared
            shared = code_to_items[code]
            payload = {
                "id": f"p2_constituents_{sp['id']}",
                "retrieved_at": now(),
                "note": f"shared constituents with ths_code={code}; see sibling raw for HTTP body",
                "ths_code": code,
                "item_count": len(shared),
                "item": shared,
            }
            save_raw(f"p2_constituents_{sp['id']}.json", payload)
            pull_meta[sp["id"]] = {"shared_ths_code": code, "n": len(shared)}
            continue
        items, meta = pull_constituents(sp["id"], code, H)
        code_to_items[code] = items
        pull_meta[sp["id"]] = {"ths_code": code, "n": len(items), **meta}
        print(f"constituents {sp['id']} {code}: {len(items)}", flush=True)
        time.sleep(0.2)

    # weight probe once on root code
    weight_probe = probe_weights(root["ths_code"], H)
    print("weight available:", weight_probe.get("available"), flush=True)

    # market caps per unique code set used by analyzable concepts
    # pull per concept group to keep raw scoped, but merge cache
    cap_cache: dict[str, dict] = {}
    registry: dict[str, dict] = {}
    concepts_out = []

    for sp in specs:
        code = sp.get("ths_code")
        items = code_to_items.get(code, []) if code else []
        # ensure registry from constituents even before caps
        for c in items:
            tc = c.get("thscode")
            if not tc:
                continue
            cid = company_id_from_thscode(tc)
            registry.setdefault(cid, {"id": cid, "name": c.get("name") or tc, "thscode": tc})

        company_ids = [company_id_from_thscode(c["thscode"]) for c in items if c.get("thscode")]
        entry = {
            "id": sp["id"],
            "name": sp["name"],
            "parent_id": sp.get("parent_id"),
            "level": sp["level"],
            "company_ids": company_ids,
            "company_count": len(company_ids),
            "analysis_enabled": bool(sp.get("analysis_enabled")),
            "ths_code": code,
            "ths_name": sp.get("ths_name"),
        }
        if sp.get("shallow"):
            entry["shallow"] = True
        if sp.get("mapping_note"):
            entry["description"] = sp["mapping_note"]
        if sp.get("coverage_note"):
            entry["description"] = (entry.get("description") + "；" if entry.get("description") else "") + sp["coverage_note"]

        if not entry["analysis_enabled"]:
            entry["rank_by_mkt_cap"] = None
            entry["rank_by_concept_weight"] = None
        else:
            # pull caps for this concept's codes (skip if already cached all)
            need = [c["thscode"] for c in items if c.get("thscode") and c["thscode"] not in cap_cache]
            if need:
                print(f"auction caps {sp['id']}: requesting {len(need)} (cache {len(cap_cache)})", flush=True)
                got = pull_auction_caps(need, H, tag=sp["id"].replace(".", "_"))
                cap_cache.update(got)
            board = build_mkt_board(items, cap_cache, registry)
            entry["rank_by_mkt_cap"] = board
            if weight_probe.get("available"):
                # not expected; leave structure for future
                entry["rank_by_concept_weight"] = empty_weight_board()
            else:
                entry["rank_by_concept_weight"] = empty_weight_board()
            print(f"rank {sp['id']}: mkt_items={len(board['items'])} constituents={len(items)}", flush=True)

        concepts_out.append(entry)

    # placeholder
    concepts_out.append(
        {
            "id": placeholder["id"],
            "name": placeholder["name"],
            "parent_id": None,
            "level": 0,
            "company_ids": [],
            "company_count": 0,
            "analysis_enabled": False,
            "rank_by_mkt_cap": None,
            "rank_by_concept_weight": None,
        }
    )

    concepts_doc = {
        "meta": {
            "theme_mode": seed.get("theme_mode"),
            "research_version": "2026-10-21.p2",
            "feeds_window_days": seed.get("feeds_window_days", FEEDS_WINDOW_DAYS),
            "rank_default": seed.get("rank_default", "mkt_cap"),
            "as_of": AS_OF,
            "as_of_tz": "Asia/Hong_Kong",
            "pulled_at": now(),
        },
        "concepts": concepts_out,
    }
    out_concepts = ROOT / "data" / "p2" / "concepts.json"
    out_concepts.write_text(json.dumps(concepts_doc, ensure_ascii=False, indent=2), encoding="utf-8")

    # feeds (needs boards already on concepts_out)
    feeds, feed_status = pull_feeds(concepts_out, registry, H)
    # Re-assert filter + human empty meta (idempotent)
    feeds, feeds_meta = filter_concept_feeds(feeds, concept_ids=[c["id"] for c in concepts_out])
    feeds_doc = {
        "meta": {
            "feeds_window_days": FEEDS_WINDOW_DAYS,
            "window_start": "2026-09-21",
            "window_end": AS_OF,
            "as_of_tz": "Asia/Hong_Kong",
            "pulled_at": now(),
            "status": feed_status,
            "source_policy": "industry_concept_only",
        },
        "concept_feeds": feeds,
        "concept_feeds_meta": feeds_meta,
    }
    out_feeds = ROOT / "data" / "p2" / "concept_feeds.json"
    out_feeds.write_text(json.dumps(feeds_doc, ensure_ascii=False, indent=2), encoding="utf-8")

    # registry
    reg_list = sorted(registry.values(), key=lambda x: x["thscode"])
    reg_doc = {
        "meta": {"count": len(reg_list), "pulled_at": now(), "as_of": AS_OF},
        "companies": reg_list,
    }
    out_reg = ROOT / "data" / "p2" / "companies_registry.json"
    out_reg.write_text(json.dumps(reg_doc, ensure_ascii=False, indent=2), encoding="utf-8")

    # notes
    feed_counts = {k: len(v) for k, v in feeds.items()}
    lines = [
        "# P2 拉数笔记",
        "",
        f"- 时点：`{AS_OF}`（Asia/Hong_Kong）；脚本拉取 UTC：`{now()}`",
        "- 源：扶摇 REST（`X-api-key`）；raw 在 `artifacts/raw/p2_*.json`（附 `.sha256`）",
        "",
        "## 成分",
    ]
    for e in concepts_out:
        if e["id"].endswith("disabled"):
            lines.append(f"- `{e['id']}`：占位，analysis_enabled=false，双榜 null")
            continue
        lines.append(f"- `{e['id']}`（{e.get('ths_code')} / {e.get('ths_name')}）：成分 {e['company_count']}；市值榜 {len((e.get('rank_by_mkt_cap') or {}).get('items') or [])} 条")
    lines += [
        "",
        "## 市值字段",
        "- 文档要求的 `GET /api/a-share/prices/snapshot` **不含** `float_market_cap`（实测仅价量字段）。",
        "- 市值排序改用文档已列字段的 `GET /api/a-share/auction/snapshot` → `float_market_cap`；prices 探针留痕于 `p2_mktcap_*.json`。",
        "",
        "## 权重榜",
        f"- 权重 API 文档写「敬请期待」；探针路径均 404/空 → `rank_by_concept_weight.items=[]`，`missing_reason=weight_api_unavailable` + `empty_reason_zh=权重数据暂不可用`（未假填；禁裸露机读码）。",
        f"- 探针 raw：`artifacts/raw/p2_weight_probe.json`；available={weight_probe.get('available')}",
        "",
        "## feeds",
        "- feeds 策略：`industry_concept_only`（禁时政灌屏）；空则 `concept_feeds_meta.empty_reason_zh`。",
        f"- 快讯 `/api/news/flash/list?tag_id=21103`：{'ok '+str(feed_status.get('flash')) if feed_status.get('flash',{}).get('ok') else '失败/空'}",
        f"- 个股 timeline：对各可分析概念市值榜 top5 试拉，30 天窗过滤。",
        f"- 条数：{json.dumps(feed_counts, ensure_ascii=False)}",
        "",
        "## 边界",
        "- 光模块与光通信：扶摇无独立「光模块」板，种子用共封装光学(CPO) `886033.TI` 代理。",
        "- 算力服务器与 AIDC供配电：共用数据中心(AIDC) `885887.TI` 成分；深核需按业务再筛。",
        "- AI应用软件：shallow=true。",
        "",
        "## 关键路径",
        "- `data/p2/concepts.json`",
        "- `data/p2/concept_feeds.json`",
        "- `data/p2/companies_registry.json`",
        "- `artifacts/raw/p2_constituents_*.json`",
        "- `artifacts/raw/p2_mktcap_*.json`",
    ]
    notes = ROOT / "data" / "p2" / "PULL_NOTES.md"
    notes.write_text("\n".join(lines) + "\n", encoding="utf-8")

    summary = {
        "concepts": [
            {
                "id": e["id"],
                "constituents": e["company_count"],
                "mkt_rank_n": None if e.get("rank_by_mkt_cap") is None else len(e["rank_by_mkt_cap"].get("items") or []),
                "weight_empty": None if e.get("rank_by_concept_weight") is None else (len(e["rank_by_concept_weight"].get("items") or []) == 0),
                "feeds_n": len(feeds.get(e["id"], [])),
            }
            for e in concepts_out
        ],
        "registry_n": len(reg_list),
        "weight_available": weight_probe.get("available"),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
