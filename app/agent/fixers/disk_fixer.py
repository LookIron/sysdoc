import os
import platform
import subprocess
import time
from pathlib import Path

MAX_TEMP_AGE_DAYS = 7


def enable_trim() -> tuple[bool, str]:
    sys = platform.system()
    try:
        if sys == "Windows":
            r = subprocess.run(
                ["fsutil", "behavior", "set", "DisableDeleteNotify", "0"],
                capture_output=True, text=True, timeout=10
            )
            if r.returncode == 0:
                return True, "TRIM enabled via fsutil"
            return False, f"fsutil failed: {r.stderr}"

        elif sys == "Darwin":
            return False, "TRIM on macOS is managed by the OS. Enable from System Settings > General > Storage."

        else:  # Linux
            r = subprocess.run(
                ["systemctl", "enable", "--now", "fstrim.timer"],
                capture_output=True, text=True, timeout=10
            )
            if r.returncode == 0:
                return True, "TRIM timer enabled via systemctl"
            return False, f"systemctl failed: {r.stderr}"

    except Exception as e:
        return False, f"Error enabling TRIM: {e}"


def clear_temp_files() -> tuple[bool, str]:
    sys = platform.system()
    deleted = 0
    errors = 0
    cutoff = time.time() - MAX_TEMP_AGE_DAYS * 86400

    if sys == "Windows":
        dirs = [
            Path(os.path.expandvars("%TEMP%")),
            Path(os.path.expandvars("%TMP%")),
        ]
    elif sys == "Darwin":
        dirs = [Path.home() / "Library/Caches"]
    else:
        dirs = [Path("/tmp")]

    for temp_dir in dirs:
        if not temp_dir.exists():
            continue
        for f in temp_dir.rglob("*"):
            try:
                if f.is_file() and f.stat().st_mtime < cutoff:
                    f.unlink()
                    deleted += 1
            except Exception:
                errors += 1

    return True, f"Cleared {deleted} temp files ({errors} skipped)"


def fix(params: dict) -> tuple[bool, str]:
    action = params.get("action", "")
    if action == "trim":
        return enable_trim()
    if action == "clear_temp":
        return clear_temp_files()
    return False, f"Unknown disk fix action: {action}"
