# Laptop Telemetry Collector - Codebase Documentation

## Overview

A Windows-only Python application that collects comprehensive laptop telemetry (80+ metrics at minute-level granularity) including CPU breakdown (user/dpc/interrupt/privileged), all physical disks with split I/O, cache memory, thermals, fan speeds, and more. Logs to JSON/CSV for later analysis.

**Version**: 0.1.0  
**Python**: 3.10+  
**Platform**: Windows 10/11

---

## Architecture

```
laptop-telemetry/
├── src/
│   └── laptop_telemetry/
│       ├── __init__.py           # Package exports
│       ├── __main__.py           # CLI entry point (Click-based)
│       ├── config/               # Configuration management
│       │   ├── __init__.py
│       │   ├── models.py         # Pydantic v2 config models
│       │   └── loader.py         # Config loading/validation
│       ├── collectors/           # Telemetry collectors (9 collectors)
│       │   ├── __init__.py
│       │   ├── base.py           # BaseCollector abstract class
│       │   ├── registry.py       # Collector registry & factory
│       │   ├── cpu.py            # CPU metrics (psutil + OHM)
│       │   ├── memory.py         # Memory metrics (psutil)
│       │   ├── disk.py           # Disk metrics (psutil + WMI)
│       │   ├── network.py        # Network metrics (psutil)
│       │   ├── thermal.py        # Temperature sensors (OHM)
│       │   ├── fan.py            # Fan speed sensors (OHM)
│       │   ├── voltage.py        # Voltage rails (OHM)
│       │   ├── battery.py        # Battery metrics (WMI)
│       │   ├── gpu.py            # GPU metrics (OHM)
│       │   └── ohm_manager.py    # OpenHardwareMonitor singleton
│       ├── exporter/             # Data exporters
│       │   ├── __init__.py
│       │   ├── base.py           # BaseExporter abstract class
│       │   ├── json_exporter.py  # JSON Lines output
│       │   └── csv_exporter.py   # CSV output (flattened)
│       ├── scheduler/            # Collection scheduling
│       │   ├── __init__.py
│       │   └── runner.py         # TelemetryRunner (main loop)
│       └── utils/                # Utilities
│           ├── __init__.py
│           ├── hardware.py       # Hardware detection
│           └── windows.py        # Windows-specific utilities
├── tests/                        # Test suite (53 tests)
├── config/
│   └── default.yaml              # Default configuration
├── pyproject.toml                # Project metadata & tooling
├── README.md                     # User documentation
└── LICENSE                       # MIT License
```

---

## Core Components

### 1. Configuration System (`config/`)

**Models** (`config/models.py`):
- Uses **Pydantic v2** with `ConfigDict` for validation
- `OutputFormat` enum: `JSONL`, `CSV`, `BOTH` (new default)
- `TelemetryConfig` - root config with nested models:
  - `CollectionConfig` - interval, duration
  - `OutputConfig` - format, directory, filename_template, rotation
  - `CollectorsConfig` - per-collector settings (CPU, Memory, Disk, etc.)
  - `LoggingConfig` - log level, file, rotation, retention
  - `OpenHardwareMonitorConfig` - DLL path

**Loader** (`config/loader.py`):
- `load_config()` - loads from YAML file or defaults
- `create_default_config()` - generates default config dict
- Environment variable override: `OPENHARDWAREMONITOR_DLL`

### 2. Collector Framework (`collectors/`)

**Base Classes** (`collectors/base.py`):
- `CollectorProtocol` - structural typing interface
- `BaseCollector` - abstract base with:
  - `collect()` → `dict[str, Any]` (must implement)
  - `is_enabled()` - config-based enablement
  - Statistics tracking (success/error counts, success rate)
- `CollectorRegistry` - registration & instantiation

**Registry** (`collectors/registry.py`):
- `TelemetryCollectorRegistry` - enhanced registry
- `create_enabled_collectors(config)` - factory for all enabled collectors
- Handles OHM-dependent collectors (thermal, fan, voltage, gpu) with shared config

**OHM Manager** (`collectors/ohm_manager.py`):
- Thread-safe singleton for OpenHardwareMonitor connection
- Manages hardware initialization, sensor updates, cleanup
- Provides `SensorType` and `HardwareType` enums from OHM

