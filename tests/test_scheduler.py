"""
Unit tests for scheduler/runner.
"""

from unittest.mock import Mock, patch

from src.laptop_telemetry.config.models import TelemetryConfig
from src.laptop_telemetry.scheduler.runner import TelemetryRunner


class TestTelemetryRunner:
    """Tests for TelemetryRunner."""

    def test_init(self):
        """Test runner initialization."""
        config = TelemetryConfig()
        runner = TelemetryRunner(config)

        assert runner.config == config
        assert runner.collection_interval == 60
        assert runner.duration == 0
        assert runner.running is False
        assert "json" in runner.exporters

    def test_start_stop(self):
        """Test start and stop."""
        config = TelemetryConfig()
        runner = TelemetryRunner(config)

        runner.start()
        assert runner.running is True
        assert runner.collection_thread is not None

        runner.stop()
        assert runner.running is False

    @patch("src.laptop_telemetry.scheduler.runner.TelemetryCollectorRegistry")
    def test_collect_once(self, mock_registry_class):
        """Test collect_once."""
        config = TelemetryConfig()
        runner = TelemetryRunner(config)

        # Mock registry
        mock_registry = Mock()
        mock_collector = Mock()
        mock_collector.collect.return_value = {"usage_percent": 25.5}
        mock_registry.create_enabled_collectors.return_value = {"cpu": mock_collector}
        mock_registry_class.return_value = mock_registry

        # Recreate runner with mocked registry
        runner.collector_registry = mock_registry

        data = runner.collect_once()

        assert "start_timestamp" in data
        assert "end_timestamp" in data
        assert "hostname" in data
        assert "cpu" in data
        assert data["cpu"]["usage_percent"] == 25.5
