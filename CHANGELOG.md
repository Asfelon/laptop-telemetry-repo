> **⚠️ Disclaimer**: This CHANGELOG.md file is **LLM-generated for testing purposes only**. It is a **sample and not legally binding**. Do not use this Changelog for production purposes without proper legal review.

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial project structure with src-layout
- CPU, Memory, Disk, Network, Thermal, Fan, Voltage, Battery, GPU collectors
- JSON Lines and CSV exporters with file rotation
- Interval-aligned scheduler with precise timing
- YAML configuration with Pydantic validation
- CLI with Click (interval, output, format, duration, once, dry-run options)
- OpenHardwareMonitor integration for enhanced sensor data
- Comprehensive test suite with pytest

### Changed
- JSONExporter now uses single file per run (like CSVExporter), appending records across multiple export() calls instead of creating a new file each time
- Fixed ruff deprecation warning by moving lint settings to [tool.ruff.lint] section in pyproject.toml

### Deprecated
- N/A

### Removed
- N/A

### Fixed
- N/A

### Security
- N/A

## [0.1.0] - 2026-11-08

### Added
- Initial release of laptop-telemetry
- Windows-only telemetry collection for 80+ metrics
- Collector registry pattern for extensibility
- Dual output format (JSONL + CSV)
- Configuration-driven collection
- Hardware detection utilities