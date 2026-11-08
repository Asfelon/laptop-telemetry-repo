"""
Base classes for telemetry collectors.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional, Protocol


class CollectorProtocol(Protocol):
    """Protocol defining the interface for telemetry collectors."""

    def collect(self) -> dict[str, Any]: ...

    def is_enabled(self, config: Optional[dict[str, Any]] = None) -> bool: ...

    def handle_error(self, error: Exception) -> None: ...

    def handle_success(self) -> None: ...

    def get_stats(self) -> dict[str, Any]: ...


@dataclass(slots=True)
class CollectorStats:
    """Statistics for a collector."""

    name: str
    error_count: int
    success_count: int
    last_collection_time: datetime | None
    success_rate: float


class BaseCollector(ABC):
    """
    Abstract base class for all telemetry collectors.

    Subclasses must implement the collect() method to gather specific metrics.
    """

    def __init__(
        self,
        name: str,
        config: Optional[dict[str, Any]] = None,
        full_config: Optional[dict[str, Any]] = None,
    ) -> None:
        self.name = name
        self.config = config or {}
        self.full_config = full_config
        self.last_collection_time: Optional[datetime] = None
        self.error_count = 0
        self.success_count = 0

    @abstractmethod
    def collect(self) -> dict[str, Any]:
        """
        Collect telemetry data.

        Returns:
            dict[str, Any]: Collected metrics
        """
        ...

    def is_enabled(self, config: Optional[dict[str, Any]] = None) -> bool:
        """
        Check if this collector is enabled based on configuration.

        Args:
            config: Collector-specific configuration

        Returns:
            bool: True if collector should be used
        """
        return True

    def handle_error(self, error: Exception) -> None:
        """
        Handle collection errors.

        Args:
            error: The exception that occurred
        """
        self.error_count += 1

    def handle_success(self) -> None:
        """Handle successful collection."""
        self.success_count += 1
        self.last_collection_time = datetime.now()

    def get_stats(self) -> dict[str, Any]:
        """
        Get collection statistics.

        Returns:
            dict[str, Any]: Collection statistics
        """
        total = self.success_count + self.error_count
        return {
            "name": self.name,
            "error_count": self.error_count,
            "success_count": self.success_count,
            "last_collection_time": self.last_collection_time,
            "success_rate": (self.success_count / total) if total > 0 else 0.0,
        }


class CollectorRegistry:
    """
    Registry for managing telemetry collectors.

    This class handles the registration, discovery, and instantiation of
    collectors based on configuration.
    """

    def __init__(self) -> None:
        self._collectors: dict[str, Any] = {}
        self._collector_classes: dict[str, type[BaseCollector]] = {}

    def register(self, name: str, collector_class: type[BaseCollector]) -> None:
        """
        Register a collector class.

        Args:
            name: Unique name for the collector
            collector_class: Collector class (subclass of BaseCollector)
        """
        if not issubclass(collector_class, BaseCollector):
            raise ValueError(f"Collector class {collector_class} must inherit from BaseCollector")

        self._collector_classes[name] = collector_class  # type: ignore[assignment]

    def create_collector(self, name: str, config: Optional[dict[str, Any]] = None) -> BaseCollector:
        """
        Create a collector instance.

        Args:
            name: Name of the collector to create
            config: Configuration for the collector

        Returns:
            BaseCollector: Collector instance

        Raises:
            KeyError: If collector name is not registered
        """
        if name not in self._collector_classes:
            raise KeyError(f"Unknown collector: {name}")

        collector_class = self._collector_classes[name]
        return collector_class(name, config)

    def get_collector_names(self) -> list[str]:
        """
        Get list of registered collector names.

        Returns:
            list[str]: List of collector names
        """
        return list(self._collector_classes.keys())

    def is_collector_enabled(self, name: str, config: Optional[dict[str, Any]] = None) -> bool:
        """
        Check if a collector is enabled based on configuration.

        Args:
            name: Name of the collector
            config: Configuration for the collector

        Returns:
            bool: True if collector is enabled
        """
        if name not in self._collector_classes:
            return False

        collector_class = self._collector_classes[name]
        return collector_class(name, config).is_enabled(config)
