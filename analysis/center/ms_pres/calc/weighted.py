"""Calculate tropical cyclone center from 3D pressure minimum at each z-level.

Method: weighted_centroid with vertical continuity
- z=0: Search within r_search from ss_slp center, then refine
- z≥1: Use previous z-level center as initial guess, then refine
- Process z-levels sequentially from bottom to top for each time step

Usage:
    python $WORK/tc_analyze/analysis/center/ms_pres/calc/weighted.py
    python $WORK/tc_analyze/analysis/center/ms_pres/calc/weighted.py --z-first 0 --z-last 10
    python $WORK/tc_analyze/analysis/center/ms_pres/calc/weighted.py -zf 5 -zl 20 --r-search 300e3
    python $WORK/tc_analyze/analysis/center/ms_pres/calc/weighted.py --r-search 250e3 --r-refine 150e3
"""

import argparse
import datetime
import os

import numpy as np
from joblib import Parallel, delayed

from utils.center import create_coordinate_meshgrid, find_pressure_center
from utils.config import AnalysisConfig
from utils.grid import GridHandler

R_REFINE_DEFAULT = 100e3  # Default refinement radius for weighted centroid iteration
R_SEARCH_DEFAULT = 100e3  # Default initial search radius from ss_slp center


def parse_args():
    """Parse command-line arguments for z-level range and search radii."""
    parser = argparse.ArgumentParser(
        description="Calculate TC center from 3D pressure data using weighted_centroid method."
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
        help=f"Refinement radius for weighted centroid in meters (default: {R_REFINE_DEFAULT:.0f})",
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
    config = AnalysisConfig(config_file=args.config)
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
    print(f"Center finding method: weighted_centroid with vertical continuity")
    print(f"  z={z_first}: Initial search radius from ss_slp center: {r_search:.0f} m ({r_search * 1e-3:.1f} km)")
    print(f"  z>{z_first}: Use previous z-level center as initial guess")
    print(f"  All z-levels: Refinement radius: {r_refine:.0f} m ({r_refine * 1e-3:.1f} km)")

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

    # Output directory
    OUTPUT_DIR = config.get_center_path("ms_pres")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Process each time step (z-levels are processed sequentially within each time step)
    print(f"\nProcessing {n_time} time steps with {config.n_jobs} parallel jobs...")
    print(f"Each time step processes {n_z} z-levels sequentially from z={z_first} to z={z_last}")

    results = Parallel(n_jobs=config.n_jobs, verbose=10)(
        delayed(process_t_all_z)(
            t, z_first, z_last, data_memmap, X, Y, config, grid,
            ss_slp_center, r_search, r_refine
        )
        for t in range(config.t_first, config.t_last + 1)
    )

    # Collect results
    for t_idx, (center_tz, iterations_tz) in enumerate(results):
        center_all[t_idx, :, :] = center_tz
        iterations_all[t_idx, :] = iterations_tz

    # Save combined results as .npz file with metadata: shape (nt, nz, 2)
    filename = config.center_configs.get("ms_pres_weighted", "weighted_center.npz")
    combined_metadata = {
        "center": center_all,
        "method": "weighted_centroid_vertical_continuity",
        "created_at": datetime.datetime.utcnow().isoformat() + "Z",
        "actual_iterations": iterations_all,
        "z_first": z_first,
        "z_last": z_last,
        "r_refine": r_refine,
        "r_search": r_search,
        "max_iterations": 100,
        "convergence_threshold_x": config.dx * 1e-2,
        "convergence_threshold_y": config.dy * 1e-2,
    }
    np.savez(os.path.join(OUTPUT_DIR, filename), **combined_metadata)

    print(f"\nCompleted processing z-levels {z_first} to {z_last}")
    print(f"Saved file: {OUTPUT_DIR}/{filename} (shape: {center_all.shape})")
    print(f"  Method: weighted_centroid with vertical continuity")
    print(f"  z={z_first} uses r_search={r_search:.0f} m ({r_search * 1e-3:.1f} km) from ss_slp center")
    print(f"  z>{z_first} uses previous z-level center as initial guess")
    print(f"  r_refine={r_refine:.0f} m ({r_refine * 1e-3:.1f} km), max_iterations=100")
    print(f"  Mean iterations: {np.mean(iterations_all):.1f}, Max: {np.max(iterations_all)}")
    print(f"  All parameters are stored in the npz file metadata")


def process_t_all_z(t, z_first, z_last, data_memmap, X, Y, config, grid,
                     ss_slp_center, r_search, r_refine):
    """Process all z-levels for a single time step.

    Uses vertical continuity: z=z_first uses ss_slp center, z>z_first uses
    previous z-level center as initial guess.

    Args:
        t: Time step index
        z_first: First z-level to process
        z_last: Last z-level to process
        data_memmap: Memory-mapped 3D pressure data
        X: X-coordinate meshgrid
        Y: Y-coordinate meshgrid
        config: AnalysisConfig instance
        grid: GridHandler instance
        ss_slp_center: SS SLP center coordinates, shape (nt, 2)
        r_search: Initial search radius from ss_slp center (used only for z=z_first)
        r_refine: Refinement radius for weighted centroid method

    Returns:
        Tuple of (center_z, iterations_z):
            - center_z: numpy array of shape (n_z, 2) with [x, y] coordinates
            - iterations_z: numpy array of shape (n_z,) with iteration counts
    """
    n_z = z_last - z_first + 1
    center_z = np.zeros((n_z, 2))
    iterations_z = np.zeros(n_z, dtype=int)

    # Get ss_slp center for this time step
    ss_x, ss_y = ss_slp_center[t]

    # Process each z-level sequentially
    for z_idx, z in enumerate(range(z_first, z_last + 1)):
        data = data_memmap[t, z, :, :]

        if z == z_first:
            # First z-level: search within r_search from ss_slp center
            R = np.sqrt((X - ss_x) ** 2 + (Y - ss_y) ** 2)
            mask = R <= r_search

            # Find pressure minimum within the masked region
            min_idx = np.unravel_index(
                np.argmin(np.where(mask, data, np.inf)),
                data.shape
            )
            x_init = X[min_idx]
            y_init = Y[min_idx]
        else:
            # Use previous z-level center as initial guess
            x_init, y_init = center_z[z_idx - 1, :]

        # Refine center position using weighted centroid method
        x_c, y_c, num_iter = find_pressure_center(
            X, Y, data, config,
            r_refine=r_refine,
            x_init=x_init,
            y_init=y_init
        )

        center_z[z_idx, :] = [x_c, y_c]
        iterations_z[z_idx] = num_iter

    return center_z, iterations_z


def load_ss_slp_center(config):
    """Load ss_slp center coordinates.

    Args:
        config: AnalysisConfig instance

    Returns:
        numpy array of shape (nt, 2) with [x, y] coordinates
    """
    center_dir = config.get_center_path("ss_slp")

    # Try multiple possible filenames from center_configs
    possible_keys = ["ss_slp_weighted", "ss_slp", "ss_slp_smoothed"]
    for key in possible_keys:
        filename = config.center_configs.get(key)
        if filename:
            # Try .npz file
            file_path = os.path.join(center_dir, filename)
            if os.path.exists(file_path):
                if filename.endswith('.npz'):
                    data = np.load(file_path)
                    center = data["center"]  # shape: (nt, 2)
                    return center
                elif filename.endswith('.npy'):
                    center = np.load(file_path)  # shape: (nt, 2)
                    return center

    # Try default filenames
    npz_path = os.path.join(center_dir, "center.npz")
    if os.path.exists(npz_path):
        data = np.load(npz_path)
        center = data["center"]  # shape: (nt, 2)
        return center

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
        "Please run ss_slp center calculation (weighted.py or smoothed.py) first."
    )


if __name__ == "__main__":
    main()
