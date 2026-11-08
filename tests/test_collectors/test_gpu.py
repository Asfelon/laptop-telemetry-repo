"""
Unit tests for GPU collector.
"""

from src.laptop_telemetry.collectors.gpu import GPUCollector


class TestGPUCollector:
    """Tests for GPUCollector."""

    def test_init(self):
        """Test collector initialization."""
        collector = GPUCollector("gpu")
        assert collector.name == "gpu"
        assert collector.error_count == 0
        assert collector.success_count == 0

    def test_is_enabled_default(self):
        """Test is_enabled with default config."""
        collector = GPUCollector("gpu")
        assert collector.is_enabled() is True

    def test_is_enabled_disabled(self):
        """Test is_enabled with disabled config."""
        collector = GPUCollector("gpu", {"enabled": False})
        assert collector.is_enabled() is False

    def test_collect_placeholder(self):
        """Test placeholder collection."""
        collector = GPUCollector("gpu")
        data = collector.collect()

        assert "gpus" in data
        assert isinstance(data["gpus"], list)
