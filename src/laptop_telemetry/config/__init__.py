"""
Configuration module for laptop telemetry collector.
"""

from .loader import load_config
from .models import (
    BatteryConfig,
    CollectionConfig,
    CollectorConfig,
    CollectorsConfig,
    CPUConfig,
    DiskConfig,
    FanConfig,
    GPUConfig,
    LoggingConfig,
    MemoryConfig,
    NetworkConfig,
    OpenHardwareMonitorConfig,
    OutputConfig,
    OutputFormat,
    RotationConfig,
    TelemetryConfig,
    ThermalConfig,
    VoltageConfig,
)

__all__ = [
    "load_config",
    "TelemetryConfig",
    "CollectionConfig",
    "OutputConfig",
    "RotationConfig",
    "OutputFormat",
    "CollectorConfig",
    "CPUConfig",
    "MemoryConfig",
    "DiskConfig",
    "NetworkConfig",
    "ThermalConfig",
    "FanConfig",
    "VoltageConfig",
    "BatteryConfig",
    "GPUConfig",
    "OpenHardwareMonitorConfig",
    "CollectorsConfig",
    "LoggingConfig",
]