**Individual Collectors** (9 total):
| Collector | Source | Key Metrics |
|-----------|--------|-------------|
| `cpu.py` | psutil + OHM | Usage breakdown (user/sys/idle/dpc/interrupt/privileged), per-core, frequency, temp, power, cache, system counters, process/thread counts |
| `memory.py` | psutil | Virtual memory, swap, page faults, NUMA |
| `disk.py` | psutil + WMI | Per physical disk: usage, I/O rates, latency, queue depth, split I/O, SMART, hardware info |
| `network.py` | psutil | Per interface: throughput, packets, errors, drops, IP/MAC, link speed |
| `thermal.py` | OHM | All temperature sensors (CPU package/cores, GPU, motherboard, VRM, storage) |
| `fan.py` | OHM | RPM, min/max RPM, duty cycle %, control mode |
| `voltage.py` | OHM | Key rails (Vcore, VCCIO, DRAM, 3.3V, 5V, 12V) with min/max |
| `battery.py` | WMI | Capacity (design/full/remaining), status, charge %, time remaining, cycle count, temp, voltage, current |
| `gpu.py` | OHM | Usage, memory, temperature, fan, power, clocks, driver info |

### 3. Export System (`exporter/`)

**Base** (`exporter/base.py`):
- `BaseExporter` - abstract with `export(data: List[Dict]) → bool`
- Statistics tracking (export_count, error_count, success_rate)

**JSON Exporter** (`exporter/json_exporter.py`):
- JSON Lines format (one JSON object per line)
- Creates new file per collection with timestamp: `telemetry_{hostname}_{timestamp}.jsonl`

**CSV Exporter** (`exporter/csv_exporter.py`):
- Flattens nested structures with underscore separator
- Priority columns first: `serial_number`, `start_timestamp`, `end_timestamp`, `hostname`
- Appends to single file per run: `telemetry_{hostname}_{timestamp}.csv`
- Handles lists of dicts by creating indexed columns

### 4. Scheduler (`scheduler/runner.py`)

**TelemetryRunner** - Main orchestration class:
- Interval-aligned collection loop (sleeps to next interval boundary)
- Pre-creates all collectors at startup (not per-interval)
- Parallel collection for non-OHM collectors (ThreadPoolExecutor, max_workers=4)
- Sequential collection for OHM collectors (shared connection)
- Exports to all configured exporters
- Duration limiting with pre/post collection checks
- Graceful shutdown with exporter cleanup

### 5. CLI (`__main__.py`)

**Click-based CLI** with commands:
- `laptop_telemetry` (default) - run collector
- `laptop_telemetry run` - explicit run command
- `laptop_telemetry generate-config` - create default YAML config

**Options**:
- `-c, --config` - config file path
- `-i, --interval` - collection interval (seconds)
- `-o, --output` - output directory
- `-f, --format` - `jsonl`, `csv`, or `both` (default: both)
- `-d, --duration` - duration in seconds (0 = infinite)
- `--once` - collect once and exit
- `--dry-run` - show what would be collected
- `--list-sensors` - list available sensors
- `--collector-status` - show collector enabled status
- `--validate-config` - validate config and exit

---

## Data Flow

```
┌─────────────────┐
│   CLI / Config  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ TelemetryRunner │
│  (scheduler)    │
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌───────┐ ┌─────────┐
│ OHM   │ │ Other   │
│ Coll. │ │ Coll.   │
│(seq)  │ │(parallel)│
└───┬───┘ └────┬────┘
    │          │
    └────┬─────┘
         ▼
┌─────────────────┐
│  Merge Data     │
│ (serial_number, │
│  timestamps,    │
│  hostname,      │
│  collector data)│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Exporters     │
│  (JSON + CSV)   │
└─────────────────┘
```

---

## Configuration Reference

### Default Configuration (`config/default.yaml`)

```yaml
collection:
  interval_seconds: 60
  duration_seconds: 0  # 0 = infinite

output:
  format: "both"              # jsonl, csv, or both
  directory: "./logs"
  filename_template: "telemetry_{hostname}_{date}.{ext}"
  rotation:
    max_size_mb: 100
    max_files: 30
    compress: true

collectors:
  cpu:
    enabled: true
    per_core: true
    include_temperature: true
    include_power: true
    include_cache: true
    include_system_counters: true
  memory:
    enabled: true
    include_swap: true
    include_page_faults: true
    include_numa: true
  disk:
    enabled: true
    physical_disks: "all"
    partitions: "all"
    include_io: true
    include_smart: true
    include_temperature: true
  network:
    enabled: true
    interfaces: "all"
  thermal:
    enabled: true
    sensors: "all"
  fan:
    enabled: true
    sensors: "all"
  voltage:
    enabled: true
    rails: "all"
  battery:
    enabled: true
  gpu:
    enabled: true
    devices: "all"

openhardwaremonitor:
  dll_path: null  # Set via OPENHARDWAREMONITOR_DLL env var

logging:
  level: "INFO"
  file: "./logs/collector.log"
  rotation: "10 MB"
  retention: "30 days"
```

### Filename Template Variables

- `{hostname}` - Computer name
- `{date}` - Date in YYYYMMDD format
- `{ext}` - Extension placeholder (replaced with `jsonl` or `csv`)

