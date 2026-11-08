# Troubleshooting Guide

Common issues and solutions for the Laptop Telemetry Collector.

## Quick Diagnostics

Run these commands to diagnose issues:

```bash
# Validate configuration
python -m laptop_telemetry --validate-config

# List available sensors
python -m laptop_telemetry --list-sensors

# Show collector status
python -m laptop_telemetry --collector-status

# Dry run (show what would be collected)
python -m laptop_telemetry --dry-run

# Run once with debug logging
python -m laptop_telemetry --once --config config/default.yaml 2>&1 | head -50
```

---

## Installation Issues

### `ModuleNotFoundError: No module named 'laptop_telemetry'`

**Cause**: Package not installed or not in PYTHONPATH.

**Solution**:
```bash
# Install in development mode
pip install -e .

# Or with uv
uv sync --all-extras --dev
```

### `ImportError: DLL load failed` / `pythonnet` issues

**Cause**: `pythonnet` cannot load .NET runtime or OHM DLL.

**Solutions**:
1. Install .NET 6+ Runtime: https://dotnet.microsoft.com/download
2. Ensure `OpenHardwareMonitorLib.dll` is accessible
3. Check architecture match (x64 Python + x64 DLL)
4. Try: `pip install --force-reinstall pythonnet`

### `PermissionError` on install

**Cause**: Insufficient permissions for site-packages.

**Solution**:
```bash
# Use virtual environment
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"

# Or use --user flag
pip install --user -e ".[dev]"
```

---

## OpenHardwareMonitor Issues

### "OpenHardwareMonitorLib.dll not found"

**Cause**: DLL path not configured.

**Solutions**:
1. Set environment variable:
   ```powershell
   $env:OPENHARDWAREMONITOR_DLL = "C:\path\to\OpenHardwareMonitorLib.dll"
   ```
2. Or configure in `config/default.yaml`:
   ```yaml
   openhardwaremonitor:
     dll_path: "C:/path/to/OpenHardwareMonitorLib.dll"
   ```

### "OHM DLL load failed: BadImageFormatException"

**Cause**: Architecture mismatch (32-bit vs 64-bit).

**Solution**:
- Use 64-bit Python (check with `python -c "import platform; print(platform.architecture())"`)
- Download 64-bit OHM DLL (standard release is 64-bit)
- Ensure .NET 6+ 64-bit runtime installed

### "OHM sensors not appearing" / "No thermal/fan/voltage data"

**Cause**: OHM not running or sensors not detected.

**Solutions**:
1. Run OpenHardwareMonitor GUI once to initialize sensors
2. Run collector as Administrator (some sensors need elevated privileges)
3. Check OHM GUI: sensors must be "visible" (not hidden)
4. Update OHM to latest version (v0.9.6+)
5. Some laptops have limited sensor exposure - hardware limitation

### "Access denied" when loading OHM DLL

**Cause**: Windows security blocking unsigned DLL.

**Solutions**:
1. Unblock the DLL file:
   ```powershell
   Unblock-File -Path "C:\path\to\OpenHardwareMonitorLib.dll"
   ```
