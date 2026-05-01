import os
import psutil

KNOWN_HOGS = frozenset({
    "wuauserv", "musnotification", "msmpeng", "mrt",
    "malwarebytes", "avast", "avg", "mcshield", "norton", "bitdefender",
    "ccsvchst", "AvastSvc", "avgnt",
})

TEMP_DIRS = ("/tmp", "/var/tmp", os.path.expandvars("%TEMP%"), os.path.expandvars("%TMP%"))


def _is_suspicious(proc_info: dict) -> bool:
    exe = proc_info.get("exe") or ""
    if not exe:
        return True
    for tmp in TEMP_DIRS:
        if exe.startswith(tmp):
            return True
    return False


def collect() -> dict:
    fields = ["pid", "name", "cpu_percent", "memory_info", "status", "create_time", "exe"]
    all_procs: list[dict] = []

    for p in psutil.process_iter(fields):
        try:
            info = p.info
            ram_mb = round(info["memory_info"].rss / 1024**2, 1) if info["memory_info"] else 0
            all_procs.append({
                "pid": info["pid"],
                "name": info["name"],
                "cpu_pct": info["cpu_percent"] or 0,
                "ram_mb": ram_mb,
                "status": info["status"],
                "create_time": info["create_time"],
                "exe": info["exe"],
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    top_cpu = sorted(all_procs, key=lambda x: x["cpu_pct"], reverse=True)[:10]
    top_ram = sorted(all_procs, key=lambda x: x["ram_mb"], reverse=True)[:10]
    suspicious = [p for p in all_procs if _is_suspicious(p)][:10]
    known_hogs = [p for p in all_procs if (p["name"] or "").lower() in KNOWN_HOGS]

    return {
        "total_processes": len(all_procs),
        "top_cpu": top_cpu,
        "top_ram": top_ram,
        "suspicious": suspicious,
        "known_hogs": known_hogs,
    }
