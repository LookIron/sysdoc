from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any


@dataclass
class MachineRegisterRequest:
    machine_id: str
    hostname: str | None = None
    os_name: str | None = None
    os_arch: str | None = None
    cpu_model: str | None = None
    cpu_cores: int | None = None
    ram_total_gb: float | None = None


@dataclass
class MachineRegisterResponse:
    id: str
    machine_id: str
    created: bool


@dataclass
class ScanResponse:
    scan_id: str
    health_score: int
    issues_detected: int


@dataclass
class Issue:
    code: str
    severity: str
    title: str
    description: str
    fix_available: bool = False
    fix_command: str | None = None


@dataclass
class ScoreResult:
    health_score: int
    score_performance: int
    score_storage: int
    score_security: int
    score_stability: int


@dataclass
class ScanPayload:
    machine_id: str
    collected_at: str | None = None
    cpu: dict[str, Any] = field(default_factory=dict)
    memory: dict[str, Any] = field(default_factory=dict)
    disk: dict[str, Any] = field(default_factory=dict)
    network: dict[str, Any] = field(default_factory=dict)
    processes: dict[str, Any] = field(default_factory=dict)
    startup: dict[str, Any] = field(default_factory=dict)
