#!/usr/bin/env python3
"""
Check HDF5 coordinate file contents
Usage: python check_coords.py ss_slp_coords.h5
"""
import sys
import h5py
import numpy as np

if len(sys.argv) < 2:
    print("Usage: python check_coords.py <coords.h5>")
    sys.exit(1)

filename = sys.argv[1]

with h5py.File(filename, "r") as f:
    print(f"File: {filename}")
    print(f"Datasets: {list(f.keys())}")
    print()

    for key in f.keys():
        data = f[key][:]
        print(f"{key}:")
        print(f"  shape: {data.shape}")
        print(f"  dtype: {data.dtype}")
        print(f"  min: {data.min()}")
        print(f"  max: {data.max()}")
        print(f"  first 5: {data[:5]}")
        print(f"  last 5: {data[-5:]}")
        print()
