"""Calculate tropical cyclone center from sea level pressure minimum.

Usage:
    python $WORK/tc_analyze/analysis/center/calc/ss_slp_center_calc.py
    python $WORK/tc_analyze/analysis/center/calc/ss_slp_center_calc.py --r-refine 150e3
"""

import argparse
import os
import numpy as np
from joblib import Parallel, delayed

from utils.center import create_coordinate_meshgrid, find_pressure_center
from utils.config import AnalysisConfig
from utils.grid import GridHandler

R_REFINE_DEFAULT = 100e3  # Default refinement radius for weighted centroid iteration


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Calculate TC center from sea level pressure using weighted centroid method."
    )
    parser.add_argument(
        "--r-refine",
        "-rr",
        type=float,
        default=R_REFINE_DEFAULT,
        help=f"Refinement radius for weighted centroid iteration in meters (default: {R_REFINE_DEFAULT:.0f})",
    )
    return parser.parse_args()


def main():
    """Main function to find TC centers for all time steps."""
    args = parse_args()
    r_refine = args.r_refine

    config = AnalysisConfig()
    grid = GridHandler(config)

    print(f"Processing time steps 0 to {config.nt - 1} (inclusive)")
    print(f"Refinement radius for weighted centroid: {r_refine:.0f} m ({r_refine * 1e-3:.1f} km)")

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
        delayed(process_t)(t, data_memmap, X, Y, config, r_refine) for t in range(config.nt)
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
    OUTPUT_DIR = config.get_data_path("center/ss_slp")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    center = np.stack([x_c_evo, y_c_evo], axis=1)

    # Generate filename based on parameters
    filename = f"center_rrefine{r_refine * 1e-3:.0f}km.npz"

    np.savez(
        os.path.join(OUTPUT_DIR, filename),
        center=center,
        r_refine=r_refine,
        max_iterations=100,
        convergence_threshold_x=config.dx * 1e-2,
        convergence_threshold_y=config.dy * 1e-2,
        actual_iterations=np.array(iterations),
    )
    print(f"\nSaved center coordinates: {OUTPUT_DIR}/{filename} (shape: {center.shape})")
    print(f"  r_refine={r_refine:.0f} m ({r_refine * 1e-3:.1f} km), max_iterations=100")
    print(f"  Mean iterations: {np.mean(iterations):.1f}, Max: {np.max(iterations)}")


def process_t(t, data_memmap, X, Y, config, r_refine):
    """Process a single time step.

    Args:
        t: Time step index
        data_memmap: Memory-mapped pressure data
        X: X-coordinate meshgrid
        Y: Y-coordinate meshgrid
        config: AnalysisConfig instance
        r_refine: Refinement radius for weighted centroid iteration in meters

    Returns:
        Tuple of (x_center, y_center, num_iterations) in meters and count
    """
    data = data_memmap[t]
    x_c, y_c, num_iter = find_pressure_center(X, Y, data, config, r_refine=r_refine)
    print(f"t={t}: x_c={x_c:.1f} m, y_c={y_c:.1f} m, iterations={num_iter}")
    return x_c, y_c, num_iter


if __name__ == "__main__":
    main()
