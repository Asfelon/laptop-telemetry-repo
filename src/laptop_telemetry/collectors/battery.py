"""
Battery telemetry collector.
"""

from typing import Any, Optional

import psutil

from .base import BaseCollector


class BatteryCollector(BaseCollector):
    """
    Collector for battery telemetry data.

    Collects battery capacity, status, health, and information.
    """

    def __init__(self, name: str, config: Optional[dict[str, Any]] = None) -> None:
        super().__init__(name, config)

    def is_enabled(self, config: Optional[dict[str, Any]] = None) -> bool:
        """Check if battery collector is enabled."""
        cfg = config or self.config or {}
        enabled: bool = cfg.get("enabled", True)
        return enabled

    def collect(self) -> dict[str, Any]:
        """
        Collect battery telemetry data.

        Returns:
            dict[str, Any]: Battery telemetry data
        """
        try:
            data: dict[str, Any] = {}

            # Get battery info via psutil
            battery = psutil.sensors_battery()

            if battery is None:
                data["present"] = False
                return data

            data["present"] = True
            data["charge_percent"] = battery.percent
            data["status"] = "charging" if battery.power_plugged else "discharging"

            # Time remaining
            if (
                battery.secsleft != psutil.POWER_TIME_UNLIMITED
                and battery.secsleft != psutil.POWER_TIME_UNKNOWN
            ):
                data["time_remaining_minutes"] = battery.secsleft // 60
            else:
                data["time_remaining_minutes"] = None

            # Additional info would come from WMI Win32_Battery
            # For now, use placeholders
            data["capacity_full_mwh"] = None
            data["capacity_design_mwh"] = None
            data["capacity_remaining_mwh"] = None
            data["voltage_v"] = None
            data["current_ma"] = None
            data["cycle_count"] = None
            data["temperature_celsius"] = None
            data["manufacturer"] = None
            data["model"] = None
            data["serial"] = None
            data["chemistry"] = None

            return data

        except Exception as e:
            self.handle_error(e)
            return {"present": False}
