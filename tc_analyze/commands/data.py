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


@app.command("annotate")
def annotate_file(
    filepath: str = typer.Argument(..., help="Path to .npz file (relative or absolute)"),
    config_file: Optional[str] = typer.Option(None, "--config", "-c", help="Configuration file"),
):
    """Interactively add or edit metadata in .npz files.

    This command allows you to add custom metadata (description, notes, author, etc.)
    to existing .npz files through an interactive menu.

    Examples:
        tc-analyze data annotate center/ss_slp/center.npz
        tc-analyze data annotate /path/to/file.npz
    """
    try:
        # Resolve file path
        if not os.path.isabs(filepath):
            if os.path.exists(filepath):
                full_path = os.path.abspath(filepath)
            else:
                try:
                    config = AnalysisConfig(config_file=config_file, auto_parse_args=False)
                    full_path = os.path.join(config.data_dir, filepath)
                except:
                    full_path = filepath
        else:
            full_path = filepath

        # Check file existence
        if not os.path.exists(full_path):
            typer.secho(f"✗ File not found: {full_path}", fg=typer.colors.RED)
            raise typer.Exit(1)

        # Check file extension
        if not full_path.endswith('.npz'):
            typer.secho(f"✗ This command only works with .npz files", fg=typer.colors.RED)
            typer.echo(f"  File: {full_path}")
            raise typer.Exit(1)

        # Load existing data
        data = np.load(full_path)
        save_dict = {key: data[key] for key in data.files}

        typer.secho(f"\n📝 Annotating: {os.path.basename(full_path)}\n", fg=typer.colors.CYAN, bold=True)
        typer.echo(f"  Path: {full_path}\n")

        # Interactive loop
        modified = False
        while True:
            # Display current keys
            typer.secho("📦 Current keys:", fg=typer.colors.GREEN)
            for key in sorted(save_dict.keys()):
                value = save_dict[key]
                if isinstance(value, np.ndarray):
                    typer.echo(f"  {key:30} [ndarray, shape={value.shape}]")
                else:
                    value_str = str(value)
                    if len(value_str) > 50:
                        value_str = value_str[:47] + "..."
                    typer.echo(f"  {key:30} = {value_str}")
            typer.echo("")

            # Show menu
            typer.secho("Options:", fg=typer.colors.YELLOW)
            typer.echo("  [a] Add new metadata")
            typer.echo("  [e] Edit existing metadata")
            typer.echo("  [d] Delete metadata")
            typer.echo("  [s] Save and exit")
            typer.echo("  [q] Quit without saving")
            typer.echo("")

            choice = typer.prompt("Choose an option", type=str).lower()

            if choice == 'a':
                # Add new metadata
                typer.echo("")
                key = typer.prompt("Enter key name (e.g., 'description', 'notes', 'author')")

                if key in save_dict:
                    overwrite = typer.confirm(f"Key '{key}' already exists. Overwrite?")
                    if not overwrite:
                        continue

                value_type = typer.prompt(
                    "Value type",
                    type=typer.Choice(["string", "number", "array"], case_sensitive=False),
                    default="string"
                )

                if value_type == "string":
                    value = typer.prompt("Enter value")
                    save_dict[key] = value
                elif value_type == "number":
                    value = typer.prompt("Enter number", type=float)
                    save_dict[key] = value
                elif value_type == "array":
                    typer.echo("Enter array values separated by spaces (e.g., '1 2 3 4 5')")
                    values_str = typer.prompt("Values")
                    values = [float(x) for x in values_str.split()]
                    save_dict[key] = np.array(values)

                typer.secho(f"✓ Added '{key}'", fg=typer.colors.GREEN)
                modified = True

            elif choice == 'e':
                # Edit existing metadata
                typer.echo("")
                # Filter out array keys (typically data, not metadata)
                editable_keys = [k for k, v in save_dict.items() if not isinstance(v, np.ndarray) or v.size == 1]

                if not editable_keys:
                    typer.secho("No editable metadata found (only arrays present)", fg=typer.colors.YELLOW)
                    continue

                typer.echo("Editable keys:")
                for i, key in enumerate(editable_keys, 1):
                    value = save_dict[key]
                    if isinstance(value, np.ndarray):
                        value = value.item()
                    typer.echo(f"  [{i}] {key} = {value}")
                typer.echo("")

                key_choice = typer.prompt("Enter key number or name")

                # Try to parse as number
                try:
                    idx = int(key_choice) - 1
                    if 0 <= idx < len(editable_keys):
                        key = editable_keys[idx]
                    else:
                        typer.secho("Invalid number", fg=typer.colors.RED)
                        continue
                except ValueError:
                    key = key_choice

                if key not in save_dict:
                    typer.secho(f"Key '{key}' not found", fg=typer.colors.RED)
                    continue

                current_value = save_dict[key]
                if isinstance(current_value, np.ndarray):
                    current_value = current_value.item()

                typer.echo(f"Current value: {current_value}")
                new_value = typer.prompt("Enter new value", default=str(current_value))

                # Try to preserve type
                if isinstance(current_value, (int, float)):
                    try:
                        save_dict[key] = float(new_value)
                    except ValueError:
                        save_dict[key] = new_value
                else:
                    save_dict[key] = new_value

                typer.secho(f"✓ Updated '{key}'", fg=typer.colors.GREEN)
                modified = True

            elif choice == 'd':
                # Delete metadata
                typer.echo("")
                # Filter out main data arrays
                deletable_keys = [k for k in save_dict.keys() if k not in ['center', 'data']]

                if not deletable_keys:
                    typer.secho("No deletable metadata found", fg=typer.colors.YELLOW)
                    continue

                typer.echo("Deletable keys:")
                for i, key in enumerate(deletable_keys, 1):
                    typer.echo(f"  [{i}] {key}")
                typer.echo("")

                key_choice = typer.prompt("Enter key number or name to delete")

                try:
                    idx = int(key_choice) - 1
                    if 0 <= idx < len(deletable_keys):
                        key = deletable_keys[idx]
                    else:
                        typer.secho("Invalid number", fg=typer.colors.RED)
                        continue
                except ValueError:
                    key = key_choice

                if key not in save_dict:
                    typer.secho(f"Key '{key}' not found", fg=typer.colors.RED)
                    continue

                if key in ['center', 'data']:
                    typer.secho(f"Cannot delete main data array '{key}'", fg=typer.colors.RED)
                    continue

                confirm = typer.confirm(f"Delete '{key}'?")
                if confirm:
                    del save_dict[key]
                    typer.secho(f"✓ Deleted '{key}'", fg=typer.colors.GREEN)
                    modified = True

            elif choice == 's':
                # Save and exit
                if not modified:
                    typer.echo("No changes made.")
                    return

                typer.echo("")
                confirm = typer.confirm("Save changes?")
                if confirm:
                    # Create backup
                    backup_path = full_path + ".backup"
                    import shutil
                    shutil.copy2(full_path, backup_path)
                    typer.echo(f"  Created backup: {backup_path}")

                    # Save with new metadata
                    np.savez(full_path, **save_dict)
                    typer.secho(f"\n✓ Saved changes to {os.path.basename(full_path)}",
                               fg=typer.colors.GREEN, bold=True)
                    typer.echo("")
                    return
                else:
                    typer.echo("Save cancelled.")

            elif choice == 'q':
                # Quit without saving
                if modified:
                    confirm = typer.confirm("You have unsaved changes. Quit anyway?")
                    if not confirm:
                        continue
                typer.echo("Exited without saving.")
                return

            else:
                typer.secho("Invalid option. Please choose a, e, d, s, or q.", fg=typer.colors.RED)

    except Exception as e:
        typer.secho(f"\n✗ Error: {e}", fg=typer.colors.RED)
        import traceback
        traceback.print_exc()
        raise typer.Exit(1)
