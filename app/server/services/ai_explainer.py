from __future__ import annotations
import os
from datetime import date
from anthropic import AsyncAnthropic

_client: AsyncAnthropic | None = None
_cache: dict[str, tuple[str, str]] = {}  # key → (explanation, date_str)

SYSTEM_PROMPT = """You are SysDoc, an AI system diagnostics expert. You analyze computer performance data and explain problems in plain language that non-technical users can understand.
Rules:
- Write in 2-4 short paragraphs maximum
- Start with the most impactful problem
- Use analogies when helpful (e.g. "like a car engine overheating")
- End with one clear recommended action
- Never use technical jargon without explaining it
- Speak directly to the user ("your computer", "you should")
- Language: match the OS locale (es for Spanish systems, en for English)"""


def _get_client() -> AsyncAnthropic:
    global _client
    if _client is None:
        _client = AsyncAnthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    return _client


def _cache_key(machine_id: str) -> str:
    return f"{machine_id}:{date.today().isoformat()}"


def _build_prompt(machine: dict, scan: dict, issues: list[dict]) -> str:
    issue_lines = "\n".join(
        f"- [{i.get('severity', '?')}] {i.get('issue_code', '?')}: {i.get('title', '')} — {i.get('description', '')[:120]}"
        for i in issues[:5]
    )
    return (
        f"Machine: {machine.get('hostname', 'unknown')} running {machine.get('os_name', 'unknown')} "
        f"on {machine.get('cpu_model', 'unknown')}\n"
        f"Health Score: {scan.get('health_score', 0)}/100 "
        f"(Performance: {scan.get('score_performance', 0)}, Storage: {scan.get('score_storage', 0)}, "
        f"Security: {scan.get('score_security', 0)}, Stability: {scan.get('score_stability', 0)})\n\n"
        f"Active issues detected:\n{issue_lines or '(none)'}\n\n"
        "Explain in plain language why this computer is slow and what the user should do."
    )


async def generate_explanation(
    machine: dict,
    scan: dict,
    issues: list[dict],
) -> tuple[str, bool]:
    machine_id = machine.get("machine_id") or machine.get("id", "unknown")
    key = _cache_key(machine_id)

    if key in _cache:
        explanation, _ = _cache[key]
        return explanation, True

    client = _get_client()
    user_prompt = _build_prompt(machine, scan, issues)

    response = await client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=300,
        temperature=0.3,
        system=[
            {
                "type": "text",
                "text": SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[{"role": "user", "content": user_prompt}],
    )

    explanation = response.content[0].text  # type: ignore
    _cache[key] = (explanation, date.today().isoformat())
    return explanation, False
