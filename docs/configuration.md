# Configuration Reference

Complete reference for the Laptop Telemetry Collector configuration file.

## Configuration File Location

The collector looks for configuration in this order:

1. `--config` CLI argument
2. `config/default.yaml` (relative to working directory)
3. `./config.yaml`
4. `~/.config/laptop-telemetry/config.yaml`
5. Built-in defaults

Generate a default configuration:

```bash
python -m laptop_telemetry generate-config --output config/my_config.yaml
```

## Configuration Structure

```yaml
collection:
  interval_seconds: 60
  duration_seconds: 0

output:
  format: "both"
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
  dll_path: ""

logging:
  level: "INFO"
  file: "./logs/collector.log"
  rotation: "10 MB"
  retention: "30 days"
```

## Section Reference

### `collection`

Controls the collection schedule.

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `interval_seconds` | integer | `60` | Collection interval (1-3600 seconds). Must divide evenly into 3600 for alignment. |
| `duration_seconds` | integer | `0` | Total collection duration. `0` = infinite. |

**Interval Alignment**: The scheduler aligns collections to wall-clock boundaries. For example, with `interval_seconds: 60`, collections occur at :00, :01, :02, etc. Valid intervals: 1, 2, 3, 4, 5, 6, 10, 12, 15, 20, 30, 60, 120, 180, 300, 360, 600, 900, 1800, 3600.

### `output`

Controls output format and file management.

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `format` | string | `"both"` | Output format: `"jsonl"`, `"csv"`, or `"both"` |
| `directory` | string | `"./logs"` | Output directory (created if missing) |
| `filename_template` | string | `"telemetry_{hostname}_{date}.{ext}"` | Template with placeholders |
| `rotation.max_size_mb` | integer | `100` | Max file size before rotation |
| `rotation.max_files` | integer | `30` | Max rotated files to keep |
| `rotation.compress` | boolean | `true` | Compress rotated files with gzip |

**Filename Placeholders**:

| Placeholder | Description |
|-------------|-------------|
| `{hostname}` | System hostname |
| `{date}` | Date in YYYYMMDD format |
| `{time}` | Time in HHMMSS format |
| `{datetime}` | ISO datetime (YYYYMMDD_HHMMSS) |
| `{ext}` | Extension (jsonl or csv) |
| `{pid}` | Process ID |

### `collectors`

Enable/disable and configure individual collectors.

#### Common Options

All collectors support:
- `enabled` (boolean): Enable/disable the collector

#### `cpu`

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `per_core` | boolean | `true` | Collect per-core metrics |
| `include_temperature` | boolean | `true` | Include CPU temperature (requires OHM) |
| `include_power` | boolean | `true` | Include power consumption (requires OHM) |
| `include_cache` | boolean | `true` | Include cache hierarchy info |
| `include_system_counters` | boolean | `true` | Include context switches, interrupts, syscalls |

#### `memory`

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `include_swap` | boolean | `true` | Include swap metrics |
| `include_page_faults` | boolean | `true` | Include page fault details |
| `include_numa` | boolean | `true` | Include NUMA node stats |

#### `disk`

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `physical_disks` | string/array | `"all"` | Physical disks to monitor: `"all"` or list of device IDs |
| `partitions` | string/array | `"all"` | Partitions to monitor: `"all"` or list of mount points |
| `include_io` | boolean | `true` | Include I/O rates and latency |
| `include_smart` | boolean | `true` | Include SMART health attributes |
| `include_temperature` | boolean | `true` | Include disk temperature |

#### `network`

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `interfaces` | string/array | `"all"` | Interfaces to monitor: `"all"` or list of interface names |

#### `thermal`

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `sensors` | string/array | `"all"` | Sensors to monitor: `"all"` or list of sensor names |

#### `fan`

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `sensors` | string/array | `"all"` | Fan sensors to monitor: `"all"` or list of sensor names |

#### `voltage`

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `rails` | string/array | `"all"` | Voltage rails to monitor: `"all"` or list of rail names |

#### `battery`

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `enabled` | boolean | `true` | Enable battery collector (laptops only) |

