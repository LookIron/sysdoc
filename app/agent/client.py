import httpx
from dotenv import load_dotenv
import os

load_dotenv()

BASE_URL = os.getenv("SYSDOC_SERVER_URL", "http://localhost:8000")


class AgentClient:
    def __init__(self, machine_id: str):
        self._machine_id = machine_id
        self._http = httpx.Client(base_url=BASE_URL, timeout=10)

    def register(self, info: dict) -> dict:
        r = self._http.post("/api/v1/machines/register", json=info)
        r.raise_for_status()
        return r.json()

    def send_scan(self, payload: dict) -> dict:
        r = self._http.post(f"/api/v1/machines/{self._machine_id}/scan", json=payload)
        r.raise_for_status()
        return r.json()

    def get_pending_commands(self) -> list[dict]:
        r = self._http.get(f"/api/v1/machines/{self._machine_id}/pending_commands")
        r.raise_for_status()
        return r.json().get("commands", [])

    def report_fix_result(self, fix_id: str, success: bool, output: str) -> None:
        self._http.post(
            f"/api/v1/machines/{self._machine_id}/fix/{fix_id}/result",
            json={"success": success, "output": output},
        )

    def close(self) -> None:
        self._http.close()
