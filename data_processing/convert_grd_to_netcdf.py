#!/usr/bin/env python3
"""
Convert multi-time .grd → NetCDF

2D データの例:
python $WORK/tc_analyze/data_processing/convert_grd_to_netcdf.py \
    ss_slp.grd ss_slp.nc \
    --varname ss_slp \
    --nx 2048 --ny 2048 \
    --dx 2000.0 --dy 1732.0508075688772

3D データの例:
python $WORK/tc_analyze/data_processing/convert_grd_to_netcdf.py \
    ms_pres.grd ms_pres.nc \
    --varname ms_pres \
    --nx 2048 --ny 2048 --nz 74 \
    --dx 2000.0 --dy 1732.0508075688772 \
    --z-coords-file $WORK/p-nicam/

Config file を使う例:
python $WORK/tc_analyze/data_processing/convert_grd_to_netcdf.py \
    --config convert_config.json
"""

import argparse
import json
import os
import time

import numpy as np
from netCDF4 import Dataset


def read_timestep(filename, dtype, nx, ny, nz, timestep):
    """Read data for a specific timestep from .grd file"""
    count = nx * ny * nz
    offset = timestep * count * 4  # >f4 = 4 bytes
    data = np.fromfile(filename, dtype=dtype, count=count, offset=offset)
    if nz == 1:
        return data.reshape(ny, nx)
    return data.reshape(nz, ny, nx)


def load_config(config_file):
    """Load configuration from JSON file"""
    with open(config_file, "r", encoding="utf-8") as f:
        return json.load(f)


