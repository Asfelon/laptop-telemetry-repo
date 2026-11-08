"""
Voltage telemetry collector.
"""

from typing import Any, Optional

from .base import BaseCollector
from .ohm_manager import OHMManager


class VoltageCollector(BaseCollector):
    """
    Collector for voltage telemetry data.

    Collects voltage readings for key rails (Vcore, VCCIO, DRAM, 3.3V, 5V, 12V)
    via OpenHardwareMonitor.
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
        """Check if voltage collector is enabled."""
        cfg = config or self.config or {}
        enabled: bool = cfg.get("enabled", True)
        return enabled

    def collect(self) -> dict[str, Any]:
        """
        Collect voltage telemetry data.

        Returns:
            dict[str, Any]: Voltage telemetry data
        """
        try:
            data: dict[str, Any] = {"voltages": []}

            ohm = OHMManager(self.full_config)
            if not ohm.initialize():
                return data

            ohm.update_all()

            sensor_type = ohm.sensor_type
            if sensor_type is None:
                return data

            voltage_sensors = ohm.get_sensors(sensor_type.Voltage)
            for sensor_info in voltage_sensors:
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
                    "voltage_v": round(sensor.Value, 3) if sensor.Value else 0.0,
                }
                # Add min/max if available
                if hasattr(sensor, "Min") and sensor.Min:
                    sensor_data["min_v"] = round(sensor.Min, 3)
                if hasattr(sensor, "Max") and sensor.Max:
                    sensor_data["max_v"] = round(sensor.Max, 3)
                data["voltages"].append(sensor_data)

            return data

        except Exception as e:
            self.handle_error(e)
            return {"voltages": []}
