"""
Laptop Telemetry Collector

A Windows-only Python application that collects comprehensive laptop telemetry
(80+ metrics at minute-level granularity) including CPU breakdown (user/dpc/interrupt/privileged),
all physical disks with split I/O, cache memory, thermals, fan speeds, and more.

Logs to JSON/CSV for later analysis.
"""

__version__ = "0.1.0"

from .collectors.registry import TelemetryCollectorRegistry
from .config.loader import load_config
from .exporter.csv_exporter import CSVExporter
from .exporter.json_exporter import JSONExporter
from .scheduler.runner import TelemetryRunner

__all__ = [
    "load_config",
    "TelemetryCollectorRegistry",
    "JSONExporter",
    "CSVExporter",
    "TelemetryRunner",
]
