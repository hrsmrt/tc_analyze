"""Utility functions for finding tropical cyclone centers from pressure fields.

This module provides functions to locate low pressure centers using
weighted centroid method with iterative refinement, and to load center
coordinates from files.
"""

import os
import numpy as np


def find_pressure_center(
    X, Y, data_2d, config, r_refine=100e3, max_iterations=100, verbose=False,
    x_init=None, y_init=None
):
    """Find the center of low pressure using weighted centroid method.

    This function iteratively refines the center position by calculating
    a weighted centroid within a refinement radius. The weights are based on
    pressure deficit (data_max - data), giving higher weight to lower pressure.

    Args:
        X: 2D meshgrid of x-coordinates (m)
        Y: 2D meshgrid of y-coordinates (m)
        data_2d: 2D pressure field (Pa)
        config: AnalysisConfig instance
        r_refine: Refinement radius for weighted centroid iteration (m)
        max_iterations: Maximum number of refinement iterations
        verbose: If True, print iteration details
        x_init: Initial x-coordinate guess (m). If None, uses location of minimum pressure
        y_init: Initial y-coordinate guess (m). If None, uses location of minimum pressure

    Returns:
        Tuple of (x_center, y_center, num_iterations) in meters and count
    """
    # Initial guess: use provided x_init/y_init or location of minimum pressure
    if x_init is not None and y_init is not None:
        x_c = x_init
        y_c = y_init
    else:
        iy, ix = np.unravel_index(np.argmin(data_2d, axis=None), data_2d.shape)
        x_c = ix * config.dx + config.dx * 0.5
        y_c = iy * config.dy + config.dy * 0.5

    # Pre-calculate constants for optimization
    data_max = data_2d.max()
    threshold_x = config.dx * 1e-2
    threshold_y = config.dy * 1e-2

    # Iterative refinement
    num_iterations = max_iterations
    for i in range(max_iterations):
        x_c_n, y_c_n = _iteration_step(
            X, Y, data_2d, x_c, y_c, r_refine, data_max, config
        )

        # Check convergence
        if abs(x_c_n - x_c) < threshold_x and abs(y_c_n - y_c) < threshold_y:
            num_iterations = i + 1
            if verbose:
                print(f"  Converged in {num_iterations} iterations: x={x_c_n:.1f}, y={y_c_n:.1f}")
            break

        x_c = x_c_n
        y_c = y_c_n

    return x_c, y_c, num_iterations


def _iteration_step(X, Y, data, x_c, y_c, r_refine, data_max, config):
    """Perform one iteration of weighted centroid refinement.

    Args:
        X: X-coordinate meshgrid
        Y: Y-coordinate meshgrid
        data: 2D pressure field
        x_c: Current x-center estimate (m)
        y_c: Current y-center estimate (m)
        r_refine: Refinement radius for weighted centroid calculation (m)
        data_max: Maximum pressure value in the field
        config: AnalysisConfig instance

    Returns:
        Tuple of updated (x_center, y_center) in meters
    """
    # Calculate distances with periodic boundary condition in x
    dx = X - x_c
    dx = np.where(dx > config.x_width * 0.5, dx - config.x_width, dx)
    dx = np.where(dx < -config.x_width * 0.5, dx + config.x_width, dx)
    dy = Y - y_c

    # Distance squared for mask (avoid sqrt for performance)
    dist_sq = dx * dx + dy * dy
    mask = dist_sq <= r_refine * r_refine

    # Calculate weights (higher weight for lower pressure)
    # w = data_max - data within search radius, 0 outside
    w = np.where(mask, data_max - data, 0.0)
    w_sum = w.sum()

    # Handle edge cases (no valid points or numerical issues)
    if w_sum <= 0 or not np.isfinite(w_sum):
        return x_c, y_c

    # Calculate weighted centroid displacement
    inv_w_sum = 1.0 / w_sum

    # Update center with weighted displacement (with periodic boundary)
    x_c_new = x_c + (w * dx).sum() * inv_w_sum
    x_c_new = x_c_new % config.x_width  # Periodic boundary in x

    y_c_new = y_c + (w * dy).sum() * inv_w_sum
    y_c_new = y_c_new % config.y_width  # Periodic boundary in y

    return x_c_new, y_c_new


def create_coordinate_meshgrid(config):
    """Create 2D meshgrid for horizontal coordinates.

    Args:
        config: AnalysisConfig instance

    Returns:
        Tuple of (X, Y) meshgrids in meters
    """
    x = np.arange(config.dx * 0.5, config.x_width, config.dx)
    y = np.arange(config.dy * 0.5, config.y_width, config.dy)
    X, Y = np.meshgrid(x, y)
    return X, Y


def load_center_coordinates(config, center_type):
    """Load TC center coordinates from file.

    Loads center coordinates based on config.center_configs settings.
    The filename is determined by the center_configs dictionary in setting.json.

    Args:
        config: AnalysisConfig instance
        center_type: Type of center coordinates ("ss_slp" or "ms_pres")

    Returns:
        Tuple of (center_x, center_y, metadata):
            - center_x: numpy array
                - For ss_slp: shape (nt,)
                - For ms_pres: shape (nt, nz)
            - center_y: numpy array (same shape as center_x)
            - metadata: dict containing additional information from the npz file

    Raises:
        FileNotFoundError: If the center file is not found
        ValueError: If center_type is not supported

    Examples:
        >>> config = AnalysisConfig()
        >>> # Load ss_slp center (2D)
        >>> cx, cy, meta = load_center_coordinates(config, "ss_slp")
        >>> # cx.shape = (nt,), cy.shape = (nt,)
        >>>
        >>> # Load ms_pres center (3D)
        >>> cx, cy, meta = load_center_coordinates(config, "ms_pres")
        >>> # cx.shape = (nt, nz), cy.shape = (nt, nz)
    """
    if center_type not in config.center_configs:
        raise ValueError(
            f"Unsupported center_type: {center_type}. "
            f"Must be one of {list(config.center_configs.keys())}"
        )

    # Get filename from config
    filename = config.center_configs[center_type]

    # Construct full path
    center_dir = os.path.join(config.data_dir, f"center/{center_type}")
    center_path = os.path.join(center_dir, filename)

    # Check if file exists
    if not os.path.exists(center_path):
        raise FileNotFoundError(
            f"Center file not found: {center_path}\n"
            f"Please run the corresponding center calculation script first:\n"
            f"  - For ss_slp: python analysis/center/calc/ss_slp_center_calc.py\n"
            f"  - For ms_pres: python analysis/center/calc/ms_pres_center_calc.py"
        )

    # Load data
    data = np.load(center_path)

    # Extract center coordinates
    center = data["center"]  # shape: (nt, 2) or (nt, nz, 2)

    if center_type == "ss_slp":
        # 2D center: shape (nt, 2)
        center_x = center[:, 0]  # shape: (nt,)
        center_y = center[:, 1]  # shape: (nt,)
    elif center_type == "ms_pres":
        # 3D center: shape (nt, nz, 2)
        center_x = center[:, :, 0]  # shape: (nt, nz)
        center_y = center[:, :, 1]  # shape: (nt, nz)
    else:
        # This should not happen due to the check at the beginning
        raise ValueError(f"Unsupported center_type: {center_type}")

    # Extract metadata (all keys except 'center')
    metadata = {key: data[key] for key in data.files if key != "center"}

    return center_x, center_y, metadata
