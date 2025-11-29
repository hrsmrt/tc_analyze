"""Calculate tropical cyclone center from 3D pressure minimum at each z-level.

Method: smoothed_minimum with vertical continuity
- z=0: Smooth local region around ss_slp center, find minimum
- z≥1: Smooth local region around previous z-level center, find minimum
- Optionally refine with weighted centroid
- Process z-levels sequentially from bottom to top for each time step

Usage:
    python $WORK/tc_analyze/analysis/center/ms_pres/calc/smoothed.py
    python $WORK/tc_analyze/analysis/center/ms_pres/calc/smoothed.py --z-first 0 --z-last 10
    python $WORK/tc_analyze/analysis/center/ms_pres/calc/smoothed.py --r-smooth 500e3
    python $WORK/tc_analyze/analysis/center/ms_pres/calc/smoothed.py --r-smooth 600e3 --refine
    python $WORK/tc_analyze/analysis/center/ms_pres/calc/smoothed.py --r-smooth 500e3 --refine --r-refine 150e3
"""

import argparse
import datetime
import os

import numpy as np
from joblib import Parallel, delayed
from scipy.ndimage import gaussian_filter

from utils.center import create_coordinate_meshgrid, find_pressure_center
from utils.config import AnalysisConfig
from utils.grid import GridHandler

R_REFINE_DEFAULT = 100e3  # Default refinement radius (if --refine is enabled)
R_SMOOTH_DEFAULT = 500e3  # Default smoothing radius for smoothed_minimum method
R_SEARCH_DEFAULT = 100e3  # Default local search region radius (for z=0, around ss_slp center)


def parse_args():
    """Parse command-line arguments for z-level range and smoothing parameters."""
    parser = argparse.ArgumentParser(
        description="Calculate TC center from 3D pressure data using smoothed_minimum method with vertical continuity."
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
        help=f"Local search region radius in meters (default: {R_SEARCH_DEFAULT:.0f})",
    )
    parser.add_argument(
        "--r-smooth",
        "-rsm",
        type=float,
        default=R_SMOOTH_DEFAULT,
        help=f"Smoothing radius in meters (default: {R_SMOOTH_DEFAULT:.0f})",
    )
    parser.add_argument(
        "--refine",
        action="store_true",
        help="Apply weighted centroid refinement after smoothing",
    )
    parser.add_argument(
        "--r-refine",
        "-rr",
        type=float,
        default=R_REFINE_DEFAULT,
        help=f"Refinement radius for weighted centroid (used if --refine is enabled, default: {R_REFINE_DEFAULT:.0f})",
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

    # Determine z-level range and smoothing parameters
    z_first = args.z_first if args.z_first is not None else 0
    z_last = args.z_last if args.z_last is not None else config.nz - 1
    r_search = args.r_search
    r_smooth = args.r_smooth
    refine = args.refine
    r_refine = args.r_refine

    # Validate z-level range
    if z_first < 0 or z_last >= config.nz or z_first > z_last:
        raise ValueError(
            f"Invalid z-level range: z_first={z_first}, z_last={z_last}. "
            f"Must satisfy: 0 <= z_first <= z_last < {config.nz}"
        )

    print(f"Processing z-levels {z_first} to {z_last} (inclusive)")
    print(f"Processing time steps {config.t_first} to {config.t_last} (inclusive)")
    print(f"Center finding method: smoothed_minimum with vertical continuity")
    print(f"  z={z_first}: Search region radius from ss_slp center: {r_search:.0f} m ({r_search * 1e-3:.1f} km)")
    print(f"  z>{z_first}: Use previous z-level center as initial guess")
    print(f"  All z-levels: Smoothing radius: {r_smooth:.0f} m ({r_smooth * 1e-3:.1f} km)")
    if refine:
        print(f"  Refinement after smoothing: enabled (r_refine={r_refine * 1e-3:.1f} km)")
    else:
        print(f"  Refinement after smoothing: disabled")

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
            ss_slp_center, r_search, r_smooth, refine, r_refine
        )
        for t in range(config.t_first, config.t_last + 1)
    )

    # Collect results
    for t_idx, (center_tz, iterations_tz) in enumerate(results):
        center_all[t_idx, :, :] = center_tz
        iterations_all[t_idx, :] = iterations_tz

    # Save combined results as .npz file with metadata: shape (nt, nz, 2)
    filename = config.center_configs.get("ms_pres_smoothed", "smoothed_center.npz")
    combined_metadata = {
        "center": center_all,
        "method": "smoothed_minimum_vertical_continuity",
        "created_at": datetime.datetime.utcnow().isoformat() + "Z",
        "actual_iterations": iterations_all,
        "z_first": z_first,
        "z_last": z_last,
        "r_search": r_search,
        "r_smooth": r_smooth,
        "refine_after_smooth": refine,
    }
    if refine:
        combined_metadata.update({
            "r_refine": r_refine,
            "max_iterations": 100,
            "convergence_threshold_x": config.dx * 1e-2,
            "convergence_threshold_y": config.dy * 1e-2,
        })
    np.savez(os.path.join(OUTPUT_DIR, filename), **combined_metadata)

    print(f"\nCompleted processing z-levels {z_first} to {z_last}")
    print(f"Saved file: {OUTPUT_DIR}/{filename} (shape: {center_all.shape})")
    print(f"  Method: smoothed_minimum with vertical continuity")
    print(f"  z={z_first} uses r_search={r_search:.0f} m ({r_search * 1e-3:.1f} km) from ss_slp center")
    print(f"  z>{z_first} uses previous z-level center as initial guess")
    print(f"  r_smooth={r_smooth:.0f} m ({r_smooth * 1e-3:.1f} km)")
    if refine:
        print(f"  Refinement after smoothing: enabled (r_refine={r_refine * 1e-3:.1f} km)")
        print(f"  Mean refinement iterations: {np.mean(iterations_all):.1f}, Max: {np.max(iterations_all)}")
    print(f"  All parameters are stored in the npz file metadata")


