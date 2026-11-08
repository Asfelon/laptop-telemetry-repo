"""
Hardware detection utilities.
"""

import platform
from typing import Any

import psutil


def get_hardware_info() -> dict[str, Any]:
    """
    Get comprehensive hardware information.

    Returns:
        dict[str, Any]: Hardware information
    """
    info: dict[str, Any] = {
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
        },
        "cpu": {
            "physical_cores": psutil.cpu_count(logical=False),
            "logical_cores": psutil.cpu_count(logical=True),
            "max_frequency_mhz": psutil.cpu_freq().max if psutil.cpu_freq() else None,
        },
        "memory": {
            "total_bytes": psutil.virtual_memory().total,
        },
        "disks": [],
    }

    # Disk information
    for part in psutil.disk_partitions(all=False):
        try:
            usage = psutil.disk_usage(part.mountpoint)
            info["disks"].append(
                {
                    "device": part.device,
                    "mountpoint": part.mountpoint,
                    "fstype": part.fstype,
                    "total_bytes": usage.total,
                }
            )
        except Exception:
            pass

    return info


def get_cpu_info() -> dict[str, Any]:
    """Get detailed CPU information."""
    return {
        "physical_cores": psutil.cpu_count(logical=False),
        "logical_cores": psutil.cpu_count(logical=True),
        "frequency": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None,
        "per_cpu_frequency": [f._asdict() for f in psutil.cpu_freq(percpu=True)]
        if psutil.cpu_freq(percpu=True)
        else None,
    }


def get_memory_info() -> dict[str, Any]:
    """Get detailed memory information."""
    vm = psutil.virtual_memory()
    return {
        "total": vm.total,
        "available": vm.available,
        "used": vm.used,
        "free": vm.free,
        "percent": vm.percent,
    }


def get_disk_info() -> dict[str, Any]:
    """Get detailed disk information."""
    disks = []
    for part in psutil.disk_partitions(all=False):
        try:
            usage = psutil.disk_usage(part.mountpoint)
            disks.append(
                {
                    "device": part.device,
                    "mountpoint": part.mountpoint,
                    "fstype": part.fstype,
                    "total": usage.total,
                    "used": usage.used,
                    "free": usage.free,
                    "percent": (usage.used / usage.total * 100) if usage.total > 0 else 0,
                }
            )
        except Exception:
            pass
    return {"disks": disks}
