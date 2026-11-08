"""
Unit tests for Network collector.
"""

from unittest.mock import Mock, patch

from src.laptop_telemetry.collectors.network import NetworkCollector


class TestNetworkCollector:
    """Tests for NetworkCollector."""

    def test_init(self):
        """Test collector initialization."""
        collector = NetworkCollector("network")
        assert collector.name == "network"
        assert collector.error_count == 0
        assert collector.success_count == 0

    def test_is_enabled_default(self):
        """Test is_enabled with default config."""
        collector = NetworkCollector("network")
        assert collector.is_enabled() is True

    def test_is_enabled_disabled(self):
        """Test is_enabled with disabled config."""
        collector = NetworkCollector("network", {"enabled": False})
        assert collector.is_enabled() is False

    @patch("src.laptop_telemetry.collectors.network.psutil.net_io_counters")
    @patch("src.laptop_telemetry.collectors.network.psutil.net_if_addrs")
    @patch("src.laptop_telemetry.collectors.network.psutil.net_if_stats")
    def test_collect_basic(self, mock_net_if_stats, mock_net_if_addrs, mock_net_io_counters):
        """Test basic collection."""
        # Setup mocks
        mock_io = Mock()
        mock_io.bytes_sent = 1000000
        mock_io.bytes_recv = 2000000
        mock_io.packets_sent = 1000
        mock_io.packets_recv = 2000
        mock_io.errin = 0
        mock_io.errout = 0
        mock_io.dropin = 0
        mock_io.dropout = 0
        mock_net_io_counters.return_value = {"Ethernet": mock_io}

        mock_addr = Mock()
        mock_addr.family = 2  # AF_INET
        mock_addr.address = "192.168.1.100"
        mock_net_if_addrs.return_value = {"Ethernet": [mock_addr]}

        mock_stat = Mock()
        mock_stat.speed = 1000
        mock_stat.isup = True
        mock_stat.mtu = 1500
        mock_net_if_stats.return_value = {"Ethernet": mock_stat}

        collector = NetworkCollector("network", {"interfaces": "all"})
        data = collector.collect()

        assert "interfaces" in data
        assert len(data["interfaces"]) >= 0
