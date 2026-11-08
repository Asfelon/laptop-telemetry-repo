# Laptop Telemetry Collector - Architecture Design

## Project Overview
A Windows-only Python application that collects **comprehensive** laptop telemetry (80+ metrics at minute-level granularity) including CPU breakdown (user/dpc/interrupt/privileged), all physical disks with split I/O, cache memory, thermals, fan speeds, and more. Logs to JSON/CSV for later analysis.

## Technology Stack

### Core Libraries
| Library | Purpose | Windows Support |
|---------|---------|-----------------|
| `psutil` | CPU, RAM, Disk, Network, Process info | ✅ Excellent |
| `wmi` | Windows Management Instrumentation queries | ✅ Native |
| `pythonnet` + `OpenHardwareMonitorLib` | Hardware sensors (temps, fans, voltages) | ✅ Best for thermals/fans |
| `pypiwin32` / `pywin32` | Windows API access | ✅ Native |

### Logging & Config
| Library | Purpose |
|---------|---------|
| `loguru` | Structured logging with rotation |
| `pydantic` | Configuration validation |
| `pyyaml` | YAML config file support |
| `click` / `argparse` | CLI argument parsing |

### Testing
| Library | Purpose |
|---------|---------|
| `pytest` | Unit testing |
| `pytest-mock` | Mocking hardware calls |

---

## Project Structure

```
laptop-telemetry/
├── src/
│   └── laptop_telemetry/
│       ├── __init__.py
│       ├── __main__.py          # Entry point
│       ├── config/
│       │   ├── __init__.py
│       │   ├── models.py        # Pydantic config models
│       │   └── loader.py        # Config loading (YAML + CLI)
│       ├── collectors/
│       │   ├── __init__.py
│       │   ├── base.py          # Abstract base collector
│       │   ├── cpu.py           # CPU metrics (usage, freq, temp, power, cache)
│       │   ├── memory.py        # RAM metrics (virtual, swap, page faults, NUMA)
│       │   ├── disk.py          # Disk metrics (physical + partitions, I/O, SMART)
│       │   ├── network.py       # Network metrics (per interface, throughput, errors)
│       │   ├── thermal.py       # Temperature sensors (CPU, GPU, MB, storage, VRM)
│       │   ├── fan.py           # Fan speed sensors (RPM, duty cycle, control mode)
│       │   ├── voltage.py       # Voltage rails (Vcore, VCCIO, DRAM, 3.3V, 5V, 12V)
│       │   ├── battery.py       # Battery metrics (capacity, health, status, info)
│       │   ├── gpu.py           # GPU metrics (usage, memory, clocks, power, driver)
│       │   └── registry.py      # Collector registry/factory
│       ├── exporters/
│       │   ├── __init__.py
│       │   ├── base.py          # Abstract base exporter
│       │   ├── json_exporter.py # JSON Lines output
│       │   └── csv_exporter.py  # CSV output
│       ├── scheduler/
│       │   ├── __init__.py
│       │   └── runner.py        # Periodic collection scheduler
│       └── utils/
│           ├── __init__.py
│           ├── hardware.py      # Hardware detection helpers
│           └── windows.py       # Windows-specific utilities
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_collectors/
│   │   ├── test_cpu.py
│   │   ├── test_memory.py
│   │   ├── test_disk.py
│   │   ├── test_network.py
│   │   ├── test_thermal.py
│   │   ├── test_fan.py
│   │   ├── test_voltage.py
│   │   ├── test_battery.py
│   │   └── test_gpu.py
│   └── test_integration.py
├── config/
│   └── default.yaml             # Default configuration
├── scripts/
│   └── install_ohm.py           # OpenHardwareMonitor setup helper
├── pyproject.toml
├── README.md
├── LICENSE
└── .gitignore
```

---

## Data Models

