"""
Unit tests for configuration.
"""

from unittest.mock import mock_open, patch

from src.laptop_telemetry.config.loader import create_default_config, load_config
from src.laptop_telemetry.config.models import CollectionConfig, OutputConfig, TelemetryConfig


class TestConfigModels:
    """Tests for configuration models."""

    def test_default_collection_config(self):
        """Test default collection config."""
        config = CollectionConfig()
        assert config.interval_seconds == 60
        assert config.duration_seconds == 0

    def test_custom_collection_config(self):
        """Test custom collection config."""
        config = CollectionConfig(interval_seconds=30, duration_seconds=3600)
        assert config.interval_seconds == 30
        assert config.duration_seconds == 3600

    def test_default_output_config(self):
        """Test default output config."""
        config = OutputConfig()
        assert config.format.value == "both"
        assert config.directory == "./logs"

    def test_full_telemetry_config(self):
        """Test full telemetry config."""
        config = TelemetryConfig()
        assert config.collection.interval_seconds == 60
        assert config.output.format.value == "both"
        assert config.collectors.cpu.enabled is True
        assert config.collectors.memory.enabled is True
        assert config.collectors.disk.enabled is True


class TestConfigLoader:
    """Tests for configuration loader."""

    def test_create_default_config(self):
        """Test creating default config."""
        config = create_default_config()

        assert "collection" in config
        assert "output" in config
        assert "collectors" in config
        assert "logging" in config
        assert config["collection"]["interval_seconds"] == 60
        assert config["output"]["format"] == "both"

    @patch(
        "src.laptop_telemetry.config.loader.open",
        new_callable=mock_open,
        read_data="collection:\n  interval_seconds: 30\n",
    )
    @patch("src.laptop_telemetry.config.loader.os.path.exists")
    def test_load_config_from_file(self, mock_exists, mock_file):
        """Test loading config from file."""
        mock_exists.return_value = True

        config = load_config("config.yaml")

        assert config.collection.interval_seconds == 30

    @patch("src.laptop_telemetry.config.loader.os.path.exists")
    def test_load_config_default(self, mock_exists):
        """Test loading default config when file doesn't exist."""
        mock_exists.return_value = False

        config = load_config("nonexistent.yaml")

        assert config.collection.interval_seconds == 60
