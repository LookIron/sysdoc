from __future__ import annotations
from typing import Any


def extract(machine_uuid: str, payload: dict) -> dict[str, Any]:
    cpu = payload.get("cpu", {})
    mem = payload.get("memory", {})
    disk = payload.get("disk", {})
    net = payload.get("network", {})

    partitions = disk.get("partitions") or []
    disk_usage = partitions[0].get("usage_pct") if partitions else None

    return {
        "machine_id": machine_uuid,
        "cpu_usage_pct": cpu.get("cpu_usage_pct"),
        "cpu_temp_c": cpu.get("cpu_temp_c"),
        "cpu_freq_mhz": cpu.get("cpu_freq_mhz"),
        "cpu_freq_max_mhz": cpu.get("cpu_freq_max_mhz"),
        "ram_usage_pct": mem.get("ram_usage_pct"),
        "ram_available_gb": mem.get("ram_available_gb"),
        "disk_read_mbps": disk.get("disk_read_mbps"),
        "disk_write_mbps": disk.get("disk_write_mbps"),
        "disk_usage_pct": disk_usage,
        "net_upload_mbps": net.get("net_upload_mbps"),
        "net_download_mbps": net.get("net_download_mbps"),
    }
