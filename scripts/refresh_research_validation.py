"""Validate the published research data and refresh the UI verification record.

Offline only. Does not change the snapshot, research conclusions, or archived
Agent usage/cost records. Run after publishing a new frontend snapshot.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path

from validate_frontend import validate


ROOT = Path(__file__).resolve().parents[1]


def refresh() -> dict:
    snapshot_path = ROOT / "frontend/public/data/snapshot.json"
    raw = snapshot_path.read_bytes()
    snapshot = json.loads(raw.decode("utf-8-sig"))
    checks = validate(snapshot)
    checked = datetime.now(timezone(timedelta(hours=8)))
    companies = snapshot["companies"]
    sources = list(snapshot["sources"].values())
    public = sum(bool(source.get("url")) and source.get("access", "").startswith("public") for source in sources)
    nodes = snapshot["graph"]["nodes"]
    events = snapshot.get("events") or ([snapshot["event"]] if snapshot.get("event") else [])
    record = {
        "snapshot_data_hash": snapshot["meta"]["data_hash"],
        "snapshot_sha256": hashlib.sha256(raw).hexdigest(),
        "research_version": snapshot["meta"]["research_version"],
        "checked_at": checked.isoformat(timespec="seconds"),
        "checked_date": checked.date().isoformat(),
        "timezone": "Asia/Hong_Kong",
        "checks": checks,
        "status": "passed",
        "scope": "当前研究数据的结构、引用与口径检查；不代表事实准确率或研究阶段运行次数",
        "current_counts": {
            "companies": len(companies),
            "reviewed_companies": sum(company["research_status"] == "reviewed" for company in companies),
            "candidate_companies": sum(company["research_status"] == "candidate" for company in companies),
            "sources": len(sources),
            "public_sources": public,
            "restricted_sources": len(sources) - public,
            "graph_nodes": len(nodes),
            "structure_nodes": sum(node["type"] != "company" for node in nodes),
            "company_nodes": sum(node["type"] == "company" for node in nodes),
            "companies_with_cited_business_facts": sum(
                any(claim.get("kind") == "fact" and claim.get("source_ids") for claim in company.get("claims", []))
                for company in companies
            ),
            "companies_with_numeric_metrics": sum(
                any(metric.get("value") is not None for metric in company.get("metrics", []))
                for company in companies
            ),
            "comparison_pairs": len(snapshot["pairs"]),
            "events": len(events),
        },
        "archived_workflow": {
            "source": "data/round2/evaluation.json",
            "scope": "早期8家公司、4组对照的归档研究运行，不包括后续补充研究或本次界面开发",
            "completed_stages": snapshot["evaluation"]["completed_stages"],
            "validation_checks": snapshot["evaluation"]["validation_checks"],
            "workflow": snapshot["evaluation"]["workflow"],
        },
    }
    target = ROOT / "frontend/src/researchValidation.json"
    target.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return record


if __name__ == "__main__":
    result = refresh()
    print(json.dumps(result, ensure_ascii=False))
