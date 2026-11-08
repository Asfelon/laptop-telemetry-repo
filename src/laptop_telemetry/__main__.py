"""
Main entry point for laptop telemetry collector.
"""

import sys
from pathlib import Path

import click

from .collectors.registry import TelemetryCollectorRegistry
from .config.loader import create_default_config, load_config
from .scheduler.runner import TelemetryRunner


@click.group(invoke_without_command=True)
@click.version_option(version="0.1.0")
@click.option("--config", "-c", type=click.Path(exists=True), help="Path to configuration file")
@click.option("--interval", "-i", type=int, help="Collection interval in seconds")
@click.option("--output", "-o", type=click.Path(), help="Output directory")
@click.option("--format", "-f", type=click.Choice(["jsonl", "csv", "both"]), help="Output format")
@click.option("--duration", "-d", type=int, default=0, help="Duration in seconds (0 = infinite)")
@click.option("--once", is_flag=True, help="Collect once and exit")
@click.option("--dry-run", is_flag=True, help="Show what would be collected without collecting")
@click.option("--list-sensors", is_flag=True, help="List available sensors and exit")
@click.option("--collector-status", is_flag=True, help="Show collector status and exit")
@click.option("--validate-config", is_flag=True, help="Validate configuration and exit")
def cli(
    config,
    interval,
    output,
    format,
    duration,
    once,
    dry_run,
    list_sensors,
    collector_status,
    validate_config,
):
    """Laptop Telemetry Collector - Comprehensive system telemetry for Windows."""
    if not click.get_current_context().invoked_subcommand:
        # Default behavior: run the collector
        from .config.loader import load_config
        from .scheduler.runner import TelemetryRunner

        try:
            telemetry_config = load_config(config)
        except Exception as e:
            click.echo(f"Error loading configuration: {e}", err=True)
            sys.exit(1)

        if interval:
            telemetry_config.collection.interval_seconds = interval
        if output:
            telemetry_config.output.directory = output
        if format:
            telemetry_config.output.format = format
        if duration:
            telemetry_config.collection.duration_seconds = duration

        if validate_config:
            click.echo("Configuration is valid!")
            click.echo(f"Collection interval: {telemetry_config.collection.interval_seconds}s")
            click.echo(f"Output format: {telemetry_config.output.format.value}")
            click.echo(f"Output directory: {telemetry_config.output.directory}")
            return

        if dry_run:
            click.echo("Dry run - would collect:")
            click.echo(f"  Interval: {telemetry_config.collection.interval_seconds}s")
            click.echo(
                f"  Duration: {telemetry_config.collection.duration_seconds}s (0 = infinite)"
            )
            click.echo(
                f"  Output: {telemetry_config.output.directory} "
                f"({telemetry_config.output.format.value})"
            )
            click.echo("  Enabled collectors:")
            collector_names = [
                "cpu",
                "memory",
                "disk",
                "network",
                "thermal",
                "fan",
                "voltage",
                "battery",
                "gpu",
            ]
            for name in collector_names:
                collector_config = telemetry_config.collectors.model_dump().get(name, {})
                if collector_config.get("enabled", False):
                    click.echo(f"    - {name}")
            return

        if list_sensors:
            click.echo("Available sensors:")
            collector_names = [
                "cpu",
                "memory",
                "disk",
                "network",
                "thermal",
                "fan",
                "voltage",
                "battery",
                "gpu",
            ]
            for name in collector_names:
                click.echo(f"  - {name}")
            return

        if collector_status:
            click.echo("Collector status:")
            collector_names = [
                "cpu",
                "memory",
                "disk",
                "network",
                "thermal",
                "fan",
                "voltage",
                "battery",
                "gpu",
            ]
            for name in collector_names:
                click.echo(f"  {name}: enabled")
            return

        if once:
            click.echo("Collecting telemetry once...")
            runner = TelemetryRunner(telemetry_config)
            data = runner.collect_once()
            click.echo(f"Collected data keys: {list(data.keys())}")
            # Export the collected data
            for exporter in runner.exporters.values():
                try:
                    exporter.export([data])
                    click.echo(f"Exported to {exporter.name}")
                except Exception as e:
                    click.echo(f"Error exporting: {e}", err=True)
            # Close exporters
            for exporter in runner.exporters.values():
                if hasattr(exporter, "close"):
                    exporter.close()
            return

        click.echo(
            f"Starting telemetry collection "
            f"(interval: {telemetry_config.collection.interval_seconds}s)"
        )
        fmt = telemetry_config.output.format
        fmt_str = fmt.value if hasattr(fmt, "value") else str(fmt)
        click.echo(f"Output: {telemetry_config.output.directory} ({fmt_str})")
        click.echo("Press Ctrl+C to stop")

        try:
            runner = TelemetryRunner(telemetry_config)
            runner.start()
            import time

            while runner.running:
                time.sleep(1)
        except KeyboardInterrupt:
            click.echo("\nStopping...")
            runner.stop()
            click.echo("Stopped.")
        return


