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
    with optional file rotation and compression.
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

    def export(self, data: list[dict[str, Any]]) -> bool:
        """
        Export telemetry data to JSON Lines format.

        Args:
            data: List of telemetry records to export

        Returns:
            bool: True if export was successful
        """
        if not data:
            return True

        try:
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            hostname = os.environ.get("COMPUTERNAME", "unknown")
            filename = f"telemetry_{hostname}_{timestamp}.jsonl"
            filepath = self.output_dir / filename

            # Write data to file
            with open(filepath, "w", encoding="utf-8") as f:
                for record in data:
                    # Add timestamp if not present
                    if "timestamp" not in record:
                        record["timestamp"] = datetime.now().isoformat()

                    # Write JSON line
                    json.dump(record, f, ensure_ascii=False)
                    f.write("\n")

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
        """Close the exporter."""
        pass
