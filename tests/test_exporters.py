"""
Unit tests for exporters.
"""

import tempfile
from unittest.mock import mock_open, patch

from src.laptop_telemetry.exporter.csv_exporter import CSVExporter
from src.laptop_telemetry.exporter.json_exporter import JSONExporter


class TestJSONExporter:
    """Tests for JSONExporter."""

    def test_init(self):
        """Test exporter initialization."""
        with tempfile.TemporaryDirectory() as tmpdir:
            exporter = JSONExporter("json", tmpdir)
            assert exporter.name == "json"
            assert str(exporter.output_dir) == tmpdir

    def test_export_empty(self):
        """Test exporting empty data."""
        with tempfile.TemporaryDirectory() as tmpdir:
            exporter = JSONExporter("json", tmpdir)
            result = exporter.export([])
            assert result is True

    @patch("src.laptop_telemetry.exporter.json_exporter.open", new_callable=mock_open)
    @patch("src.laptop_telemetry.exporter.json_exporter.datetime")
    @patch("src.laptop_telemetry.exporter.json_exporter.os.environ.get")
    def test_export_data(self, mock_environ, mock_datetime, mock_file):
        """Test exporting data."""
        mock_environ.return_value = "TEST-PC"
        mock_datetime.now.return_value.strftime.return_value = "20261107_213000"
        mock_datetime.now.return_value.isoformat.return_value = "2026-11-07T21:30:00"

        with tempfile.TemporaryDirectory() as tmpdir:
            exporter = JSONExporter("json", tmpdir)
            data = [{"cpu": {"usage_percent": 25.5}, "memory": {"usage_percent": 50.0}}]
            result = exporter.export(data)

            assert result is True
            mock_file.assert_called()


class TestCSVExporter:
    """Tests for CSVExporter."""

    def test_init(self):
        """Test exporter initialization."""
        with tempfile.TemporaryDirectory() as tmpdir:
            exporter = CSVExporter("csv", tmpdir)
            assert exporter.name == "csv"
            assert str(exporter.output_dir) == tmpdir

    def test_export_empty(self):
        """Test exporting empty data."""
        with tempfile.TemporaryDirectory() as tmpdir:
            exporter = CSVExporter("csv", tmpdir)
            result = exporter.export([])
            assert result is True

    def test_flatten_record(self):
        """Test record flattening."""
        with tempfile.TemporaryDirectory() as tmpdir:
            exporter = CSVExporter("csv", tmpdir)
            record = {
                "cpu": {"usage_percent": 25.5, "frequency_mhz": 2800},
                "memory": {"usage_percent": 50.0},
            }
            flattened = exporter._flatten_record(record)

            assert "cpu_usage_percent" in flattened
            assert flattened["cpu_usage_percent"] == 25.5
            assert "cpu_frequency_mhz" in flattened
            assert flattened["cpu_frequency_mhz"] == 2800
            assert "memory_usage_percent" in flattened
            assert flattened["memory_usage_percent"] == 50.0
