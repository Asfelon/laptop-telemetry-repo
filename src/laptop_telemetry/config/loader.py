"""
Configuration loading and validation.
"""

import os
from typing import Any, Dict, Optional

import yaml
from loguru import logger

from .models import TelemetryConfig


def load_config(config_path: Optional[str] = None) -> TelemetryConfig:
    """
    Load configuration from YAML file or use defaults.

    Args:
        config_path: Path to YAML configuration file

    Returns:
        TelemetryConfig: Validated configuration object
    """
    # Determine config file path
    if config_path is None:
        config_path = get_default_config_path()

    if config_path and os.path.exists(config_path):
        with open(config_path, "r") as f:
            config_data = yaml.safe_load(f)
        logger.info(f"Loaded configuration from {config_path}")
    else:
        # Default configuration
        config_data = {}
        logger.info("Using default configuration")

    # Allow environment variable to override OpenHardwareMonitor DLL path
    ohm_dll_env = os.environ.get("OPENHARDWAREMONITOR_DLL")
    if ohm_dll_env:
        if "openhardwaremonitor" not in config_data:
            config_data["openhardwaremonitor"] = {}
        # Only override if config value is empty/falsy
        existing = config_data["openhardwaremonitor"].get("dll_path")
        if not existing:
            config_data["openhardwaremonitor"]["dll_path"] = ohm_dll_env

    try:
        config = TelemetryConfig(**config_data)
        logger.info("Configuration loaded and validated successfully")
        return config
    except Exception as e:
        logger.error(f"Configuration validation failed: {e}")
        raise


def get_default_config_path() -> str:
    """Get the default configuration file path."""
    # Look for config/default.yaml in project root (parent of src/)
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    return os.path.join(project_root, "config", "default.yaml")


def create_default_config() -> Dict[str, Any]:
    """Create default configuration dictionary."""
    return {
        "collection": {"interval_seconds": 60, "duration_seconds": 0},
        "output": {
            "format": "both",
            "directory": "./logs",
            "filename_template": "telemetry_{hostname}_{date}.{ext}",
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
