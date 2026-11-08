# Laptop Telemetry Collector

A Windows-only Python application that collects comprehensive laptop telemetry (80+ metrics at minute-level granularity) including CPU breakdown (user/dpc/interrupt/privileged), all physical disks with split I/O, cache memory, thermals, fan speeds, and more. Logs to JSON/CSV for later analysis.

## Features

- **CPU Metrics**: Overall usage, per-core usage, user/system/idle/DPC/interrupt/privileged breakdown, frequency (current/min/max), temperature, power consumption, cache hierarchy, system counters (context switches, interrupts, syscalls), process/thread counts
- **Memory Metrics**: Virtual memory (total, available, used, free, active, inactive, modified, standby, cached, shared, buffers, page tables, commit limit, committed, dirty, writeback, mapped, nonpaged/paged pool), swap, page fault details, NUMA stats
- **Disk Metrics**: Per physical disk (not just partitions), usage, I/O rates (bytes/sec, IOPS), latency, queue depth, split I/O/sec, idle time %, temperature, SMART health attributes, hardware info (model, serial, firmware, interface, media type)
- **Network Metrics**: Per interface throughput, packets, errors, drops, IP/MAC addresses, link speed
- **Thermal Metrics**: All temperature sensors (CPU package/cores, GPU core/memory, motherboard, VRM, storage)
- **Fan Metrics**: RPM, min/max RPM, duty cycle %, control mode
- **Voltage Metrics**: Key rails (Vcore, VCCIO, DRAM, 3.3V, 5V, 12V) with min/max tracking
- **Battery Metrics**: Capacity (design/full/remaining), status, charge %, time remaining, cycle count, temperature, voltage, current, manufacturer info
- **GPU Metrics**: Usage, memory, temperature, fan, power, clocks, driver info

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd laptop-telemetry

# Install dependencies
pip install -e .

# Or install with development dependencies
pip install -e ".[dev]"
```

## Quick Start

```bash
# Run with default configuration (60s interval, JSONL output)
python -m laptop_telemetry

# Run with custom interval and output directory
python -m laptop_telemetry --interval 30 --output ./my_logs

# Run once and exit
python -m laptop_telemetry --once

# Generate default configuration file
python -m laptop_telemetry generate-config --output config/my_config.yaml

# Run with custom configuration
python -m laptop_telemetry --config config/my_config.yaml
```

## Configuration

The collector uses a YAML configuration file. Generate a default configuration:

```bash
python -m laptop_telemetry generate-config --output config/default.yaml
```

### Configuration Options

```yaml
collection:
  interval_seconds: 60      # Collection interval (1-3600 seconds)
  duration_seconds: 0       # Duration (0 = infinite)

output:
  format: "jsonl"           # jsonl or csv
  directory: "./logs"       # Output directory
  filename_template: "telemetry_{hostname}_{date}.jsonl"
  rotation:
    max_size_mb: 100        # Max file size before rotation
    max_files: 30           # Max number of rotated files
    compress: true          # Compress rotated files

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

logging:
  level: "INFO"
  file: "./logs/collector.log"
  rotation: "10 MB"
  retention: "30 days"
```

## CLI Options

```bash
python -m laptop_telemetry --help

Options:
  -c, --config PATH         Path to configuration file
  -i, --interval INTEGER    Collection interval in seconds
  -o, --output PATH         Output directory
  -f, --format [jsonl|csv]  Output format
  -d, --duration INTEGER    Duration in seconds (0 = infinite)
  --once                    Collect once and exit
  --dry-run                 Show what would be collected without collecting
  --list-sensors            List available sensors and exit
  --collector-status        Show collector status and exit
  --validate-config         Validate configuration and exit
