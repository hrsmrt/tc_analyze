"""
Metadata utilities for reading and analyzing data files.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

import numpy as np


def read_npz_metadata(file_path: str) -> Dict[str, Any]:
    """
    Read metadata from .npz file.

    Args:
        file_path: Path to .npz file

    Returns:
        Dictionary containing metadata
    """
    data = np.load(file_path)

    metadata = {
        "file_path": file_path,
        "file_size": os.path.getsize(file_path),
        "format": "npz",
        "keys": list(data.keys()),
    }

    # Extract common metadata fields
    if "center" in data:
        metadata["data_shape"] = data["center"].shape
        metadata["data_dtype"] = str(data["center"].dtype)

    if "data" in data:
        metadata["data_shape"] = data["data"].shape
        metadata["data_dtype"] = str(data["data"].dtype)

    # Extract parameter metadata
    for key in data.keys():
        if key not in ["center", "data"]:
            value = data[key]
            if value.ndim == 0:  # Scalar
                metadata[key] = value.item()
            else:
                metadata[f"{key}_shape"] = value.shape

    return metadata


def read_npy_metadata(file_path: str) -> Dict[str, Any]:
    """
    Read metadata from .npy file.

    Args:
        file_path: Path to .npy file

    Returns:
        Dictionary containing metadata
    """
    data = np.load(file_path)

    metadata = {
        "file_path": file_path,
        "file_size": os.path.getsize(file_path),
        "format": "npy",
        "data_shape": data.shape,
        "data_dtype": str(data.dtype),
    }

    return metadata


def read_data_metadata(file_path: str) -> Optional[Dict[str, Any]]:
    """
    Read metadata from data file (auto-detect format).

    Args:
        file_path: Path to data file

    Returns:
        Dictionary containing metadata, or None if file not found
    """
    if not os.path.exists(file_path):
        return None

    if file_path.endswith(".npz"):
        return read_npz_metadata(file_path)
    elif file_path.endswith(".npy"):
        return read_npy_metadata(file_path)
    else:
        return {
            "file_path": file_path,
            "file_size": os.path.getsize(file_path),
            "format": "unknown",
        }


def find_data_files(base_dir: str, pattern: str = "*.npz") -> List[str]:
    """
    Find data files matching pattern.

    Args:
        base_dir: Base directory to search
        pattern: Glob pattern (e.g., "*.npz", "*.npy")

    Returns:
        List of file paths
    """
    base_path = Path(base_dir)
    if not base_path.exists():
        return []

    return [str(p) for p in base_path.rglob(pattern)]


def format_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted string (e.g., "2.3 MB")
    """
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def format_shape(shape: tuple) -> str:
    """
    Format array shape in human-readable format.

    Args:
        shape: Array shape tuple

    Returns:
        Formatted string (e.g., "(120, 74, 1000)")
    """
    return f"({', '.join(map(str, shape))})"


def get_data_statistics(data_array: np.ndarray) -> Dict[str, float]:
    """
    Calculate statistics for data array.

    Args:
        data_array: NumPy array

    Returns:
        Dictionary with statistics (min, max, mean, std)
    """
    # Handle NaN values
    valid_data = data_array[np.isfinite(data_array)]

    if len(valid_data) == 0:
        return {
            "min": np.nan,
            "max": np.nan,
            "mean": np.nan,
            "std": np.nan,
            "nan_count": data_array.size,
        }

    return {
        "min": float(np.min(valid_data)),
        "max": float(np.max(valid_data)),
        "mean": float(np.mean(valid_data)),
        "std": float(np.std(valid_data)),
        "nan_count": int(np.sum(~np.isfinite(data_array))),
    }
