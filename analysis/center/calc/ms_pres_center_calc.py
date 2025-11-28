"""Calculate tropical cyclone center from 3D pressure minimum at each z-level.

Search for pressure minimum within r_search from ss_slp center, then refine
the position using weighted centroid method within r_refine.

Usage:
    python $WORK/tc_analyze/analysis/center/calc/ms_pres_center_calc.py
    python $WORK/tc_analyze/analysis/center/calc/ms_pres_center_calc.py --z-first 0 --z-last 10
    python $WORK/tc_analyze/analysis/center/calc/ms_pres_center_calc.py -zf 5 -zl 20 --r-search 300e3
    python $WORK/tc_analyze/analysis/center/calc/ms_pres_center_calc.py --r-search 250e3 --r-refine 150e3
"""

import argparse
import os

import numpy as np
from joblib import Parallel, delayed

from utils.center import create_coordinate_meshgrid, find_pressure_center
from utils.config import AnalysisConfig
from utils.grid import GridHandler

R_REFINE_DEFAULT = 100e3  # Default refinement radius for weighted centroid iteration
R_SEARCH_DEFAULT = 200e3  # Default initial search radius from ss_slp center


def parse_args():
    """Parse command-line arguments for z-level range and search radii."""
    parser = argparse.ArgumentParser(
        description="Calculate TC center from 3D pressure data at each z-level. "
        "First finds pressure minimum within r_search from ss_slp center, "
        "then refines position using weighted centroid within r_refine."
    )
    parser.add_argument(
        "--z-first",
        "-zf",
        type=int,
        default=None,
        help="First z-level to process (default: 0)",
    )
    parser.add_argument(
        "--z-last",
        "-zl",
        type=int,
        default=None,
        help="Last z-level to process (default: nz-1)",
    )
    parser.add_argument(
        "--r-search",
        "-rs",
        type=float,
        default=R_SEARCH_DEFAULT,
        help=f"Initial search radius from ss_slp center in meters (default: {R_SEARCH_DEFAULT:.0f})",
    )
    parser.add_argument(
        "--r-refine",
        "-rr",
        type=float,
        default=R_REFINE_DEFAULT,
        help=f"Refinement radius for weighted centroid iteration in meters (default: {R_REFINE_DEFAULT:.0f})",
    )
    parser.add_argument(
        "--config",
        "-c",
        type=str,
        default=None,
        help="Configuration file path",
    )
    return parser.parse_args()


def main():
    """Main function to process all z-levels and time steps."""
    args = parse_args()
    config = AnalysisConfig()
    grid = GridHandler(config)

    # Determine z-level range and search radii
    z_first = args.z_first if args.z_first is not None else 0
    z_last = args.z_last if args.z_last is not None else config.nz - 1
    r_search = args.r_search
    r_refine = args.r_refine

    # Validate z-level range
    if z_first < 0 or z_last >= config.nz or z_first > z_last:
        raise ValueError(
            f"Invalid z-level range: z_first={z_first}, z_last={z_last}. "
            f"Must satisfy: 0 <= z_first <= z_last < {config.nz}"
        )

    print(f"Processing z-levels {z_first} to {z_last} (inclusive)")
    print(f"Processing time steps {config.t_first} to {config.t_last} (inclusive)")
    print(f"Initial search radius from ss_slp center: {r_search:.0f} m ({r_search * 1e-3:.1f} km)")
    print(f"Refinement radius for weighted centroid: {r_refine:.0f} m ({r_refine * 1e-3:.1f} km)")

    # Load ss_slp center coordinates (2D center, shape: nt, 2)
    ss_slp_center = load_ss_slp_center(config)
    print(f"Loaded ss_slp center: shape {ss_slp_center.shape}")

    # Create coordinate meshgrid
    X, Y = create_coordinate_meshgrid(config)

    # Load 3D pressure data
    data_memmap = np.memmap(
        f"{config.input_folder}ms_pres.grd",
        dtype=">f4",
        mode="r",
        shape=(config.nt, config.nz, config.ny, config.nx),
    )

    # Prepare array to store all results: shape (nt, nz, 2)
    n_time = config.t_last - config.t_first + 1
    n_z = z_last - z_first + 1
    center_all = np.zeros((n_time, n_z, 2))
    iterations_all = np.zeros((n_time, n_z), dtype=int)

    # Process each z-level
    for z_idx, z in enumerate(range(z_first, z_last + 1)):
        print(f"\nProcessing z-level {z} (height: {grid.vgrid[z]:.1f} m)")

        # Parallel processing over time steps for this z-level
        results = Parallel(n_jobs=config.n_jobs)(
            delayed(process_t)(t, z, data_memmap, X, Y, config, ss_slp_center, r_search, r_refine)
            for t in range(config.t_first, config.t_last + 1)
        )

        # Collect results for this z-level
        for t_idx, (x_c, y_c, num_iter) in enumerate(results):
            center_all[t_idx, z_idx, 0] = x_c
            center_all[t_idx, z_idx, 1] = y_c
            iterations_all[t_idx, z_idx] = num_iter

    # Save results as .npz file with metadata: shape (nt, nz, 2)
    OUTPUT_DIR = config.get_data_path("center/ms_pres")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Generate filename based on parameters
    filename = f"center_rsearch{r_search * 1e-3:.0f}km_rrefine{r_refine * 1e-3:.0f}km.npz"

    np.savez(
        os.path.join(OUTPUT_DIR, filename),
        center=center_all,
        r_refine=r_refine,
        r_search=r_search,
        max_iterations=100,
        convergence_threshold_x=config.dx * 1e-2,
        convergence_threshold_y=config.dy * 1e-2,
        actual_iterations=iterations_all,
        z_first=z_first,
        z_last=z_last,
    )

    print(f"\nCompleted processing z-levels {z_first} to {z_last}")
    print(f"Saved center coordinates: {OUTPUT_DIR}/{filename} (shape: {center_all.shape})")
    print(f"  r_search={r_search:.0f} m ({r_search * 1e-3:.1f} km)")
    print(f"  r_refine={r_refine:.0f} m ({r_refine * 1e-3:.1f} km), max_iterations=100")
    print(f"  Mean iterations: {np.mean(iterations_all):.1f}, Max: {np.max(iterations_all)}")


