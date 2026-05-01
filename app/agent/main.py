import argparse
import platform
import time
import uuid
from pathlib import Path

from dotenv import load_dotenv

from client import AgentClient
from collectors import cpu, memory, disk, network, processes, startup

load_dotenv()

MACHINE_ID_FILE = Path.home() / ".sysdoc" / "machine_id"
COLLECT_INTERVAL = 30
FIX_POLL_INTERVAL = 5


def load_or_create_machine_id() -> str:
    MACHINE_ID_FILE.parent.mkdir(parents=True, exist_ok=True)
    if MACHINE_ID_FILE.exists():
        return MACHINE_ID_FILE.read_text().strip()
    machine_id = str(uuid.uuid4())
    MACHINE_ID_FILE.write_text(machine_id)
    return machine_id


def collect_all() -> dict:
    return {
        "cpu": cpu.collect(),
        "memory": memory.collect(),
        "disk": disk.collect(),
        "network": network.collect(),
        "processes": processes.collect(),
        "startup": startup.collect(),
    }


def machine_info(machine_id: str) -> dict:
    import psutil
    return {
        "machine_id": machine_id,
        "hostname": platform.node(),
        "os_name": platform.system(),
        "os_arch": platform.machine(),
        "cpu_model": platform.processor(),
        "cpu_cores": psutil.cpu_count(logical=True),
        "ram_total_gb": round(psutil.virtual_memory().total / 1024**3, 2),
    }


def run(debug: bool = False) -> None:
    machine_id = load_or_create_machine_id()
    client = AgentClient(machine_id)

    if debug:
        print(f"[agent] machine_id={machine_id}")

    try:
        info = machine_info(machine_id)
        client.register(info)
        if debug:
            print(f"[agent] registered: {info['hostname']}")
    except Exception as e:
        if debug:
            print(f"[agent] registration failed (will retry): {e}")

    last_collect = 0.0
    last_fix_poll = 0.0

    while True:
        now = time.time()

        if now - last_collect >= COLLECT_INTERVAL:
            try:
                payload = collect_all()
                result = client.send_scan(payload)
                if debug:
                    print(f"[agent] scan sent → health_score={result.get('health_score')}")
            except Exception as e:
                if debug:
                    print(f"[agent] scan error: {e}")
            last_collect = now

        if now - last_fix_poll >= FIX_POLL_INTERVAL:
            try:
                cmds = client.get_pending_commands()
                for cmd in cmds:
                    if debug:
                        print(f"[agent] fix command: {cmd}")
            except Exception as e:
                if debug:
                    print(f"[agent] fix poll error: {e}")
            last_fix_poll = now

        time.sleep(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SysDoc agent daemon")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    args = parser.parse_args()
    run(debug=args.debug)
