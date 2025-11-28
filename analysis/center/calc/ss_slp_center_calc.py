"""Calculate tropical cyclone center from sea level pressure minimum.

Supports two methods:
1. weighted_centroid: Iterative weighted centroid refinement (default)
2. smoothed_minimum: Gaussian smoothing + minimum finding

Usage:
    python $WORK/tc_analyze/analysis/center/calc/ss_slp_center_calc.py
    python $WORK/tc_analyze/analysis/center/calc/ss_slp_center_calc.py --r-refine 150e3
    python $WORK/tc_analyze/analysis/center/calc/ss_slp_center_calc.py --method smoothed_minimum
    python $WORK/tc_analyze/analysis/center/calc/ss_slp_center_calc.py --method smoothed_minimum --r-smooth 500e3
"""

import argparse
import os
import numpy as np
from joblib import Parallel, delayed

from utils.center import (
    create_coordinate_meshgrid,
    find_pressure_center,
    find_pressure_center_smoothed
)
from utils.config import AnalysisConfig
from utils.grid import GridHandler

R_REFINE_DEFAULT = 100e3  # Default refinement radius for weighted centroid iteration
R_SMOOTH_DEFAULT = 500e3  # Default smoothing radius for smoothed_minimum method


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Calculate TC center from sea level pressure."
    )
    parser.add_argument(
        "--method",
        "-m",
        type=str,
        default=None,
        choices=["weighted_centroid", "smoothed_minimum"],
        help="Center finding method (default: from setting.json or weighted_centroid)",
    )
    parser.add_argument(
        "--r-refine",
        "-rr",
        type=float,
        default=R_REFINE_DEFAULT,
        help=f"Refinement radius for weighted centroid method in meters (default: {R_REFINE_DEFAULT:.0f})",
    )
    parser.add_argument(
        "--r-smooth",
        "-rs",
        type=float,
        default=R_SMOOTH_DEFAULT,
        help=f"Smoothing radius for smoothed_minimum method in meters (default: {R_SMOOTH_DEFAULT:.0f})",
    )
    parser.add_argument(
        "--refine-after-smooth",
        action="store_true",
        help="For smoothed_minimum: apply weighted centroid refinement after smoothing",
    )
    return parser.parse_args()


def main():
    """Main function to find TC centers for all time steps."""
    args = parse_args()

    config = AnalysisConfig()
    grid = GridHandler(config)

    # Determine method: command-line arg > setting.json > default
    method = args.method if args.method is not None else config.center_method
    r_refine = args.r_refine
    r_smooth = args.r_smooth
    refine_after_smooth = args.refine_after_smooth

    print(f"Processing time steps 0 to {config.nt - 1} (inclusive)")
    print(f"Center finding method: {method}")

    if method == "weighted_centroid":
        print(f"Refinement radius for weighted centroid: {r_refine:.0f} m ({r_refine * 1e-3:.1f} km)")
    elif method == "smoothed_minimum":
        print(f"Smoothing radius: {r_smooth:.0f} m ({r_smooth * 1e-3:.1f} km)")
        if refine_after_smooth:
            print(f"Refinement after smoothing: enabled (r_refine={r_refine * 1e-3:.1f} km)")

    # Create coordinate meshgrid
    X, Y = create_coordinate_meshgrid(config)

    data_memmap = np.memmap(
        f"{config.input_folder}ss_slp.grd",
        dtype=">f4",
        mode="r",
        shape=(config.nt, config.ny, config.nx),
    )

    # Parallel processing over all time steps
    results = Parallel(n_jobs=config.n_jobs)(
        delayed(process_t)(
            t, data_memmap, X, Y, config, method, r_refine, r_smooth, refine_after_smooth
        ) for t in range(config.nt)
    )

    # Collect results
    x_c_evo = []
    y_c_evo = []
    iterations = []
    for t, (x, y, num_iter) in zip(range(config.nt), results):
        x_c_evo.append(x)
        y_c_evo.append(y)
        iterations.append(num_iter)

    # Save results as .npz file with metadata: shape (nt, 2)
    OUTPUT_DIR = config.get_center_path("ss_slp")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    center = np.stack([x_c_evo, y_c_evo], axis=1)

    # Get filename from config (default: "center.npz")
    filename = config.center_configs.get("ss_slp", "center.npz")

    # Prepare metadata
    metadata = {
        "center": center,
        "method": method,
        "actual_iterations": np.array(iterations),
    }

    if method == "weighted_centroid":
        metadata.update({
            "r_refine": r_refine,
            "max_iterations": 100,
            "convergence_threshold_x": config.dx * 1e-2,
            "convergence_threshold_y": config.dy * 1e-2,
        })
    elif method == "smoothed_minimum":
        metadata.update({
            "r_smooth": r_smooth,
            "refine_after_smooth": refine_after_smooth,
        })
        if refine_after_smooth:
            metadata.update({
                "r_refine": r_refine,
                "max_iterations": 100,
                "convergence_threshold_x": config.dx * 1e-2,
                "convergence_threshold_y": config.dy * 1e-2,
            })

    np.savez(os.path.join(OUTPUT_DIR, filename), **metadata)

    print(f"\nSaved center coordinates: {OUTPUT_DIR}/{filename} (shape: {center.shape})")
    print(f"  Method: {method}")
    if method == "weighted_centroid":
        print(f"  r_refine={r_refine:.0f} m ({r_refine * 1e-3:.1f} km), max_iterations=100")
        print(f"  Mean iterations: {np.mean(iterations):.1f}, Max: {np.max(iterations)}")
    elif method == "smoothed_minimum":
        print(f"  r_smooth={r_smooth:.0f} m ({r_smooth * 1e-3:.1f} km)")
        if refine_after_smooth:
            print(f"  Refinement after smoothing: enabled (r_refine={r_refine * 1e-3:.1f} km)")
            print(f"  Mean refinement iterations: {np.mean(iterations):.1f}, Max: {np.max(iterations)}")
    print(f"  All parameters are stored in the npz file metadata")


def process_t(t, data_memmap, X, Y, config, method, r_refine, r_smooth, refine_after_smooth):
    """Process a single time step.

    Args:
        t: Time step index
        data_memmap: Memory-mapped pressure data
        X: X-coordinate meshgrid
        Y: Y-coordinate meshgrid
        config: AnalysisConfig instance
        method: Center finding method ("weighted_centroid" or "smoothed_minimum")
        r_refine: Refinement radius for weighted centroid method in meters
        r_smooth: Smoothing radius for smoothed_minimum method in meters
        refine_after_smooth: Whether to refine after smoothing

    Returns:
        Tuple of (x_center, y_center, num_iterations) in meters and count
    """
    data = data_memmap[t]

    if method == "weighted_centroid":
        x_c, y_c, num_iter = find_pressure_center(X, Y, data, config, r_refine=r_refine)
    elif method == "smoothed_minimum":
        x_c, y_c, num_iter = find_pressure_center_smoothed(
            X, Y, data, config,
            r_smooth=r_smooth,
            refine=refine_after_smooth,
            r_refine=r_refine
        )
    else:
        raise ValueError(f"Unknown method: {method}")

    print(f"t={t}: x_c={x_c:.1f} m, y_c={y_c:.1f} m, iterations={num_iter}")
    return x_c, y_c, num_iter


if __name__ == "__main__":
    main()
