> **⚠️ Disclaimer**: This CONTRIBUTING.md file is **LLM-generated for testing purposes only**. It is a **sample and not legally binding**. Do not use this Contributing Guide for production purposes without proper legal review.

# Contributing to Laptop Telemetry

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Branching Strategy](#branching-strategy)
- [Commit Message Format](#commit-message-format)
- [Pull Request Process](#pull-request-process)
- [Code Style](#code-style)
- [Testing](#testing)
- [Documentation](#documentation)

## Code of Conduct

This project adheres to the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/laptop-telemetry.git
   cd laptop-telemetry
   ```
3. Add the upstream remote:
   ```bash
   git remote add upstream https://github.com/ORIGINAL_OWNER/laptop-telemetry.git
   ```

## Development Setup

### Prerequisites

- Windows 10/11 (required for hardware sensor access)
- Python 3.10+
- [uv](https://github.com/astral-sh/uv) (recommended) or pip
- OpenHardwareMonitorLib.dll (optional, for enhanced sensor data)

### Installation

```bash
# Using uv (recommended)
uv sync --all-extras --dev

# Or using pip
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### OpenHardwareMonitor Setup (Optional)

For thermal, fan, voltage, and GPU metrics:

1. Download OpenHardwareMonitor from https://openhardwaremonitor.org/
2. Extract `OpenHardwareMonitorLib.dll` to a known location
3. Set the environment variable:
   ```powershell
   $env:OPENHARDWAREMONITOR_DLL = "C:\path\to\OpenHardwareMonitorLib.dll"
   ```

## Branching Strategy

We follow [GitHub Flow](https://docs.github.com/en/get-started/quickstart/github-flow):

- `main` - Protected branch, always deployable
- Feature branches: `feature/short-description`
- Bug fix branches: `fix/short-description`
- Documentation branches: `docs/short-description`
- Refactoring branches: `refactor/short-description`
- Maintenance branches: `chore/short-description`
- Release branches: `release/vX.Y.Z`

### Branch Naming Examples

- `feature/add-gpu-memory-tracking`
- `fix/memory-leak-in-disk-collector`
- `docs/update-configuration-reference`
- `refactor/collector-base-class`
- `chore/update-dependencies`
- `release/v1.0.0`

## Commit Message Format

We use [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <short summary>

<body>

<footer>
```

### Types

| Type | Description |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `style` | Formatting, no code change |
| `refactor` | Code restructuring |
| `perf` | Performance improvement |
| `test` | Adding/modifying tests |
| `chore` | Maintenance, build, deps |
| `ci` | CI/CD changes |

### Examples

```
feat(collectors): add GPU temperature monitoring

Implements GPU thermal metrics collection via OpenHardwareMonitor.
Includes core temperature, memory temperature, and hotspot detection.

Closes #42
```

```
fix(exporter): handle empty data in CSV export

CSV exporter now writes header row even when no data rows exist,
preventing downstream parsing errors.

Fixes #123
```

```
docs(config): add environment variable override examples

Adds examples for OHM_DLL_PATH and LOG_LEVEL environment variables.
```

## Pull Request Process

### Before Submitting

- [ ] Run tests locally: `pytest`
- [ ] Run linting: `ruff check src/ tests/`
- [ ] Run formatting: `ruff format src/ tests/`
- [ ] Run type checking: `mypy src/`
- [ ] Update CHANGELOG.md under `[Unreleased]`
- [ ] Update documentation if API changes
- [ ] Add tests for new functionality

### PR Requirements

- [ ] Descriptive title following conventional commits
- [ ] Clear description of changes and motivation
- [ ] Linked issues (Closes #123, Relates to #456)
- [ ] Tests added/updated for new functionality
- [ ] Documentation updated if API changes
- [ ] CHANGELOG.md entry added (under [Unreleased])
- [ ] CI passes (all checks green)
- [ ] Code review approved by at least 1 maintainer
- [ ] No merge conflicts with main

### PR Template

See [.github/PULL_REQUEST_TEMPLATE.md](.github/PULL_REQUEST_TEMPLATE.md)

## Code Style

### Python Standards

Follow the [python-coding-standards](.roo/skills/python-coding-standards/SKILL.md) skill:

- **Type annotations**: Full type hints (PEP 484, 585, 604)
- **Pydantic v2**: ConfigDict, field_validator, model_validator
- **Dataclasses**: Use `slots=True` where appropriate
- **Protocols**: For structural typing
- **Pattern matching**: match/case for complex conditionals

### Tooling

| Tool | Purpose | Config |
|------|---------|--------|
| Ruff | Linting & formatting | `pyproject.toml` |
| MyPy | Type checking | `pyproject.toml` |
| pytest | Testing | `pyproject.toml` |
| pre-commit | Git hooks | `.pre-commit-config.yaml` |

### Running Checks

```bash
# Linting
ruff check src/ tests/

# Formatting
ruff format src/ tests/

# Type checking
mypy src/

# All checks (via pre-commit)
pre-commit run --all-files
```

## Testing

### Test Structure

```
tests/
├── conftest.py              # Shared fixtures
├── test_config.py           # Config tests
├── test_exporters.py        # Exporter tests
├── test_scheduler.py        # Scheduler tests
└── test_collectors/         # Collector tests
    ├── test_cpu.py
    ├── test_memory.py
    ├── test_disk.py
    ├── test_network.py
    ├── test_thermal.py
    ├── test_fan.py
    ├── test_voltage.py
    ├── test_battery.py
    └── test_gpu.py
```

### Running Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=src --cov-report=html

# Specific test file
pytest tests/test_collectors/test_cpu.py

# Specific test
pytest tests/test_collectors/test_cpu.py::TestCPUCollector::test_collect_metrics
```

### Test Guidelines

- Use pytest fixtures from `conftest.py`
- Mock external dependencies (WMI, OHM, psutil)
- Test both success and error paths
- Aim for >80% coverage
- Use descriptive test names: `test_<method>_<scenario>_<expected>`

## Documentation

### Required Updates

- **README.md**: For user-facing changes
- **docs/configuration.md**: For config changes
- **docs/hardware_support.md**: For new sensor support
- **docs/troubleshooting.md**: For known issues
- **CHANGELOG.md**: Under `[Unreleased]` section
- **Docstrings**: Google-style for all public APIs

### Docstring Example

```python
def collect_cpu_metrics(config: CPUConfig) -> dict[str, Any]:
    """Collect CPU metrics based on configuration.

    Args:
        config: CPU collector configuration.

    Returns:
        Dictionary containing CPU metrics.

    Raises:
        RuntimeError: If metrics collection fails.
    """
```

## Release Process

Maintainers only:

1. Create `release/vX.Y.Z` branch from `main`
2. Update `CHANGELOG.md` with release notes
3. Update version in `pyproject.toml` (or `uv version`)
4. Create PR to `main`
5. After merge, tag release: `git tag -s vX.Y.Z -m "Release vX.Y.Z"`
6. Push tag: `git push origin vX.Y.Z`
7. GitHub Actions builds and publishes to PyPI
8. GitHub Release created automatically

## Questions?

- Open a [question issue](.github/ISSUE_TEMPLATE/question.md)
- Check existing [discussions](https://github.com/owner/repo/discussions)
- Review [architecture docs](ARCHITECTURE.md)

---

Thank you for contributing! 🎉