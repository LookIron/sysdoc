from __future__ import annotations
from datetime import datetime
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from db.supabase import get_client
from services.ai_explainer import generate_explanation

router = APIRouter(prefix="/api/v1")


class ExplainBody(BaseModel):
    machine_id: str


@router.post("/ai/explain")
async def explain(body: ExplainBody):
    db = get_client()

    machine = db.table("machines").select("*").eq("machine_id", body.machine_id).execute()
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
    if not scan.data:
        raise HTTPException(status_code=404, detail="No scans found for machine")

    scan_row = scan.data[0]

    if (scan_row.get("health_score") or 100) >= 70:
        return {"explanation": None, "cached": False, "generated_at": None, "skipped": "health_score >= 70"}

    issues = (
        db.table("issues")
        .select("*")
        .eq("scan_id", scan_row["id"])
        .is_("resolved_at", None)
        .execute()
    )

    explanation, cached = await generate_explanation(machine_row, scan_row, issues.data or [])

    return {
        "explanation": explanation,
        "cached": cached,
        "generated_at": datetime.utcnow().isoformat() + "Z",
    }
