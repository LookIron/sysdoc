from unittest.mock import MagicMock, patch
import sys, types

# Stub wmi for non-Windows
wmi_stub = types.ModuleType("wmi")
sys.modules.setdefault("wmi", wmi_stub)

from collectors import cpu, memory, disk, network, processes, startup


class TestCpuCollector:
    def test_returns_expected_keys(self):
        result = cpu.collect()
        for key in ("cpu_usage_pct", "cpu_freq_mhz", "cpu_freq_max_mhz", "cpu_temp_c",
                     "cpu_cores_physical", "cpu_cores_logical", "cpu_model", "throttling_detected"):
            assert key in result

    def test_throttling_detected_when_freq_below_80_pct(self):
        freq_mock = MagicMock()
        freq_mock.current = 1000.0
        freq_mock.max = 3000.0
        with patch("collectors.cpu.psutil.cpu_freq", return_value=freq_mock):
            with patch("collectors.cpu.psutil.cpu_percent", return_value=50.0):
                result = cpu.collect()
        assert result["throttling_detected"] is True

    def test_no_throttling_at_full_speed(self):
        freq_mock = MagicMock()
        freq_mock.current = 3000.0
        freq_mock.max = 3200.0
        with patch("collectors.cpu.psutil.cpu_freq", return_value=freq_mock):
            with patch("collectors.cpu.psutil.cpu_percent", return_value=10.0):
                result = cpu.collect()
        assert result["throttling_detected"] is False

    def test_no_crash_when_freq_unavailable(self):
        with patch("collectors.cpu.psutil.cpu_freq", return_value=None):
            with patch("collectors.cpu.psutil.cpu_percent", return_value=0.0):
                result = cpu.collect()
        assert result["throttling_detected"] is False
        assert result["cpu_freq_mhz"] is None


class TestMemoryCollector:
    def test_returns_expected_keys(self):
        result = memory.collect()
        for key in ("ram_total_gb", "ram_used_gb", "ram_available_gb", "ram_usage_pct",
                     "swap_total_gb", "swap_used_gb", "swap_usage_pct",
                     "top_processes", "memory_leak_candidates"):
            assert key in result

    def test_top_processes_is_list(self):
        result = memory.collect()
        assert isinstance(result["top_processes"], list)
        assert len(result["top_processes"]) <= 10


class TestDiskCollector:
    def test_returns_expected_keys(self):
        result = disk.collect()
        for key in ("partitions", "disk_read_mbps", "disk_write_mbps", "smart_data", "trim_enabled"):
            assert key in result

    def test_partitions_is_list(self):
        result = disk.collect()
        assert isinstance(result["partitions"], list)

    def test_partition_has_expected_fields(self):
        result = disk.collect()
        if result["partitions"]:
            p = result["partitions"][0]
            for f in ("device", "mountpoint", "total_gb", "used_gb", "free_gb", "usage_pct"):
                assert f in p


class TestNetworkCollector:
    def test_returns_expected_keys(self):
        result = network.collect()
        for key in ("net_upload_mbps", "net_download_mbps", "cloud_sync_processes"):
            assert key in result

    def test_cloud_sync_is_list(self):
        result = network.collect()
        assert isinstance(result["cloud_sync_processes"], list)


class TestProcessesCollector:
    def test_returns_expected_keys(self):
        result = processes.collect()
        for key in ("total_processes", "top_cpu", "top_ram", "suspicious", "known_hogs"):
            assert key in result

    def test_top_lists_bounded(self):
        result = processes.collect()
        assert len(result["top_cpu"]) <= 10
        assert len(result["top_ram"]) <= 10

    def test_suspicious_detects_no_exe(self):
        proc_info = {"pid": 999, "name": "badproc", "cpu_pct": 0, "ram_mb": 0,
                     "status": "running", "create_time": 0, "exe": None}
        assert processes._is_suspicious(proc_info) is True

    def test_suspicious_detects_temp_path(self):
        proc_info = {"pid": 998, "name": "weird", "cpu_pct": 0, "ram_mb": 0,
                     "status": "running", "create_time": 0, "exe": "/tmp/malware"}
        assert processes._is_suspicious(proc_info) is True

    def test_normal_process_not_suspicious(self):
        proc_info = {"pid": 1, "name": "bash", "cpu_pct": 0, "ram_mb": 10,
                     "status": "running", "create_time": 0, "exe": "/bin/bash"}
        assert processes._is_suspicious(proc_info) is False


class TestStartupCollector:
    def test_returns_expected_keys(self):
        result = startup.collect()
        for key in ("items", "ghost_count", "suspicious_count"):
            assert key in result

    def test_ghost_detection(self):
        result = startup._categorize("myapp", "/nonexistent/path/to/app")
        assert result == "ghost"

    def test_essential_detection(self):
        result = startup._categorize("launchd", "/sbin/launchd")
        assert result == "essential"

    def test_ghost_count_matches_items(self):
        result = startup.collect()
        expected = sum(1 for i in result["items"] if i["category"] == "ghost")
        assert result["ghost_count"] == expected
