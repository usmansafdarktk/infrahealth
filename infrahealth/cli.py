import click
import json
from .health import get_server_health


@click.group()
def cli():
    """infrahealth: A CLI for infrastructure health monitoring."""
    pass


@click.group(name="check")
def check():
    """Commands to check infrastructure health."""
    pass


@check.command(name="server")
@click.option("--format", default="text", help="Output format (text/json)", type=click.Choice(["text", "json"]))
@click.option("--detailed", is_flag=True, help="Show detailed metrics (network, uptime, processes, load)")
def server(format: str, detailed: bool):
    """Check server health (CPU, memory, disk, and optional detailed metrics)."""
    try:
        health = get_server_health(detailed=detailed)
        if format == "json":
            click.echo(json.dumps(health, indent=2))
        else:
            output = [
                f"CPU: {health['cpu_percent']:.1f}%",
                f"Memory: {health['memory_percent']:.1f}%",
                f"Disk: {health['disk_percent']:.1f}%"
            ]
            if detailed:
                output.extend([
                    f"Network Sent: {health['network_bytes_sent']:,} bytes",
                    f"Network Received: {health['network_bytes_received']:,} bytes",
                    f"Uptime: {health['uptime_seconds'] / 3600:.1f} hours",
                    f"Processes: {health['process_count']:,}"
                ])
                if "load_avg_1min" in health:
                    output.extend([
                        f"Load Average (1min): {health['load_avg_1min']:.2f}",
                        f"Load Average (5min): {health['load_avg_5min']:.2f}",
                        f"Load Average (15min): {health['load_avg_15min']:.2f}"
                    ])
            click.echo("\n".join(output))
    except RuntimeError as e:
        click.echo(f"Error: {str(e)}", err=True)
        exit(1)


cli.add_command(check)


def main():
    """Entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