@cli.command()
@click.option("--config", "-c", type=click.Path(exists=True), help="Path to configuration file")
@click.option("--interval", "-i", type=int, help="Collection interval in seconds")
@click.option("--output", "-o", type=click.Path(), help="Output directory")
@click.option("--format", "-f", type=click.Choice(["jsonl", "csv", "both"]), help="Output format")
@click.option("--duration", "-d", type=int, default=0, help="Duration in seconds (0 = infinite)")
@click.option("--once", is_flag=True, help="Collect once and exit")
@click.option("--dry-run", is_flag=True, help="Show what would be collected without collecting")
@click.option("--list-sensors", is_flag=True, help="List available sensors and exit")
@click.option("--collector-status", is_flag=True, help="Show collector status and exit")
@click.option("--validate-config", is_flag=True, help="Validate configuration and exit")
def run(
    config,
    interval,
    output,
    format,
    duration,
    once,
    dry_run,
    list_sensors,
    collector_status,
    validate_config,
):
    """Run the telemetry collector."""

    # Load configuration
    try:
        telemetry_config = load_config(config)
    except Exception as e:
        click.echo(f"Error loading configuration: {e}", err=True)
        sys.exit(1)

    # Override config with CLI options
    if interval:
        telemetry_config.collection.interval_seconds = interval
    if output:
        telemetry_config.output.directory = output
    if format:
        from .config.models import OutputFormat

        telemetry_config.output.format = OutputFormat(format)
    if duration:
        telemetry_config.collection.duration_seconds = duration

    # Validate config
    if validate_config:
        click.echo("Configuration is valid!")
        click.echo(f"Collection interval: {telemetry_config.collection.interval_seconds}s")
        click.echo(f"Output format: {telemetry_config.output.format.value}")
        click.echo(f"Output directory: {telemetry_config.output.directory}")
        return

    # Create runner
    runner = TelemetryRunner(telemetry_config)

    # List sensors
    if list_sensors:
        click.echo("Available sensors:")
        TelemetryCollectorRegistry()
        # Register collectors to get names
        from .collectors.battery import BatteryCollector
        from .collectors.cpu import CPUCollector
        from .collectors.disk import DiskCollector
        from .collectors.fan import FanCollector
        from .collectors.gpu import GPUCollector
        from .collectors.memory import MemoryCollector
        from .collectors.network import NetworkCollector
        from .collectors.thermal import ThermalCollector
        from .collectors.voltage import VoltageCollector

        collectors = [
            ("cpu", CPUCollector),
            ("memory", MemoryCollector),
            ("disk", DiskCollector),
            ("network", NetworkCollector),
            ("thermal", ThermalCollector),
            ("fan", FanCollector),
            ("voltage", VoltageCollector),
            ("battery", BatteryCollector),
            ("gpu", GPUCollector),
        ]

        for name, _ in collectors:
            click.echo(f"  - {name}")
        return

    # Collector status
    if collector_status:
        click.echo("Collector status:")
        from .collectors.battery import BatteryCollector
        from .collectors.cpu import CPUCollector
        from .collectors.disk import DiskCollector
        from .collectors.fan import FanCollector
        from .collectors.gpu import GPUCollector
        from .collectors.memory import MemoryCollector
        from .collectors.network import NetworkCollector
        from .collectors.thermal import ThermalCollector
        from .collectors.voltage import VoltageCollector

        collectors = [
            ("cpu", CPUCollector),
            ("memory", MemoryCollector),
            ("disk", DiskCollector),
            ("network", NetworkCollector),
            ("thermal", ThermalCollector),
            ("fan", FanCollector),
            ("voltage", VoltageCollector),
            ("battery", BatteryCollector),
            ("gpu", GPUCollector),
        ]

        for name, collector_class in collectors:
            collector = collector_class(name)
            enabled = collector.is_enabled(telemetry_config.collectors.dict().get(name, {}))
            click.echo(f"  {name}: {'enabled' if enabled else 'disabled'}")
        return

    # Dry run
    if dry_run:
        click.echo("Dry run - would collect:")
        click.echo(f"  Interval: {telemetry_config.collection.interval_seconds}s")
        click.echo(f"  Duration: {telemetry_config.collection.duration_seconds}s (0 = infinite)")
        fmt = telemetry_config.output.format
        fmt_str = fmt.value if hasattr(fmt, "value") else str(fmt)
        click.echo(
            f"  Output: {telemetry_config.output.directory} "
            f"({fmt_str})"
        )
        click.echo("  Enabled collectors:")
        collector_names = [
            "cpu",
            "memory",
            "disk",
            "network",
            "thermal",
            "fan",
            "voltage",
            "battery",
            "gpu",
        ]
        for name in collector_names:
            collector_config = telemetry_config.collectors.model_dump().get(name, {})
            if collector_config.get("enabled", False):
                click.echo(f"    - {name}")
        return

    # Run once
    if once:
        click.echo("Collecting telemetry once...")
        data = runner.collect_once()
        click.echo(f"Collected data keys: {list(data.keys())}")
        return

    # Run continuously
    click.echo(
        f"Starting telemetry collection (interval: {telemetry_config.collection.interval_seconds}s)"
    )
    fmt = telemetry_config.output.format
    fmt_str = fmt.value if hasattr(fmt, "value") else str(fmt)
    click.echo(
        f"Output: {telemetry_config.output.directory} ({fmt_str})"
    )
    click.echo("Press Ctrl+C to stop")

    runner = TelemetryRunner(telemetry_config)
    try:
        runner.start()
        # Keep main thread alive
        while runner.running:
            import time

            time.sleep(1)
    except KeyboardInterrupt:
        click.echo("\nStopping...")
        runner.stop()
        click.echo("Stopped.")


@cli.command()
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    default="config/default.yaml",
    help="Output path for default config",
)
def generate_config(output):
    """Generate default configuration file."""
    config = create_default_config()

    import yaml

    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)

    click.echo(f"Default configuration written to {output_path}")


if __name__ == "__main__":
    cli()
