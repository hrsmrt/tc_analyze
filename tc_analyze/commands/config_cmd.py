"""
Configuration management commands.
"""

import os
import sys
from typing import Optional

import typer

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from utils.config import AnalysisConfig

app = typer.Typer(help="Configuration management")


@app.command("show")
def show_config(
    config_file: Optional[str] = typer.Option(None, "--config", "-c", help="Configuration file"),
):
    """Display current configuration."""
    try:
        config = AnalysisConfig(config_file=config_file, auto_parse_args=False)

        typer.secho("\n⚙️  Configuration\n", fg=typer.colors.CYAN, bold=True)

        # File information
        typer.echo(f"  Config file:    {config._config_path}")

        # Grid settings
        typer.secho("\n  📐 Grid Settings:", fg=typer.colors.YELLOW)
        typer.echo(f"    glevel:       {config.glevel}")
        typer.echo(f"    nx, ny, nz:   {config.nx} × {config.ny} × {config.nz}")
        typer.echo(f"    dx, dy:       {config.dx:.1f} m × {config.dy:.1f} m")
        typer.echo(f"    domain size:  {config.x_width/1e3:.1f} km × {config.y_width/1e3:.1f} km")

        # Time settings
        typer.secho("\n  ⏱️  Time Settings:", fg=typer.colors.YELLOW)
        typer.echo(f"    nt:           {config.nt}")
        typer.echo(f"    t_first:      {config.t_first}")
        typer.echo(f"    t_last:       {config.t_last}")
        typer.echo(f"    dt_output:    {config.dt_hour} hours")

        # Center settings
        typer.secho("\n  🎯 Center Settings:", fg=typer.colors.YELLOW)
        typer.echo(f"    center_type:  {config.center_type_str}")
        typer.echo(f"    center_path:  {config.center_path_str}")

        # Paths
        typer.secho("\n  📁 Paths:", fg=typer.colors.YELLOW)
        typer.echo(f"    input_folder: {config.input_folder}")
        typer.echo(f"    data_dir:     {config.data_dir}")
        typer.echo(f"    fig_dir:      {config.fig_dir}")
        typer.echo(f"    vgrid_file:   {config.vgrid_filepath}")

        # Computation
        typer.secho("\n  💻 Computation:", fg=typer.colors.YELLOW)
        typer.echo(f"    n_jobs:       {config.n_jobs}")
        typer.echo(f"    f (Coriolis): {config.f:.2e} s⁻¹")

        typer.echo("")

    except Exception as e:
        typer.secho(f"✗ Error: {e}", fg=typer.colors.RED)
        raise typer.Exit(1)


@app.command("validate")
def validate_config(
    config_file: Optional[str] = typer.Option(None, "--config", "-c", help="Configuration file"),
):
    """Validate configuration and check file existence."""
    try:
        config = AnalysisConfig(config_file=config_file, auto_parse_args=False)

        typer.secho("\n🔍 Validating Configuration\n", fg=typer.colors.CYAN, bold=True)

        all_valid = True

        # Check input folder
        if os.path.exists(config.input_folder):
            typer.secho(f"  ✓ Input folder exists: {config.input_folder}", fg=typer.colors.GREEN)
        else:
            typer.secho(f"  ✗ Input folder not found: {config.input_folder}", fg=typer.colors.RED)
            all_valid = False

        # Check data directory
        if os.path.exists(config.data_dir):
            typer.secho(f"  ✓ Data directory exists: {config.data_dir}", fg=typer.colors.GREEN)
        else:
            typer.secho(f"  ⚠ Data directory not found: {config.data_dir}", fg=typer.colors.YELLOW)
            typer.echo(f"    (Will be created when needed)")

        # Check fig directory
        if os.path.exists(config.fig_dir):
            typer.secho(f"  ✓ Figure directory exists: {config.fig_dir}", fg=typer.colors.GREEN)
        else:
            typer.secho(f"  ⚠ Figure directory not found: {config.fig_dir}", fg=typer.colors.YELLOW)
            typer.echo(f"    (Will be created when needed)")

        # Check vgrid file
        if os.path.exists(config.vgrid_filepath):
            typer.secho(f"  ✓ Vertical grid file exists: {config.vgrid_filepath}", fg=typer.colors.GREEN)
        else:
            typer.secho(f"  ✗ Vertical grid file not found: {config.vgrid_filepath}", fg=typer.colors.RED)
            all_valid = False

        # Check center coordinates
        center_dir = os.path.join(config.data_dir, config.center_path_str)
        center_npz = os.path.join(center_dir, "center.npz")
        center_npy = os.path.join(center_dir, "center.npy")

        if os.path.exists(center_npz):
            typer.secho(f"  ✓ Center coordinates found: {os.path.relpath(center_npz, config.data_dir)}", fg=typer.colors.GREEN)
        elif os.path.exists(center_npy):
            typer.secho(f"  ✓ Center coordinates found: {os.path.relpath(center_npy, config.data_dir)}", fg=typer.colors.GREEN)
        else:
            typer.secho(f"  ⚠ Center coordinates not found in: {os.path.relpath(center_dir, config.data_dir)}", fg=typer.colors.YELLOW)
            typer.echo(f"    (Run 'tc-analyze center calculate' to generate)")

        # Check write permissions
        try:
            test_file = os.path.join(config.data_dir, ".write_test")
            os.makedirs(config.data_dir, exist_ok=True)
            with open(test_file, "w") as f:
                f.write("test")
            os.remove(test_file)
            typer.secho(f"  ✓ Data directory is writable", fg=typer.colors.GREEN)
        except Exception as e:
            typer.secho(f"  ✗ Data directory is not writable: {e}", fg=typer.colors.RED)
            all_valid = False

        # Summary
        typer.echo("")
        if all_valid:
            typer.secho("✓ Configuration is valid", fg=typer.colors.GREEN, bold=True)
        else:
            typer.secho("✗ Configuration has errors", fg=typer.colors.RED, bold=True)
            raise typer.Exit(1)

        typer.echo("")

    except Exception as e:
        typer.secho(f"✗ Error: {e}", fg=typer.colors.RED)
        raise typer.Exit(1)