### Telemetry Sample (JSON Lines format) - 80+ Metrics per Minute Record
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
    "usage_per_core": [
      {"core": 0, "total": 15.2, "user": 10.1, "system": 3.2, "idle": 84.8, "dpc": 0.5, "interrupt": 0.3, "privileged": 1.1},
      {"core": 1, "total": 30.1, "user": 22.3, "system": 4.1, "idle": 69.9, "dpc": 1.2, "interrupt": 0.8, "privileged": 1.7},
      {"core": 2, "total": 18.7, "user": 12.4, "system": 3.8, "idle": 81.3, "dpc": 0.4, "interrupt": 0.2, "privileged": 1.9},
      {"core": 3, "total": 25.4, "user": 18.7, "system": 3.5, "idle": 74.6, "dpc": 1.1, "interrupt": 0.6, "privileged": 1.5}
    ],
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
  "memory": {
    "total_bytes": 17179869184,
    "available_bytes": 8589934592,
    "used_bytes": 8589934592,
    "free_bytes": 2147483648,
    "usage_percent": 50.0,
    "active_bytes": 4294967296,
    "inactive_bytes": 2147483648,
    "modified_bytes": 1073741824,
    "standby_bytes": 3221225472,
    "cached_bytes": 3221225472,
    "shared_bytes": 536870912,
    "buffers_bytes": 268435456,
    "page_tables_bytes": 67108864,
    "commit_limit_bytes": 25769803776,
    "committed_as_bytes": 12884901888,
    "dirty_bytes": 16777216,
    "writeback_bytes": 8388608,
    "mapped_bytes": 1073741824,
    "nonpaged_pool_bytes": 536870912,
    "paged_pool_bytes": 1073741824,
    "swap_total_bytes": 4294967296,
    "swap_used_bytes": 1073741824,
    "swap_free_bytes": 3221225472,
    "swap_usage_percent": 25.0,
    "page_faults_sec": 2000,
    "page_reads_sec": 256,
    "page_writes_sec": 128,
    "cache_faults_sec": 500,
    "transition_faults_sec": 50,
    "demand_zero_faults_sec": 1500,
    "copy_on_write_faults_sec": 200
  },
  "disk": [
    {
      "device": "C:",
      "device_id": "\\\\.\\PHYSICALDRIVE0",
      "mountpoint": "C:\\",
      "fstype": "NTFS",
      "total_bytes": 1000204886016,
      "used_bytes": 450123456789,
      "free_bytes": 550081429227,
      "usage_percent": 45.0,
      "read_bytes_sec": 1048576,
      "write_bytes_sec": 2097152,
      "read_iops": 120,
      "write_iops": 85,
      "read_latency_ms": 2.5,
      "write_latency_ms": 3.1,
      "queue_depth": 2.3,
      "split_io_sec": 15,
      "idle_time_percent": 85.0,
      "temperature_celsius": 38.0,
      "health_percent": 95,
      "power_on_hours": 12500,
      "model": "Samsung SSD 970 EVO Plus 1TB",
      "serial": "S4EVNX0R123456",
      "firmware": "2B2QEXM7",
      "interface": "NVMe",
      "media_type": "SSD",
      "bytes_per_sector": 512,
      "partitions": 3,
      "smart_reallocated_sectors": 0,
      "smart_power_on_hours": 12500,
      "smart_power_cycles": 850,
      "smart_wear_leveling": 15,
      "smart_temperature_celsius": 38
    },
    {
      "device": "D:",
      "device_id": "\\\\.\\PHYSICALDRIVE1",
      "mountpoint": "D:\\",
      "fstype": "NTFS",
      "total_bytes": 2000398934016,
      "used_bytes": 1200123456789,
      "free_bytes": 800275477227,
      "usage_percent": 60.0,
      "read_bytes_sec": 524288,
      "write_bytes_sec": 1048576,
      "read_iops": 65,
      "write_iops": 42,
      "read_latency_ms": 8.2,
      "write_latency_ms": 12.5,
      "queue_depth": 1.8,
      "split_io_sec": 8,
      "idle_time_percent": 92.0,
      "temperature_celsius": 42.0,
      "health_percent": 98,
      "power_on_hours": 8500,
      "model": "Seagate ST2000LM007",
      "serial": "WFL123456",
      "firmware": "SDM1",
      "interface": "SATA",
      "media_type": "HDD",
      "bytes_per_sector": 4096,
      "partitions": 1,
      "smart_reallocated_sectors": 0,
      "smart_seek_errors": 0,
      "smart_spin_retry": 0,
      "smart_power_on_hours": 8500,
      "smart_power_cycles": 620,
      "smart_temperature_celsius": 42
    }
  ],
  "network": [
    {
      "interface": "Wi-Fi",
      "ipv4": "192.168.1.105",
      "ipv6": "fe80::1234:5678:9abc:def0",
      "mac": "00:11:22:33:44:55",
      "speed_mbps": 866,
      "bytes_sent_sec": 1048576,
      "bytes_recv_sec": 5242880,
      "packets_sent_sec": 850,
      "packets_recv_sec": 4200,
      "errors_in_sec": 0,
      "errors_out_sec": 0,
      "drops_in_sec": 2,
      "drops_out_sec": 1
    },
    {
      "interface": "Ethernet",
      "ipv4": "10.0.0.50",
      "ipv6": "fe80::abcd:ef01:2345:6789",
      "mac": "00:11:22:33:44:66",
      "speed_mbps": 1000,
      "bytes_sent_sec": 2097152,
      "bytes_recv_sec": 10485760,
      "packets_sent_sec": 1500,
      "packets_recv_sec": 8500,
      "errors_in_sec": 0,
      "errors_out_sec": 0,
      "drops_in_sec": 0,
      "drops_out_sec": 0
    }
  ],
  "thermal": [
    {
      "name": "CPU Package",
      "sensor_type": "CPU",
      "temperature_celsius": 52.0,
      "high_threshold_celsius": 95.0,
      "critical_threshold_celsius": 105.0
    },
    {
      "name": "CPU Core 0",
      "sensor_type": "CPU",
      "temperature_celsius": 50.0,
      "high_threshold_celsius": 95.0,
      "critical_threshold_celsius": 105.0
    },
    {
      "name": "CPU Core 1",
      "sensor_type": "CPU",
      "temperature_celsius": 53.0,
      "high_threshold_celsius": 95.0,
      "critical_threshold_celsius": 105.0
    },
    {
      "name": "GPU Core",
      "sensor_type": "GPU",
      "temperature_celsius": 45.0,
      "high_threshold_celsius": 85.0,
      "critical_threshold_celsius": 95.0
    },
    {
      "name": "GPU Memory",
      "sensor_type": "GPU",
      "temperature_celsius": 48.0,
      "high_threshold_celsius": 90.0,
      "critical_threshold_celsius": 100.0
    },
    {
      "name": "Motherboard",
      "sensor_type": "Motherboard",
      "temperature_celsius": 38.0,
      "high_threshold_celsius": 70.0,
      "critical_threshold_celsius": 80.0
    },
    {
      "name": "NVMe SSD",
      "sensor_type": "Storage",
      "temperature_celsius": 38.0,
      "high_threshold_celsius": 70.0,
      "critical_threshold_celsius": 80.0
    },
    {
      "name": "SATA HDD",
      "sensor_type": "Storage",
      "temperature_celsius": 42.0,
      "high_threshold_celsius": 55.0,
      "critical_threshold_celsius": 60.0
    },
    {
      "name": "VRM",
      "sensor_type": "Motherboard",
      "temperature_celsius": 55.0,
      "high_threshold_celsius": 100.0,
      "critical_threshold_celsius": 110.0
    }
  ],
  "fan": [
    {
      "name": "CPU Fan",
      "speed_rpm": 2400,
      "max_speed_rpm": 5000,
      "min_speed_rpm": 600,
      "duty_cycle_percent": 48,
      "control_mode": "auto"
    },
    {
      "name": "GPU Fan",
      "speed_rpm": 1800,
      "max_speed_rpm": 3500,
      "min_speed_rpm": 0,
      "duty_cycle_percent": 51,
      "control_mode": "auto"
    },
    {
      "name": "Chassis Fan 1",
      "speed_rpm": 1200,
      "max_speed_rpm": 2000,
      "min_speed_rpm": 400,
      "duty_cycle_percent": 60,
      "control_mode": "auto"
    }
  ],
  "voltage": [
    {
      "name": "CPU Vcore",
      "voltage_v": 1.15,
      "min_v": 0.8,
      "max_v": 1.35
    },
    {
      "name": "CPU VCCIO",
      "voltage_v": 1.05,
      "min_v": 0.95,
      "max_v": 1.15
    },
    {
      "name": "DRAM Voltage",
      "voltage_v": 1.2,
      "min_v": 1.15,
      "max_v": 1.25
    },
    {
      "name": "3.3V Rail",
      "voltage_v": 3.31,
      "min_v": 3.14,
      "max_v": 3.47
    },
    {
      "name": "5V Rail",
      "voltage_v": 5.02,
      "min_v": 4.75,
      "max_v": 5.25
    },
    {
      "name": "12V Rail",
      "voltage_v": 12.05,
      "min_v": 11.4,
      "max_v": 12.6
    }
  ],
  "battery": {
    "present": true,
    "charge_percent": 78,
    "status": "discharging",
    "capacity_full_mwh": 56000,
    "capacity_design_mwh": 60000,
    "capacity_remaining_mwh": 43680,
    "voltage_v": 11.4,
    "current_ma": -2800,
    "cycle_count": 245,
    "temperature_celsius": 32.0,
    "time_remaining_minutes": 185,
    "manufacturer": "Samsung SDI",
    "model": "SR Real Battery",
    "serial": "123456789",
    "chemistry": "Li-ion"
  },
  "gpu": [
    {
      "name": "NVIDIA GeForce RTX 3070 Laptop GPU",
      "gpu_usage_percent": 12.5,
      "memory_usage_percent": 35.2,
      "memory_total_mb": 8192,
      "memory_used_mb": 2884,
      "memory_free_mb": 5308,
      "temperature_celsius": 45.0,
      "fan_speed_rpm": 1800,
      "fan_speed_percent": 51,
      "power_watts": 35.2,
      "power_limit_watts": 80.0,
      "core_clock_mhz": 1380,
      "memory_clock_mhz": 7000,
      "driver_version": "546.33",
      "vbios_version": "94.04.38.00.53"
    }
  ]
}
```

---

## Collector Implementation Strategy

### 1. CPU Collector (`psutil` + WMI + OpenHardwareMonitor)
- **Core metrics**: Overall usage %, per-core usage %
- **Detailed breakdown**: user, system, idle, DPC, interrupt, privileged time % (via `psutil.cpu_times(percpu=True)`)
- **Frequency**: Current, min, max, per-core (via WMI `Win32_Processor` + `psutil.cpu_freq(percpu=True)`)
- **Temperature**: Package + per-core via OpenHardwareMonitor (primary) → WMI fallback
- **Power**: Package, cores, GPU via OpenHardwareMonitor → WMI `Win32_Processor` fallback
- **System counters**: Context switches/sec, interrupts/sec, syscalls/sec (via `psutil`)
- **Process/thread counts**: Total, running, sleeping, threads (via `psutil`)
- **Cache hierarchy**: L1d, L1i, L2, L3 sizes via WMI `Win32_CacheMemory`

### 2. Memory Collector (`psutil` + WMI)
- **Virtual memory**: total, available, used, free, active, inactive, modified, standby, cached, shared, buffers, page_tables, commit_limit, committed_as, dirty, writeback, mapped, nonpaged_pool, paged_pool
- **Swap**: total, used, free, cached, in/out bytes/sec
- **Page fault details**: faults/sec, reads/sec, writes/sec, cache faults, transition faults, demand zero, copy-on-write
- **NUMA stats** (if applicable): hit, miss, foreign, interleave, local, other

### 3. Disk Collector (`psutil` + WMI + OpenHardwareMonitor)
- **Per physical disk** (not just partitions): `\\.\PHYSICALDRIVE0`, `\\.\PHYSICALDRIVE1`, etc.
- **Usage**: total, used, free, % per partition/mountpoint
- **I/O rates**: read/write bytes/sec, read/write IOPS, read/write latency ms, queue depth
- **Split I/O/sec**: Critical for HDD fragmentation detection
- **Idle time %**: Disk utilization
- **Temperature**: OpenHardwareMonitor (primary) → WMI SMART (`MSStorageDriver_FailurePredictData`) fallback
- **Health**: SMART attributes (reallocated sectors, power-on hours, power cycles, wear leveling, temperature)
- **Hardware info**: Model, serial, firmware, interface (NVMe/SATA), media type (SSD/HDD), sector size, partitions
- **Physical disk mapping**: Link partitions to physical drives

### 4. Network Collector (`psutil` + WMI)
- **Per interface**: IPv4, IPv6, MAC, link speed
- **Throughput**: bytes sent/recv per sec, packets sent/recv per sec
- **Errors**: in/out errors, drops, collisions

### 5. Thermal Collector (OpenHardwareMonitorLib via pythonnet → WMI fallback)
- **All temperature sensors**: CPU package, per-core, GPU core/memory, motherboard, VRM, storage (NVMe/SATA), ambient
- **Thresholds**: High and critical thresholds per sensor
- **Sensor typing**: CPU, GPU, Motherboard, Storage, VRM, Ambient

### 6. Fan Collector (OpenHardwareMonitorLib via pythonnet → WMI fallback)
- **All fans**: CPU, GPU, chassis/system fans
- **Metrics**: Current RPM, min/max RPM, duty cycle %, control mode (auto/manual)

### 7. Voltage Collector (OpenHardwareMonitorLib via pythonnet)
- **Key rails**: CPU Vcore, VCCIO, DRAM, 3.3V, 5V, 12V
- **Min/max tracking**: Per rail

### 8. Battery Collector (WMI `Win32_Battery` + `Win32_BatteryStatus`)
- **Capacity**: Design, full charge, remaining (mWh)
- **Status**: Charging/discharging/full, charge %, time remaining
- **Health**: Cycle count, temperature, voltage, current
- **Info**: Manufacturer, model, serial, chemistry

### 9. GPU Collector (OpenHardwareMonitorLib → WMI `Win32_VideoController` fallback)
- **Usage**: GPU compute %, memory %
- **Memory**: Total, used, free (MB)
- **Thermals**: Temperature, fan speed (RPM + %)
- **Power**: Current draw, power limit
- **Clocks**: Core, memory
- **Driver info**: Version, VBIOS

---

## Configuration Schema (YAML)

```yaml
# config/default.yaml
collection:
  interval_seconds: 10
  duration_seconds: 0  # 0 = infinite

