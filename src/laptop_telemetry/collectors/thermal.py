"""
Thermal telemetry collector.
"""

from typing import Any, Optional

from .base import BaseCollector
from .ohm_manager import OHMManager


class ThermalCollector(BaseCollector):
    """
    Collector for thermal telemetry data.

    Collects temperature readings from all available sensors
    (CPU, GPU, motherboard, storage, VRM, etc.) via OpenHardwareMonitor.
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
        """Check if thermal collector is enabled."""
        cfg = config or self.config or {}
        enabled: bool = cfg.get("enabled", True)
        return enabled

    def collect(self) -> dict[str, Any]:
        """
        Collect thermal telemetry data.

        Returns:
            dict[str, Any]: Thermal telemetry data
        """
        try:
            data: dict[str, Any] = {"sensors": []}

            ohm = OHMManager(self.full_config)
            if not ohm.initialize():
                return data

            ohm.update_all()

            sensor_type = ohm.sensor_type
            if sensor_type is None:
                return data

            temp_sensors = ohm.get_sensors(sensor_type.Temperature)
            for sensor_info in temp_sensors:
                hardware = sensor_info.hardware
                sensor = sensor_info.sensor
                sub_hardware = sensor_info.sub_hardware

                sensor_data = {
                    "name": sensor.Name,
                    "sensor_type": (
                        hardware.HardwareType.ToString()
                        if not sub_hardware
                        else f"{hardware.HardwareType.ToString()} ({sub_hardware.Name})"
                    ),
                    "temperature_celsius": round(sensor.Value, 1) if sensor.Value else 0.0,
                }
                # Add thresholds if available
                if hasattr(sensor, "Max") and sensor.Max:
                    sensor_data["high_threshold_celsius"] = round(sensor.Max, 1)
                data["sensors"].append(sensor_data)

            return data

        except Exception as e:
            self.handle_error(e)
            return {"sensors": []}
