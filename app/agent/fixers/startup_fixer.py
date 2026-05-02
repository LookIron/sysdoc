import platform
import subprocess
from pathlib import Path


def _safe_name(name: str) -> str:
    return name.replace("..", "").replace("/", "").replace("\\", "").strip()


def disable_startup_item(name: str, source: str) -> tuple[bool, str]:
    name = _safe_name(name)
    sys = platform.system()

    try:
        if sys == "Darwin":
            dirs = [
                Path.home() / "Library/LaunchAgents",
                Path("/Library/LaunchAgents"),
                Path("/Library/LaunchDaemons"),
            ]
            for d in dirs:
                plist = d / f"{name}.plist"
                if plist.exists():
                    r = subprocess.run(
                        ["launchctl", "unload", str(plist)],
                        capture_output=True, text=True, timeout=10
                    )
                    if r.returncode == 0:
                        return True, f"Disabled {name} via launchctl"
                    return False, f"launchctl unload failed: {r.stderr}"
            return False, f"Plist not found for {name}"

        elif sys == "Windows":
            import winreg  # type: ignore
            for hive, subkey in [
                (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run"),
                (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run"),
            ]:
                try:
                    key = winreg.OpenKey(hive, subkey, 0, winreg.KEY_SET_VALUE | winreg.KEY_READ)
                    winreg.DeleteValue(key, name)
                    return True, f"Removed {name} from registry Run key"
                except FileNotFoundError:
                    continue
                except Exception as e:
                    return False, f"Registry error: {e}"
            return False, f"Registry key {name} not found"

        else:  # Linux
            autostart = Path.home() / ".config/autostart" / f"{name}.desktop"
            if autostart.exists():
                content = autostart.read_text(errors="ignore")
                if "Hidden=true" not in content:
                    autostart.write_text(content + "\nHidden=true")
                return True, f"Disabled {name} in autostart"
            return False, f"Desktop file not found: {autostart}"

    except Exception as e:
        return False, f"Error disabling startup item: {e}"


def remove_ghost_entry(name: str, source: str) -> tuple[bool, str]:
    return disable_startup_item(name, source)


def fix(params: dict) -> tuple[bool, str]:
    name = params.get("name", "")
    source = params.get("source", "")
    action = params.get("action", "disable")
    if not name:
        return False, "No startup item name provided"
    if action == "remove":
        return remove_ghost_entry(name, source)
    return disable_startup_item(name, source)
