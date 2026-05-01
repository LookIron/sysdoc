from __future__ import annotations
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from db.supabase import get_client

router = APIRouter(prefix="/api/v1")


class MachineRegisterBody(BaseModel):
    machine_id: str
    hostname: str | None = None
    os_name: str | None = None
    os_arch: str | None = None
    cpu_model: str | None = None
    cpu_cores: int | None = None
    ram_total_gb: float | None = None


@router.post("/machines/register")
async def register_machine(body: MachineRegisterBody):
    db = get_client()

    existing = (
        db.table("machines")
        .select("id, machine_id")
        .eq("machine_id", body.machine_id)
        .execute()
    )

    if existing.data:
        row = existing.data[0]
        db.table("machines").update({"last_seen": "now()"}).eq("machine_id", body.machine_id).execute()
        return {"id": row["id"], "machine_id": row["machine_id"], "created": False}

    result = (
        db.table("machines")
        .insert({
            "machine_id": body.machine_id,
            "hostname": body.hostname,
            "os_name": body.os_name,
            "os_arch": body.os_arch,
            "cpu_model": body.cpu_model,
            "cpu_cores": body.cpu_cores,
            "ram_total_gb": body.ram_total_gb,
        })
        .execute()
    )

    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to register machine")

    row = result.data[0]
    return {"id": row["id"], "machine_id": row["machine_id"], "created": True}
