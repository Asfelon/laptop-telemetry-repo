"""
Unit tests for Thermal collector.
"""

from src.laptop_telemetry.collectors.thermal import ThermalCollector


class TestThermalCollector:
    """Tests for ThermalCollector."""

    def test_init(self):
        """Test collector initialization."""
        collector = ThermalCollector("thermal")
        assert collector.name == "thermal"
        assert collector.error_count == 0
        assert collector.success_count == 0

    def test_is_enabled_default(self):
        """Test is_enabled with default config."""
        collector = ThermalCollector("thermal")
        assert collector.is_enabled() is True

    def test_is_enabled_disabled(self):
        """Test is_enabled with disabled config."""
        collector = ThermalCollector("thermal", {"enabled": False})
        assert collector.is_enabled() is False

    def test_collect_placeholder(self):
        """Test placeholder collection."""
        collector = ThermalCollector("thermal")
        data = collector.collect()

        assert "sensors" in data
        assert isinstance(data["sensors"], list)
