"""Plot horizontal distribution of tropical cyclone center by height (smoothed_minimum method).

Plots the TC center positions on x-y plane at each time step, colored by height.
Shows how center location varies with height in horizontal plane.
Reads from smoothed_center.npz (or configured filename in center_configs).

Usage:
    python $WORK/tc_analyze/analysis/center/ms_pres/plot/smoothed_center_horizontal_plot.py
    python $WORK/tc_analyze/analysis/center/ms_pres/plot/smoothed_center_horizontal_plot.py dark_background
"""
import os
import matplotlib
matplotlib.use('Agg')  # GUI描画のオーバーヘッド削減
import matplotlib.pyplot as plt
import numpy as np
from joblib import Parallel, delayed
from mpl_toolkits.axes_grid1 import make_axes_locatable

from utils.config import AnalysisConfig
from utils.grid import GridHandler
from utils.plotting import parse_style_argument

# スタイルシートの解析
mpl_style_sheet = parse_style_argument()

config = AnalysisConfig()
grid = GridHandler(config)

# Load smoothed center data
center_dir = config.get_center_path("ms_pres", data_type="data")
filename = config.center_configs.get("ms_pres_smoothed", "smoothed_center.npz")
filepath = os.path.join(center_dir, filename)

# Try to load combined file first, fallback to per-z-level files
if os.path.exists(filepath):
    print(f"Loading combined file: {filepath}")
    data = np.load(filepath)
    center = data['center']  # shape: (nt, nz, 2)
    nt, nz_data, _ = center.shape

    # Load metadata
    method = data.get('method', 'smoothed_minimum')
    r_smooth = data.get('r_smooth', None)
    refine_after_smooth = data.get('refine_after_smooth', False)
    r_refine = data.get('r_refine', None)
    z_first = data.get('z_first', 0)
    z_last = data.get('z_last', config.nz - 1)
    created_at = data.get('created_at', 'Unknown')
else:
    # Load from per-z-level files
    print(f"Combined file not found: {filepath}")
    print(f"Loading from individual z-level files...")

    # Find all smoothed_center_z*.npz files
    import glob
    z_files = sorted(glob.glob(os.path.join(center_dir, "smoothed_center_z*.npz")))

    if len(z_files) == 0:
        raise FileNotFoundError(
            f"No center files found in {center_dir}\n"
            f"Please run: python analysis/center/ms_pres/calc/smoothed.py"
        )

    print(f"Found {len(z_files)} z-level files")

    # Load first file to get dimensions
    first_data = np.load(z_files[0])
    nt = first_data['center'].shape[0]
    nz_data = len(z_files)

    # Allocate array
    center = np.zeros((nt, nz_data, 2))

    # Load each z-level file
    z_levels = []
    for z_idx, z_file in enumerate(z_files):
        z_data = np.load(z_file)
        center[:, z_idx, :] = z_data['center']
        z_levels.append(z_data['z_level'])

    # Get metadata from first file
    method = first_data.get('method', 'smoothed_minimum')
    r_smooth = first_data.get('r_smooth', None)
    refine_after_smooth = first_data.get('refine_after_smooth', False)
    r_refine = first_data.get('r_refine', None)
    z_first = min(z_levels)
    z_last = max(z_levels)
    created_at = first_data.get('created_at', 'Unknown')

    print(f"Loaded center data from z={z_first} to z={z_last}")

# Get vertical grid for the z-range used in calculation
vgrid = grid.vgrid[z_first:z_last+1]  # in meters
if len(vgrid) != nz_data:
    print(f"Warning: vgrid length ({len(vgrid)}) doesn't match data nz ({nz_data})")
    vgrid = vgrid[:nz_data]

# Convert to km
vgrid_km = vgrid * 1e-3

output_dir = os.path.join(config.get_center_path("ms_pres", data_type="fig"), "smoothed", "horizontal")
os.makedirs(output_dir, exist_ok=True)


def process_t(t):
    """Plot horizontal distribution for a single time step."""
    x_centers = center[t, :, 0] * 1e-3  # Convert to km
    y_centers = center[t, :, 1] * 1e-3  # Convert to km

    plt.style.use(mpl_style_sheet)
    fig, ax = plt.subplots(figsize=(6, 5))

    # Scatter plot colored by height
    scatter = ax.scatter(
        x_centers,
        y_centers,
        c=vgrid_km,
        cmap='viridis',
        s=50,
        edgecolors='black',
        linewidths=0.5,
        alpha=0.8
    )

    ax.set_aspect('equal', 'box')
    ax.set_xlim(0, config.x_width * 1e-3)
    ax.set_ylim(0, config.y_width * 1e-3)
    ax.set_xlabel("X [km]")
    ax.set_ylabel("Y [km]")
    ax.grid(True, alpha=0.3)

    # Add colorbar
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.1)
    cbar = plt.colorbar(scatter, cax=cax, label="Height [km]")

    # Title with time and method info
    time_hour = config.time_list[t] if t < len(config.time_list) else t * config.dt / 3600
    title = f"TC Center by Height (smoothed_minimum)\nt = {time_hour:.0f} hour"
    if r_smooth is not None:
        title += f"\nr_smooth={r_smooth*1e-3:.0f}km"
    if refine_after_smooth and r_refine is not None:
        title += f", r_refine={r_refine*1e-3:.0f}km"
    ax.set_title(title, fontsize=10)

    output_path = os.path.join(output_dir, f"horizontal_smoothed_t{str(t).zfill(3)}.png")
    fig.savefig(output_path, dpi=100)
    plt.close()


# Process all time steps in parallel
Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t) for t in range(config.t_first, config.t_last + 1)
)

print(f"Saved horizontal scatter plots: {output_dir}/horizontal_smoothed_t*.png")
print(f"Method: {method}")
if r_smooth is not None:
    print(f"r_smooth: {r_smooth:.0f} m ({r_smooth*1e-3:.1f} km)")
if refine_after_smooth:
    print(f"Refine after smooth: enabled")
    if r_refine is not None:
        print(f"r_refine: {r_refine:.0f} m ({r_refine*1e-3:.1f} km)")
print(f"Z-range: {z_first} to {z_last} (heights: {vgrid[0]:.0f} to {vgrid[-1]:.0f} m)")
print(f"Created: {created_at}")
