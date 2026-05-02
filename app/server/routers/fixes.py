from __future__ import annotations
from datetime import datetime
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from db.supabase import get_client

router = APIRouter(prefix="/api/v1")

ALLOWED_FIX_CODES = frozenset({"FIX_P04_GHOST", "FIX_P10_TRIM", "FIX_CLR_TEMP", "FIX_P01_INFO", "FIX_P03_RESTART", "FIX_STARTUP_TOGGLE"})


class FixBody(BaseModel):
    issue_id: str
    fix_code: str


class FixResultBody(BaseModel):
    success: bool
    output: str


def _resolve_machine_uuid(db, machine_id: str) -> str:
    result = db.table("machines").select("id").eq("machine_id", machine_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Machine not found")
    return result.data[0]["id"]


@router.post("/machines/{machine_id}/fix")
async def queue_fix(machine_id: str, body: FixBody):
    if body.fix_code not in ALLOWED_FIX_CODES:
        raise HTTPException(status_code=400, detail=f"Unknown fix code: {body.fix_code}")

    db = get_client()
    machine_uuid = _resolve_machine_uuid(db, machine_id)

    cmd = db.table("pending_commands").insert({
        "machine_id": machine_uuid,
        "fix_code": body.fix_code,
        "params": {"issue_id": body.issue_id},
        "status": "queued",
    }).execute()

    if not cmd.data:
        raise HTTPException(status_code=500, detail="Failed to queue fix")

    db.table("fix_history").insert({
        "machine_id": machine_uuid,
        "issue_id": body.issue_id,
        "fix_code": body.fix_code,
    }).execute()

    return {"fix_id": cmd.data[0]["id"], "status": "queued"}


@router.get("/machines/{machine_id}/pending_commands")
async def get_pending_commands(machine_id: str):
    db = get_client()
    machine_uuid = _resolve_machine_uuid(db, machine_id)

    cmds = (
        db.table("pending_commands")
        .select("*")
        .eq("machine_id", machine_uuid)
        .eq("status", "queued")
        .order("created_at")
        .execute()
    )

    return {"commands": cmds.data or []}


@router.post("/machines/{machine_id}/fix/{fix_id}/result")
async def report_fix_result(machine_id: str, fix_id: str, body: FixResultBody):
    db = get_client()
    machine_uuid = _resolve_machine_uuid(db, machine_id)

    db.table("pending_commands").update({
        "status": "success" if body.success else "failed",
        "output": body.output,
        "success": body.success,
        "completed_at": datetime.utcnow().isoformat(),
    }).eq("id", fix_id).eq("machine_id", machine_uuid).execute()

    db.table("fix_history").update({
        "success": body.success,
        "output": body.output,
    }).eq("machine_id", machine_uuid).execute()

    return {"ok": True}


@router.get("/machines/{machine_id}/fix/{fix_id}")
async def get_fix_status(machine_id: str, fix_id: str):
    db = get_client()
    machine_uuid = _resolve_machine_uuid(db, machine_id)

    cmd = (
        db.table("pending_commands")
        .select("id, status, output, success, created_at, completed_at, fix_code")
        .eq("id", fix_id)
        .eq("machine_id", machine_uuid)
        .execute()
    )

    if not cmd.data:
        raise HTTPException(status_code=404, detail="Fix command not found")

    return cmd.data[0]