output:
  format: "jsonl"  # jsonl or csv
  directory: "./logs"
  filename_template: "telemetry_{hostname}_{date}.jsonl"
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
    physical_disks: "all"  # or list of device IDs
    partitions: "all"      # or list of mountpoints
    include_io: true
    include_smart: true
    include_temperature: true
  network:
    enabled: true
    interfaces: "all"      # or list of interface names
  thermal:
    enabled: true
    sensors: "all"         # or list of sensor names
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

---

## Error Handling Strategy

1. **Graceful Degradation**: If a sensor/collector fails, log warning and continue with others
2. **Fallback Chains**: 
   - Thermal: OpenHardwareMonitor → WMI → None
   - Fan: OpenHardwareMonitor → WMI → None
   - Disk temp: OpenHardwareMonitor → WMI SMART → None
3. **Retry Logic**: Transient WMI failures retry with exponential backoff
4. **Health Checks**: Startup validation of available sensors

---

## CLI Interface

```bash
# Run with default config
python -m laptop_telemetry

# Run with custom config
python -m laptop_telemetry --config config/production.yaml

# Override specific settings
python -m laptop_telemetry --interval 60 --output ./my_logs --format csv

# Dry run - show what would be collected
python -m laptop_telemetry --dry-run

# List available sensors
python -m laptop_telemetry --list-sensors

# Validate config
python -m laptop_telemetry --validate-config

# Show collector status
python -m laptop_telemetry --collector-status

# Export single snapshot to stdout
python -m laptop_telemetry --once --format json
```

