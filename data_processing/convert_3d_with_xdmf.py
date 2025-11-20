#!/usr/bin/env python3
"""
Convert multi-time 3D .grd → HDF5 + XDMF (ParaView SAFE)

⭐ 最速構成：
  - Topology: 3DCoRectMesh
  - Geometry: VXVYVZ (x, y, z 座標を HDF5 から読み込み)
  - データ: HDF5（圧縮なし）

Example with config file:
python $WORK/tc_analyze/data_processing/convert_3d_with_xdmf.py --config convert_config.json

Example with command-line arguments:
python $WORK/tc_analyze/data_processing/convert_3d_with_xdmf.py \
    --input temperature.grd \
    --output-prefix temperature \
    --varname temperature \
    --nx 2048 --ny 2048 --nz 50 \
    --dx 1000.0 --dy 1000.0 \
    --z-coords-file z_coords.txt

Config file format (JSON):
{
    "input": "temperature.grd",
    "output_prefix": "temperature",
    "varname": "temperature",
    "nx": 2048,
    "ny": 2048,
    "nz": 50,
    "dx": 1000.0,
    "dy": 1000.0,
    "z_coords_file": "z_coords.txt"
}

出力ファイル:
  - temperature_coords.h5: x, y, z 座標（全タイムステップで共有）
  - temperature_0000.h5, temperature_0001.h5, ...: 各タイムステップのデータ
  - temperature.xdmf: ParaView用メタデータファイル
"""

import argparse
import json
import os
import time

import h5py
import numpy as np


def read_3d_timestep(filename, dtype, nx, ny, nz, timestep):
    """Read 3D data for a specific timestep from .grd file"""
    count = nx * ny * nz
    offset = timestep * count * 4  # >f4 = 4 bytes
    data = np.fromfile(filename, dtype=dtype, count=count, offset=offset)
    arr3d = data.reshape(nz, ny, nx)
    return arr3d


def write_hdf5(filename, dataset_name, arr3d):
    """Write 3D array to HDF5 file (without coordinates)"""
    with h5py.File(filename, "w") as f:
        f.create_dataset(dataset_name, data=arr3d, compression=None)


def write_coords_hdf5(filename, nx, ny, dx, dy, z_coords):
    """Write X, Y, Z coordinate arrays to HDF5 file"""
    # Generate x and y coordinates
    x_coords = np.arange(nx + 1, dtype=np.float32) * dx
    y_coords = np.arange(ny + 1, dtype=np.float32) * dy

    with h5py.File(filename, "w") as f:
        f.create_dataset("x_coords", data=x_coords, compression=None, chunks=None)
        f.create_dataset("y_coords", data=y_coords, compression=None, chunks=None)
        f.create_dataset("z_coords", data=np.array(z_coords, dtype=np.float32),
                        compression=None, chunks=None)


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


def write_xdmf(xdmf_filename, prefix, varname, nt, nx, ny, nz, coords_file):
    """
    ParaView 最速構成:
    - Topology: 3DCoRectMesh
    - Geometry: VXVYVZ (x, y, z 座標を HDF5 から読み込み)
    """
    px = nx + 1
    py = ny + 1
    pz = nz + 1

    with open(xdmf_filename, "w", encoding="utf-8") as f:
        f.write("""<?xml version="1.0" ?>
<Xdmf Version="3.0">
  <Domain>
    <Grid Name="TimeSeries" GridType="Collection" CollectionType="Temporal">
""")

        for t in range(nt):
            h5name = f"{prefix}_{t:04d}.h5"

            f.write(f"""
      <Grid Name="Step{t}" GridType="Uniform">
        <Time Value="{t}" />

        <Topology TopologyType="3DRectMesh" Dimensions="{pz} {py} {px}" />

        <Geometry GeometryType="VXVYVZ">
          <DataItem Format="HDF" NumberType="Float" Precision="4" Dimensions="{px}">
            {coords_file}:/x_coords
          </DataItem>
          <DataItem Format="HDF" NumberType="Float" Precision="4" Dimensions="{py}">
            {coords_file}:/y_coords
          </DataItem>
          <DataItem Format="HDF" NumberType="Float" Precision="4" Dimensions="{pz}">
            {coords_file}:/z_coords
          </DataItem>
        </Geometry>

        <Attribute Name="{varname}" AttributeType="Scalar" Center="Cell">
          <DataItem Format="HDF" NumberType="Float" Precision="4" Dimensions="{nz} {ny} {nx}">
            {h5name}:/{varname}
          </DataItem>
        </Attribute>

      </Grid>
""")

        f.write("""
    </Grid>
  </Domain>
</Xdmf>
""")


