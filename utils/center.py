"""Utility functions for finding tropical cyclone centers from pressure fields.

This module provides functions to locate low pressure centers using
weighted centroid method with iterative refinement.
"""

import numpy as np


def find_pressure_center(
    X, Y, data_2d, config, r_max_ite=100e3, max_iterations=100, verbose=False,
    x_init=None, y_init=None
):
    """Find the center of low pressure using weighted centroid method.

    This function iteratively refines the center position by calculating
    a weighted centroid within a search radius. The weights are based on
    pressure deficit (data_max - data), giving higher weight to lower pressure.

    Args:
        X: 2D meshgrid of x-coordinates (m)
        Y: 2D meshgrid of y-coordinates (m)
        data_2d: 2D pressure field (Pa)
        config: AnalysisConfig instance
        r_max_ite: Maximum search radius for weighted centroid (m)
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
            X, Y, data_2d, x_c, y_c, r_max_ite, data_max, config
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


def _iteration_step(X, Y, data, x_c, y_c, r_max_ite, data_max, config):
    """Perform one iteration of weighted centroid refinement.

    Args:
        X: X-coordinate meshgrid
        Y: Y-coordinate meshgrid
        data: 2D pressure field
        x_c: Current x-center estimate (m)
        y_c: Current y-center estimate (m)
        r_max_ite: Maximum radius for weighted centroid calculation (m)
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
    mask = dist_sq <= r_max_ite * r_max_ite

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
