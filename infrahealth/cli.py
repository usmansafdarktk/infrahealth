# infrahealth/cli.py
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
def server(format: str):
    """Check server health (CPU, memory, disk)."""
    try:
        health = get_server_health()
        if format == "json":
            click.echo(json.dumps(health, indent=2))
        else:
            click.echo(
                f"CPU: {health['cpu']:.1f}% | Memory: {health['memory']:.1f}% | Disk: {health['disk']:.1f}%")
    except RuntimeError as e:
        click.echo(f"Error: {str(e)}", err=True)
        exit(1)


cli.add_command(check)


def main():
    """Entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
