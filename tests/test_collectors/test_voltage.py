"""
Unit tests for Voltage collector.
"""

from src.laptop_telemetry.collectors.voltage import VoltageCollector


class TestVoltageCollector:
    """Tests for VoltageCollector."""

    def test_init(self):
        """Test collector initialization."""
        collector = VoltageCollector("voltage")
        assert collector.name == "voltage"
        assert collector.error_count == 0
        assert collector.success_count == 0

    def test_is_enabled_default(self):
        """Test is_enabled with default config."""
        collector = VoltageCollector("voltage")
        assert collector.is_enabled() is True

    def test_is_enabled_disabled(self):
        """Test is_enabled with disabled config."""
        collector = VoltageCollector("voltage", {"enabled": False})
        assert collector.is_enabled() is False

    def test_collect_placeholder(self):
        """Test placeholder collection."""
        collector = VoltageCollector("voltage")
        data = collector.collect()

        assert "voltages" in data
        assert isinstance(data["voltages"], list)
