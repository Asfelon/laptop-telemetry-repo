"""
Collectors module for laptop telemetry.
"""

from .base import BaseCollector, CollectorRegistry
from .registry import TelemetryCollectorRegistry

__all__ = ["BaseCollector", "CollectorRegistry", "TelemetryCollectorRegistry"]
