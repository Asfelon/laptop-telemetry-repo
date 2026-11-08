"""
Pydantic models for configuration validation.
"""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator


class OutputFormat(str, Enum):
    JSONL = "jsonl"
    CSV = "csv"
    BOTH = "both"


class CollectionConfig(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
    )

    interval_seconds: int = Field(default=60, ge=1, le=3600)
    duration_seconds: int = Field(default=0, ge=0)  # 0 = infinite


class RotationConfig(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
    )

    max_size_mb: int = Field(default=100, ge=1)
    max_files: int = Field(default=30, ge=1)
    compress: bool = Field(default=True)


class OutputConfig(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
        use_enum_values=True,
    )

    format: OutputFormat = Field(default=OutputFormat.BOTH)
    directory: str = Field(default="./logs")
    filename_template: str = Field(default="telemetry_{hostname}_{date}.{ext}")
    rotation: RotationConfig = Field(default_factory=RotationConfig)


class CollectorConfig(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
    )

    enabled: bool = Field(default=True)


class CPUConfig(CollectorConfig):
    per_core: bool = Field(default=True)
    include_temperature: bool = Field(default=True)
    include_power: bool = Field(default=True)
    include_cache: bool = Field(default=True)
    include_system_counters: bool = Field(default=True)


class MemoryConfig(CollectorConfig):
    include_swap: bool = Field(default=True)
    include_page_faults: bool = Field(default=True)
    include_numa: bool = Field(default=True)


class DiskConfig(CollectorConfig):
    physical_disks: str = Field(default="all")  # "all" or list of device IDs
    partitions: str = Field(default="all")  # "all" or list of mountpoints
    include_io: bool = Field(default=True)
    include_smart: bool = Field(default=True)
    include_temperature: bool = Field(default=True)


class NetworkConfig(CollectorConfig):
    interfaces: str = Field(default="all")  # "all" or list of interface names


class ThermalConfig(CollectorConfig):
    sensors: str = Field(default="all")  # "all" or list of sensor names


class FanConfig(CollectorConfig):
    sensors: str = Field(default="all")


class VoltageConfig(CollectorConfig):
    rails: str = Field(default="all")


class BatteryConfig(CollectorConfig):
    pass


class GPUConfig(CollectorConfig):
    devices: str = Field(default="all")


class OpenHardwareMonitorConfig(BaseModel):
    """OpenHardwareMonitor configuration."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
    )

    dll_path: Optional[str] = Field(default=None, description="Path to OpenHardwareMonitorLib.dll")


class CollectorsConfig(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
    )

    cpu: CPUConfig = Field(default_factory=CPUConfig)
    memory: MemoryConfig = Field(default_factory=MemoryConfig)
    disk: DiskConfig = Field(default_factory=DiskConfig)
    network: NetworkConfig = Field(default_factory=NetworkConfig)
    thermal: ThermalConfig = Field(default_factory=ThermalConfig)
    fan: FanConfig = Field(default_factory=FanConfig)
    voltage: VoltageConfig = Field(default_factory=VoltageConfig)
    battery: BatteryConfig = Field(default_factory=BatteryConfig)
    gpu: GPUConfig = Field(default_factory=GPUConfig)


class LoggingConfig(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
    )

    level: str = Field(default="INFO")
    file: str = Field(default="./logs/collector.log")
    rotation: str = Field(default="10 MB")
    retention: str = Field(default="30 days")


class TelemetryConfig(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
        populate_by_name=True,
        use_enum_values=True,
    )

    collection: CollectionConfig = Field(default_factory=CollectionConfig)
    output: OutputConfig = Field(default_factory=OutputConfig)
    collectors: CollectorsConfig = Field(default_factory=CollectorsConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    openhardwaremonitor: OpenHardwareMonitorConfig = Field(
        default_factory=OpenHardwareMonitorConfig
    )

    @model_validator(mode="after")
    def validate_output_config(self) -> "TelemetryConfig":
        if self.output.format == OutputFormat.CSV and "csv" not in self.output.filename_template:
            self.output.filename_template = self.output.filename_template.replace(".{ext}", ".csv")
        elif (
            self.output.format == OutputFormat.JSONL
            and "jsonl" not in self.output.filename_template
        ):
            self.output.filename_template = self.output.filename_template.replace(
                ".{ext}", ".jsonl"
            )
        # For BOTH format, keep the .{ext} placeholder so each exporter can use its own extension
        elif self.output.format == OutputFormat.BOTH and ".{ext}" not in self.output.filename_template:
            # If no placeholder, add it before the extension
            if self.output.filename_template.endswith(".jsonl"):
                self.output.filename_template = self.output.filename_template.replace(".jsonl", ".{ext}")
            elif self.output.filename_template.endswith(".csv"):
                self.output.filename_template = self.output.filename_template.replace(".csv", ".{ext}")
        return self
