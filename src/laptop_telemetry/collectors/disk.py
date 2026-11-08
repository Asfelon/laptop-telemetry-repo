"""
Disk telemetry collector.
"""

import time
from typing import Any, Optional

import psutil

from .base import BaseCollector


class DiskCollector(BaseCollector):
    """
    Collector for disk telemetry data.

    Collects physical disk info, partition usage, I/O counters,
    SMART attributes, and temperatures.
    """

    def __init__(self, name: str, config: Optional[dict[str, Any]] = None) -> None:
        super().__init__(name, config)
        self._last_io_counters: dict[str, Any] = {}
        self._last_time: float | None = None
        self._physical_disks_cache: list[dict[str, Any]] | None = None
        self._wmi_connection: Any = None

    def is_enabled(self, config: Optional[dict[str, Any]] = None) -> bool:
        """Check if disk collector is enabled."""
        cfg = config or self.config or {}
        enabled: bool = cfg.get("enabled", True)
        return enabled

    def collect(self) -> dict[str, Any]:
        """
        Collect disk telemetry data.

        Returns:
            dict[str, Any]: Disk telemetry data
        """
        try:
            data: dict[str, Any] = {"disks": []}

            # Get physical disks
            physical_disks = self._get_physical_disks()

            # Get partition usage
            partitions = psutil.disk_partitions(all=False)

            # Get I/O counters
            io_counters = psutil.disk_io_counters(perdisk=True)

            current_time = time.time()

            for disk in physical_disks:
                disk_data = self._collect_disk_data(disk, partitions, io_counters, current_time)
                if disk_data:
                    data["disks"].append(disk_data)

            # Update last counters for rate calculation
            self._last_io_counters = io_counters or {}
            self._last_time = current_time

            return data

        except Exception as e:
            self.handle_error(e)
            return {"disks": []}

    def _get_physical_disks(self) -> list[dict[str, Any]]:
        """Get physical disk information (cached)."""
        if self._physical_disks_cache is not None:
            return self._physical_disks_cache

        disks: list[dict[str, Any]] = []

        try:
            # On Windows, use WMI to get physical disk info
            import wmi

            if self._wmi_connection is None:
                self._wmi_connection = wmi.WMI()
            c = self._wmi_connection

            for disk in c.Win32_DiskDrive():
                disk_info = {
                    "device_id": disk.DeviceID,
                    "model": disk.Model,
                    "serial": disk.SerialNumber,
                    "firmware": disk.FirmwareRevision,
                    "size_bytes": int(disk.Size) if disk.Size else 0,
                    "interface": disk.InterfaceType,
                    "media_type": disk.MediaType,
                    "partitions": disk.Partitions,
                    "bytes_per_sector": disk.BytesPerSector,
                    "sectors_per_track": disk.SectorsPerTrack,
                    "tracks_per_cylinder": disk.TracksPerCylinder,
                    "cylinders": disk.TotalCylinders,
                }
                disks.append(disk_info)

        except Exception as e:
            self.handle_error(e)
            # Fallback: use psutil disk partitions
            for part in psutil.disk_partitions(all=False):
                disks.append(
                    {
                        "device_id": part.device,
                        "model": "Unknown",
                        "serial": "Unknown",
                        "firmware": "Unknown",
                        "size_bytes": 0,
                        "interface": "Unknown",
                        "media_type": "Unknown",
                        "partitions": 1,
                        "bytes_per_sector": 512,
                        "sectors_per_track": 63,
                        "tracks_per_cylinder": 255,
                        "cylinders": 0,
                    }
                )

        self._physical_disks_cache = disks
        return disks

    def _collect_disk_data(
        self, disk: dict[str, Any], partitions: list, io_counters: dict, current_time: float
    ) -> Optional[dict[str, Any]]:
        """Collect data for a single physical disk."""
        try:
            device_id = disk["device_id"]

            # Find matching partition
            mountpoint = None
            fstype = None
            for part in partitions:
                if part.device.startswith(device_id.replace("\\\\.\\", "")):
                    mountpoint = part.mountpoint
                    fstype = part.fstype
                    break

            # Get usage for mountpoint
            usage = None
            if mountpoint:
                try:
                    usage = psutil.disk_usage(mountpoint)
                except Exception:
                    pass

            # Get I/O counters for this disk
            disk_io = io_counters.get(device_id.replace("\\\\.\\", ""), None)

            # Calculate rates
            read_bytes_sec = 0
            write_bytes_sec = 0
            read_iops = 0
            write_iops = 0
            read_latency_ms = 0
            write_latency_ms = 0
            queue_depth = 0
            split_io_sec = 0
            idle_time_percent = 0

            if disk_io and self._last_io_counters and self._last_time:
                time_delta = current_time - self._last_time
                if time_delta > 0:
                    last_io = self._last_io_counters.get(device_id.replace("\\\\.\\", ""), None)
                    if last_io:
                        read_bytes_sec = (disk_io.read_bytes - last_io.read_bytes) / time_delta
                        write_bytes_sec = (disk_io.write_bytes - last_io.write_bytes) / time_delta
                        read_iops = (disk_io.read_count - last_io.read_count) / time_delta
                        write_iops = (disk_io.write_count - last_io.write_count) / time_delta

                        # Latency (if available)
                        if hasattr(disk_io, "read_time") and hasattr(last_io, "read_time"):
                            read_time_delta = disk_io.read_time - last_io.read_time
                            if read_iops > 0:
                                read_latency_ms = (read_time_delta / read_iops) * 1000

                        if hasattr(disk_io, "write_time") and hasattr(last_io, "write_time"):
                            write_time_delta = disk_io.write_time - last_io.write_time
                            if write_iops > 0:
                                write_latency_ms = (write_time_delta / write_iops) * 1000

                        # Queue depth (busy_time is available on Linux, not Windows)
                        if hasattr(disk_io, "busy_time") and hasattr(last_io, "busy_time"):
                            busy_delta = disk_io.busy_time - last_io.busy_time
                            queue_depth = busy_delta / (time_delta * 1000)  # Convert to seconds

                        # Split I/O (not available in psutil on Windows)
                        # if hasattr(disk_io, 'split_count') and hasattr(
                        #     last_io, 'split_count'
                        # ):
                        #     split_io_sec = (
                        #         disk_io.split_count - last_io.split_count
                        #     ) / time_delta

                        # Idle time (not available in psutil on Windows)
                        # if hasattr(disk_io, 'idle_time') and hasattr(last_io, 'idle_time'):
                        #     idle_delta = disk_io.idle_time - last_io.idle_time
                        #     idle_time_percent = (idle_delta / (time_delta * 1000)) * 100

            # Build disk data
            disk_data: dict[str, Any] = {
                "device": mountpoint or device_id,
                "device_id": device_id,
                "mountpoint": mountpoint,
                "fstype": fstype,
                "total_bytes": usage.total if usage else disk.get("size_bytes", 0),
                "used_bytes": usage.used if usage else 0,
                "free_bytes": usage.free if usage else 0,
                "usage_percent": (usage.used / usage.total * 100)
                if usage and usage.total > 0
                else 0,
                "read_bytes_sec": round(read_bytes_sec, 2),
                "write_bytes_sec": round(write_bytes_sec, 2),
                "read_iops": round(read_iops, 2),
                "write_iops": round(write_iops, 2),
                "read_latency_ms": round(read_latency_ms, 2),
                "write_latency_ms": round(write_latency_ms, 2),
                "queue_depth": round(queue_depth, 2),
                "split_io_sec": round(split_io_sec, 2),
                "idle_time_percent": round(idle_time_percent, 2),
                "model": disk.get("model", "Unknown"),
                "serial": disk.get("serial", "Unknown"),
                "firmware": disk.get("firmware", "Unknown"),
                "interface": disk.get("interface", "Unknown"),
                "media_type": disk.get("media_type", "Unknown"),
                "bytes_per_sector": disk.get("bytes_per_sector", 512),
                "partitions": disk.get("partitions", 0),
            }

            # Temperature (placeholder for OpenHardwareMonitor)
            if self.config.get("include_temperature", True):
                disk_data["temperature_celsius"] = self._get_disk_temperature(device_id)

            # SMART attributes (placeholder for WMI SMART)
            if self.config.get("include_smart", True):
                smart_data = self._get_smart_data(device_id)
                if smart_data:
                    disk_data.update(smart_data)

            # Health percentage (placeholder)
            disk_data["health_percent"] = 100
            disk_data["power_on_hours"] = 0

            return disk_data

        except Exception as e:
            self.handle_error(e)
            return None

    def _get_disk_temperature(self, device_id: str) -> Optional[float]:
        """Get disk temperature (placeholder for OpenHardwareMonitor)."""
        # This would be implemented with OpenHardwareMonitorLib
        return None

    def _get_smart_data(self, device_id: str) -> Optional[dict[str, Any]]:
        """Get SMART attributes (placeholder for WMI)."""
        # This would be implemented with WMI MSStorageDriver_FailurePredictData
        return None
