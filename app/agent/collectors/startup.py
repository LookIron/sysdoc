import os
import platform
import subprocess
from pathlib import Path

ESSENTIAL_NAMES = frozenset({
    "securityd", "launchd", "systemd", "winlogon", "csrss",
    "lsass", "services", "smss", "wininit",
})

SUSPICIOUS_NAMES = frozenset({
    "cryptominer", "xmrig", "monero",
})


def _categorize(name: str, path: str | None) -> str:
    low = name.lower()
    if low in ESSENTIAL_NAMES:
        return "essential"
    if low in SUSPICIOUS_NAMES:
        return "suspicious"
    if path and not Path(path).exists():
        return "ghost"
    return "unknown"


def _darwin_items() -> list[dict]:
    items = []
    dirs = [
        Path.home() / "Library/LaunchAgents",
        Path("/Library/LaunchAgents"),
        Path("/Library/LaunchDaemons"),
    ]
    for d in dirs:
        if not d.exists():
            continue
        for plist in d.glob("*.plist"):
            try:
                result = subprocess.run(
                    ["plutil", "-convert", "json", "-o", "-", str(plist)],
                    capture_output=True, text=True, timeout=3
                )
                if result.returncode != 0:
                    continue
                import json
                data = json.loads(result.stdout)
                prog_args = data.get("ProgramArguments", [])
                path = data.get("Program") or (prog_args[0] if prog_args else None)
                name = plist.stem
                items.append({
                    "name": name,
                    "path": path,
                    "enabled": not data.get("Disabled", False),
                    "source": str(d),
                    "category": _categorize(name, path),
                })
            except Exception:
                pass
    return items


def _windows_items() -> list[dict]:
    items = []
    try:
        import winreg  # type: ignore
        keys = [
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run"),
            (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run"),
        ]
        for hive, subkey in keys:
            try:
                key = winreg.OpenKey(hive, subkey)
                i = 0
                while True:
                    try:
                        name, value, _ = winreg.EnumValue(key, i)
                        items.append({
                            "name": name,
                            "path": value.split('"')[1] if '"' in value else value.split()[0],
                            "enabled": True,
                            "source": subkey,
                            "category": _categorize(name, value),
                        })
                        i += 1
                    except OSError:
                        break
            except Exception:
                pass
    except ImportError:
        pass

    startup_folder = Path(os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"))
    if startup_folder.exists():
        for f in startup_folder.iterdir():
            items.append({
                "name": f.stem,
                "path": str(f),
                "enabled": True,
                "source": "startup_folder",
                "category": _categorize(f.stem, str(f)),
            })
    return items


def _linux_items() -> list[dict]:
    items = []
    autostart = Path.home() / ".config/autostart"
    if autostart.exists():
        for desktop in autostart.glob("*.desktop"):
            try:
                text = desktop.read_text(errors="ignore")
                name = desktop.stem
                exec_line = next((l for l in text.splitlines() if l.startswith("Exec=")), "")
                path = exec_line.replace("Exec=", "").split()[0] if exec_line else None
                hidden = "Hidden=true" in text
                items.append({
                    "name": name,
                    "path": path,
                    "enabled": not hidden,
                    "source": str(autostart),
                    "category": _categorize(name, path),
                })
            except Exception:
                pass
    return items


def collect() -> dict:
    sys = platform.system()
    if sys == "Darwin":
        items = _darwin_items()
    elif sys == "Windows":
        items = _windows_items()
    else:
        items = _linux_items()

    return {
        "items": items,
        "ghost_count": sum(1 for i in items if i["category"] == "ghost"),
        "suspicious_count": sum(1 for i in items if i["category"] == "suspicious"),
    }
