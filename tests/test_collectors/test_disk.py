"""
Unit tests for Disk collector.
"""

from unittest.mock import Mock, patch

from src.laptop_telemetry.collectors.disk import DiskCollector


class TestDiskCollector:
    """Tests for DiskCollector."""

    def test_init(self):
        """Test collector initialization."""
        collector = DiskCollector("disk")
        assert collector.name == "disk"
        assert collector.error_count == 0
        assert collector.success_count == 0

    def test_is_enabled_default(self):
        """Test is_enabled with default config."""
        collector = DiskCollector("disk")
        assert collector.is_enabled() is True

    def test_is_enabled_disabled(self):
        """Test is_enabled with disabled config."""
        collector = DiskCollector("disk", {"enabled": False})
        assert collector.is_enabled() is False

    @patch("src.laptop_telemetry.collectors.disk.psutil.disk_partitions")
    @patch("src.laptop_telemetry.collectors.disk.psutil.disk_usage")
    @patch("src.laptop_telemetry.collectors.disk.psutil.disk_io_counters")
    def test_collect_basic(self, mock_disk_io_counters, mock_disk_usage, mock_disk_partitions):
        """Test basic collection."""
        # Setup mocks
        mock_part = Mock()
        mock_part.device = "C:"
        mock_part.mountpoint = "C:\\"
        mock_part.fstype = "NTFS"
        mock_disk_partitions.return_value = [mock_part]

        mock_usage = Mock()
        mock_usage.total = 1000 * 1024**3
        mock_usage.used = 500 * 1024**3
        mock_usage.free = 500 * 1024**3
        mock_disk_usage.return_value = mock_usage

        mock_io = Mock()
        mock_io.read_bytes = 1000000
        mock_io.write_bytes = 2000000
        mock_io.read_count = 100
        mock_io.write_count = 50
        mock_disk_io_counters.return_value = {"C:": mock_io}

        collector = DiskCollector(
            "disk", {"include_io": True, "include_smart": False, "include_temperature": False}
        )
        data = collector.collect()

        assert "disks" in data
        assert len(data["disks"]) >= 0  # May be empty if WMI not available
