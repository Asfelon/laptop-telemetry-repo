"""
Unit tests for Battery collector.
"""

from unittest.mock import Mock, patch

from src.laptop_telemetry.collectors.battery import BatteryCollector


class TestBatteryCollector:
    """Tests for BatteryCollector."""

    def test_init(self):
        """Test collector initialization."""
        collector = BatteryCollector("battery")
        assert collector.name == "battery"
        assert collector.error_count == 0
        assert collector.success_count == 0

    def test_is_enabled_default(self):
        """Test is_enabled with default config."""
        collector = BatteryCollector("battery")
        assert collector.is_enabled() is True

    def test_is_enabled_disabled(self):
        """Test is_enabled with disabled config."""
        collector = BatteryCollector("battery", {"enabled": False})
        assert collector.is_enabled() is False

    @patch("src.laptop_telemetry.collectors.battery.psutil.sensors_battery")
    def test_collect_no_battery(self, mock_sensors_battery):
        """Test collection when no battery present."""
        mock_sensors_battery.return_value = None

        collector = BatteryCollector("battery")
        data = collector.collect()

        assert "present" in data
        assert data["present"] is False

    @patch("src.laptop_telemetry.collectors.battery.psutil.sensors_battery")
    def test_collect_with_battery(self, mock_sensors_battery):
        """Test collection with battery present."""
        mock_battery = Mock()
        mock_battery.percent = 75
        mock_battery.power_plugged = False
        mock_battery.secsleft = 3600  # 1 hour
        mock_sensors_battery.return_value = mock_battery

        collector = BatteryCollector("battery")
        data = collector.collect()

        assert "present" in data
        assert data["present"] is True
        assert "charge_percent" in data
        assert data["charge_percent"] == 75
        assert "status" in data
        assert data["status"] == "discharging"
        assert "time_remaining_minutes" in data
        assert data["time_remaining_minutes"] == 60
