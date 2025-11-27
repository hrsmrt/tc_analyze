"""Calculate tropical cyclone center from 3D pressure minimum at each z-level.

Usage:
    python $WORK/tc_analyze/analysis/center/calc/ms_pres_center_calc.py
    python $WORK/tc_analyze/analysis/center/calc/ms_pres_center_calc.py --z-first 0 --z-last 10
    python $WORK/tc_analyze/analysis/center/calc/ms_pres_center_calc.py -zf 5 -zl 20
"""

import argparse
import os

import numpy as np
from joblib import Parallel, delayed

from utils.center import create_coordinate_meshgrid, find_pressure_center
from utils.config import AnalysisConfig
from utils.grid import GridHandler

R_MAX_ITE = 100e3


def parse_args():
    """Parse command-line arguments for z-level range."""
    parser = argparse.ArgumentParser(
        description="Calculate TC center from 3D pressure data at each z-level"
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

    # Determine z-level range
    z_first = args.z_first if args.z_first is not None else 0
    z_last = args.z_last if args.z_last is not None else config.nz - 1

    # Validate z-level range
    if z_first < 0 or z_last >= config.nz or z_first > z_last:
        raise ValueError(
            f"Invalid z-level range: z_first={z_first}, z_last={z_last}. "
            f"Must satisfy: 0 <= z_first <= z_last < {config.nz}"
        )

    print(f"Processing z-levels {z_first} to {z_last} (inclusive)")
    print(f"Processing time steps {config.t_first} to {config.t_last} (inclusive)")

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

    # Process each z-level
    for z_idx, z in enumerate(range(z_first, z_last + 1)):
        print(f"\nProcessing z-level {z} (height: {grid.vgrid[z]:.1f} m)")

        # Parallel processing over time steps for this z-level
        results = Parallel(n_jobs=config.n_jobs)(
            delayed(process_t)(t, z, data_memmap, X, Y, config)
            for t in range(config.t_first, config.t_last + 1)
        )

        # Collect results for this z-level
        for t_idx, (x_c, y_c) in enumerate(results):
            center_all[t_idx, z_idx, 0] = x_c
            center_all[t_idx, z_idx, 1] = y_c

    # Save results as single .npy file: shape (nt, nz, 2)
    OUTPUT_DIR = config.get_data_path("center/ms_pres")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    np.save(os.path.join(OUTPUT_DIR, "center.npy"), center_all)

    print(f"\nCompleted processing z-levels {z_first} to {z_last}")
    print(f"Saved center coordinates: {OUTPUT_DIR}/center.npy (shape: {center_all.shape})")


def process_t(t, z, data_memmap, X, Y, config):
    """Process a single time step at a specific z-level.

    Args:
        t: Time step index
        z: Z-level index
        data_memmap: Memory-mapped 3D pressure data
        X: X-coordinate meshgrid
        Y: Y-coordinate meshgrid
        config: AnalysisConfig instance

    Returns:
        Tuple of (x_center, y_center) in meters
    """
    data = data_memmap[t, z, :, :]
    x_c, y_c = find_pressure_center(X, Y, data, config, r_max_ite=R_MAX_ITE)
    return x_c, y_c


if __name__ == "__main__":
    main()