def load_z_coords(z_coords_file):
    """Load z coordinates from text file (one value per line)"""
    z_coords = []
    with open(z_coords_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                z_coords.append(float(line))
    return z_coords


def write_netcdf(output_file, input_file, varname, nx, ny, nz, nt, dtype,
                 dx, dy, z_coords, units="", long_name=""):
    """Write NetCDF file with CF conventions"""

    # Create x, y coordinates
    x_coords = np.arange(nx, dtype=np.float32) * dx
    y_coords = np.arange(ny, dtype=np.float32) * dy

    # Time coordinates (assuming sequential timesteps)
    time_coords = np.arange(nt, dtype=np.float32)

    with Dataset(output_file, "w", format="NETCDF4") as nc:
        # Create dimensions
        nc.createDimension("time", nt)
        nc.createDimension("x", nx)
        nc.createDimension("y", ny)
        if nz > 1:
            nc.createDimension("z", nz)

        # Create coordinate variables
        time_var = nc.createVariable("time", "f4", ("time",))
        time_var.units = "days since 2000-01-01 00:00:00"
        time_var.calendar = "standard"
        time_var.long_name = "time"
        time_var[:] = time_coords

        x_var = nc.createVariable("x", "f4", ("x",))
        x_var.units = "m"
        x_var.long_name = "x coordinate"
        x_var[:] = x_coords

        y_var = nc.createVariable("y", "f4", ("y",))
        y_var.units = "m"
        y_var.long_name = "y coordinate"
        y_var[:] = y_coords

        if nz > 1:
            z_var = nc.createVariable("z", "f4", ("z",))
            z_var.units = "m"
            z_var.long_name = "z coordinate"
            z_var[:] = np.array(z_coords, dtype=np.float32)

        # Create data variable
        if nz == 1:
            dimensions = ("time", "y", "x")
        else:
            dimensions = ("time", "z", "y", "x")

        # チャンクサイズを最適化（時間方向に1、空間方向に適切なサイズ）
        if nz == 1:
            chunks = (1, min(512, ny), min(512, nx))
        else:
            chunks = (1, min(10, nz), min(256, ny), min(256, nx))

        data_var = nc.createVariable(varname, "f4", dimensions,
                                     zlib=False,  # 圧縮なしで高速化
                                     chunksizes=chunks)
        if units:
            data_var.units = units
        if long_name:
            data_var.long_name = long_name
        else:
            data_var.long_name = varname

        # Write data for each timestep
        print(f"[INFO] Writing {nt} timesteps to NetCDF...")
        for t in range(nt):
            t0 = time.time()
            arr = read_timestep(input_file, dtype, nx, ny, nz, t)
            if nz == 1:
                data_var[t, :, :] = arr
            else:
                data_var[t, :, :, :] = arr

            if (t + 1) % 10 == 0 or t == nt - 1:
                print(f"[INFO] Written {t + 1}/{nt} timesteps "
                      f"({time.time() - t0:.3f} s)")

        # Global attributes
        nc.description = f"Converted from {input_file}"
        nc.history = f"Created {time.ctime(time.time())}"
        nc.source = "convert_grd_to_netcdf.py"
        nc.Conventions = "CF-1.8"


def main():
    """Main function to convert .grd file to NetCDF format"""
    parser = argparse.ArgumentParser(
        description="Convert .grd → NetCDF"
    )
    parser.add_argument("--config", help="JSON configuration file")
    parser.add_argument("input", nargs="?", help="Input .grd file")
    parser.add_argument("output", nargs="?", help="Output .nc file")
    parser.add_argument("--varname", help="Variable name")
    parser.add_argument("--nx", type=int, help="Grid size in x direction")
    parser.add_argument("--ny", type=int, help="Grid size in y direction")
    parser.add_argument("--nz", type=int, help="Grid size in z direction (default: 1)")
    parser.add_argument("--dtype", help='Data type (default: ">f4")')
    parser.add_argument("--dx", type=float, help="Grid spacing in x direction")
    parser.add_argument("--dy", type=float, help="Grid spacing in y direction")
    parser.add_argument(
        "--z-coords", type=float, nargs='+',
        help="Z coordinates (space-separated)"
    )
    parser.add_argument(
        "--z-coords-file",
        help="Text file with z coordinates (one value per line)"
    )
    parser.add_argument("--units", help="Variable units")
    parser.add_argument("--long-name", help="Variable long name")
    args = parser.parse_args()

    # Load config file if provided
    config = {}
    if args.config:
        config = load_config(args.config)

    # Override config with command-line arguments
    input_file = args.input or config.get("input")
    output_file = args.output or config.get("output")
    varname = args.varname or config.get("varname", "data")
    nx = args.nx or config.get("nx")
    ny = args.ny or config.get("ny")
    nz = args.nz or config.get("nz", 1)
    dtype = args.dtype or config.get("dtype", ">f4")
    dx = args.dx or config.get("dx", 1.0)
    dy = args.dy or config.get("dy", 1.0)
    units = args.units or config.get("units", "")
    long_name = args.long_name or config.get("long_name", "")

    # Handle z_coords
    z_coords = None
    if args.z_coords:
        z_coords = args.z_coords
    elif args.z_coords_file:
        z_coords = load_z_coords(args.z_coords_file)
    elif "z_coords" in config:
        z_coords = config["z_coords"]
    elif "z_coords_file" in config:
        z_coords = load_z_coords(config["z_coords_file"])

    # Validate required parameters
    if not all([input_file, output_file, nx, ny]):
        parser.error(
            "Missing required parameters. "
            "Provide either --config or --input, --output, --nx, --ny"
        )

    # Calculate number of timesteps from file size
    filesize = os.path.getsize(input_file)
    step_bytes = nx * ny * nz * 4

    if filesize % step_bytes != 0:
        raise ValueError(
            f"ファイルサイズがステップ数と一致しません。"
            f"filesize={filesize}, step_bytes={step_bytes}"
        )

    nt = filesize // step_bytes
    print(f"[INFO] nt = {nt}, nx = {nx}, ny = {ny}, nz = {nz}")

    # Set default z coordinates
    if nz > 1:
        if z_coords is None:
            z_coords = [float(i) for i in range(nz)]
        elif len(z_coords) != nz:
            raise ValueError(
                f"z_coords には nz ({nz}) 個の値が必要です。"
                f"現在: {len(z_coords)}"
            )
    else:
        z_coords = [0.0]

    # Write NetCDF file
    write_netcdf(output_file, input_file, varname, nx, ny, nz, nt, dtype,
                dx, dy, z_coords, units, long_name)

    print(f"[INFO] NetCDF file saved → {output_file}")


if __name__ == "__main__":
    main()
