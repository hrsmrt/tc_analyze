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
from utils.center import load_center_coordinates

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


@app.command("inspect")
def inspect_center(
    center_type: str = typer.Argument(..., help="Center type: ss_slp or ms_pres"),
    config_file: Optional[str] = typer.Option(None, "--config", "-c", help="Configuration file"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed information"),
):
    """Inspect center coordinate file and display metadata.

    Examples:
        tc-analyze center inspect ss_slp
        tc-analyze center inspect ms_pres
        tc-analyze center inspect ss_slp --verbose
    """
    try:
        config = AnalysisConfig(config_file=config_file, auto_parse_args=False)

        typer.secho(f"\n🔍 Inspecting {center_type} center coordinates\n", fg=typer.colors.CYAN, bold=True)

        # Validate center type
        if center_type not in config.center_configs:
            typer.secho(f"✗ Unknown center type: {center_type}", fg=typer.colors.RED)
            typer.echo(f"  Available types: {', '.join(config.center_configs.keys())}")
            raise typer.Exit(1)

        # Get filename from config
        filename = config.center_configs[center_type]
        center_dir = os.path.join(config.data_dir, f"center/{center_type}")
        filepath = os.path.join(center_dir, filename)

        typer.echo(f"  File: {filepath}")

        # Check if file exists
        if not os.path.exists(filepath):
            # Try alternative extension
            base, ext = os.path.splitext(filename)
            if ext == '.npz':
                alt_filename = base + '.npy'
            elif ext == '.npy':
                alt_filename = base + '.npz'
            else:
                alt_filename = None

            if alt_filename:
                alt_path = os.path.join(center_dir, alt_filename)
                if os.path.exists(alt_path):
                    filepath = alt_path
                    typer.secho(f"  Using alternative: {filepath}", fg=typer.colors.YELLOW)

        if not os.path.exists(filepath):
            typer.secho(f"\n✗ File not found: {filepath}", fg=typer.colors.RED)
            typer.echo(f"  Please run center calculation first:")
            typer.echo(f"    - For ss_slp: python analysis/center/calc/ss_slp_center_calc.py")
            typer.echo(f"    - For ms_pres: python analysis/center/calc/ms_pres_center_calc.py")
            raise typer.Exit(1)

        # Load data
        file_ext = os.path.splitext(filepath)[1]
        typer.echo(f"  Format: {file_ext}")
        typer.echo("")

        if file_ext == '.npz':
            data = np.load(filepath)
            center = data["center"]
            has_metadata = True
        elif file_ext == '.npy':
            center = np.load(filepath)
            data = None
            has_metadata = False
        else:
            typer.secho(f"✗ Unsupported file format: {file_ext}", fg=typer.colors.RED)
            raise typer.Exit(1)

        # Display center data info
        typer.secho("📍 Center Coordinates:", fg=typer.colors.GREEN, bold=True)
        typer.echo(f"  Shape: {center.shape}")

        if center.ndim == 2:
            typer.echo(f"  Type: 2D center (nt={center.shape[0]})")
            typer.echo(f"  X range: [{center[:, 0].min()/1e3:.2f}, {center[:, 0].max()/1e3:.2f}] km")
            typer.echo(f"  Y range: [{center[:, 1].min()/1e3:.2f}, {center[:, 1].max()/1e3:.2f}] km")
        elif center.ndim == 3:
            typer.echo(f"  Type: 3D center (nt={center.shape[0]}, nz={center.shape[1]})")
            typer.echo(f"  X range: [{center[:, :, 0].min()/1e3:.2f}, {center[:, :, 0].max()/1e3:.2f}] km")
            typer.echo(f"  Y range: [{center[:, :, 1].min()/1e3:.2f}, {center[:, :, 1].max()/1e3:.2f}] km")

        # Display metadata
        if has_metadata and data is not None:
            typer.echo("")
            typer.secho("📊 Metadata:", fg=typer.colors.GREEN, bold=True)

            metadata_keys = [key for key in data.files if key != "center"]

            for key in sorted(metadata_keys):
                value = data[key]

                # Format specific keys
                if key in ["r_refine", "r_search"]:
                    if isinstance(value, (int, float, np.number)):
                        km_value = value / 1e3
                    else:
                        km_value = value.item() / 1e3
                    typer.echo(f"  {key:30s}: {value:.0f} m ({km_value:.1f} km)")
                elif key == "actual_iterations":
                    if isinstance(value, np.ndarray):
                        typer.echo(f"  {key:30s}: mean={value.mean():.2f}, max={value.max()}")
                        if verbose:
                            typer.echo(f"    Shape: {value.shape}")
                elif key in ["z_first", "z_last"]:
                    typer.echo(f"  {key:30s}: {value}")
                elif key == "max_iterations":
                    typer.echo(f"  {key:30s}: {value}")
                elif key in ["convergence_threshold_x", "convergence_threshold_y"]:
                    if verbose:
                        typer.echo(f"  {key:30s}: {value}")
                else:
                    if verbose:
                        if isinstance(value, np.ndarray):
                            typer.echo(f"  {key:30s}: array(shape={value.shape}, dtype={value.dtype})")
                        else:
                            typer.echo(f"  {key:30s}: {value}")
        else:
            typer.echo("")
            typer.secho("ℹ️  No metadata (npy format)", fg=typer.colors.YELLOW)

        typer.secho(f"\n✓ Inspection complete", fg=typer.colors.GREEN, bold=True)
        typer.echo("")

    except Exception as e:
        typer.secho(f"\n✗ Error: {e}", fg=typer.colors.RED)
        if verbose:
            import traceback
            traceback.print_exc()
        raise typer.Exit(1)
