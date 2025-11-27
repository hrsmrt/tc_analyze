"""Calculate tropical cyclone center from sea level pressure minimum."""
# python $WORK/tc_analyze/analysis/center/calc/ss_slp_center_calc.py

import os
import numpy as np
from joblib import Parallel, delayed

from utils.center import create_coordinate_meshgrid, find_pressure_center
from utils.config import AnalysisConfig
from utils.grid import GridHandler

R_MAX_ITE = 100e3


config = AnalysisConfig()
grid = GridHandler(config)

# Create coordinate meshgrid
X, Y = create_coordinate_meshgrid(config)

data_memmap = np.memmap(
    f"{config.input_folder}ss_slp.grd",
    dtype=">f4",
    mode="r",
    shape=(config.nt, config.ny, config.nx),
)


def main():
    """Main function to find TC centers for all time steps."""
    # Parallel processing over all time steps
    results = Parallel(n_jobs=config.n_jobs)(
        delayed(process_t)(t) for t in range(config.nt)
    )

    # Collect results
    x_c_evo = []
    y_c_evo = []
    for t, (x, y) in zip(range(config.nt), results):
        x_c_evo.append(x)
        y_c_evo.append(y)

    # Save results as single .npy file: shape (nt, 2)
    OUTPUT_DIR = config.get_data_path("center/ss_slp")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    center = np.stack([x_c_evo, y_c_evo], axis=1)
    np.save(os.path.join(OUTPUT_DIR, "center.npy"), center)
    print(f"Saved center coordinates: {OUTPUT_DIR}/center.npy (shape: {center.shape})")


def process_t(t):
    """Process a single time step.

    Args:
        t: Time step index

    Returns:
        Tuple of (x_center, y_center) in meters
    """
    data = data_memmap[t]
    x_c, y_c = find_pressure_center(X, Y, data, config, r_max_ite=R_MAX_ITE)
    print(f"t={t}: x_c={x_c:.1f} m, y_c={y_c:.1f} m")
    return x_c, y_c


if __name__ == "__main__":
    main()
