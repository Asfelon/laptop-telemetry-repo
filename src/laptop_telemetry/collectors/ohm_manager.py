"""
OpenHardwareMonitor Manager - Singleton for shared OHM connection.
"""

import threading
from dataclasses import dataclass
from typing import Any, Optional, TypeAlias

from ..utils.windows import load_openhardwaremonitor

# Type alias for sensor tuples
SensorTuple: TypeAlias = tuple[Any, Any] | tuple[Any, Any, Any]


@dataclass(slots=True)
class SensorInfo:
    """Container for sensor information."""

    hardware: Any
    sensor: Any
    sub_hardware: Any | None = None


class OHMManager:
    """Singleton manager for OpenHardwareMonitor connection with thread safety."""

    _instance: Optional["OHMManager"] = None
    _lock = threading.Lock()
    _computer: Any = None
    _hardware: Any = None
    _initialized: bool = False
    _config: Optional[dict[str, Any]] = None

    def __new__(cls, config: Optional[dict[str, Any]] = None) -> "OHMManager":
        """Create or return the singleton instance with thread safety."""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._config = config
            return cls._instance

    def initialize(self) -> bool:
        """Initialize the OHM connection if not already initialized.

        Returns:
            True if initialization succeeded or was already initialized, False otherwise.
        """
        with self._lock:
            if not self._initialized:
                self._hardware = load_openhardwaremonitor(self._config)
                if self._hardware:
                    self._computer = self._hardware.Computer()
                    self._computer.CPUEnabled = True
                    self._computer.GPUEnabled = True
                    self._computer.MainboardEnabled = True
                    self._computer.HDDEnabled = True
                    self._computer.Open()
                    self._initialized = True
                    return True
            return self._initialized

    def update_all(self) -> None:
        """Update all hardware sensors."""
        with self._lock:
            if self._computer:
                for hardware in self._computer.Hardware:
                    hardware.Update()
                # Also update sub-hardware
                for hardware in self._computer.Hardware:
                    for sub in hardware.SubHardware:
                        sub.Update()

    def get_sensors(self, sensor_type: Any) -> list[SensorInfo]:
        """
        Get all sensors of a specific type.

        Args:
            sensor_type: The sensor type to filter by (from OHM SensorType enum).

        Returns:
            List of SensorInfo objects containing hardware, sensor, and optional sub_hardware.
        """
        with self._lock:
            if not self._computer:
                return []
            sensors: list[SensorInfo] = []
            for hardware in self._computer.Hardware:
                for sensor in hardware.Sensors:
                    if sensor.SensorType == sensor_type:
                        sensors.append(SensorInfo(hardware=hardware, sensor=sensor))
                for sub in hardware.SubHardware:
                    for sensor in sub.Sensors:
                        if sensor.SensorType == sensor_type:
                            sensors.append(
                                SensorInfo(hardware=hardware, sensor=sensor, sub_hardware=sub)
                            )
            return sensors

    def close(self) -> None:
        """Close the OHM connection."""
        with self._lock:
            if self._computer:
                self._computer.Close()
                self._initialized = False
                self._computer = None
                self._hardware = None

    @property
    def is_initialized(self) -> bool:
        """Check if OHM is initialized."""
        return self._initialized

    @property
    def sensor_type(self) -> Any | None:
        """Get the SensorType enum from OHM hardware."""
        return self._hardware.SensorType if self._hardware else None

    @property
    def hardware_type(self) -> Any | None:
        """Get the HardwareType enum from OHM hardware."""
        return self._hardware.HardwareType if self._hardware else None
