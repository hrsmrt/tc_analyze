"""
Data management commands.
"""

import os
import sys
from pathlib import Path
from typing import Optional

import typer
import numpy as np

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from utils.metadata import (
    read_data_metadata,
    find_data_files,
    format_size,
    format_shape,
    get_data_statistics,
)
from utils.config import AnalysisConfig

app = typer.Typer(help="Data management and inspection")


@app.command("list")
def list_data(
    data_type: Optional[str] = typer.Option(None, "--type", "-t", help="Filter by type (center, azim, 3d, 2d)"),
    config_file: Optional[str] = typer.Option(None, "--config", "-c", help="Configuration file"),
):
    """List all data files."""
    try:
        config = AnalysisConfig(config_file=config_file, auto_parse_args=False)
        data_dir = config.data_dir

        if not os.path.exists(data_dir):
            typer.secho(f"✗ Data directory not found: {data_dir}", fg=typer.colors.RED)
            raise typer.Exit(1)

        typer.secho(f"\n📂 Data Directory: {data_dir}\n", fg=typer.colors.CYAN, bold=True)

        # Find all .npz files
        npz_files = find_data_files(data_dir, "*.npz")
        npy_files = find_data_files(data_dir, "*.npy")

        all_files = npz_files + npy_files

        if not all_files:
            typer.secho("No data files found.", fg=typer.colors.YELLOW)
            return

        # Filter by type if specified
        if data_type:
            all_files = [f for f in all_files if data_type in f]

        # Sort and display
        all_files.sort()

        for file_path in all_files:
            rel_path = os.path.relpath(file_path, data_dir)
            size = format_size(os.path.getsize(file_path))
            typer.echo(f"  {rel_path:<60} {size:>10}")

        typer.echo(f"\n  Total: {len(all_files)} files")

    except Exception as e:
        typer.secho(f"✗ Error: {e}", fg=typer.colors.RED)
        raise typer.Exit(1)


@app.command("info")
def data_info(
    path: str = typer.Argument(..., help="Relative path to data file (e.g., center/ss_slp/center.npz)"),
    config_file: Optional[str] = typer.Option(None, "--config", "-c", help="Configuration file"),
):
    """Display detailed information about a data file."""
    try:
        config = AnalysisConfig(config_file=config_file, auto_parse_args=False)
        data_dir = config.data_dir

        # Construct full path
        full_path = os.path.join(data_dir, path)

        # Try different extensions if file doesn't exist
        if not os.path.exists(full_path):
            for ext in [".npz", ".npy"]:
                if os.path.exists(full_path + ext):
                    full_path = full_path + ext
                    break

        if not os.path.exists(full_path):
            typer.secho(f"✗ File not found: {full_path}", fg=typer.colors.RED)
            raise typer.Exit(1)

        # Read metadata
        metadata = read_data_metadata(full_path)

        # Display information
        rel_path = os.path.relpath(full_path, data_dir)
        typer.secho(f"\n📊 Data File: {rel_path}\n", fg=typer.colors.CYAN, bold=True)

        typer.echo(f"  Format:     {metadata['format']}")
        typer.echo(f"  File size:  {format_size(metadata['file_size'])}")

        if "data_shape" in metadata:
            typer.echo(f"  Shape:      {format_shape(metadata['data_shape'])}")
            typer.echo(f"  Data type:  {metadata['data_dtype']}")

        # Display metadata fields
        if metadata["format"] == "npz":
            typer.echo(f"\n  📦 Available keys: {', '.join(metadata['keys'])}")

            typer.echo(f"\n  ⚙️  Parameters:")
            for key, value in metadata.items():
                if key not in ["file_path", "file_size", "format", "keys", "data_shape", "data_dtype"]:
                    if not key.endswith("_shape"):
                        typer.echo(f"    {key:30} {value}")

        typer.echo("")

    except Exception as e:
        typer.secho(f"✗ Error: {e}", fg=typer.colors.RED)
        raise typer.Exit(1)


@app.command("stats")
def data_stats(
    path: str = typer.Argument(..., help="Relative path to data file"),
    config_file: Optional[str] = typer.Option(None, "--config", "-c", help="Configuration file"),
):
    """Display statistics for a data file."""
    try:
        config = AnalysisConfig(config_file=config_file, auto_parse_args=False)
        data_dir = config.data_dir

        # Construct full path
        full_path = os.path.join(data_dir, path)

        # Try different extensions
        if not os.path.exists(full_path):
            for ext in [".npz", ".npy"]:
                if os.path.exists(full_path + ext):
                    full_path = full_path + ext
                    break

        if not os.path.exists(full_path):
            typer.secho(f"✗ File not found: {full_path}", fg=typer.colors.RED)
            raise typer.Exit(1)

        # Load data
        if full_path.endswith(".npz"):
            data_obj = np.load(full_path)
            # Try to find the main data array
            if "center" in data_obj:
                data_array = data_obj["center"]
            elif "data" in data_obj:
                data_array = data_obj["data"]
            else:
                typer.secho(f"✗ No 'center' or 'data' key found in {path}", fg=typer.colors.RED)
                raise typer.Exit(1)
        else:
            data_array = np.load(full_path)

        # Calculate statistics
        stats = get_data_statistics(data_array)

        # Display
        rel_path = os.path.relpath(full_path, data_dir)
        typer.secho(f"\n📈 Statistics: {rel_path}\n", fg=typer.colors.CYAN, bold=True)

        typer.echo(f"  Shape:      {format_shape(data_array.shape)}")
        typer.echo(f"  Data type:  {data_array.dtype}")
        typer.echo(f"\n  Statistics:")
        typer.echo(f"    Min:      {stats['min']:.6f}")
        typer.echo(f"    Max:      {stats['max']:.6f}")
        typer.echo(f"    Mean:     {stats['mean']:.6f}")
        typer.echo(f"    Std Dev:  {stats['std']:.6f}")

        if stats['nan_count'] > 0:
            typer.echo(f"    NaN/Inf:  {stats['nan_count']} ({stats['nan_count']/data_array.size*100:.1f}%)")

        typer.echo("")

    except Exception as e:
        typer.secho(f"✗ Error: {e}", fg=typer.colors.RED)
        raise typer.Exit(1)
