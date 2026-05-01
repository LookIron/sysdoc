import platform
import subprocess
import time
import psutil

_prev_io: tuple[float, float, float] | None = None


def _io_mbps() -> tuple[float, float]:
    global _prev_io
    try:
        counters = psutil.disk_io_counters()
        now = time.time()
        if _prev_io and counters:
            prev_time, prev_read, prev_write = _prev_io
            elapsed = now - prev_time
            read_mbps = round((counters.read_bytes - prev_read) / 1024**2 / elapsed, 2)
            write_mbps = round((counters.write_bytes - prev_write) / 1024**2 / elapsed, 2)
            _prev_io = (now, counters.read_bytes, counters.write_bytes)
            return max(0.0, read_mbps), max(0.0, write_mbps)
        if counters:
            _prev_io = (now, counters.read_bytes, counters.write_bytes)
    except Exception:
        pass
    return 0.0, 0.0


def _smart_data(device: str) -> dict | None:
    try:
        result = subprocess.run(
            ["smartctl", "-A", "-j", device],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode not in (0, 4):
            return None
        import json
        data = json.loads(result.stdout)
        attrs = {a["id"]: a for a in data.get("ata_smart_attributes", {}).get("table", [])}
        pending = attrs.get(197, {}).get("raw", {}).get("value", 0)
        reallocated = attrs.get(5, {}).get("raw", {}).get("value", 0)
        return {
            "pending_sectors": pending,
            "reallocated_sectors": reallocated,
            "health_status": data.get("smart_status", {}).get("passed", None),
        }
    except Exception:
        return None


def _trim_enabled(mountpoint: str) -> bool | None:
    try:
        if platform.system() == "Windows":
            r = subprocess.run(
                ["fsutil", "behavior", "query", "DisableDeleteNotify"],
                capture_output=True, text=True, timeout=5
            )
            return "0" in r.stdout
        if platform.system() == "Darwin":
            r = subprocess.run(["trimforce"], capture_output=True, text=True, timeout=3)
            return r.returncode == 0
    except Exception:
        pass
    return None


def collect() -> dict:
    partitions = []
    for part in psutil.disk_partitions(all=False):
        try:
            usage = psutil.disk_usage(part.mountpoint)
            partitions.append({
                "device": part.device,
                "mountpoint": part.mountpoint,
                "fstype": part.fstype,
                "total_gb": round(usage.total / 1024**3, 2),
                "used_gb": round(usage.used / 1024**3, 2),
                "free_gb": round(usage.free / 1024**3, 2),
                "usage_pct": usage.percent,
            })
        except (PermissionError, OSError):
            pass

    read_mbps, write_mbps = _io_mbps()

    main_device = partitions[0]["device"] if partitions else None
    smart = _smart_data(main_device) if main_device else None

    return {
        "partitions": partitions,
        "disk_read_mbps": read_mbps,
        "disk_write_mbps": write_mbps,
        "smart_data": smart,
        "trim_enabled": _trim_enabled(partitions[0]["mountpoint"]) if partitions else None,
    }
