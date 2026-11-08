"""
CSV exporter for laptop telemetry.
"""

import csv
import os
from datetime import datetime
from pathlib import Path
from typing import Any

from .base import BaseExporter

# Priority columns that should appear first in CSV output
PRIORITY_COLUMNS = ["serial_number", "start_timestamp", "end_timestamp", "hostname"]


class CSVExporter(BaseExporter):
    """
    Exporter for CSV format telemetry data.

    Writes telemetry data in CSV format with a single file per run.
    Each row represents one collection interval with timestamp.
    Handles nested data structures by flattening them.
    """

    def __init__(self, name: str, output_dir: str = "./logs") -> None:
        """
        Initialize CSV exporter.

        Args:
            name: Exporter name
            output_dir: Output directory for CSV files
        """
        super().__init__(name)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._filepath: Path | None = None
        self._file_handle: Any = None
        self._writer: Any = None
        self._headers_written = False
        self._fieldnames: list[str] | None = None

    def _get_filepath(self) -> Path:
        """Get or create the output file path for this run."""
        if self._filepath is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            hostname = os.environ.get("COMPUTERNAME", "unknown")
            filename = f"telemetry_{hostname}_{timestamp}.csv"
            self._filepath = self.output_dir / filename
        return self._filepath

    def _ensure_file_open(self) -> None:
        """Ensure the CSV file is open for writing."""
        if self._file_handle is None:
            filepath = self._get_filepath()
            # Open in append mode to support multiple exports
            self._file_handle = open(filepath, "a", newline="", encoding="utf-8")

    def _close_file(self) -> None:
        """Close the CSV file if open."""
        if self._file_handle:
            self._file_handle.close()
            self._file_handle = None
            self._writer = None

    def export(self, data: list[dict[str, Any]]) -> bool:
        """
        Export telemetry data to CSV format (appends to single file).

        Args:
            data: List of telemetry records to export

        Returns:
            bool: True if export was successful
        """
        if not data:
            return True

        try:
            self._ensure_file_open()

            # Flatten nested data structures
            flattened_data: list[dict[str, Any]] = []
            for record in data:
                flattened = self._flatten_record(record)
                flattened_data.append(flattened)

            if not flattened_data:
                return True

            # Determine fieldnames from first record with priority ordering
            if self._fieldnames is None:
                all_fields = list(flattened_data[0].keys())
                priority = [c for c in PRIORITY_COLUMNS if c in all_fields]
                others = [c for c in all_fields if c not in PRIORITY_COLUMNS]
                self._fieldnames = priority + others

            # Create writer if not exists
            if self._writer is None:
                self._writer = csv.DictWriter(self._file_handle, fieldnames=self._fieldnames)

            # Write headers if not written yet
            if not self._headers_written:
                self._writer.writeheader()
                self._headers_written = True

            # Write data rows
            for row in flattened_data:
                # Ensure all fieldnames are present
                row_data = {fn: row.get(fn, "") for fn in self._fieldnames}
                self._writer.writerow(row_data)

            # Flush to ensure data is written
            self._file_handle.flush()

            self.handle_success()
            return True

        except Exception as e:
            self.handle_error(e)
            return False

    def close(self) -> None:
        """Close the exporter and file handle."""
        self._close_file()

    def _flatten_record(
        self, record: dict[str, Any], parent_key: str = "", sep: str = "_"
    ) -> dict[str, Any]:
        """
        Flatten nested dictionary structure.

        Args:
            record: Record to flatten
            parent_key: Parent key for nested structures
            sep: Separator for nested keys

        Returns:
            dict[str, Any]: Flattened record
        """
        items: list[tuple[str, Any]] = []

        for key, value in record.items():
            new_key = f"{parent_key}{sep}{key}" if parent_key else key

            if isinstance(value, dict):
                items.extend(self._flatten_record(value, new_key, sep=sep).items())
            elif isinstance(value, list):
                # Flatten list of dictionaries into individual columns
                if value and isinstance(value[0], dict):
                    for i, item in enumerate(value):
                        if isinstance(item, dict):
                            items.extend(
                                self._flatten_record(item, f"{new_key}{sep}{i}", sep=sep).items()
                            )
                        else:
                            items.append((f"{new_key}{sep}{i}", item))
                else:
                    # Convert simple list to string representation
                    items.append((new_key, str(value)))
            else:
                items.append((new_key, value))

        return dict(items)

    def export_single_record(self, record: dict[str, Any]) -> bool:
        """
        Export single telemetry record.

        Args:
            record: Telemetry record to export

        Returns:
            bool: True if export was successful
        """
        return self.export([record])
