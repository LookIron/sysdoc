import platform
import psutil


def _cpu_temp() -> float | None:
    try:
        if platform.system() == "Windows":
            import wmi  # type: ignore
            w = wmi.WMI(namespace="root\\wmi")
            temps = w.MSAcpi_ThermalZoneTemperature()
            if temps:
                return round((temps[0].CurrentTemperature / 10.0) - 273.15, 1)
        else:
            sensors = psutil.sensors_temperatures()
            for key in ("coretemp", "cpu_thermal", "k10temp", "acpitz"):
                entries = sensors.get(key, [])
                if entries:
                    return round(entries[0].current, 1)
    except Exception:
        pass
    return None


def _cpu_model() -> str:
    try:
        if platform.system() == "Windows":
            import wmi  # type: ignore
            w = wmi.WMI()
            return w.Win32_Processor()[0].Name.strip()
        return platform.processor() or "Unknown"
    except Exception:
        return platform.processor() or "Unknown"


def collect() -> dict:
    try:
        freq = psutil.cpu_freq()
        freq_mhz = round(freq.current, 1) if freq else None
        freq_max = round(freq.max, 1) if freq else None
        throttling = bool(freq_mhz and freq_max and freq_mhz / freq_max < 0.80)
    except Exception:
        freq_mhz = freq_max = None
        throttling = False

    return {
        "cpu_usage_pct": psutil.cpu_percent(interval=0.5),
        "cpu_freq_mhz": freq_mhz,
        "cpu_freq_max_mhz": freq_max,
        "cpu_temp_c": _cpu_temp(),
        "cpu_cores_physical": psutil.cpu_count(logical=False),
        "cpu_cores_logical": psutil.cpu_count(logical=True),
        "cpu_model": _cpu_model(),
        "throttling_detected": throttling,
    }
