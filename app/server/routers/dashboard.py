from __future__ import annotations
from fastapi import APIRouter, HTTPException
from db.supabase import get_client

router = APIRouter(prefix="/api/v1")


@router.get("/machines/{machine_id}/dashboard")
async def get_dashboard(machine_id: str):
    db = get_client()

    machine = db.table("machines").select("*").eq("machine_id", machine_id).execute()
    if not machine.data:
        raise HTTPException(status_code=404, detail="Machine not found")

    machine_row = machine.data[0]
    machine_uuid = machine_row["id"]

    scan = (
        db.table("scans")
        .select("*")
        .eq("machine_id", machine_uuid)
        .order("scanned_at", desc=True)
        .limit(1)
        .execute()
    )

    scan_row = scan.data[0] if scan.data else None
    issues = []
    ai_explanation = None

    if scan_row:
        issues_result = (
            db.table("issues")
            .select("*")
            .eq("scan_id", scan_row["id"])
            .is_("resolved_at", None)
            .execute()
        )
        issues = issues_result.data or []
        ai_explanation = (scan_row.get("raw_data") or {}).get("ai_explanation")

    return {
        "machine": machine_row,
        "scan": {**scan_row, "issues": issues, "ai_explanation": ai_explanation} if scan_row else None,
    }


@router.get("/machines/{machine_id}/metrics")
async def get_metrics(machine_id: str, hours: int = 1):
    db = get_client()

    machine = db.table("machines").select("id").eq("machine_id", machine_id).execute()
    if not machine.data:
        raise HTTPException(status_code=404, detail="Machine not found")

    machine_uuid = machine.data[0]["id"]

    metrics = (
        db.table("metrics")
        .select("*")
        .eq("machine_id", machine_uuid)
        .order("recorded_at", desc=True)
        .limit(hours * 12)
        .execute()
    )

    return list(reversed(metrics.data or []))


@router.get("/machines/{machine_id}/issues")
async def get_machine_issues(machine_id: str):
    db = get_client()

    machine = db.table("machines").select("id").eq("machine_id", machine_id).execute()
    if not machine.data:
        raise HTTPException(status_code=404, detail="Machine not found")

    machine_uuid = machine.data[0]["id"]

    issues = (
        db.table("issues")
        .select("*")
        .eq("machine_id", machine_uuid)
        .is_("resolved_at", None)
        .order("created_at", desc=True)
        .execute()
    )

    return issues.data or []
