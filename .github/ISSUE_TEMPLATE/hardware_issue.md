---
name: Hardware Compatibility Issue
about: Report hardware sensor compatibility issues
title: "[HARDWARE] "
labels: ["hardware", "compatibility"]
---

## Hardware Information

| Component | Details |
|-----------|---------|
| **Laptop/Model** | [e.g., Dell XPS 15 9520, Lenovo ThinkPad T14s Gen 3] |
| **CPU** | [e.g., Intel Core i7-12700H, AMD Ryzen 7 6800U] |
| **GPU** | [e.g., NVIDIA RTX 3050 Ti, AMD Radeon 680M, Intel Iris Xe] |
| **RAM** | [e.g., 32GB DDR5-4800] |
| **Storage** | [e.g., 1TB Samsung 980 Pro NVMe] |
| **BIOS/UEFI Version** | [e.g., 1.12.0] |

## Operating System

- **Windows Version**: [e.g., Windows 11 Pro 23H2 Build 22631.2715]
- **Python Version**: [e.g., 3.11.5]
- **Package Version**: [e.g., 0.1.0]

## OpenHardwareMonitor

- **OHM Version**: [e.g., 0.9.6, or "not installed"]
- **DLL Path**: [e.g., C:\Program Files\OpenHardwareMonitor\OpenHardwareMonitorLib.dll]
- **Run as Admin**: [Yes/No]

## Sensor Status

Run `python -m laptop_telemetry --list-sensors` and paste output here:

```
# Paste output here
```

Run `python -m laptop_telemetry --collector-status` and paste output here:

```
# Paste output here
```

## Working Sensors

List sensors that work correctly:

- [ ] CPU usage (overall)
- [ ] CPU per-core usage
- [ ] CPU frequency
- [ ] CPU temperature
- [ ] CPU power
- [ ] Memory (virtual/swap)
- [ ] Disk usage
- [ ] Disk I/O
- [ ] Disk temperature
- [ ] Disk SMART
- [ ] Network throughput
- [ ] Thermal sensors (CPU package, cores, GPU, motherboard, etc.)
- [ ] Fan speeds
- [ ] Voltage rails
- [ ] Battery (capacity, status, cycles, temp)
- [ ] GPU (usage, memory, temp, fan, power, clocks)

## Non-Working / Missing Sensors

List sensors that don't work or are missing:

| Sensor | Expected | Actual | Notes |
|--------|----------|--------|-------|
| CPU temp | Per-core temps | Only package temp | OHM shows per-core in GUI |
| Fan 2 | RPM | 0 / missing | Second fan not detected |
| VCCIO voltage | Voltage reading | Not present | Motherboard doesn't expose |

## OHM GUI Comparison

If using OpenHardwareMonitor, compare with OHM GUI:

1. Open OHM GUI
2. Expand all sensors
3. Note which sensors appear in OHM but not in collector
4. Screenshot or list discrepancies

## Logs

Run a single collection with debug logging:

```bash
python -m laptop_telemetry --once --config config/default.yaml 2>&1 | tee debug.log
```

Paste relevant portions of `debug.log` here (sanitize paths/hostnames):

```
# Paste logs here
```

## Additional Information

- Does this work on other similar hardware?
- Any vendor-specific software installed (Dell Command Monitor, Lenovo Vantage, ASUS Armoury Crate, etc.)?
- Secure Boot enabled? [Yes/No]
- Virtualization enabled in BIOS? [Yes/No]
- Any error messages in Windows Event Viewer related to WMI or OHM?

## Suggested Fix

If you know what might fix this (e.g., specific WMI class, OHM sensor name, registry key), describe it here.