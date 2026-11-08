# Hardware Support Matrix

This document details the hardware sensor compatibility for the Laptop Telemetry Collector.

## Overview

The collector uses multiple backends for hardware sensor data:

| Backend | Purpose | Requirements |
|---------|---------|--------------|
| **psutil** | CPU, Memory, Disk, Network, Battery | Built-in, cross-platform |
| **WMI** | Basic thermal, battery, hardware info | Windows built-in |
| **OpenHardwareMonitor (OHM)** | Enhanced thermal, fan, voltage, GPU | External DLL required |

## Sensor Coverage by Component

### CPU Metrics

| Metric | psutil | WMI | OHM | Notes |
|--------|--------|-----|-----|-------|
| Overall usage % | ✅ | | | Per-core available |
| User/System/Idle/DPC/Interrupt/Privileged | ✅ | | | Windows-specific breakdown |
| Frequency (current/min/max) | ✅ | | | Per-core available |
| Temperature | | ✅ | ✅ | OHM more accurate |
| Power consumption | | | ✅ | Package, cores, GPU, DRAM |
| Cache hierarchy (L1/L2/L3) | ✅ | | | Static info |
| System counters (ctx switches, interrupts, syscalls) | ✅ | | | Per-second rates |
| Process/thread counts | ✅ | | | |

### Memory Metrics

| Metric | psutil | WMI | OHM | Notes |
|--------|--------|-----|-----|-------|
| Virtual memory (total/avail/used/free) | ✅ | | | |
| Active/Inactive/Modified/Standby/Cached | ✅ | | | Windows-specific |
| Shared/Buffers/Page tables | ✅ | | | |
| Commit limit/Committed/Dirty/Writeback | ✅ | | | |
| Mapped/Nonpaged/Paged pool | ✅ | | | |
| Swap | ✅ | | | |
| Page fault details | ✅ | | | |
| NUMA stats | ✅ | | | If applicable |

### Disk Metrics

| Metric | psutil | WMI | OHM | Notes |
|--------|--------|-----|-----|-------|
| Physical disks (not just partitions) | ✅ | ✅ | | WMI for hardware info |
| Usage (total/used/free) | ✅ | | | Per partition |
| I/O rates (bytes/sec, IOPS) | ✅ | | | Per disk |
| Latency / Queue depth | ✅ | | | |
| Split I/O/sec | ✅ | | | Windows-specific |
| Idle time % | ✅ | | | |
| Temperature | | ✅ | ✅ | OHM preferred |
| SMART health attributes | | ✅ | ✅ | WMI + OHM |
| Hardware info (model, serial, firmware, interface, media type) | | ✅ | | |

### Network Metrics

| Metric | psutil | WMI | OHM | Notes |
|--------|--------|-----|-----|-------|
| Per-interface throughput | ✅ | | | Bytes/packets sent/recv |
| Errors / Drops | ✅ | | | |
| IP / MAC addresses | ✅ | ✅ | | |
| Link speed | | ✅ | | WMI Win32_NetworkAdapter |

### Thermal Sensors

| Sensor Type | WMI | OHM | Notes |
|-------------|-----|-----|-------|
| CPU Package | ✅ | ✅ | OHM: per-core temps |
| CPU Cores | | ✅ | Individual core temps |
| GPU Core | | ✅ | NVIDIA/AMD/Intel |
| GPU Memory | | ✅ | |
| Motherboard | | ✅ | VRM, chipset, ambient |
| VRM | | ✅ | Voltage regulator modules |
| Storage (NVMe/SSD/HDD) | ✅ | ✅ | SMART + OHM |

### Fan Sensors

| Metric | WMI | OHM | Notes |
|--------|-----|-----|-------|
| RPM | | ✅ | Per fan |
| Min/Max RPM | | ✅ | |
| Duty cycle % | | ✅ | PWM control |
| Control mode | | ✅ | Auto/Manual |

### Voltage Rails

| Rail | OHM | Notes |
|------|-----|-------|
| Vcore (CPU core voltage) | ✅ | |
| VCCIO / VCCSA (System agent) | ✅ | |
| DRAM voltage | ✅ | |
| 3.3V / 5V / 12V | ✅ | Main power rails |
| GPU voltage | ✅ | If available |
| Min/Max tracking | ✅ | Per rail |