def process_t_all_z(t, z_first, z_last, data_memmap, X, Y, config, grid,
                     ss_slp_center, r_search, r_smooth, refine, r_refine):
    """Process all z-levels for a single time step.

    Uses vertical continuity: z=z_first uses ss_slp center, z>z_first uses
    previous z-level center as initial guess. Applies Gaussian smoothing to
    local region around the initial guess, then finds minimum.

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
        r_search: Local search region radius (used only for z=z_first)
        r_smooth: Smoothing radius for Gaussian filter
        refine: Whether to refine after smoothing
        r_refine: Refinement radius (used if refine=True)

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

    # Calculate sigma for Gaussian filter (in grid cells)
    sigma_x = r_smooth / (3.0 * config.dx)
    sigma_y = r_smooth / (3.0 * config.dy)

    # Process each z-level sequentially
    for z_idx, z in enumerate(range(z_first, z_last + 1)):
        data = data_memmap[t, z, :, :]

        if z == z_first:
            # First z-level: search within r_search from ss_slp center
            search_center_x, search_center_y = ss_x, ss_y
        else:
            # Use previous z-level center as search center
            search_center_x, search_center_y = center_z[z_idx - 1, :]

        # Calculate distance from search center
        R = np.sqrt((X - search_center_x) ** 2 + (Y - search_center_y) ** 2)

        # Create mask for local search region
        mask = R <= r_search

        # Apply Gaussian smoothing to the entire field
        # (scipy.ndimage.gaussian_filter requires full array)
        data_smoothed = gaussian_filter(data, sigma=(sigma_y, sigma_x), mode='wrap')

        # Find minimum within the local search region
        min_idx = np.unravel_index(
            np.argmin(np.where(mask, data_smoothed, np.inf)),
            data.shape
        )
        x_c = X[min_idx]
        y_c = Y[min_idx]

        # Optional refinement using weighted centroid method
        num_iter = 0
        if refine:
            x_c, y_c, num_iter = find_pressure_center(
                X, Y, data, config,
                r_refine=r_refine,
                x_init=x_c,
                y_init=y_c
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
