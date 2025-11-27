"""
TC center analysis commands.
"""

import os
import sys
from typing import Optional

import typer
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from utils.config import AnalysisConfig

app = typer.Typer(help="TC center analysis")


@app.command("plot")
def plot_center(
    method: str = typer.Option("ss_slp", "--method", "-m", help="Method: ss_slp or ms_pres"),
    z_level: Optional[int] = typer.Option(None, "--z-level", "-z", help="Z-level for ms_pres (default: 0)"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path"),
    config_file: Optional[str] = typer.Option(None, "--config", "-c", help="Configuration file"),
    show_grid: bool = typer.Option(False, "--grid", help="Show grid lines"),
):
    """Plot TC center trajectory."""
    try:
        config = AnalysisConfig(config_file=config_file, auto_parse_args=False)

        typer.secho(f"\n🎨 Plotting TC center trajectory ({method})\n", fg=typer.colors.CYAN, bold=True)

        # Determine center data path
        if method == "ss_slp":
            center_path = "center/ss_slp"
            typer.echo(f"  Method: Sea Level Pressure (2D)")
        elif method == "ms_pres":
            center_path = "center/ms_pres"
            if z_level is None:
                z_level = 0
            typer.echo(f"  Method: 3D Pressure (z-level: {z_level})")
        else:
            typer.secho(f"✗ Unknown method: {method}", fg=typer.colors.RED)
            raise typer.Exit(1)

        # Load center data
        center_dir = os.path.join(config.data_dir, center_path)
        center_file = os.path.join(center_dir, "center.npz")

        if not os.path.exists(center_file):
            center_file = os.path.join(center_dir, "center.npy")

        if not os.path.exists(center_file):
            typer.secho(f"✗ Center data not found: {center_file}", fg=typer.colors.RED)
            typer.echo(f"  Run center calculation first.")
            raise typer.Exit(1)

        # Load data
        if center_file.endswith(".npz"):
            data = np.load(center_file)
            center = data["center"]
        else:
            center = np.load(center_file)

        # Extract x, y coordinates
        if method == "ss_slp":
            # shape: (nt, 2)
            x_coords = center[:, 0]
            y_coords = center[:, 1]
        elif method == "ms_pres":
            # shape: (nt, nz, 2)
            x_coords = center[:, z_level, 0]
            y_coords = center[:, z_level, 1]

        typer.echo(f"  Data shape: {center.shape}")
        typer.echo(f"  Time steps: {len(x_coords)}")

        # Convert to km
        x_km = x_coords / 1e3
        y_km = y_coords / 1e3

        # Create plot
        fig, ax = plt.subplots(figsize=(10, 8))

        # Plot trajectory
        ax.plot(x_km, y_km, 'b-', linewidth=2, label='Trajectory')
        ax.plot(x_km[0], y_km[0], 'go', markersize=10, label='Start')
        ax.plot(x_km[-1], y_km[-1], 'ro', markersize=10, label='End')

        # Mark every N hours
        time_step = config.dt_hour
        mark_interval = max(1, 6 // time_step)  # Mark every 6 hours
        for i in range(0, len(x_km), mark_interval):
            ax.plot(x_km[i], y_km[i], 'ko', markersize=4)
            ax.text(x_km[i], y_km[i], f'{i*time_step}h', fontsize=8, ha='right')

        ax.set_xlabel('X [km]', fontsize=12)
        ax.set_ylabel('Y [km]', fontsize=12)
        ax.set_title(f'TC Center Trajectory ({method})', fontsize=14, fontweight='bold')
        ax.legend(loc='best')
        ax.set_aspect('equal')

        if show_grid:
            ax.grid(True, alpha=0.3)

        # Determine output path
        if output is None:
            output_dir = config.get_fig_path("center")
            os.makedirs(output_dir, exist_ok=True)
            if method == "ss_slp":
                output = os.path.join(output_dir, "trajectory_ss_slp.png")
            else:
                output = os.path.join(output_dir, f"trajectory_ms_pres_z{z_level:03d}.png")

        # Save figure
        fig.savefig(output, dpi=150, bbox_inches='tight')
        plt.close()

        typer.secho(f"\n✓ Plot saved: {output}", fg=typer.colors.GREEN, bold=True)
        typer.echo("")

    except Exception as e:
        typer.secho(f"✗ Error: {e}", fg=typer.colors.RED)
        import traceback
        traceback.print_exc()
        raise typer.Exit(1)
