"""
CPU telemetry collector.
"""

from typing import Any, Optional

import psutil
from loguru import logger

from .base import BaseCollector


class CPUCollector(BaseCollector):
    """
    Collector for CPU telemetry data.

    Collects CPU usage, frequency, temperature, power, cache info,
    and system counters.
    """

    def __init__(self, name: str, config: Optional[dict[str, Any]] = None) -> None:
        super().__init__(name, config)
        self._last_cpu_times: Any = None
        self._last_per_cpu_times: Any = None

        # Cache static CPU info
        self._cores_physical = psutil.cpu_count(logical=False)
        self._cores_logical = psutil.cpu_count(logical=True)
        self._cpu_freq_min = 0
        self._cpu_freq_max = 0
        self._has_cpu_freq = hasattr(psutil, "cpu_freq")
        if self._has_cpu_freq:
            try:
                freq = psutil.cpu_freq()
                if freq:
                    self._cpu_freq_min = freq.min if freq.min else 0
                    self._cpu_freq_max = freq.max if freq.max else 0
            except (AttributeError, NotImplementedError):
                self._has_cpu_freq = False

        # Prime CPU percent (first call returns 0.0)
        psutil.cpu_percent(interval=None)
        psutil.cpu_percent(interval=None, percpu=True)

    def is_enabled(self, config: Optional[dict[str, Any]] = None) -> bool:
        """Check if CPU collector is enabled."""
        cfg = config or self.config or {}
        enabled: bool = cfg.get("enabled", True)
        return enabled

    def collect(self) -> dict[str, Any]:
        """
        Collect CPU telemetry data.

        Returns:
            dict[str, Any]: CPU telemetry data
        """
        try:
            data: dict[str, Any] = {}

            # Overall CPU usage (non-blocking)
            cpu_percent = psutil.cpu_percent(interval=None)
            data["usage_percent"] = cpu_percent

            # Detailed CPU times breakdown
            cpu_times = psutil.cpu_times()
            if cpu_times:
                data["usage_user_percent"] = self._calculate_percent(cpu_times.user, cpu_times)
                data["usage_system_percent"] = self._calculate_percent(cpu_times.system, cpu_times)
                data["usage_idle_percent"] = self._calculate_percent(cpu_times.idle, cpu_times)

                # Windows-specific: DPC, interrupt, privileged
                if hasattr(cpu_times, "dpc"):
                    data["usage_dpc_percent"] = self._calculate_percent(cpu_times.dpc, cpu_times)
                if hasattr(cpu_times, "interrupt"):
                    data["usage_interrupt_percent"] = self._calculate_percent(
                        cpu_times.interrupt, cpu_times
                    )
                if hasattr(cpu_times, "privileged"):
                    data["usage_privileged_percent"] = self._calculate_percent(
                        cpu_times.privileged, cpu_times
                    )

            # Per-core usage (non-blocking)
            if self.config.get("per_core", True):
                per_cpu_percent = psutil.cpu_percent(interval=None, percpu=True)
                per_cpu_times = psutil.cpu_times(percpu=True)

                data["usage_per_core"] = []
                for i, (percent, times) in enumerate(zip(per_cpu_percent, per_cpu_times)):
                    core_data = {
                        "core": i,
                        "total": percent,
                        "user": self._calculate_percent(times.user, times),
                        "system": self._calculate_percent(times.system, times),
                        "idle": self._calculate_percent(times.idle, times),
                    }

                    if hasattr(times, "dpc"):
                        core_data["dpc"] = self._calculate_percent(times.dpc, times)
                    if hasattr(times, "interrupt"):
                        core_data["interrupt"] = self._calculate_percent(times.interrupt, times)
                    if hasattr(times, "privileged"):
                        core_data["privileged"] = self._calculate_percent(times.privileged, times)

                    data["usage_per_core"].append(core_data)

            # CPU frequency
            if self._has_cpu_freq:
                try:
                    freq = psutil.cpu_freq()
                    if freq:
                        data["frequency_mhz"] = freq.current
                        data["frequency_min_mhz"] = self._cpu_freq_min
                        data["frequency_max_mhz"] = self._cpu_freq_max
                except (AttributeError, NotImplementedError):
                    pass

            # Per-core frequency
            if self._has_cpu_freq and self.config.get("per_core", True):
                try:
                    per_cpu_freq = psutil.cpu_freq(percpu=True)
                    if per_cpu_freq:
                        data["frequency_per_core_mhz"] = [f.current for f in per_cpu_freq]
                except (AttributeError, NotImplementedError):
                    pass

            # CPU temperature (if available via psutil)
            if self.config.get("include_temperature", True):
                temps = self._get_cpu_temperatures()
                if temps:
                    data["temperature_celsius"] = temps.get("package", 0)
                    data["temperature_per_core_celsius"] = temps.get("cores", [])

            # CPU power (if available)
            if self.config.get("include_power", True):
                power = self._get_cpu_power()
                if power:
                    data["power_watts"] = power.get("total", 0)
                    data["power_package_watts"] = power.get("package", 0)
                    data["power_cores_watts"] = power.get("cores", 0)
                    data["power_gpu_watts"] = power.get("gpu", 0)

            # System counters
            if self.config.get("include_system_counters", True):
                cpu_stats = psutil.cpu_stats()
                data["context_switches_sec"] = cpu_stats.ctx_switches
                data["interrupts_sec"] = cpu_stats.interrupts
                data["syscalls_sec"] = cpu_stats.syscalls

            # Process/thread counts (single iteration)
            try:
                procs = list(psutil.process_iter(["status", "num_threads"]))
                data["processes_total"] = len(procs)
                data["processes_running"] = sum(
                    1 for p in procs if p.info["status"] == psutil.STATUS_RUNNING
                )
                data["processes_sleeping"] = sum(
                    1 for p in procs if p.info["status"] == psutil.STATUS_SLEEPING
                )
                data["threads_total"] = sum(p.info["num_threads"] or 0 for p in procs)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                data["processes_total"] = len(psutil.pids())
                data["processes_running"] = 0
                data["processes_sleeping"] = 0
                data["threads_total"] = 0

            # CPU core counts (cached)
            data["cores_physical"] = self._cores_physical
            data["cores_logical"] = self._cores_logical

            # Cache hierarchy (Windows-specific via WMI)
            if self.config.get("include_cache", True):
                cache_info = self._get_cache_info()
                if cache_info:
                    data.update(cache_info)

            return data

        except Exception as e:
            logger.error(f"CPU collection error: {e}")
            return {}

    def _calculate_percent(self, value: float, times: Any) -> float:
        """Calculate percentage of a CPU time value.

        Args:
            value: The time value to calculate percentage for.
            times: The CPU times object containing all time values.

        Returns:
            The percentage as a float rounded to 1 decimal place.
        """
        attrs: list[str] = []
        for attr in dir(times):
            if attr.startswith("_"):
                continue
            try:
                attr_value = getattr(times, attr)
                if isinstance(attr_value, (int, float)):
                    attrs.append(attr)
            except Exception:
                continue

        total = 0.0
        for attr in attrs:
            try:
                total += getattr(times, attr)
            except Exception:
                continue

        if total > 0:
            result: float = round((value / total) * 100, 1)
            return result
        return 0.0

    def _get_cpu_temperatures(self) -> Optional[dict[str, Any]]:
        """Get CPU temperatures (placeholder for OpenHardwareMonitor integration).

        Returns:
            Dictionary with temperature data or None if not available.
        """
        # This would be implemented with OpenHardwareMonitorLib
        # For now, return None to indicate not available
        return None

    def _get_cpu_power(self) -> Optional[dict[str, Any]]:
        """Get CPU power consumption (placeholder for OpenHardwareMonitor integration).

        Returns:
            Dictionary with power data or None if not available.
        """
        # This would be implemented with OpenHardwareMonitorLib
        return None

    def _get_cache_info(self) -> Optional[dict[str, Any]]:
        """Get CPU cache hierarchy information.

        Returns:
            Dictionary with cache info or None if not available.
        """
        # This would be implemented with WMI Win32_CacheMemory
        # For now, return None
        return None