2. Or via Properties → General → "Unblock" checkbox
3. Run PowerShell as Admin and set execution policy temporarily:
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
   ```

---

## WMI Issues

### "WMI query failed" / "Access denied" / "RPC server unavailable"

**Cause**: WMI permissions or service issues.

**Solutions**:
1. Run as Administrator
2. Check WMI service running:
   ```powershell
   Get-Service winmgmt
   Restart-Service winmgmt -Force
   ```
3. Rebuild WMI repository (last resort):
   ```powershell
   winmgmt /verifyrepository
   winmgmt /salvagerepository
   # If corrupted:
   winmgmt /resetrepository
   ```
4. Enable WMI in Windows Firewall for remote access (if applicable)

### "No disk/thermal/battery data from WMI"

**Cause**: WMI classes not available on this hardware.

**Solutions**:
- Some metrics require specific WMI providers (vendor-specific)
- Install vendor management software (Dell Command Monitor, Lenovo Vantage, etc.)
- Use OHM as primary backend for these metrics

---

## Collector-Specific Issues

### CPU Collector

| Issue | Cause | Solution |
|-------|-------|----------|
| Per-core usage all zeros | psutil version | Upgrade psutil: `pip install -U psutil` |
| Frequency always max | Power plan | Set Windows power plan to "Balanced" |
| DPC/Interrupt always 0 | Windows version | Requires Windows 10 1809+ |
| Temperature = null | OHM not configured | Set up OHM DLL |

### Memory Collector

| Issue | Cause | Solution |
|-------|-------|----------|
| NUMA stats empty | Non-NUMA system | Normal - only on multi-socket/AMD EPYC |
| Page faults very high | Memory pressure | Investigate memory leaks in applications |
| Swap not reported | No pagefile | Configure pagefile in Windows |

### Disk Collector

| Issue | Cause | Solution |
|-------|-------|----------|
| Physical disks not found | Permissions | Run as Administrator |
| SMART data missing | Drive/Controller | Some RAID controllers hide SMART; NVMe may need `nvme-cli` |
| Temperature = 0 | Drive doesn't report | Hardware limitation |
| I/O rates spike | Antivirus/Indexing | Exclude log directory from scanning |

### Network Collector

| Issue | Cause | Solution |
|-------|-------|----------|
| Interface missing | Virtual adapter | Filter: `interfaces: ["Ethernet", "Wi-Fi"]` in config |
| Link speed = 0 | WMI issue | Run as Admin; update NIC drivers |
| Bytes/sec seems wrong | 32-bit counter wrap | psutil handles this; check for counter reset |

### Thermal/Fan/Voltage Collectors

| Issue | Cause | Solution |
|-------|-------|----------|
| All sensors null | OHM not loaded | Verify DLL path; check logs for "OHM initialized" |
| Some sensors missing | Hardware/OHM support | Check OHM GUI; submit hardware report |
| Fan RPM = 0 | Fan not monitored | Some fans only report % duty cycle |
| Voltage rails missing | Sensor not exposed | Motherboard dependent |

### Battery Collector

| Issue | Cause | Solution |
|-------|-------|----------|
| Not detected on desktop | No battery | Normal - disable in config: `battery.enabled: false` |
| Cycle count = 0 | WMI not reporting | Some manufacturers don't expose |
| Time remaining fluctuating | Estimation algorithm | Normal - based on current discharge rate |

### GPU Collector

| Issue | Cause | Solution |
|-------|-------|----------|
| No GPU data | OHM/GPU driver | Update GPU drivers; OHM v0.9.6+ |
| Only one GPU shown | Multi-GPU laptop | Check `devices: "all"` in config |
| Memory usage wrong | Shared memory | Integrated GPUs share system RAM |

---

## Output/Exporter Issues

### "Permission denied" writing logs

**Cause**: Output directory not writable.

**Solution**:
```bash
# Create directory with permissions
mkdir logs
# Or configure writable path
output:
  directory: "C:/Users/YourUser/Documents/telemetry_logs"
```

### CSV file empty / missing headers

**Cause**: No data collected yet or exporter bug.

**Solution**:
- Wait for first collection interval
- Check `--dry-run` output
- Verify collectors enabled in config

### JSONL parsing errors

**Cause**: Corrupted line (partial write).

**Solution**:
- Enable rotation to prevent huge files
- Use `jq` with `--seq` for robust parsing:
  ```bash
  jq --seq . telemetry_*.jsonl
  ```

### File rotation not working

**Cause**: Size threshold not reached or permission issue.

**Solution**:
- Check `rotation.max_size_mb` in config
- Verify write permissions
- Check logs for "Rotating file" messages

---

## Scheduler/Timing Issues

### Collections not aligned to interval

**Cause**: Start time offset or system clock changes.

**Solution**:
- Scheduler aligns to next interval boundary
- First collection may be shorter
- Use `--once` for immediate single collection

### High CPU usage by collector

**Cause**: Too frequent interval or too many collectors.

**Solutions**:
- Increase `interval_seconds` (minimum 10s recommended)
- Disable unused collectors
- Check for OHM polling overhead (reduce OHM sensors)

### Collector hangs / timeout

**Cause**: WMI/OHM query blocking.

**Solutions**:
- Run with `--collector-status` to identify slow collector
- Disable problematic collector
- Increase timeout in code (not configurable yet)

---

## Configuration Issues

### "ValidationError" on config load

**Cause**: Invalid YAML or schema violation.

**Solution**:
```bash
# Validate config
python -m laptop_telemetry --validate-config --config config/my_config.yaml