---

## Output Formats

### JSON Lines (`.jsonl`)

Each line is a complete JSON object with all metrics for that collection interval. Nested structure preserved.

```json
{
  "serial_number": "ABC123",
  "start_timestamp": "2026-11-08T10:30:00",
  "end_timestamp": "2026-11-08T10:30:02",
  "hostname": "LAPTOP-ABC123",
  "cpu": {
    "usage_percent": 23.5,
    "usage_user_percent": 15.2,
    "usage_per_core": [...]
  },
  "memory": {...},
  "disk": [...]
}
```

### CSV (`.csv`)

Flattened structure with nested keys joined by underscores:
- `cpu_usage_percent`
- `cpu_usage_per_core_0_total`
- `disk_0_read_bytes_sec`
- `thermal_0_value`

Priority columns appear first: `serial_number`, `start_timestamp`, `end_timestamp`, `hostname`

---

## Hardware Sensor Support

For thermal, fan, voltage, and GPU metrics, the collector uses **OpenHardwareMonitorLib** via pythonnet:

1. Download OpenHardwareMonitor from https://openhardwaremonitor.org/
2. Extract `OpenHardwareMonitorLib.dll` to a known location
3. Set environment variable:

```powershell
$env:OPENHARDWAREMONITOR_DLL = "C:\path\to\OpenHardwareMonitorLib.dll"
```

Or configure in YAML:
```yaml
openhardwaremonitor:
  dll_path: "C:/path/to/OpenHardwareMonitorLib.dll"
```

Without OpenHardwareMonitor, the collector falls back to WMI for basic temperature data.

---

## Development

### Setup

```bash
# Install dependencies
pip install -e .

# Install with development dependencies
pip install -e ".[dev]"
```

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=term-missing

# Run specific test module
pytest tests/test_config.py -v
```

### Code Quality

```bash
# Linting
ruff check src/
ruff format src/

# Type checking
mypy src/
```

### Project Standards

- **Python 3.10+** with modern type hints
- **Pydantic v2** for configuration validation
- **dataclasses with slots=True** for performance
- **Protocol** for structural typing
- **Google-style docstrings**
- **Ruff** for linting/formatting (line-length=100)
- **pytest** for testing

---

## Key Design Decisions

1. **Pre-create collectors at startup** - Avoids overhead of instantiation per interval
2. **OHM collectors run sequentially** - Share single OHM connection (thread-safe singleton)
3. **Other collectors run in parallel** - ThreadPoolExecutor with 4 workers
4. **Interval-aligned collection** - Sleeps to next interval boundary for consistent timestamps
5. **Dual output by default** - Both JSONL and CSV generated simultaneously
6. **Flattened CSV** - Nested structures flattened with underscore separator for analysis tools
7. **Windows-only** - Uses psutil, WMI, and OpenHardwareMonitorLib (Windows-specific)

---

## Extending the Collector

### Adding a New Collector

1. Create `collectors/new_collector.py` inheriting from `BaseCollector`
2. Implement `collect()` method returning `dict[str, Any]`
3. Add config model in `config/models.py` (e.g., `NewCollectorConfig`)
4. Register in `scheduler/runner.py` `_register_collectors()`
5. Add to `config/default.yaml` under `collectors`
6. Add tests in `tests/test_collectors/test_new_collector.py`

### Adding a New Exporter

1. Create `exporter/new_exporter.py` inheriting from `BaseExporter`
2. Implement `export(data: List[Dict]) → bool`
3. Add to `scheduler/runner.py` `_initialize_exporters()`
4. Add format option to `OutputFormat` enum and CLI choices

---

## Dependencies

| Package | Purpose |
|---------|---------|
| `psutil>=5.9.0` | System metrics (CPU, memory, disk, network) |
| `wmi>=1.5.1` | Windows Management Instrumentation |
| `pythonnet>=3.0.0` | .NET interop for OpenHardwareMonitorLib |
| `pydantic>=2.5.0` | Configuration validation |
| `pyyaml>=6.0` | YAML config file parsing |
| `loguru>=0.7.0` | Logging |
| `click>=8.1.0` | CLI framework |
| `pandas>=2.0.0` | Data processing (used in tests) |

### Dev Dependencies

| Package | Purpose |
|---------|---------|
| `pytest>=7.4.0` | Testing framework |
| `pytest-mock>=3.12.0` | Mocking utilities |
| `pytest-cov>=4.1.0` | Coverage reporting |
| `ruff>=0.1.0` | Linting/formatting |
| `mypy>=1.7.0` | Type checking |
| `black>=23.0.0` | Code formatting |

---

## License

MIT License - See LICENSE file for details.