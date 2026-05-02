import psutil

PROTECTED_PIDS = frozenset(range(100))
PROTECTED_NAMES = frozenset({
    "launchd", "systemd", "kernel", "kernel_task", "winlogon",
    "csrss", "lsass", "services", "smss", "wininit", "svchost",
    "init", "kthreadd",
})


def kill_process(pid: int, name: str) -> tuple[bool, str]:
    if pid in PROTECTED_PIDS:
        return False, f"Cannot kill protected PID {pid}"

    if name.lower() in PROTECTED_NAMES:
        return False, f"Cannot kill protected process: {name}"

    try:
        proc = psutil.Process(pid)
        actual_name = proc.name()

        if actual_name.lower() != name.lower():
            return False, f"Process name mismatch: expected {name}, found {actual_name}"

        proc.terminate()
        try:
            proc.wait(timeout=5)
        except psutil.TimeoutExpired:
            proc.kill()

        return True, f"Terminated process {name} (PID {pid})"

    except psutil.NoSuchProcess:
        return False, f"Process {name} (PID {pid}) no longer exists"
    except psutil.AccessDenied:
        return False, f"Access denied when terminating {name} (PID {pid})"
    except Exception as e:
        return False, f"Error killing process: {e}"


def fix(params: dict) -> tuple[bool, str]:
    pid = params.get("pid")
    name = params.get("name", "")
    if pid is None or not name:
        return False, "pid and name are required"
    return kill_process(int(pid), name)
