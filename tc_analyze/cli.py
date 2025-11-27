"""
TC-Analyze Command Line Interface

Tropical Cyclone Analysis Tool CLI for data management and utilities.
"""

import typer
from typing import Optional

# Create main app
app = typer.Typer(
    name="tc-analyze",
    help="Tropical Cyclone Analysis Tool - Data Management and Utilities",
    add_completion=True,
    no_args_is_help=True,
)


def version_callback(value: bool):
    """Display version information."""
    if value:
        typer.echo("tc-analyze version 2.0.0")
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit",
    )
):
    """
    Tropical Cyclone Analysis Tool

    A command-line interface for managing and analyzing tropical cyclone data.
    """
    pass


# Import and register subcommands
def register_commands():
    """Register all subcommands."""
    from tc_analyze.commands import data, config_cmd, center

    app.add_typer(data.app, name="data", help="Data management and inspection")
    app.add_typer(config_cmd.app, name="config", help="Configuration management")
    app.add_typer(center.app, name="center", help="TC center analysis")


# Register commands when module is imported
register_commands()


if __name__ == "__main__":
    app()
