"""
Unit tests for CPU collector.
"""

import sys
from unittest.mock import Mock, patch

import pytest

from src.laptop_telemetry.collectors.cpu import CPUCollector


class TestCPUCollector:
    """Tests for CPUCollector."""

    def test_init(self):
        """Test collector initialization."""
        collector = CPUCollector("cpu")
        assert collector.name == "cpu"
        assert collector.error_count == 0
        assert collector.success_count == 0

    def test_is_enabled_default(self):
        """Test is_enabled with default config."""
        collector = CPUCollector("cpu")
        assert collector.is_enabled() is True

    def test_is_enabled_disabled(self):
        """Test is_enabled with disabled config."""
        collector = CPUCollector("cpu", {"enabled": False})
        assert collector.is_enabled() is False

    @pytest.mark.skipif(
        sys.platform == "darwin",
        reason="psutil.cpu_freq() not available on macOS",
    )
    @patch("src.laptop_telemetry.collectors.cpu.psutil.cpu_percent")
    @patch("src.laptop_telemetry.collectors.cpu.psutil.cpu_times")
    @patch("src.laptop_telemetry.collectors.cpu.psutil.cpu_freq")
    @patch("src.laptop_telemetry.collectors.cpu.psutil.cpu_count")
    @patch("src.laptop_telemetry.collectors.cpu.psutil.pids")
    @patch("src.laptop_telemetry.collectors.cpu.psutil.process_iter")
    @patch("src.laptop_telemetry.collectors.cpu.psutil.cpu_stats")
    def test_collect_basic(
        self,
        mock_cpu_stats,
        mock_process_iter,
        mock_pids,
        mock_cpu_count,
        mock_cpu_freq,
        mock_cpu_times,
        mock_cpu_percent,
    ):
        """Test basic collection."""
        # Setup mocks
        mock_cpu_percent.return_value = 25.5
        mock_cpu_times.return_value = Mock(
            user=100, system=50, idle=850, dpc=5, interrupt=3, privileged=20
        )
        mock_cpu_freq.return_value = Mock(current=2800, min=800, max=4200)
        mock_cpu_count.side_effect = [4, 8]  # physical, logical
        mock_pids.return_value = [1, 2, 3, 4, 5]
        mock_process_iter.return_value = [
            Mock(info={"status": "running", "num_threads": 10}),
            Mock(info={"status": "sleeping", "num_threads": 5}),
            Mock(info={"status": "sleeping", "num_threads": 3}),
            Mock(info={"status": "sleeping", "num_threads": 2}),
            Mock(info={"status": "sleeping", "num_threads": 1}),
        ]
        mock_cpu_stats.return_value = Mock(ctx_switches=1000, interrupts=500, syscalls=200)

        collector = CPUCollector(
            "cpu",
            {
                "per_core": False,
                "include_temperature": False,
                "include_power": False,
                "include_cache": False,
                "include_system_counters": True,
            },
        )
        data = collector.collect()

        assert "usage_percent" in data
        assert data["usage_percent"] == 25.5
        assert "usage_user_percent" in data
        assert "usage_system_percent" in data
        assert "usage_idle_percent" in data
        assert "usage_dpc_percent" in data
        assert "usage_interrupt_percent" in data
        assert "usage_privileged_percent" in data
        assert "frequency_mhz" in data
        assert data["frequency_mhz"] == 2800
        assert "cores_physical" in data
        assert data["cores_physical"] == 4
        assert "cores_logical" in data
        assert data["cores_logical"] == 8
        assert "context_switches_sec" in data
        assert "interrupts_sec" in data
        assert "syscalls_sec" in data
        assert "processes_total" in data
        assert data["processes_total"] == 5

    @pytest.mark.skipif(
        sys.platform != "darwin",
        reason="Test for macOS where psutil.cpu_freq() is not available",
    )
    @patch("src.laptop_telemetry.collectors.cpu.psutil.cpu_percent")
    @patch("src.laptop_telemetry.collectors.cpu.psutil.cpu_times")
    @patch("src.laptop_telemetry.collectors.cpu.psutil.cpu_count")
    @patch("src.laptop_telemetry.collectors.cpu.psutil.pids")
    @patch("src.laptop_telemetry.collectors.cpu.psutil.process_iter")
    @patch("src.laptop_telemetry.collectors.cpu.psutil.cpu_stats")
    def test_collect_basic_macos(
        self,
        mock_cpu_stats,
        mock_process_iter,
        mock_pids,
        mock_cpu_count,
        mock_cpu_times,
        mock_cpu_percent,
    ):
        """Test basic collection on macOS (no cpu_freq)."""
        # Setup mocks
        mock_cpu_percent.return_value = 25.5
        mock_cpu_times.return_value = Mock(
            user=100, system=50, idle=850, dpc=5, interrupt=3, privileged=20
        )
        mock_cpu_count.side_effect = [4, 8]  # physical, logical
        mock_pids.return_value = [1, 2, 3, 4, 5]
        mock_process_iter.return_value = [
            Mock(info={"status": "running", "num_threads": 10}),
            Mock(info={"status": "sleeping", "num_threads": 5}),
            Mock(info={"status": "sleeping", "num_threads": 3}),
            Mock(info={"status": "sleeping", "num_threads": 2}),
            Mock(info={"status": "sleeping", "num_threads": 1}),
        ]
        mock_cpu_stats.return_value = Mock(ctx_switches=1000, interrupts=500, syscalls=200)

        collector = CPUCollector(
            "cpu",
            {
                "per_core": False,
                "include_temperature": False,
                "include_power": False,
                "include_cache": False,
                "include_system_counters": True,
            },
        )
        data = collector.collect()

        assert "usage_percent" in data
        assert data["usage_percent"] == 25.5
        assert "usage_user_percent" in data
        assert "usage_system_percent" in data
        assert "usage_idle_percent" in data
        assert "usage_dpc_percent" in data
        assert "usage_interrupt_percent" in data
        assert "usage_privileged_percent" in data
        # frequency_mhz should NOT be present on macOS
        assert "frequency_mhz" not in data
        assert "cores_physical" in data
        assert data["cores_physical"] == 4
        assert "cores_logical" in data
        assert data["cores_logical"] == 8
        assert "context_switches_sec" in data
        assert "interrupts_sec" in data
        assert "syscalls_sec" in data
        assert "processes_total" in data
        assert data["processes_total"] == 5
