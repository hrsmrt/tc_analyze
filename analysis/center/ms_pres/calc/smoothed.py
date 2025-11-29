"""Calculate tropical cyclone center from 3D pressure minimum at each z-level.

Method: smoothed_minimum
- Apply Gaussian smoothing to pressure field
- Find minimum in smoothed field
- Optionally refine with weighted centroid

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

from utils.center import create_coordinate_meshgrid, find_pressure_center_smoothed
from utils.config import AnalysisConfig
from utils.grid import GridHandler

R_REFINE_DEFAULT = 100e3  # Default refinement radius (if --refine is enabled)
R_SMOOTH_DEFAULT = 500e3  # Default smoothing radius for smoothed_minimum method


def parse_args():
    """Parse command-line arguments for z-level range and smoothing parameters."""
    parser = argparse.ArgumentParser(
        description="Calculate TC center from 3D pressure data using smoothed_minimum method."
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
    print(f"Center finding method: smoothed_minimum")
    print(f"Smoothing radius: {r_smooth:.0f} m ({r_smooth * 1e-3:.1f} km)")
    if refine:
        print(f"Refinement after smoothing: enabled (r_refine={r_refine * 1e-3:.1f} km)")
    else:
        print(f"Refinement after smoothing: disabled")

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
        print(f"\nProcessing z-level {z}/{z_last} (height: {grid.vgrid[z]:.1f} m) - {n_time} time steps with {config.n_jobs} parallel jobs")

        # Parallel processing over time steps for this z-level
        results = Parallel(n_jobs=config.n_jobs, verbose=10)(
            delayed(process_t)(
                t, z, data_memmap, X, Y, config,
                r_smooth, refine, r_refine
            )
            for t in range(config.t_first, config.t_last + 1)
        )

        # Collect results for this z-level
        for t_idx, (x_c, y_c, num_iter) in enumerate(results):
            center_all[t_idx, z_idx, 0] = x_c
            center_all[t_idx, z_idx, 1] = y_c
            iterations_all[t_idx, z_idx] = num_iter

    # Save results as .npz file with metadata: shape (nt, nz, 2)
    OUTPUT_DIR = config.get_center_path("ms_pres")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Get filename from config, default: "smoothed_center.npz"
    filename = config.center_configs.get("ms_pres_smoothed", "smoothed_center.npz")

    # Prepare metadata
    metadata = {
        "center": center_all,
        "method": "smoothed_minimum",
        "created_at": datetime.datetime.utcnow().isoformat() + "Z",
        "actual_iterations": iterations_all,
        "z_first": z_first,
        "z_last": z_last,
        "r_smooth": r_smooth,
        "refine_after_smooth": refine,
    }

    if refine:
        metadata.update({
            "r_refine": r_refine,
            "max_iterations": 100,
            "convergence_threshold_x": config.dx * 1e-2,
            "convergence_threshold_y": config.dy * 1e-2,
        })

    np.savez(os.path.join(OUTPUT_DIR, filename), **metadata)

    print(f"\nCompleted processing z-levels {z_first} to {z_last}")
    print(f"Saved center coordinates: {OUTPUT_DIR}/{filename} (shape: {center_all.shape})")
    print(f"  Method: smoothed_minimum")
    print(f"  r_smooth={r_smooth:.0f} m ({r_smooth * 1e-3:.1f} km)")
    if refine:
        print(f"  Refinement after smoothing: enabled (r_refine={r_refine * 1e-3:.1f} km)")
        print(f"  Mean refinement iterations: {np.mean(iterations_all):.1f}, Max: {np.max(iterations_all)}")
    print(f"  All parameters are stored in the npz file metadata")


def process_t(t, z, data_memmap, X, Y, config, r_smooth, refine, r_refine):
    """Process a single time step at a specific z-level.

    Args:
        t: Time step index
        z: Z-level index
        data_memmap: Memory-mapped 3D pressure data
        X: X-coordinate meshgrid
        Y: Y-coordinate meshgrid
        config: AnalysisConfig instance
        r_smooth: Smoothing radius
        refine: Whether to refine after smoothing
        r_refine: Refinement radius (used if refine=True)

    Returns:
        Tuple of (x_center, y_center, num_iterations) in meters and count
    """
    data = data_memmap[t, z, :, :]

    # Use smoothed minimum method
    x_c, y_c, num_iter = find_pressure_center_smoothed(
        X, Y, data, config,
        r_smooth=r_smooth,
        refine=refine,
        r_refine=r_refine
    )

    return x_c, y_c, num_iter


if __name__ == "__main__":
    main()