### Battery Metrics

| Metric | psutil | WMI | Notes |
|--------|--------|-----|-------|
| Capacity (design/full/remaining) | ✅ | ✅ | |
| Status (charging/discharging/full) | ✅ | ✅ | |
| Charge % | ✅ | ✅ | |
| Time remaining | ✅ | ✅ | Estimated |
| Cycle count | | ✅ | WMI BatteryCycleCount |
| Temperature | | ✅ | If sensor present |
| Voltage / Current | | ✅ | |
| Manufacturer info | | ✅ | Name, chemistry, serial |

### GPU Metrics

| Metric | OHM | Notes |
|--------|-----|-------|
| GPU usage % | ✅ | 3D/Compute/Video engines |
| Memory usage | ✅ | Used/total |
| Temperature (core/memory/hotspot) | ✅ | |
| Fan speed (RPM/%) | ✅ | |
| Power draw | ✅ | |
| Clocks (core/memory) | ✅ | Current/max |
| Driver version | ✅ | |
| VBIOS version | ✅ | |

## Known Compatibility

### Tested Hardware

| Vendor | Model | CPU | GPU | Sensors Working |
|--------|-------|-----|-----|-----------------|
| Dell | XPS 15 9520 | Intel 12th Gen | RTX 3050 Ti | All |
| Lenovo | ThinkPad T14s | AMD Ryzen 6000 | Integrated | All except GPU |
| ASUS | ROG Zephyrus G14 | AMD Ryzen 9 | RTX 4060 | All |
| HP | Spectre x360 | Intel 13th Gen | Arc / Integrated | Most |
| Custom | Desktop | Intel 14th Gen | RTX 4090 | All |

### Known Limitations

1. **OHM DLL Required**: Without `OpenHardwareMonitorLib.dll`, thermal/fan/voltage/GPU metrics fall back to WMI (limited)
2. **Admin Rights**: Some WMI queries require Administrator privileges
3. **Laptop vs Desktop**: Battery metrics only on laptops
4. **Virtual Machines**: Limited sensor access in VMs
5. **ARM64 Windows**: OHM DLL is x64 only; psutil/WMI work natively
6. **Secure Boot**: May block unsigned OHM DLL loading

## OpenHardwareMonitor Setup

### Download

1. Visit: https://openhardwaremonitor.org/
2. Download latest release (v0.9.6+ recommended)
3. Extract `OpenHardwareMonitorLib.dll`

### Configuration

Set environment variable (persistent):

```powershell
# User scope
[Environment]::SetEnvironmentVariable("OPENHARDWAREMONITOR_DLL", "C:\path\to\OpenHardwareMonitorLib.dll", "User")

# Or system scope (requires admin)
[Environment]::SetEnvironmentVariable("OPENHARDWAREMONITOR_DLL", "C:\path\to\OpenHardwareMonitorLib.dll", "Machine")
```

Or in config file (`config/default.yaml`):

```yaml
openhardwaremonitor:
  dll_path: "C:/path/to/OpenHardwareMonitorLib.dll"
```

### Verification

Run with `--list-sensors` to see detected sensors:

```bash
python -m laptop_telemetry --list-sensors
```

### DLL Integrity

Verify SHA256 of downloaded DLL:

```powershell
Get-FileHash -Algorithm SHA256 OpenHardwareMonitorLib.dll
```

Compare with official release hashes.

## Troubleshooting Sensor Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| No thermal sensors | OHM DLL not found | Set `OPENHARDWAREMONITOR_DLL` |
| Partial GPU data | Driver/OHM version mismatch | Update GPU drivers + OHM |
| Fan RPM = 0 | Fan not monitored by OHM | Check OHM GUI for sensor |
| Voltage rails missing | Sensor not exposed | Hardware limitation |
| Permission errors | WMI needs admin | Run as Administrator |
| OHM DLL load failed | Architecture mismatch | Use x64 Python + x64 DLL |

## Contributing Hardware Reports

If you test on new hardware, please submit a [hardware issue](.github/ISSUE_TEMPLATE/hardware_issue.md) with:

- Laptop/model
- CPU/GPU
- Which sensors work/don't work
- OHM version
- Output of `--list-sensors`