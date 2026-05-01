import time
import psutil

_prev_net: tuple[float, float, float] | None = None

CLOUD_SYNC_NAMES = frozenset({
    "onedrive", "googledrivesync", "googledrive", "dropbox",
    "box", "mega", "icloud", "bird",  # bird = iCloud daemon on macOS
})


def _net_mbps() -> tuple[float, float]:
    global _prev_net
    try:
        counters = psutil.net_io_counters()
        now = time.time()
        if _prev_net and counters:
            prev_time, prev_sent, prev_recv = _prev_net
            elapsed = now - prev_time
            upload = round((counters.bytes_sent - prev_sent) / 1024**2 / elapsed, 3)
            download = round((counters.bytes_recv - prev_recv) / 1024**2 / elapsed, 3)
            _prev_net = (now, counters.bytes_sent, counters.bytes_recv)
            return max(0.0, upload), max(0.0, download)
        if counters:
            _prev_net = (now, counters.bytes_sent, counters.bytes_recv)
    except Exception:
        pass
    return 0.0, 0.0


def _cloud_sync_processes() -> list[dict]:
    found = []
    for p in psutil.process_iter(["pid", "name"]):
        try:
            name = (p.info["name"] or "").lower().replace(".exe", "")
            if name not in CLOUD_SYNC_NAMES:
                continue
            try:
                io = p.io_counters()
                read_mb = round(io.read_bytes / 1024**2, 1)
                write_mb = round(io.write_bytes / 1024**2, 1)
            except (psutil.AccessDenied, AttributeError):
                read_mb = write_mb = None
            found.append({
                "pid": p.info["pid"],
                "name": p.info["name"],
                "read_mb": read_mb,
                "write_mb": write_mb,
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return found


def collect() -> dict:
    upload_mbps, download_mbps = _net_mbps()
    return {
        "net_upload_mbps": upload_mbps,
        "net_download_mbps": download_mbps,
        "cloud_sync_processes": _cloud_sync_processes(),
    }