---

## Dependencies (pyproject.toml)

```toml
[project]
name = "laptop-telemetry"
version = "0.1.0"
description = "Windows laptop telemetry collector for CPU, RAM, Disk, Thermals, Fan Speed"
requires-python = ">=3.10"
dependencies = [
    "psutil>=5.9.0",
    "wmi>=1.5.1",
    "pythonnet>=3.0.0",
    "pydantic>=2.5.0",
    "pyyaml>=6.0",
    "loguru>=0.7.0",
    "click>=8.1.0",
    "pandas>=2.0.0",  # For CSV export optimization
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-mock>=3.12.0",
    "pytest-cov>=4.1.0",
    "ruff>=0.1.0",
    "mypy>=1.7.0",
]

[build-system]
requires = ["setuptools>=68.0", "wheel"]
build-backend = "setuptools.build_meta"

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]

[tool.ruff]
line-length = 100
target-version = "py310"
```

---

## OpenHardwareMonitor Setup

Since OpenHardwareMonitorLib requires a DLL, we'll provide:
1. A download script (`scripts/install_ohm.py`) that fetches the latest release
2. Documentation on manual installation
3. Graceful handling if not available (fallback to WMI)

---

## Next Steps

1. ✅ Architecture designed
2. Create project structure and config
3. Implement core collectors
4. Implement exporters
5. Add scheduler and CLI
6. Write tests
7. Create documentation