def main():
    """Main function to convert 3D .grd file to HDF5 + XDMF format"""
    parser = argparse.ArgumentParser(
        description="3D grd → HDF5 + XDMF (ParaView SAFE)"
    )
    parser.add_argument("--config", help="JSON configuration file")
    parser.add_argument("--input", help="Input .grd file")
    parser.add_argument("--output-prefix", help="Output file prefix")
    parser.add_argument("--varname", help="Variable name")
    parser.add_argument("--nx", type=int, help="Grid size in x direction")
    parser.add_argument("--ny", type=int, help="Grid size in y direction")
    parser.add_argument("--nz", type=int, help="Grid size in z direction")
    parser.add_argument("--dtype", help='Data type (default: ">f4")')
    parser.add_argument("--dx", type=float, help="Grid spacing in x direction")
    parser.add_argument("--dy", type=float, help="Grid spacing in y direction")
    parser.add_argument(
        "--z-coords", type=float, nargs='+',
        help="Z coordinates (space-separated, must be nz+1 values)"
    )
    parser.add_argument(
        "--z-coords-file",
        help="Text file with z coordinates (one value per line)"
    )
    args = parser.parse_args()

    # Load config file if provided
    config = {}
    if args.config:
        config = load_config(args.config)

    # Override config with command-line arguments
    input_file = args.input or config.get("input")
    output_prefix = args.output_prefix or config.get("output_prefix")
    varname = args.varname or config.get("varname", "data")
    nx = args.nx or config.get("nx")
    ny = args.ny or config.get("ny")
    nz = args.nz or config.get("nz")
    dtype = args.dtype or config.get("dtype", ">f4")
    dx = args.dx or config.get("dx", 1.0)
    dy = args.dy or config.get("dy", 1.0)

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
    if not all([input_file, output_prefix, nx, ny, nz]):
        parser.error(
            "Missing required parameters. "
            "Provide either --config or --input, --output-prefix, --nx, --ny, --nz"
        )

    # ファイルサイズから時間ステップ数を計算
    filesize = os.path.getsize(input_file)
    step_bytes = nx * ny * nz * 4

    if filesize % step_bytes != 0:
        raise ValueError(
            f"ファイルサイズがステップ数と一致しません。"
            f"filesize={filesize}, step_bytes={step_bytes}"
        )

    nt = filesize // step_bytes
    print(f"[INFO] nt = {nt}, nx = {nx}, ny = {ny}, nz = {nz}")

    # z座標のデフォルト設定と検証
    if z_coords is None:
        z_coords = [float(i) for i in range(nz + 1)]
    elif len(z_coords) != nz + 1:
        raise ValueError(
            f"z_coords には nz+1 ({nz + 1}) 個の値が必要です。"
            f"現在: {len(z_coords)}"
        )

    # 座標ファイル出力（X, Y, Z すべて）
    coords_filename = f"{output_prefix}_coords.h5"
    write_coords_hdf5(coords_filename, nx, ny, dx, dy, z_coords)
    print(f"[INFO] Wrote coordinates → {coords_filename}")

    # HDF5 出力（データのみ）
    for t in range(nt):
        t0 = time.time()
        arr3d = read_3d_timestep(input_file, dtype, nx, ny, nz, t)
        outname = f"{output_prefix}_{t:04d}.h5"
        write_hdf5(outname, varname, arr3d)
        print(f"[INFO] Wrote {outname} ({time.time() - t0:.3f} s)")

    # XDMF 出力
    xdmf_name = f"{output_prefix}.xdmf"
    write_xdmf(
        xdmf_name, output_prefix, varname, nt,
        nx, ny, nz, coords_filename
    )
    print(f"[INFO] XDMF saved → {xdmf_name}")


if __name__ == "__main__":
    main()