#### `gpu`

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `devices` | string/array | `"all"` | GPU devices to monitor: `"all"` or list of device names |

### `openhardwaremonitor`

Configuration for OpenHardwareMonitor integration.

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `dll_path` | string | `""` | Path to `OpenHardwareMonitorLib.dll`. Empty = use `OPENHARDWAREMONITOR_DLL` env var |

**Priority**: Config file > Environment variable > Auto-detect

### `logging`

Controls application logging (separate from telemetry output).

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `level` | string | `"INFO"` | Log level: `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `file` | string | `"./logs/collector.log"` | Log file path |
| `rotation` | string | `"10 MB"` | Log rotation size (e.g., `"10 MB"`, `"100 MB"`) |
| `retention` | string | `"30 days"` | Log retention (e.g., `"30 days"`, `"1 week"`) |

## Environment Variable Overrides

All configuration options can be overridden via environment variables with prefix `LAPTOP_TELEMETRY_`:

| Config Path | Environment Variable |
|-------------|---------------------|
| `collection.interval_seconds` | `LAPTOP_TELEMETRY_COLLECTION_INTERVAL_SECONDS` |
| `output.format` | `LAPTOP_TELEMETRY_OUTPUT_FORMAT` |
| `output.directory` | `LAPTOP_TELEMETRY_OUTPUT_DIRECTORY` |
| `collectors.cpu.enabled` | `LAPTOP_TELEMETRY_COLLECTORS_CPU_ENABLED` |
| `openhardwaremonitor.dll_path` | `LAPTOP_TELEMETRY_OPENHARDWAREMONITOR_DLL_PATH` / `OPENHARDWAREMONITOR_DLL` |
| `logging.level` | `LAPTOP_TELEMETRY_LOGGING_LEVEL` |

**Boolean values**: `true`/`false`, `1`/`0`, `yes`/`no`

## Example Configurations

### Minimal (CPU + Memory only, JSONL)

```yaml
collection:
  interval_seconds: 60
  duration_seconds: 0

output:
  format: "jsonl"
  directory: "./logs"

collectors:
  cpu:
    enabled: true
  memory:
    enabled: true
  disk:
    enabled: false
  network:
    enabled: false
  thermal:
    enabled: false
  fan:
    enabled: false
  voltage:
    enabled: false
  battery:
    enabled: false
  gpu:
    enabled: false
```

### High-Frequency (10s interval, CSV only)

```yaml
collection:
  interval_seconds: 10
  duration_seconds: 3600  # 1 hour

output:
  format: "csv"
  directory: "./high_freq_logs"
  filename_template: "telemetry_{hostname}_{datetime}.{ext}"
  rotation:
    max_size_mb: 50
    max_files: 100
    compress: true

collectors:
  cpu:
    enabled: true
    per_core: true
    include_temperature: true
    include_power: true
  memory:
    enabled: true
  disk:
    enabled: true
    include_io: true
  network:
    enabled: true
  thermal:
    enabled: true
  fan:
    enabled: true
  voltage:
    enabled: true
  battery:
    enabled: true
  gpu:
    enabled: true
```

### Production (Long-term, both formats, rotation)

```yaml
collection:
  interval_seconds: 60
  duration_seconds: 0

output:
  format: "both"
  directory: "/var/log/laptop-telemetry"
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
  dll_path: "C:/Program Files/OpenHardwareMonitor/OpenHardwareMonitorLib.dll"

logging:
  level: "INFO"
  file: "/var/log/laptop-telemetry/collector.log"
  rotation: "50 MB"
  retention: "90 days"
```

## Validation

Validate your configuration:

```bash
python -m laptop_telemetry --validate-config --config config/my_config.yaml
```

Or programmatically:

```python
from laptop_telemetry.config.loader import load_config

config = load_config("config/my_config.yaml")
print(config.model_dump_json(indent=2))
```

## CLI Override Precedence

CLI arguments override config file:

1. Default values (lowest)
2. Config file
3. Environment variables
4. CLI arguments (highest)

```bash
# Config says interval=60, but CLI overrides to 30
python -m laptop_telemetry --config config/prod.yaml --interval 30