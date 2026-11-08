"""
Fan telemetry collector.
"""

from typing import Any, Optional

from .base import BaseCollector
from .ohm_manager import OHMManager


class FanCollector(BaseCollector):
    """
    Collector for fan telemetry data.

    Collects fan speed (RPM), duty cycle, and control mode
    for all available fans (CPU, GPU, chassis) via OpenHardwareMonitor.
    """

    REQUIRES_FULL_CONFIG = True

    def __init__(
        self,
        name: str,
        config: Optional[dict[str, Any]] = None,
        full_config: Optional[dict[str, Any]] = None,
    ) -> None:
        super().__init__(name, config, full_config)

    def is_enabled(self, config: Optional[dict[str, Any]] = None) -> bool:
        """Check if fan collector is enabled."""
        cfg = config or self.config or {}
        enabled: bool = cfg.get("enabled", True)
        return enabled

    def collect(self) -> dict[str, Any]:
        """
        Collect fan telemetry data.

        Returns:
            dict[str, Any]: Fan telemetry data
        """
        try:
            data: dict[str, Any] = {"fans": []}

            ohm = OHMManager(self.full_config)
            if not ohm.initialize():
                return data

            ohm.update_all()

            sensor_type = ohm.sensor_type
            if sensor_type is None:
                return data

            fan_sensors = ohm.get_sensors(sensor_type.Fan)
            for sensor_info in fan_sensors:
                hardware = sensor_info.hardware
                sensor = sensor_info.sensor
                sub_hardware = sensor_info.sub_hardware

                sensor_data = {
                    "name": sensor.Name,
                    "hardware_type": (
                        hardware.HardwareType.ToString()
                        if not sub_hardware
                        else f"{hardware.HardwareType.ToString()} ({sub_hardware.Name})"
                    ),
                    "speed_rpm": round(sensor.Value, 0) if sensor.Value else 0,
                }
                # Add min/max if available
                if hasattr(sensor, "Min") and sensor.Min:
                    sensor_data["min_speed_rpm"] = round(sensor.Min, 0)
                if hasattr(sensor, "Max") and sensor.Max:
                    sensor_data["max_speed_rpm"] = round(sensor.Max, 0)
                data["fans"].append(sensor_data)

            return data

        except Exception as e:
            self.handle_error(e)
            return {"fans": []}
