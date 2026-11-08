"""
GPU telemetry collector.
"""

from typing import Any, Optional

from .base import BaseCollector
from .ohm_manager import OHMManager


class GPUCollector(BaseCollector):
    """
    Collector for GPU telemetry data.

    Collects GPU usage, memory, temperature, fan speed, power, and clocks
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
        """Check if GPU collector is enabled."""
        cfg = config or self.config or {}
        enabled: bool = cfg.get("enabled", True)
        return enabled

    def collect(self) -> dict[str, Any]:
        """
        Collect GPU telemetry data.

        Returns:
            dict[str, Any]: GPU telemetry data
        """
        try:
            data: dict[str, Any] = {"gpus": []}

            ohm = OHMManager(self.full_config)
            if not ohm.initialize():
                return data

            ohm.update_all()

            sensor_type = ohm.sensor_type
            hardware_type = ohm.hardware_type
            if sensor_type is None or hardware_type is None or ohm._computer is None:
                return data

            # Get all sensors and filter for GPU hardware
            for hardware in ohm._computer.Hardware:
                hw_type_str = hardware.HardwareType.ToString()
                if hw_type_str != "GpuNvidia" and hw_type_str != "GpuAti":
                    continue

                gpu_data: dict[str, Any] = {
                    "name": hardware.Name,
                    "hardware_type": hw_type_str,
                }

                for sensor in hardware.Sensors:
                    if sensor.Value is None:
                        continue

                    st = sensor.SensorType
                    value = round(sensor.Value, 1)

                    if st == sensor_type.Load:
                        if "GPU" in sensor.Name or "Core" in sensor.Name:
                            gpu_data["gpu_usage_percent"] = value
                        elif "Memory" in sensor.Name:
                            gpu_data["memory_usage_percent"] = value
                    elif st == sensor_type.Temperature:
                        gpu_data["temperature_celsius"] = value
                    elif st == sensor_type.Fan:
                        gpu_data["fan_speed_rpm"] = round(value, 0)
                    elif st == sensor_type.Power:
                        gpu_data["power_watts"] = value
                    elif st == sensor_type.Clock:
                        if "Core" in sensor.Name or "GPU" in sensor.Name:
                            gpu_data["core_clock_mhz"] = round(value, 0)
                        elif "Memory" in sensor.Name:
                            gpu_data["memory_clock_mhz"] = round(value, 0)
                    elif st == sensor_type.SmallData:
                        if "Memory" in sensor.Name and "Total" in sensor.Name:
                            gpu_data["memory_total_mb"] = round(value, 0)
                        elif "Memory" in sensor.Name and "Used" in sensor.Name:
                            gpu_data["memory_used_mb"] = round(value, 0)
                        elif "Memory" in sensor.Name and "Free" in sensor.Name:
                            gpu_data["memory_free_mb"] = round(value, 0)

                # Calculate memory free if we have total and used
                if "memory_total_mb" in gpu_data and "memory_used_mb" in gpu_data:
                    gpu_data["memory_free_mb"] = (
                        gpu_data["memory_total_mb"] - gpu_data["memory_used_mb"]
                    )

                data["gpus"].append(gpu_data)

                # Also check sub-hardware
                for sub_hardware in hardware.SubHardware:
                    for sensor in sub_hardware.Sensors:
                        if sensor.Value is None:
                            continue
                        st = sensor.SensorType
                        value = round(sensor.Value, 1)

                        if st == sensor_type.Load:
                            if "GPU" in sensor.Name or "Core" in sensor.Name:
                                gpu_data["gpu_usage_percent"] = value
                            elif "Memory" in sensor.Name:
                                gpu_data["memory_usage_percent"] = value
                        elif st == sensor_type.Temperature:
                            gpu_data["temperature_celsius"] = value
                        elif st == sensor_type.Fan:
                            gpu_data["fan_speed_rpm"] = round(value, 0)
                        elif st == sensor_type.Power:
                            gpu_data["power_watts"] = value
                        elif st == sensor_type.Clock:
                            if "Core" in sensor.Name or "GPU" in sensor.Name:
                                gpu_data["core_clock_mhz"] = round(value, 0)
                            elif "Memory" in sensor.Name:
                                gpu_data["memory_clock_mhz"] = round(value, 0)
                        elif st == sensor_type.SmallData:
                            if "Memory" in sensor.Name and "Total" in sensor.Name:
                                gpu_data["memory_total_mb"] = round(value, 0)
                            elif "Memory" in sensor.Name and "Used" in sensor.Name:
                                gpu_data["memory_used_mb"] = round(value, 0)
                            elif "Memory" in sensor.Name and "Free" in sensor.Name:
                                gpu_data["memory_free_mb"] = round(value, 0)

            return data

        except Exception as e:
            self.handle_error(e)
            return {"gpus": []}
