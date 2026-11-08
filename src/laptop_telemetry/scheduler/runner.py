"""
Telemetry collection scheduler.
"""

import socket
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import Any

from loguru import logger

from ..collectors.registry import TelemetryCollectorRegistry
from ..config.models import TelemetryConfig
from ..exporter.csv_exporter import CSVExporter
from ..exporter.json_exporter import JSONExporter
from ..utils.windows import get_system_serial_number, is_windows


class TelemetryRunner:
    """
    Main telemetry collection runner.

    This class manages the periodic collection of telemetry data,
    handles exporters, and provides a clean interface for starting
    and stopping the collection process.
    """

    def __init__(self, config: TelemetryConfig) -> None:
        """
        Initialize telemetry runner.

        Args:
            config: Telemetry configuration
        """
        self.config = config
        self.collector_registry = TelemetryCollectorRegistry()
        self.exporters: dict[str, Any] = {}
        self.running = False
        self.collection_thread: threading.Thread | None = None
        self.collection_interval = config.collection.interval_seconds
        self.duration = config.collection.duration_seconds

        # Cache serial number at startup (Windows only)
        if is_windows():
            self._serial_number = get_system_serial_number()
        else:
            self._serial_number = "unknown"

        # Initialize exporters
        self._initialize_exporters()

        # Register collectors
        self._register_collectors()

        # Create enabled collectors ONCE at startup
        self.collectors = self.collector_registry.create_enabled_collectors(
            self.config.model_dump()
        )

    def _initialize_exporters(self) -> None:
        """Initialize exporters based on configuration."""
        output_dir = self.config.output.directory

        fmt = self.config.output.format
        fmt_str = fmt.value if hasattr(fmt, "value") else str(fmt)

        # Always create both unless explicitly disabled
        if fmt_str in ("jsonl", "both"):
            self.exporters["json"] = JSONExporter("json", output_dir)

        if fmt_str in ("csv", "both"):
            self.exporters["csv"] = CSVExporter("csv", output_dir)

        # If no exporters configured, use JSON as default
        if not self.exporters:
            self.exporters["json"] = JSONExporter("json", output_dir)

    def _register_collectors(self) -> None:
        """Register all available collectors."""
        # Import and register collectors here
        # This is done dynamically to avoid circular imports
        from ..collectors.battery import BatteryCollector
        from ..collectors.cpu import CPUCollector
        from ..collectors.disk import DiskCollector
        from ..collectors.memory import MemoryCollector
        from ..collectors.network import NetworkCollector
        from ..utils.windows import is_windows

        # Always available collectors
        collectors = [
            ("cpu", CPUCollector),
            ("memory", MemoryCollector),
            ("disk", DiskCollector),
            ("network", NetworkCollector),
            ("battery", BatteryCollector),
        ]

        for name, collector_class in collectors:
            self.collector_registry.register_collector(name, collector_class)  # type: ignore[type-abstract]

        # Windows-specific collectors (require wmi/pythonnet)
        if is_windows():
            from ..collectors.fan import FanCollector
            from ..collectors.gpu import GPUCollector
            from ..collectors.thermal import ThermalCollector
            from ..collectors.voltage import VoltageCollector

            windows_collectors = [
                ("thermal", ThermalCollector),
                ("fan", FanCollector),
                ("voltage", VoltageCollector),
                ("gpu", GPUCollector),
            ]

            for name, collector_class in windows_collectors:
                self.collector_registry.register_collector(name, collector_class)  # type: ignore[type-abstract]

    def start(self) -> None:
        """Start the telemetry collection."""
        if self.running:
            return

        self.running = True
        self.collection_thread = threading.Thread(target=self._collection_loop, daemon=True)
        self.collection_thread.start()

    def stop(self) -> None:
        """Stop the telemetry collection."""
        self.running = False
        if self.collection_thread:
            self.collection_thread.join(timeout=5)
        # Close exporters to flush and close files
        for exporter in self.exporters.values():
            if hasattr(exporter, "close"):
                exporter.close()

    def _collection_loop(self) -> None:
        """Main collection loop with interval alignment."""
        start_time = datetime.now()

        # Calculate first aligned collection time
        now = datetime.now()
        interval = self.collection_interval
        seconds_into_interval = now.timestamp() % interval
        first_sleep = interval - seconds_into_interval
        time.sleep(first_sleep)

        while self.running:
            cycle_start = datetime.now()

            # Timestamp at the START of collection (aligned to interval)
            collection_timestamp = cycle_start.replace(microsecond=0).isoformat()

            # Check duration limit BEFORE collecting
            if self.duration > 0:
                elapsed = (datetime.now() - start_time).total_seconds()
                if elapsed >= self.duration:
                    self.running = False
                    break

            # Collect telemetry with pre-aligned timestamp
            self._collect_and_export(collection_timestamp)

            # Check duration again after collection (in case collection took long)
            if self.duration > 0:
                elapsed = (datetime.now() - start_time).total_seconds()
                if elapsed >= self.duration:
                    self.running = False
                    break

            # Sleep for remaining interval time (accounting for collection duration)
            cycle_elapsed = (datetime.now() - cycle_start).total_seconds()
            sleep_time = max(0, self.collection_interval - cycle_elapsed)
            time.sleep(sleep_time)

        # Ensure running is False when loop exits
        self.running = False

    def _collect_and_export(self, start_timestamp: str) -> None:
        """Collect telemetry from all enabled collectors and export.

        Args:
            start_timestamp: ISO format timestamp at the start of collection.
        """
        # Use pre-created collectors
        collectors = self.collectors

        # Group collectors by dependency
        # OHM collectors share connection - run sequentially
        # Others can run in parallel
        ohm_collector_names = {"thermal", "fan", "voltage", "gpu"}
        ohm_collectors = {k: v for k, v in collectors.items() if k in ohm_collector_names}
        other_collectors = {k: v for k, v in collectors.items() if k not in ohm_collector_names}

        # Metadata FIRST for column ordering
        telemetry_data: dict[str, Any] = {
            "serial_number": self._serial_number,
            "start_timestamp": start_timestamp,
            "end_timestamp": "",  # Placeholder, updated after collection
            "hostname": self._get_hostname(),
        }

        # Run OHM collectors sequentially (shared connection)
        for name, collector in ohm_collectors.items():
            try:
                telemetry_data[name] = collector.collect()
            except Exception as e:
                logger.error(f"Error collecting {name}: {e}")

        # Run other collectors in parallel
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {executor.submit(c.collect): n for n, c in other_collectors.items()}
            for future in as_completed(futures):
                name = futures[future]
                try:
                    telemetry_data[name] = future.result()
                except Exception as e:
                    logger.error(f"Error collecting {name}: {e}")

        # Update end timestamp after collection
        telemetry_data["end_timestamp"] = datetime.now().replace(microsecond=0).isoformat()

        # Export data
        for exporter in self.exporters.values():
            try:
                exporter.export([telemetry_data])
            except Exception as e:
                logger.error(f"Error exporting: {e}")

    def _get_hostname(self) -> str:
        """Get the computer hostname."""
        try:
            return socket.gethostname()
        except Exception:
            return "localhost"

    def collect_once(self) -> dict[str, Any]:
        """
        Collect telemetry once and return the data.

        Returns:
            Dict[str, Any]: Collected telemetry data
        """
        collectors = self.collector_registry.create_enabled_collectors(self.config.model_dump())

        # Metadata FIRST for column ordering
        telemetry_data: dict[str, Any] = {
            "serial_number": self._serial_number,
            "start_timestamp": "",
            "end_timestamp": "",
            "hostname": self._get_hostname(),
        }

        start_timestamp = datetime.now().replace(microsecond=0).isoformat()
        telemetry_data["start_timestamp"] = start_timestamp

        for name, collector in collectors.items():
            try:
                data = collector.collect()
                telemetry_data[name] = data
            except Exception as e:
                logger.error(f"Error collecting {name}: {e}")

        # Update end timestamp after collection
        telemetry_data["end_timestamp"] = datetime.now().replace(microsecond=0).isoformat()

        return telemetry_data
