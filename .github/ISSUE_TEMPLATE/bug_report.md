---
name: Bug Report
about: Report a bug in the laptop telemetry collector
title: "[BUG] "
labels: ["bug"]
---

## Description

Clear and concise description of the bug.

## Steps to Reproduce

1. Step 1 (e.g., "Run `python -m laptop_telemetry --config config/default.yaml`")
2. Step 2
3. Step 3
4. Observe error

## Expected Behavior

What should happen.

## Actual Behavior

What actually happens (include error messages, stack traces, log output).

## Environment

- **OS**: [e.g., Windows 11 Pro 23H2, Windows 10 Enterprise 22H2]
- **Python Version**: [e.g., 3.11.5, 3.12.0]
- **Package Version**: [e.g., 0.1.0, or commit hash if from source]
- **OpenHardwareMonitor Version**: [e.g., 0.9.6, or "not used"]
- **Architecture**: [e.g., x64, ARM64]

## Configuration

Relevant parts of your config file (sanitize any paths):

```yaml
# Paste relevant config sections here
collection:
  interval_seconds: 60
collectors:
  cpu:
    enabled: true
    include_temperature: true
```

## Logs

```
# Paste relevant log output here
# Run with: python -m laptop_telemetry --once 2>&1 | tee debug.log
```

## Additional Context

- Does this happen consistently or intermittently?
- Any recent changes (Windows updates, driver updates, hardware changes)?
- Screenshots if applicable
- Output of `python -m laptop_telemetry --list-sensors`
- Output of `python -m laptop_telemetry --collector-status`

## Possible Solution

If you have ideas on how to fix it, describe them here.