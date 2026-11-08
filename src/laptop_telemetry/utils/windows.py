"""
Windows-specific utilities.
"""

import platform
from typing import Any, Optional


def is_windows() -> bool:
    """Check if running on Windows."""
    return platform.system() == "Windows"


def get_windows_version() -> dict[str, Any]:
    """Get Windows version information."""
    if not is_windows():
        return {"error": "Not running on Windows"}

    return {
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "build": platform.win32_ver()[1],
        "edition": platform.win32_ver()[2],
    }


def is_admin() -> bool:
    """Check if running with administrator privileges."""
    if not is_windows():
        return False

    try:
        import ctypes

        result: int = ctypes.windll.shell32.IsUserAnAdmin()
        return result != 0
    except Exception:
        return False


def get_wmi_connection(namespace: str = "root\\cimv2") -> Any | None:
    """Get WMI connection."""
    if not is_windows():
        return None

    try:
        import wmi

        wmi_conn: Any = wmi.WMI(namespace=namespace)
        return wmi_conn
    except Exception:
        return None


def get_openhardwaremonitor_dll_path(config: Optional[Any] = None) -> Optional[str]:
    """Get OpenHardwareMonitorLib.dll path from config or environment."""
    # First check config (handle both dict and Pydantic model)
    if config:
        if hasattr(config, "openhardwaremonitor"):
            # Pydantic model
            ohm = config.openhardwaremonitor
            if ohm and ohm.dll_path:
                return str(ohm.dll_path)
        elif isinstance(config, dict) and "openhardwaremonitor" in config:
            # Dict
            ohm = config["openhardwaremonitor"]
            if ohm and ohm.get("dll_path"):
                return str(ohm["dll_path"])
    # Fallback to environment variable
    import os

    return os.environ.get("OPENHARDWAREMONITOR_DLL")


def load_openhardwaremonitor(config: Optional[Any] = None) -> Any | None:
    """Load OpenHardwareMonitorLib assembly."""
    dll_path = get_openhardwaremonitor_dll_path(config)
    if not dll_path:
        return None

    try:
        import clr

        clr.AddReference(dll_path)
        from OpenHardwareMonitor import Hardware

        hardware_module: Any = Hardware
        return hardware_module
    except Exception:
        return None


def get_computer_name() -> str:
    """Get computer name."""
    import os

    return os.environ.get("COMPUTERNAME", "unknown")


def get_user_name() -> str:
    """Get current user name."""
    import os

    return os.environ.get("USERNAME", "unknown")


def get_system_serial_number() -> str:
    """Get system serial number using WMI.

    Returns:
        System serial number or 'unknown' if not available.
    """
    if not is_windows():
        return "unknown"

    try:
        import wmi

        c = wmi.WMI()
        for system in c.Win32_ComputerSystemProduct():
            if system.IdentifyingNumber:
                serial: str = system.IdentifyingNumber.strip()
                return serial
    except Exception:
        pass

    return "unknown"
