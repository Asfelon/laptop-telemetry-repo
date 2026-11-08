"""
Network telemetry collector.
"""

import time
from typing import Any, Optional

import psutil

from .base import BaseCollector


class NetworkCollector(BaseCollector):
    """
    Collector for network telemetry data.

    Collects per-interface statistics including throughput, errors, and drops.
    """

    def __init__(self, name: str, config: Optional[dict[str, Any]] = None) -> None:
        super().__init__(name, config)
        self._last_io_counters: dict[str, Any] = {}
        self._last_time: float | None = None

    def is_enabled(self, config: Optional[dict[str, Any]] = None) -> bool:
        """Check if network collector is enabled."""
        cfg = config or self.config or {}
        enabled: bool = cfg.get("enabled", True)
        return enabled

    def collect(self) -> dict[str, Any]:
        """
        Collect network telemetry data.

        Returns:
            dict[str, Any]: Network telemetry data
        """
        try:
            data: dict[str, Any] = {"interfaces": []}

            # Get network I/O counters per interface
            io_counters = psutil.net_io_counters(pernic=True)

            # Get network interface addresses
            addrs = psutil.net_if_addrs()

            # Get network interface stats
            stats = psutil.net_if_stats()

            current_time = time.time()

            for interface_name, io in io_counters.items():
                # Skip loopback
                if interface_name.lower() in ["lo", "loopback", "lo0"]:
                    continue

                # Filter by configured interfaces
                if self.config.get("interfaces") != "all":
                    allowed = self.config.get("interfaces", [])
                    if isinstance(allowed, list) and interface_name not in allowed:
                        continue

                interface_data: dict[str, Any] = {
                    "interface": interface_name,
                }

                # Get IP addresses
                if interface_name in addrs:
                    for addr in addrs[interface_name]:
                        if addr.family == 2:  # AF_INET
                            interface_data["ipv4"] = addr.address
                        elif addr.family == 10:  # AF_INET6
                            interface_data["ipv6"] = addr.address
                        elif addr.family == 17:  # AF_PACKET (MAC)
                            interface_data["mac"] = addr.address

                # Get interface stats
                if interface_name in stats:
                    stat = stats[interface_name]
                    interface_data["speed_mbps"] = stat.speed
                    interface_data["is_up"] = stat.isup
                    interface_data["mtu"] = stat.mtu

                # Calculate rates
                bytes_sent_sec = 0
                bytes_recv_sec = 0
                packets_sent_sec = 0
                packets_recv_sec = 0
                errors_in_sec = 0
                errors_out_sec = 0
                drops_in_sec = 0
                drops_out_sec = 0

                if self._last_io_counters and self._last_time:
                    time_delta = current_time - self._last_time
                    if time_delta > 0:
                        last_io = self._last_io_counters.get(interface_name)
                        if last_io:
                            bytes_sent_sec = (io.bytes_sent - last_io.bytes_sent) / time_delta
                            bytes_recv_sec = (io.bytes_recv - last_io.bytes_recv) / time_delta
                            packets_sent_sec = (io.packets_sent - last_io.packets_sent) / time_delta
                            packets_recv_sec = (io.packets_recv - last_io.packets_recv) / time_delta
                            errors_in_sec = (io.errin - last_io.errin) / time_delta
                            errors_out_sec = (io.errout - last_io.errout) / time_delta
                            drops_in_sec = (io.dropin - last_io.dropin) / time_delta
                            drops_out_sec = (io.dropout - last_io.dropout) / time_delta

                interface_data["bytes_sent_sec"] = round(bytes_sent_sec, 2)
                interface_data["bytes_recv_sec"] = round(bytes_recv_sec, 2)
                interface_data["packets_sent_sec"] = round(packets_sent_sec, 2)
                interface_data["packets_recv_sec"] = round(packets_recv_sec, 2)
                interface_data["errors_in_sec"] = round(errors_in_sec, 2)
                interface_data["errors_out_sec"] = round(errors_out_sec, 2)
                interface_data["drops_in_sec"] = round(drops_in_sec, 2)
                interface_data["drops_out_sec"] = round(drops_out_sec, 2)

                # Absolute counters
                interface_data["bytes_sent_total"] = io.bytes_sent
                interface_data["bytes_recv_total"] = io.bytes_recv
                interface_data["packets_sent_total"] = io.packets_sent
                interface_data["packets_recv_total"] = io.packets_recv
                interface_data["errors_in_total"] = io.errin
                interface_data["errors_out_total"] = io.errout
                interface_data["drops_in_total"] = io.dropin
                interface_data["drops_out_total"] = io.dropout

                data["interfaces"].append(interface_data)

            # Update last counters
            self._last_io_counters = io_counters
            self._last_time = current_time

            return data

        except Exception as e:
            self.handle_error(e)
            return {"interfaces": []}
