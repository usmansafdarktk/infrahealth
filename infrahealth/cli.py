import click
import json
from .health import get_server_health
from .docker_health import get_docker_health
from .alert import send_alert


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
@click.option("--alert", is_flag=True, help="Send email alert if metrics exceed thresholds")
def server(format: str, detailed: bool, alert: bool):
    """Check server health (CPU, memory, disk, and optional detailed metrics)."""
    try:
        health = get_server_health(detailed=detailed)
        if alert:
            alert_config = {
                "cpu_threshold": 80, "memory_threshold": 80,
                "email_from": "alert@infrahealth.com", "email_to": "admin@infrahealth.com",
                "smtp_host": "smtp.example.com", "smtp_port": 587,
                "email_user": "user", "email_password": "pass"
            }
            send_alert(health, alert_config)
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


@check.command(name="docker")
@click.option("--format", default="text", help="Output format (text/json)", type=click.Choice(["text", "json"]))
@click.option("--detailed", is_flag=True, help="Show detailed metrics (network, restart count)")
@click.option("--alert", is_flag=True, help="Send email alert if metrics exceed thresholds")
@click.option("--app-check", is_flag=True, help="Check application health via HTTP endpoint")
def docker(format: str, detailed: bool, alert: bool, app_check: bool):
    """Check health of running Docker containers."""
    try:
        health = get_docker_health(detailed=detailed, app_check=app_check)
        if not health:
            click.echo("No running Docker containers found.")
            return
        if alert:
            alert_config = {
                "cpu_threshold": 80, "memory_threshold": 80, "restart_threshold": 5,
                "email_from": "alert@infrahealth.com", "email_to": "admin@infrahealth.com",
                "smtp_host": "smtp.example.com", "smtp_port": 587,
                "email_user": "user", "email_password": "pass"
            }
            send_alert(health, alert_config)
        if format == "json":
            click.echo(json.dumps(health, indent=2))
        else:
            for container in health:
                output = [
                    f"Container: {container['name']}",
                    f"Status: {container['status']}",
                    f"CPU: {container['cpu_percent']:.1f}%",
                    f"Memory: {container['memory_percent']:.1f}%"
                ]
                if detailed:
                    output.extend([
                        f"Network Sent: {container['network_bytes_sent']:,} bytes",
                        f"Network Received: {container['network_bytes_received']:,} bytes",
                        f"Restarts: {container['restart_count']}"
                    ])
                if app_check:
                    output.append(f"App Health: {container['app_health']}")
                click.echo("\n".join(output))
                click.echo("-" * 40)
    except RuntimeError as e:
        click.echo(f"Error: {str(e)}", err=True)
        exit(1)


cli.add_command(check)


@cli.command(name="start-prometheus")
@click.option("--port", default=8000, help="Port for Prometheus exporter", type=int)
def start_prometheus(port: int):
    """Start Prometheus exporter for server and Docker metrics."""
    from .prometheus_exporter import export_metrics
    try:
        export_metrics(port)
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        exit(1)


def main():
    """Entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
