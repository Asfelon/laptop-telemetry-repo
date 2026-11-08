"""
Pytest configuration and fixtures.
"""

import sys
from pathlib import Path

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.fixture
def sample_config():
    """Sample configuration for testing."""
    return {
        "collection": {"interval_seconds": 60, "duration_seconds": 0},
        "output": {
            "format": "jsonl",
            "directory": "./logs",
            "filename_template": "telemetry_{hostname}_{date}.jsonl",
            "rotation": {"max_size_mb": 100, "max_files": 30, "compress": True},
        },
        "collectors": {
            "cpu": {
                "enabled": True,
                "per_core": True,
                "include_temperature": True,
                "include_power": True,
                "include_cache": True,
                "include_system_counters": True,
            },
            "memory": {
                "enabled": True,
                "include_swap": True,
                "include_page_faults": True,
                "include_numa": True,
            },
            "disk": {
                "enabled": True,
                "physical_disks": "all",
                "partitions": "all",
                "include_io": True,
                "include_smart": True,
                "include_temperature": True,
            },
            "network": {"enabled": True, "interfaces": "all"},
            "thermal": {"enabled": True, "sensors": "all"},
            "fan": {"enabled": True, "sensors": "all"},
            "voltage": {"enabled": True, "rails": "all"},
            "battery": {"enabled": True},
            "gpu": {"enabled": True, "devices": "all"},
        },
        "logging": {
            "level": "INFO",
            "file": "./logs/collector.log",
            "rotation": "10 MB",
            "retention": "30 days",
        },
    }