def process_t(t, z, data_memmap, X, Y, config, ss_slp_center, r_search, r_refine):
    """Process a single time step at a specific z-level.

    Search for pressure minimum within r_search from ss_slp center, then refine
    the position using weighted centroid method within r_refine.

    Args:
        t: Time step index
        z: Z-level index
        data_memmap: Memory-mapped 3D pressure data
        X: X-coordinate meshgrid
        Y: Y-coordinate meshgrid
        config: AnalysisConfig instance
        ss_slp_center: SS SLP center coordinates, shape (nt, 2)
        r_search: Initial search radius from ss_slp center in meters
        r_refine: Refinement radius for weighted centroid iteration in meters

    Returns:
        Tuple of (x_center, y_center, num_iterations) in meters and count
    """
    data = data_memmap[t, z, :, :]

    # Get ss_slp center for this time step
    ss_x, ss_y = ss_slp_center[t]

    # Calculate distance from ss_slp center
    R = np.sqrt((X - ss_x) ** 2 + (Y - ss_y) ** 2)

    # Create mask for search region (within r_search from ss_slp center)
    mask = R <= r_search

    # Find pressure minimum within the masked region
    masked_data = data.copy()
    masked_data[~mask] = np.inf  # Set values outside mask to infinity

    # Find initial position (pressure minimum in masked region)
    min_idx = np.unravel_index(np.argmin(masked_data), data.shape)
    x_init = X[min_idx]
    y_init = Y[min_idx]

    # Refine center position using weighted centroid method
    x_c, y_c, num_iter = find_pressure_center(
        X, Y, data, config,
        r_refine=r_refine,
        x_init=x_init,
        y_init=y_init
    )

    return x_c, y_c, num_iter


def load_ss_slp_center(config):
    """Load ss_slp center coordinates.

    Args:
        config: AnalysisConfig instance

    Returns:
        numpy array of shape (nt, 2) with [x, y] coordinates
    """
    center_dir = os.path.join(config.data_dir, "center/ss_slp")

    # Try to load .npz file first
    npz_path = os.path.join(center_dir, "center.npz")
    if os.path.exists(npz_path):
        data = np.load(npz_path)
        center = data["center"]  # shape: (nt, 2)
        return center

    # Try .npy file
    npy_path = os.path.join(center_dir, "center.npy")
    if os.path.exists(npy_path):
        center = np.load(npy_path)  # shape: (nt, 2)
        return center

    # Fall back to legacy .txt files
    x_path = os.path.join(center_dir, "x.txt")
    y_path = os.path.join(center_dir, "y.txt")
    if os.path.exists(x_path) and os.path.exists(y_path):
        x = np.loadtxt(x_path)
        y = np.loadtxt(y_path)
        return np.column_stack([x, y])

    raise FileNotFoundError(
        f"SS SLP center data not found in {center_dir}. "
        "Please run ss_slp_center_calc.py first."
    )


if __name__ == "__main__":
    main()
