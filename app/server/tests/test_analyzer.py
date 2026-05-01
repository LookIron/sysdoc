import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.analyzer import (
    detect_p01, detect_p02, detect_p03, detect_p04,
    detect_p05, detect_p07, detect_p08, detect_p09, detect_p10, analyze,
)


def _payload(**kwargs) -> dict:
    base = {
        "cpu": {}, "memory": {}, "disk": {}, "network": {},
        "processes": {}, "startup": {},
    }
    for k, v in kwargs.items():
        base[k] = v
    return base


class TestP01:
    def test_detects_throttling_with_high_temp(self):
        p = _payload(cpu={"throttling_detected": True, "cpu_temp_c": 91, "cpu_freq_mhz": 1000, "cpu_freq_max_mhz": 3000})
        assert len(detect_p01(p)) == 1
        assert detect_p01(p)[0].code == "P01"

    def test_no_issue_without_throttling(self):
        p = _payload(cpu={"throttling_detected": False, "cpu_temp_c": 60})
        assert detect_p01(p) == []

    def test_no_issue_throttling_but_low_temp(self):
        p = _payload(cpu={"throttling_detected": True, "cpu_temp_c": 70})
        assert detect_p01(p) == []


class TestP02:
    def test_detects_pending_sectors(self):
        p = _payload(disk={"smart_data": {"pending_sectors": 3, "reallocated_sectors": 0}})
        assert len(detect_p02(p)) == 1

    def test_detects_reallocated_sectors(self):
        p = _payload(disk={"smart_data": {"pending_sectors": 0, "reallocated_sectors": 10}})
        assert len(detect_p02(p)) == 1

    def test_no_issue_on_clean_disk(self):
        p = _payload(disk={"smart_data": {"pending_sectors": 0, "reallocated_sectors": 0}})
        assert detect_p02(p) == []

    def test_no_crash_without_smart(self):
        p = _payload(disk={})
        assert detect_p02(p) == []


class TestP03:
    def test_detects_memory_leak(self):
        p = _payload(memory={"memory_leak_candidates": [
            {"name": "chrome", "ram_mb_now": 2000, "ram_mb_baseline": 100, "growth_pct": 1900}
        ]})
        issues = detect_p03(p)
        assert len(issues) == 1
        assert issues[0].code == "P03"
        assert issues[0].fix_available is True

    def test_no_issue_without_leaks(self):
        p = _payload(memory={"memory_leak_candidates": []})
        assert detect_p03(p) == []


class TestP04:
    def test_detects_ghost_startup(self):
        p = _payload(startup={"items": [{"name": "OldApp", "path": "/missing/app", "category": "ghost"}]})
        issues = detect_p04(p)
        assert len(issues) == 1
        assert issues[0].code == "P04"
        assert issues[0].fix_available is True

    def test_no_issue_without_ghosts(self):
        p = _payload(startup={"items": [{"name": "Good", "path": "/usr/bin/good", "category": "useful"}]})
        assert detect_p04(p) == []


class TestP05:
    def test_detects_full_disk(self):
        p = _payload(disk={"partitions": [{"mountpoint": "/", "usage_pct": 95, "free_gb": 1.0}]})
        issues = detect_p05(p)
        assert len(issues) == 1
        assert issues[0].code == "P05"

    def test_no_issue_on_healthy_disk(self):
        p = _payload(disk={"partitions": [{"mountpoint": "/", "usage_pct": 60, "free_gb": 100.0}]})
        assert detect_p05(p) == []


class TestP07:
    def test_detects_cloud_sync(self):
        p = _payload(network={"cloud_sync_processes": [{"name": "OneDrive", "read_mb": 500, "write_mb": 200}]})
        issues = detect_p07(p)
        assert len(issues) == 1
        assert issues[0].code == "P07"

    def test_no_issue_without_cloud_sync(self):
        p = _payload(network={"cloud_sync_processes": []})
        assert detect_p07(p) == []


class TestP08:
    def test_detects_windows_update(self):
        p = _payload(processes={"top_cpu": [{"name": "TiWorker", "cpu_pct": 45}]})
        issues = detect_p08(p)
        assert len(issues) == 1
        assert issues[0].code == "P08"

    def test_no_issue_low_cpu(self):
        p = _payload(processes={"top_cpu": [{"name": "TiWorker", "cpu_pct": 5}]})
        assert detect_p08(p) == []


class TestP09:
    def test_detects_antivirus(self):
        p = _payload(processes={"top_cpu": [{"name": "MsMpEng", "cpu_pct": 40}]})
        issues = detect_p09(p)
        assert len(issues) == 1
        assert issues[0].code == "P09"

    def test_no_issue_low_av_cpu(self):
        p = _payload(processes={"top_cpu": [{"name": "MsMpEng", "cpu_pct": 5}]})
        assert detect_p09(p) == []


class TestP10:
    def test_detects_trim_disabled(self):
        p = _payload(disk={"trim_enabled": False})
        issues = detect_p10(p)
        assert len(issues) == 1
        assert issues[0].code == "P10"
        assert issues[0].fix_available is True

    def test_no_issue_trim_enabled(self):
        p = _payload(disk={"trim_enabled": True})
        assert detect_p10(p) == []

    def test_no_issue_trim_unknown(self):
        p = _payload(disk={"trim_enabled": None})
        assert detect_p10(p) == []


class TestAnalyzePipeline:
    def test_returns_multiple_issues(self):
        p = _payload(
            cpu={"throttling_detected": True, "cpu_temp_c": 95},
            disk={"smart_data": {"pending_sectors": 5, "reallocated_sectors": 0},
                  "trim_enabled": False, "partitions": []},
            startup={"items": [{"name": "Ghost", "category": "ghost"}]},
        )
        issues = analyze(p)
        codes = {i.code for i in issues}
        assert "P02" in codes
        assert "P04" in codes
        assert "P10" in codes

    def test_clean_system_returns_no_issues(self):
        p = _payload(
            cpu={"throttling_detected": False, "cpu_temp_c": 45},
            disk={"smart_data": {"pending_sectors": 0, "reallocated_sectors": 0},
                  "trim_enabled": True, "partitions": [{"usage_pct": 50, "free_gb": 200}]},
            memory={"memory_leak_candidates": []},
            network={"cloud_sync_processes": []},
            startup={"items": []},
            processes={"top_cpu": []},
        )
        assert analyze(p) == []
