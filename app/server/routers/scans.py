from __future__ import annotations
import os
from typing import Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from db.supabase import get_client
from services.analyzer import analyze
from services.scorer import calculate
from services.metrics_writer import extract
from services.ai_explainer import generate_explanation

router = APIRouter(prefix="/api/v1")


class ScanBody(BaseModel):
    machine_id: str | None = None
    collected_at: str | None = None
    cpu: dict[str, Any] = {}
    memory: dict[str, Any] = {}
    disk: dict[str, Any] = {}
    network: dict[str, Any] = {}
    processes: dict[str, Any] = {}
    startup: dict[str, Any] = {}


@router.post("/machines/{machine_id}/scan")
async def ingest_scan(machine_id: str, body: ScanBody):
    db = get_client()

    machine = (
        db.table("machines")
        .select("id")
        .eq("machine_id", machine_id)
        .execute()
    )
    if not machine.data:
        raise HTTPException(status_code=404, detail="Machine not registered")

    machine_uuid = machine.data[0]["id"]
    payload = body.model_dump()

    issues = analyze(payload)
    score_result = calculate(issues)

    machine_row = db.table("machines").select("*").eq("id", machine_uuid).execute().data[0]

    ai_explanation: str | None = None
    if score_result.health_score < 70 and os.getenv("ANTHROPIC_API_KEY"):
        scan_stub = {
            "health_score": score_result.health_score,
            "score_performance": score_result.score_performance,
            "score_storage": score_result.score_storage,
            "score_security": score_result.score_security,
            "score_stability": score_result.score_stability,
        }
        issue_dicts = [
            {"issue_code": i.code, "severity": i.severity, "title": i.title, "description": i.description}
            for i in issues
        ]
        try:
            ai_explanation, _ = await generate_explanation(machine_row, scan_stub, issue_dicts)
        except Exception:
            pass

    payload["ai_explanation"] = ai_explanation

    scan = (
        db.table("scans")
        .insert({
            "machine_id": machine_uuid,
            "health_score": score_result.health_score,
            "score_performance": score_result.score_performance,
            "score_storage": score_result.score_storage,
            "score_security": score_result.score_security,
            "score_stability": score_result.score_stability,
            "raw_data": payload,
        })
        .execute()
    )

    if not scan.data:
        raise HTTPException(status_code=500, detail="Failed to save scan")

    scan_uuid = scan.data[0]["id"]

    if issues:
        db.table("issues").insert([
            {
                "scan_id": scan_uuid,
                "machine_id": machine_uuid,
                "issue_code": issue.code,
                "severity": issue.severity,
                "title": issue.title,
                "description": issue.description,
                "fix_available": issue.fix_available,
                "fix_command": issue.fix_command,
            }
            for issue in issues
        ]).execute()

    metrics = extract(machine_uuid, payload)
    db.table("metrics").insert(metrics).execute()

    db.table("machines").update({"last_seen": "now()"}).eq("id", machine_uuid).execute()

    return {
        "scan_id": scan_uuid,
        "health_score": score_result.health_score,
        "issues_detected": len(issues),
    }


@router.get("/machines/{machine_id}/scans/latest")
async def get_latest_scan(machine_id: str):
    db = get_client()

    machine = db.table("machines").select("id").eq("machine_id", machine_id).execute()
    if not machine.data:
        raise HTTPException(status_code=404, detail="Machine not found")

    machine_uuid = machine.data[0]["id"]

    scan = (
        db.table("scans")
        .select("*")
        .eq("machine_id", machine_uuid)
        .order("scanned_at", desc=True)
        .limit(1)
        .execute()
    )

    if not scan.data:
        return None

    scan_data = scan.data[0]
    scan_uuid = scan_data["id"]

    issues = (
        db.table("issues")
        .select("*")
        .eq("scan_id", scan_uuid)
        .is_("resolved_at", None)
        .execute()
    )

    return {**scan_data, "issues": issues.data}
