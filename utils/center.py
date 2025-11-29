"""Utility functions for finding tropical cyclone centers from pressure fields.

This module provides functions to locate low pressure centers using:
1. Weighted centroid method with iterative refinement
2. Smoothed minimum method using Gaussian filtering

It also provides functions to load center coordinates from files.
"""

import os
import numpy as np
from scipy.ndimage import gaussian_filter


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
    # OPTIMIZATION: Work only within a bounding box around the current center
    # to avoid full-grid operations

    # Calculate bounding box (with margin for periodic boundary in x)
    # Use 1.5× r_refine as safety margin
    margin = r_refine * 1.5

    # Y-direction (no periodic boundary)
    y_min = max(0, y_c - margin)
    y_max = min(config.y_width, y_c + margin)
    iy_min = int(y_min / config.dy)
    iy_max = min(config.ny, int(np.ceil(y_max / config.dy)))

    # X-direction (handle periodic boundary)
    x_min = x_c - margin
    x_max = x_c + margin

    # Check if we need to handle periodic boundary
    need_periodic = (x_min < 0) or (x_max > config.x_width)

    if not need_periodic:
        # Simple case: no periodic boundary crossing
        ix_min = int(x_min / config.dx)
        ix_max = min(config.nx, int(np.ceil(x_max / config.dx)))

        # Extract local region
        X_local = X[iy_min:iy_max, ix_min:ix_max]
        Y_local = Y[iy_min:iy_max, ix_min:ix_max]
        data_local = data[iy_min:iy_max, ix_min:ix_max]

        # Calculate distances (no periodic boundary needed in this region)
        dx = X_local - x_c
        dy = Y_local - y_c

    else:
        # Complex case: use full grid but with periodic distance calculation
        # This is rare, so use original full-grid method
        dx = X - x_c
        dx = np.where(dx > config.x_width * 0.5, dx - config.x_width, dx)
        dx = np.where(dx < -config.x_width * 0.5, dx + config.x_width, dx)
        dy = Y - y_c
        data_local = data

    # Distance squared for mask (avoid sqrt for performance)
    dist_sq = dx * dx + dy * dy
    mask = dist_sq <= r_refine * r_refine

    # Calculate weights (higher weight for lower pressure)
    # w = data_max - data within search radius, 0 outside
    w = np.where(mask, data_max - data_local, 0.0)
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


def find_pressure_center_smoothed(
    X, Y, data_2d, config, r_smooth=500e3, refine=False, r_refine=100e3,
    max_iterations=100, verbose=False
):
    """Find the center of low pressure using smoothed minimum method.

    This function smooths the pressure field using a Gaussian filter with
    radius r_smooth, then finds the minimum of the smoothed field as the
    center position. Optionally, it can further refine the position using
    the weighted centroid method.

    Args:
        X: 2D meshgrid of x-coordinates (m)
        Y: 2D meshgrid of y-coordinates (m)
        data_2d: 2D pressure field (Pa)
        config: AnalysisConfig instance
        r_smooth: Smoothing radius for Gaussian filter (m), default 500 km
        refine: If True, further refine using weighted centroid method
        r_refine: Refinement radius for weighted centroid (m), used only if refine=True
        max_iterations: Maximum iterations for refinement, used only if refine=True
        verbose: If True, print details

    Returns:
        Tuple of (x_center, y_center, num_iterations) in meters and count
        If refine=False, num_iterations is always 0
    """
    # Calculate sigma for Gaussian filter (in grid cells)
    # Using sigma ≈ r_smooth / (2.355 * dx) for FWHM ≈ r_smooth
    # Simplified to sigma = r_smooth / (3 * dx) for effective smoothing
    sigma_x = r_smooth / (3.0 * config.dx)
    sigma_y = r_smooth / (3.0 * config.dy)

    if verbose:
        print(f"  Smoothing with r_smooth={r_smooth*1e-3:.1f} km")
        print(f"  Gaussian sigma: ({sigma_x:.1f}, {sigma_y:.1f}) grid cells")

    # Apply Gaussian smoothing
    data_smoothed = gaussian_filter(data_2d, sigma=(sigma_y, sigma_x), mode='wrap')

    # Find minimum of smoothed field
    iy, ix = np.unravel_index(np.argmin(data_smoothed, axis=None), data_smoothed.shape)
    x_c = ix * config.dx + config.dx * 0.5
    y_c = iy * config.dy + config.dy * 0.5

    if verbose:
        print(f"  Smoothed minimum at: x={x_c*1e-3:.1f} km, y={y_c*1e-3:.1f} km")

    # Optional refinement using weighted centroid method
    num_iterations = 0
    if refine:
        if verbose:
            print(f"  Refining with weighted centroid (r_refine={r_refine*1e-3:.1f} km)...")
        x_c, y_c, num_iterations = find_pressure_center(
            X, Y, data_2d, config,
            r_refine=r_refine,
            max_iterations=max_iterations,
            verbose=verbose,
            x_init=x_c,
            y_init=y_c
        )

    return x_c, y_c, num_iterations


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
    Supports both .npz and .npy formats.

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
                       (empty dict for .npy files)

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

    # Try to find the file with fallback to different extension
    if not os.path.exists(center_path):
        # Try alternative extension
        base, ext = os.path.splitext(filename)
        if ext == '.npz':
            alt_filename = base + '.npy'
        elif ext == '.npy':
            alt_filename = base + '.npz'
        else:
            alt_filename = None

        if alt_filename:
            alt_path = os.path.join(center_dir, alt_filename)
            if os.path.exists(alt_path):
                center_path = alt_path
                filename = alt_filename

    # Final check if file exists
    if not os.path.exists(center_path):
        raise FileNotFoundError(
            f"Center file not found: {center_path}\n"
            f"Please run the corresponding center calculation script first:\n"
            f"  - For ss_slp: python analysis/center/ss_slp/calc/ss_slp_center_calc.py\n"
            f"  - For ms_pres: python analysis/center/ms_pres/calc/ms_pres_center_calc.py"
        )

    # Determine file format
    file_ext = os.path.splitext(center_path)[1]

    # Load data based on file format
    if file_ext == '.npz':
        # Load .npz file
        data = np.load(center_path)
        center = data["center"]  # shape: (nt, 2) or (nt, nz, 2)
        # Extract metadata (all keys except 'center')
        metadata = {key: data[key] for key in data.files if key != "center"}
    elif file_ext == '.npy':
        # Load .npy file
        center = np.load(center_path)  # shape: (nt, 2) or (nt, nz, 2)
        # No metadata for .npy files
        metadata = {}
    else:
        raise ValueError(f"Unsupported file format: {file_ext}. Must be .npz or .npy")

    # Extract center coordinates based on center_type
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

    return center_x, center_y, metadata
