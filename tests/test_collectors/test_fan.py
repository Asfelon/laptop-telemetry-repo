"""
Unit tests for Fan collector.
"""

from src.laptop_telemetry.collectors.fan import FanCollector


class TestFanCollector:
    """Tests for FanCollector."""

    def test_init(self):
        """Test collector initialization."""
        collector = FanCollector("fan")
        assert collector.name == "fan"
        assert collector.error_count == 0
        assert collector.success_count == 0

    def test_is_enabled_default(self):
        """Test is_enabled with default config."""
        collector = FanCollector("fan")
        assert collector.is_enabled() is True

    def test_is_enabled_disabled(self):
        """Test is_enabled with disabled config."""
        collector = FanCollector("fan", {"enabled": False})
        assert collector.is_enabled() is False

    def test_collect_placeholder(self):
        """Test placeholder collection."""
        collector = FanCollector("fan")
        data = collector.collect()

        assert "fans" in data
        assert isinstance(data["fans"], list)
