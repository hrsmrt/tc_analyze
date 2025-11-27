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
    iterations = []
    for t, (x, y, num_iter) in zip(range(config.nt), results):
        x_c_evo.append(x)
        y_c_evo.append(y)
        iterations.append(num_iter)

    # Save results as .npz file with metadata: shape (nt, 2)
    OUTPUT_DIR = config.get_data_path("center/ss_slp")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    center = np.stack([x_c_evo, y_c_evo], axis=1)

    np.savez(
        os.path.join(OUTPUT_DIR, "center.npz"),
        center=center,
        r_max_ite=R_MAX_ITE,
        max_iterations=100,
        convergence_threshold_x=config.dx * 1e-2,
        convergence_threshold_y=config.dy * 1e-2,
        actual_iterations=np.array(iterations),
    )
    print(f"Saved center coordinates: {OUTPUT_DIR}/center.npz (shape: {center.shape})")
    print(f"  r_max_ite={R_MAX_ITE:.0f} m, max_iterations=100")
    print(f"  Mean iterations: {np.mean(iterations):.1f}, Max: {np.max(iterations)}")


def process_t(t):
    """Process a single time step.

    Args:
        t: Time step index

    Returns:
        Tuple of (x_center, y_center, num_iterations) in meters and count
    """
    data = data_memmap[t]
    x_c, y_c, num_iter = find_pressure_center(X, Y, data, config, r_max_ite=R_MAX_ITE)
    print(f"t={t}: x_c={x_c:.1f} m, y_c={y_c:.1f} m, iterations={num_iter}")
    return x_c, y_c, num_iter


if __name__ == "__main__":
    main()
