"""
Collector registry for managing telemetry collectors.
"""

from typing import Any, Optional

from loguru import logger

from .base import BaseCollector, CollectorRegistry


class TelemetryCollectorRegistry(CollectorRegistry):
    """
    Enhanced registry for laptop telemetry collectors.

    This registry manages all telemetry collectors and provides
    methods for creating and configuring them based on the
    telemetry configuration.
    """

    def __init__(self) -> None:
        super().__init__()
        self._config: Optional[dict[str, Any]] = None

    def register_collector(self, name: str, collector_class: type[BaseCollector]) -> None:
        """
        Register a collector class.

        Args:
            name: Unique name for the collector
            collector_class: Collector class (subclass of BaseCollector)
        """
        super().register(name, collector_class)

    def create_collector(
        self,
        name: str,
        config: Optional[dict[str, Any]] = None,
        full_config: Optional[dict[str, Any]] = None,
    ) -> BaseCollector:
        """
        Create a collector instance with configuration.

        Args:
            name: Name of the collector to create
            config: Configuration for the collector
            full_config: Full telemetry configuration
            (for collectors needing global settings like OHM)

        Returns:
            BaseCollector: Collector instance

        Raises:
            KeyError: If collector name is not registered
        """
        if name not in self._collector_classes:
            raise KeyError(f"Unknown collector: {name}")

        collector_class = self._collector_classes[name]

        # For collectors that need OpenHardwareMonitor config, pass full config
        if name in ["thermal", "fan", "voltage", "gpu"] and full_config:
            return collector_class(name, config, full_config)

        return collector_class(name, config)

    def create_enabled_collectors(self, config: dict[str, Any]) -> dict[str, BaseCollector]:
        """
        Create all enabled collectors based on configuration.

        Args:
            config: Telemetry configuration

        Returns:
            dict[str, BaseCollector]: Dictionary of enabled collectors
        """
        self._config = config
        enabled_collectors: dict[str, BaseCollector] = {}

        for collector_name in self.get_collector_names():
            try:
                collector_config = self._get_collector_config(collector_name, config)
                if self._is_collector_enabled(collector_name, collector_config):
                    collector = self.create_collector(collector_name, collector_config, config)
                    enabled_collectors[collector_name] = collector
                    logger.info(f"Created collector: {collector_name}")
                else:
                    logger.debug(f"Collector disabled: {collector_name}")
            except Exception as e:
                logger.error(f"Failed to create collector {collector_name}: {e}")

        return enabled_collectors

    def _get_collector_config(
        self, collector_name: str, config: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
        """
        Get configuration for a specific collector.

        Args:
            collector_name: Name of the collector
            config: Full telemetry configuration

        Returns:
            Optional[dict[str, Any]]: Collector configuration or None
        """
        collectors_config = config.get("collectors", {})

        # Map collector names to config sections
        config_mapping = {
            "cpu": "cpu",
            "memory": "memory",
            "disk": "disk",
            "network": "network",
            "thermal": "thermal",
            "fan": "fan",
            "voltage": "voltage",
            "battery": "battery",
            "gpu": "gpu",
        }

        config_section = config_mapping.get(collector_name)
        if config_section and config_section in collectors_config:
            result: dict[str, Any] | None = collectors_config[config_section]
            return result

        return None

    def _is_collector_enabled(self, collector_name: str, config: Optional[dict[str, Any]]) -> bool:
        """
        Check if a collector is enabled based on configuration.

        Args:
            collector_name: Name of the collector
            config: Collector configuration

        Returns:
            bool: True if collector is enabled
        """
        if not config:
            return False

        enabled: bool = config.get("enabled", False)
        return enabled

    def get_collector_stats(self, collectors: dict[str, BaseCollector]) -> dict[str, Any]:
        """
        Get statistics for all collectors.

        Args:
            collectors: Dictionary of collectors

        Returns:
            dict[str, Any]: Collection statistics
        """
        stats: dict[str, Any] = {}
        for name, collector in collectors.items():
            stats[name] = collector.get_stats()

        return stats

    def log_collection_summary(self, collectors: dict[str, BaseCollector]) -> None:
        """
        Log a summary of collection statistics.

        Args:
            collectors: Dictionary of collectors
        """
        stats = self.get_collector_stats(collectors)

        logger.info("=== Collection Summary ===")
        for name, stat in stats.items():
            logger.info(
                f"{name}: "
                f"success={stat['success_count']}, "
                f"errors={stat['error_count']}, "
                f"rate={stat['success_rate']:.2%}"
            )

        total_success = sum(s["success_count"] for s in stats.values())
        total_errors = sum(s["error_count"] for s in stats.values())

        if total_success + total_errors > 0:
            overall_rate = total_success / (total_success + total_errors)
            logger.info(f"Overall success rate: {overall_rate:.2%}")
