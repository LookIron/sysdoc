import time
import psutil

_process_baseline: dict[int, tuple[float, float]] = {}


def _top_processes(n: int = 10) -> list[dict]:
    procs = []
    for p in psutil.process_iter(["pid", "name", "memory_info", "memory_percent"]):
        try:
            mi = p.info["memory_info"]
            if mi is None:
                continue
            procs.append({
                "pid": p.info["pid"],
                "name": p.info["name"],
                "ram_mb": round(mi.rss / 1024**2, 1),
                "ram_pct": round(p.info["memory_percent"] or 0, 1),
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return sorted(procs, key=lambda x: x["ram_mb"], reverse=True)[:n]


def _leak_candidates() -> list[dict]:
    global _process_baseline
    now = time.time()
    candidates = []
    current: dict[int, tuple[float, float]] = {}

    for p in psutil.process_iter(["pid", "name", "memory_info", "create_time"]):
        try:
            mi = p.info["memory_info"]
            if mi is None:
                continue
            rss = mi.rss
            pid = p.info["pid"]
            current[pid] = (now, rss)
            if pid in _process_baseline:
                _, baseline_rss = _process_baseline[pid]
                if baseline_rss > 0 and rss / baseline_rss > 2.5:
                    candidates.append({
                        "pid": pid,
                        "name": p.info["name"],
                        "ram_mb_now": round(rss / 1024**2, 1),
                        "ram_mb_baseline": round(baseline_rss / 1024**2, 1),
                        "growth_pct": round((rss / baseline_rss - 1) * 100, 0),
                    })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    _process_baseline = current
    return candidates


def collect() -> dict:
    vm = psutil.virtual_memory()
    swap = psutil.swap_memory()
    return {
        "ram_total_gb": round(vm.total / 1024**3, 2),
        "ram_used_gb": round(vm.used / 1024**3, 2),
        "ram_available_gb": round(vm.available / 1024**3, 2),
        "ram_usage_pct": vm.percent,
        "swap_total_gb": round(swap.total / 1024**3, 2),
        "swap_used_gb": round(swap.used / 1024**3, 2),
        "swap_usage_pct": swap.percent,
        "top_processes": _top_processes(),
        "memory_leak_candidates": _leak_candidates(),
    }
