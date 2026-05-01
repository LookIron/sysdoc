from __future__ import annotations
from models.schemas import Issue

KNOWN_AV = frozenset({
    "msmpeng", "mrt", "malwarebytes", "avast", "avgnt", "mcshield",
    "norton", "ccsvchst", "bitdefender", "AvastSvc",
})


def _get(data: dict, *keys: str, default=None):
    for k in keys:
        if not isinstance(data, dict):
            return default
        data = data.get(k, default)  # type: ignore
    return data


def detect_p01(payload: dict) -> list[Issue]:
    cpu = payload.get("cpu", {})
    freq = cpu.get("cpu_freq_mhz")
    freq_max = cpu.get("cpu_freq_max_mhz")
    temp = cpu.get("cpu_temp_c")
    throttling = cpu.get("throttling_detected", False)
    if throttling and temp and temp > 85:
        pct = round(freq / freq_max * 100) if freq and freq_max else 0
        return [Issue(
            code="P01", severity="high",
            title="CPU thermal throttling detected",
            description=(
                f"Your CPU is running at {pct}% of its max speed due to high temperature "
                f"({temp}°C). This can cause slowdowns across all applications. "
                "Like a car engine overheating, your CPU is slowing itself down to cool off. "
                "Consider cleaning dust from vents or replacing thermal paste."
            ),
            fix_available=False,
        )]
    return []


def detect_p02(payload: dict) -> list[Issue]:
    smart = _get(payload, "disk", "smart_data") or {}
    pending = smart.get("pending_sectors", 0) or 0
    reallocated = smart.get("reallocated_sectors", 0) or 0
    if pending > 0 or reallocated > 5:
        return [Issue(
            code="P02", severity="critical",
            title="Hard drive sector errors detected",
            description=(
                f"Your hard drive has {pending} pending and {reallocated} reallocated sectors. "
                "These are early signs of drive failure. Back up your data immediately. "
                "Think of it like cracks appearing in a road — they will get worse over time."
            ),
            fix_available=False,
        )]
    return []


def detect_p03(payload: dict) -> list[Issue]:
    candidates = _get(payload, "memory", "memory_leak_candidates") or []
    if candidates:
        worst = max(candidates, key=lambda x: x.get("growth_pct", 0))
        return [Issue(
            code="P03", severity="high",
            title=f"Memory leak detected in {worst.get('name', 'unknown')}",
            description=(
                f"{worst.get('name')} is using {worst.get('ram_mb_now')} MB of RAM, "
                f"up {worst.get('growth_pct')}% since it started. "
                "This process is hoarding memory without releasing it, slowing your entire system."
            ),
            fix_available=True,
            fix_command="FIX_P03_RESTART",
        )]
    return []


def detect_p04(payload: dict) -> list[Issue]:
    items = _get(payload, "startup", "items") or []
    ghosts = [i for i in items if i.get("category") == "ghost"]
    if ghosts:
        names = ", ".join(g.get("name", "?") for g in ghosts[:3])
        return [Issue(
            code="P04", severity="medium",
            title=f"Ghost startup entries found ({len(ghosts)})",
            description=(
                f"Programs removed from your system are still listed as startup items: {names}. "
                "These cause errors at boot and slow down startup. Safe to remove."
            ),
            fix_available=True,
            fix_command="FIX_P04_GHOST",
        )]
    return []


def detect_p05(payload: dict) -> list[Issue]:
    partitions = _get(payload, "disk", "partitions") or []
    for part in partitions:
        usage = part.get("usage_pct", 0)
        if usage > 90:
            return [Issue(
                code="P05", severity="high",
                title=f"Disk almost full ({usage:.0f}%)",
                description=(
                    f"Your disk at {part.get('mountpoint')} is {usage:.0f}% full "
                    f"({part.get('free_gb', 0):.1f} GB free). "
                    "A full disk causes crashes, failed updates, and slowdowns. "
                    "Delete large files or move them to external storage."
                ),
                fix_available=False,
            )]
    smart = _get(payload, "disk", "smart_data") or {}
    if not smart.get("health_status", True):
        return [Issue(
            code="P05", severity="critical",
            title="SSD health check failed",
            description="Your SSD's SMART health check has failed. Replace the drive soon to avoid data loss.",
            fix_available=False,
        )]
    return []


def detect_p07(payload: dict) -> list[Issue]:
    cloud = _get(payload, "network", "cloud_sync_processes") or []
    if cloud:
        names = ", ".join(p.get("name", "?") for p in cloud)
        return [Issue(
            code="P07", severity="medium",
            title=f"Cloud sync consuming resources ({names})",
            description=(
                f"{names} is actively syncing files. This can consume significant CPU, "
                "disk I/O, and bandwidth, slowing your system while it runs."
            ),
            fix_available=False,
        )]
    return []


def detect_p08(payload: dict) -> list[Issue]:
    top_cpu = _get(payload, "processes", "top_cpu") or []
    wu_names = {"wuauserv", "tiworker", "tiworker.exe", "wuauclt"}
    for proc in top_cpu:
        if proc.get("name", "").lower() in wu_names and proc.get("cpu_pct", 0) > 20:
            return [Issue(
                code="P08", severity="medium",
                title="Windows Update running in background",
                description=(
                    f"Windows Update ({proc['name']}) is using {proc['cpu_pct']:.0f}% CPU. "
                    "This is normal but temporary. Your system will be faster once it completes."
                ),
                fix_available=False,
            )]
    return []


def detect_p09(payload: dict) -> list[Issue]:
    top_cpu = _get(payload, "processes", "top_cpu") or []
    for proc in top_cpu:
        if proc.get("name", "").lower() in KNOWN_AV and proc.get("cpu_pct", 0) > 30:
            return [Issue(
                code="P09", severity="low",
                title="Antivirus scan running silently",
                description=(
                    f"{proc['name']} is using {proc['cpu_pct']:.0f}% CPU. "
                    "Your antivirus is running a background scan. Performance will return to normal once complete."
                ),
                fix_available=False,
            )]
    return []


def detect_p10(payload: dict) -> list[Issue]:
    trim = _get(payload, "disk", "trim_enabled")
    if trim is False:
        return [Issue(
            code="P10", severity="medium",
            title="TRIM disabled on SSD",
            description=(
                "TRIM is disabled on your SSD. Without TRIM, your SSD cannot efficiently "
                "manage deleted files, leading to gradual performance degradation over time."
            ),
            fix_available=True,
            fix_command="FIX_P10_TRIM",
        )]
    return []


_DETECTORS = [
    detect_p01, detect_p02, detect_p03, detect_p04,
    detect_p05, detect_p07, detect_p08, detect_p09, detect_p10,
]


def analyze(payload: dict) -> list[Issue]:
    issues: list[Issue] = []
    for detector in _DETECTORS:
        try:
            issues.extend(detector(payload))
        except Exception:
            pass
    return issues