# Check YAML syntax
python -c "import yaml; yaml.safe_load(open('config/my_config.yaml'))"
```

### Environment variables not working

**Cause**: Wrong prefix or format.

**Solution**:
- Use `LAPTOP_TELEMETRY_` prefix
- Nested keys: `__` (double underscore) separator
- Boolean: `true`/`false`, `1`/`0`, `yes`/`no`

```bash
# Correct
export LAPTOP_TELEMETRY_COLLECTION_INTERVAL_SECONDS=30
export LAPTOP_TELEMETRY_COLLECTORS_CPU_ENABLED=true

# Wrong
export COLLECTION_INTERVAL=30
```

---

## Performance Optimization

### Reduce Collection Overhead

1. **Disable unused collectors**:
   ```yaml
   collectors:
     gpu:
       enabled: false  # If no GPU monitoring needed
   ```

2. **Reduce CPU detail**:
   ```yaml
   collectors:
     cpu:
       per_core: false
       include_system_counters: false
   ```

3. **Increase interval**:
   ```yaml
   collection:
     interval_seconds: 300  # 5 minutes instead of 60s
   ```

4. **Use CSV only** (faster than JSONL):
   ```yaml
   output:
     format: "csv"
   ```

### Disk I/O Optimization

1. **Output to SSD** (not HDD or network drive)
2. **Increase rotation size**:
   ```yaml
   output:
     rotation:
       max_size_mb: 500
   ```
3. **Disable compression** (CPU tradeoff):
   ```yaml
   output:
     rotation:
       compress: false
   ```

---

## Getting Help

### Before Reporting

1. Run diagnostics:
   ```bash
   python -m laptop_telemetry --validate-config
   python -m laptop_telemetry --list-sensors
   python -m laptop_telemetry --collector-status
   python -m laptop_telemetry --once --dry-run
   ```

2. Collect logs:
   ```bash
   python -m laptop_telemetry --once 2>&1 | tee debug.log
   ```

3. Note environment:
   - Windows version (`winver`)
   - Python version (`python --version`)
   - Package version (`pip show laptop-telemetry`)
   - OHM version (if used)

### Reporting Issues

Use the appropriate template:

- **Bug**: [.github/ISSUE_TEMPLATE/bug_report.md](.github/ISSUE_TEMPLATE/bug_report.md)
- **Feature**: [.github/ISSUE_TEMPLATE/feature_request.md](.github/ISSUE_TEMPLATE/feature_request.md)
- **Hardware**: [.github/ISSUE_TEMPLATE/hardware_issue.md](.github/ISSUE_TEMPLATE/hardware_issue.md)

Include:
- Debug log output
- Configuration file (sanitized)
- `--list-sensors` output
- Steps to reproduce

### Logs Location

- Collector logs: `./logs/collector.log` (configurable)
- Telemetry output: `./logs/telemetry_*.jsonl` / `*.csv`
- Windows Event Viewer: Applications and Services Logs → OpenHardwareMonitor (if OHM issues)

---

## Known Issues & Workarounds

| Issue | Status | Workaround |
|-------|--------|------------|
| OHM DLL requires admin on some systems | Open | Run collector as Admin |
| WMI battery cycle count always 0 | Known limitation | N/A |
| ARM64 Windows: OHM not supported | Won't fix (OHM x64 only) | Use psutil/WMI only |
| VirtualBox/VMware: limited sensors | Expected | N/A |
| Secure Boot blocks OHM DLL | Windows policy | Disable Secure Boot or sign DLL |
| High memory usage over time | Investigating | Restart collector periodically |

---

## Version-Specific Notes

### v0.1.0

- Initial release
- Windows only
- Requires Python 3.10+
- OHM DLL optional but recommended for full sensor support