"""
Memory telemetry collector.
"""

from typing import Any, Optional

import psutil

from .base import BaseCollector


class MemoryCollector(BaseCollector):
    """
    Collector for memory telemetry data.

    Collects virtual memory, swap, page faults, and NUMA statistics.
    """

    def __init__(self, name: str, config: Optional[dict[str, Any]] = None) -> None:
        super().__init__(name, config)

    def is_enabled(self, config: Optional[dict[str, Any]] = None) -> bool:
        """Check if memory collector is enabled."""
        cfg = config or self.config or {}
        enabled: bool = cfg.get("enabled", True)
        return enabled

    def collect(self) -> dict[str, Any]:
        """
        Collect memory telemetry data.

        Returns:
            dict[str, Any]: Memory telemetry data
        """
        try:
            data: dict[str, Any] = {}

            # Virtual memory
            vm = psutil.virtual_memory()
            data["total_bytes"] = vm.total
            data["available_bytes"] = vm.available
            data["used_bytes"] = vm.used
            data["free_bytes"] = vm.free
            data["usage_percent"] = vm.percent

            # Extended memory info (Windows-specific attributes)
            # These are available on Windows via psutil
            for attr in [
                "active",
                "inactive",
                "modified",
                "standby",
                "cached",
                "shared",
                "buffers",
                "page_tables",
                "commit_limit",
                "committed_as",
                "dirty",
                "writeback",
                "mapped",
                "nonpaged_pool",
                "paged_pool",
            ]:
                if hasattr(vm, attr):
                    data[f"{attr}_bytes"] = getattr(vm, attr)

            # Swap memory
            if self.config.get("include_swap", True):
                swap = psutil.swap_memory()
                data["swap_total_bytes"] = swap.total
                data["swap_used_bytes"] = swap.used
                data["swap_free_bytes"] = swap.free
                data["swap_usage_percent"] = swap.percent
                if hasattr(swap, "sin"):
                    data["swap_in_bytes_sec"] = swap.sin
                if hasattr(swap, "sout"):
                    data["swap_out_bytes_sec"] = swap.sout

            # Page fault details (would need WMI on Windows)
            if self.config.get("include_page_faults", True):
                # Placeholder for WMI implementation
                pass

            # NUMA stats (would need WMI on Windows)
            if self.config.get("include_numa", True):
                # Placeholder for WMI implementation
                pass

            return data

        except Exception as e:
            self.handle_error(e)
            return {}
