"""
Base classes for telemetry exporters.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class BaseExporter(ABC):
    """
    Abstract base class for all telemetry exporters.

    Subclasses must implement the export() method to write telemetry data
    to their specific output format.
    """

    def __init__(self, name: str):
        self.name = name
        self.export_count = 0
        self.error_count = 0

    @abstractmethod
    def export(self, data: List[Dict[str, Any]]) -> bool:
        """
        Export telemetry data.

        Args:
            data: List of telemetry records to export

        Returns:
            bool: True if export was successful
        """
        pass

    def handle_error(self, error: Exception) -> None:
        """
        Handle export errors.

        Args:
            error: The exception that occurred
        """
        self.error_count += 1

    def handle_success(self) -> None:
        """Handle successful export."""
        self.export_count += 1

    def get_stats(self) -> Dict[str, Any]:
        """
        Get export statistics.

        Returns:
            Dict[str, Any]: Export statistics
        """
        return {
            "name": self.name,
            "export_count": self.export_count,
            "error_count": self.error_count,
            "success_rate": (
                self.export_count / (self.export_count + self.error_count)
                if (self.export_count + self.error_count) > 0
                else 0.0
            ),
        }