```

## Output Format

### JSON Lines (default)

Each line is a complete JSON object with all metrics for that collection interval:

```json
{
  "timestamp": "2026-11-07T21:30:00.123456+05:30",
  "hostname": "LAPTOP-ABC123",
  "collection_interval_seconds": 60,
  "cpu": {
    "usage_percent": 23.5,
    "usage_user_percent": 15.2,
    "usage_system_percent": 5.1,
    "usage_idle_percent": 76.5,
    "usage_dpc_percent": 0.8,
    "usage_interrupt_percent": 0.5,
    "usage_privileged_percent": 8.2,
    "usage_per_core": [...],
    "frequency_mhz": 2800,
    "frequency_min_mhz": 800,
    "frequency_max_mhz": 4200,
    "frequency_per_core_mhz": [2700, 2900, 2800, 2850],
    "temperature_celsius": 52.0,
    "temperature_per_core_celsius": [50.0, 53.0, 51.0, 52.0],
    "power_watts": 15.3,
    "power_package_watts": 12.1,
    "power_cores_watts": 8.5,
    "power_gpu_watts": 3.2,
    "context_switches_sec": 12500,
    "interrupts_sec": 8500,
    "syscalls_sec": 4200,
    "processes_total": 245,
    "processes_running": 3,
    "processes_sleeping": 240,
    "threads_total": 3120,
    "cores_physical": 4,
    "cores_logical": 8,
    "cache_l1d_kb": 192,
    "cache_l1i_kb": 192,
    "cache_l2_kb": 2048,
    "cache_l3_kb": 8192
  },
  "memory": {...},
  "disk": [...],
  "network": [...],
  "thermal": [...],
  "fan": [...],
  "voltage": [...],
  "battery": {...},
  "gpu": [...]
}
```

### CSV

Flattened structure with nested keys joined by underscores (e.g., `cpu_usage_percent`, `cpu_usage_per_core_0_total`).

## Requirements

- Windows 10/11
- Python 3.10+
- Dependencies: psutil, wmi, pythonnet, pydantic, pyyaml, loguru, click, pandas

## Hardware Sensor Support

For thermal, fan, voltage, and GPU metrics, the collector uses **OpenHardwareMonitorLib** via pythonnet. To enable these:

1. Download OpenHardwareMonitor from https://openhardwaremonitor.org/
2. Extract `OpenHardwareMonitorLib.dll` to a known location
3. Set the `OPENHARDWAREMONITOR_DLL` environment variable to the DLL path

```powershell
$env:OPENHARDWAREMONITOR_DLL = "C:\path\to\OpenHardwareMonitorLib.dll"
```

Without OpenHardwareMonitor, the collector falls back to WMI for basic temperature data.

## Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
ruff check src/
ruff format src/

# Type checking
mypy src/
```

## Project Structure

```
laptop-telemetry/
├── src/
│   └── laptop_telemetry/
│       ├── __init__.py
│       ├── __main__.py          # CLI entry point
│       ├── config/
│       │   ├── __init__.py
│       │   ├── models.py        # Pydantic config models
│       │   └── loader.py        # Config loading
│       ├── collectors/
│       │   ├── __init__.py
│       │   ├── base.py          # Base collector class
│       │   ├── registry.py      # Collector registry
│       │   ├── cpu.py           # CPU metrics
│       │   ├── memory.py        # Memory metrics
│       │   ├── disk.py          # Disk metrics
│       │   ├── network.py       # Network metrics
│       │   ├── thermal.py       # Temperature sensors
│       │   ├── fan.py           # Fan speed sensors
│       │   ├── voltage.py       # Voltage rails
│       │   ├── battery.py       # Battery metrics
│       │   └── gpu.py           # GPU metrics
│       ├── exporter/
│       │   ├── __init__.py
│       │   ├── base.py          # Base exporter class
│       │   ├── json_exporter.py # JSON Lines output
│       │   └── csv_exporter.py  # CSV output
│       ├── scheduler/
│       │   ├── __init__.py
│       │   └── runner.py        # Collection scheduler
│       └── utils/
│           ├── __init__.py
│           ├── hardware.py      # Hardware detection
│           └── windows.py       # Windows utilities
├── tests/
├── config/
│   └── default.yaml
├── pyproject.toml
├── README.md
└── LICENSE
```

## License

MIT License