"""
JSON exporter for laptop telemetry.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

from .base import BaseExporter


class JSONExporter(BaseExporter):
    """
    Exporter for JSON format telemetry data.

    Writes telemetry data in JSON Lines format (one JSON object per line)
    with a single file per run, appending records across multiple export() calls.
    """

    def __init__(self, name: str, output_dir: str = "./logs") -> None:
        """
        Initialize JSON exporter.

        Args:
            name: Exporter name
            output_dir: Output directory for JSON files
        """
        super().__init__(name)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._filepath: Path | None = None
        self._file_handle: Any = None

    def _get_filepath(self) -> Path:
        """Get or create the output file path for this run."""
        if self._filepath is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            hostname = os.environ.get("COMPUTERNAME", "unknown")
            filename = f"telemetry_{hostname}_{timestamp}.jsonl"
            self._filepath = self.output_dir / filename
        return self._filepath

    def _ensure_file_open(self) -> None:
        """Ensure the JSONL file is open for writing."""
        if self._file_handle is None:
            filepath = self._get_filepath()
            # Open in append mode to support multiple exports
            self._file_handle = open(filepath, "a", encoding="utf-8")

    def _close_file(self) -> None:
        """Close the JSONL file if open."""
        if self._file_handle:
            self._file_handle.close()
            self._file_handle = None

    def export(self, data: list[dict[str, Any]]) -> bool:
        """
        Export telemetry data to JSON Lines format (appends to single file).

        Args:
            data: List of telemetry records to export

        Returns:
            bool: True if export was successful
        """
        if not data:
            return True

        try:
            self._ensure_file_open()

            for record in data:
                # Add timestamp if not present
                if "timestamp" not in record:
                    record["timestamp"] = datetime.now().isoformat()

                # Write JSON line
                json.dump(record, self._file_handle, ensure_ascii=False)
                self._file_handle.write("\n")

            # Flush to ensure data is written
            self._file_handle.flush()

            self.handle_success()
            return True

        except Exception as e:
            self.handle_error(e)
            return False

    def export_single_record(self, record: dict[str, Any]) -> bool:
        """
        Export single telemetry record.

        Args:
            record: Telemetry record to export

        Returns:
            bool: True if export was successful
        """
        return self.export([record])

    def close(self) -> None:
        """Close the exporter and file handle."""
        self._close_file()
