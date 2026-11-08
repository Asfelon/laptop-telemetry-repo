"""
Unit tests for Memory collector.
"""

from unittest.mock import Mock, patch

from src.laptop_telemetry.collectors.memory import MemoryCollector


class TestMemoryCollector:
    """Tests for MemoryCollector."""

    def test_init(self):
        """Test collector initialization."""
        collector = MemoryCollector("memory")
        assert collector.name == "memory"
        assert collector.error_count == 0
        assert collector.success_count == 0

    def test_is_enabled_default(self):
        """Test is_enabled with default config."""
        collector = MemoryCollector("memory")
        assert collector.is_enabled() is True

    def test_is_enabled_disabled(self):
        """Test is_enabled with disabled config."""
        collector = MemoryCollector("memory", {"enabled": False})
        assert collector.is_enabled() is False

    @patch("src.laptop_telemetry.collectors.memory.psutil.virtual_memory")
    @patch("src.laptop_telemetry.collectors.memory.psutil.swap_memory")
    def test_collect_basic(self, mock_swap_memory, mock_virtual_memory):
        """Test basic collection."""
        # Setup mocks
        mock_vm = Mock()
        mock_vm.total = 16 * 1024**3  # 16 GB
        mock_vm.available = 8 * 1024**3
        mock_vm.used = 8 * 1024**3
        mock_vm.free = 2 * 1024**3
        mock_vm.percent = 50.0
        mock_virtual_memory.return_value = mock_vm

        mock_swap = Mock()
        mock_swap.total = 4 * 1024**3
        mock_swap.used = 1 * 1024**3
        mock_swap.free = 3 * 1024**3
        mock_swap.percent = 25.0
        mock_swap_memory.return_value = mock_swap

        collector = MemoryCollector(
            "memory", {"include_swap": True, "include_page_faults": False, "include_numa": False}
        )
        data = collector.collect()

        assert "total_bytes" in data
        assert data["total_bytes"] == 16 * 1024**3
        assert "available_bytes" in data
        assert data["available_bytes"] == 8 * 1024**3
        assert "used_bytes" in data
        assert data["used_bytes"] == 8 * 1024**3
        assert "free_bytes" in data
        assert data["free_bytes"] == 2 * 1024**3
        assert "usage_percent" in data
        assert data["usage_percent"] == 50.0
        assert "swap_total_bytes" in data
        assert data["swap_total_bytes"] == 4 * 1024**3
        assert "swap_used_bytes" in data
        assert data["swap_used_bytes"] == 1 * 1024**3
        assert "swap_free_bytes" in data
        assert data["swap_free_bytes"] == 3 * 1024**3
        assert "swap_usage_percent" in data
        assert data["swap_usage_percent"] == 25.0
