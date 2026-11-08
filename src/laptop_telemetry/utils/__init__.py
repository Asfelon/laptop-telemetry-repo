"""
Utilities module for laptop telemetry.
"""

from .hardware import get_hardware_info
from .windows import get_windows_version, is_windows

__all__ = ["get_hardware_info", "is_windows", "get_windows_version"]
