#!/usr/bin/env python3
"""
Convert multi-time 2D .grd → 3D(1-layer) HDF5 + XDMF (ParaView SAFE)

⭐ 最速構成：
  - Topology: 3DCoRectMesh
  - Geometry: VXVYVZ (x, y, z 座標を HDF5 から読み込み)
  - データ: HDF5（圧縮なし）

python $WORK/tc_analyze/data_processing/convert_2d_to3d1layer_xdmf.py \
    ss_slp.grd ss_slp \
    --varname ss_slp \
    --nx 2048 --ny 2048 \
    --dx 2000.0 --dy 1732.0508075688772 \
    --z-coords -1.0 1.0

出力ファイル:
  - ss_slp_coords.h5: x, y, z 座標（全タイムステップで共有）
  - ss_slp_0000.h5, ss_slp_0001.h5, ...: 各タイムステップのデータ
  - ss_slp.xdmf: ParaView用メタデータファイル
"""

import argparse
import os

import h5py
import numpy as np


def read_2d_timestep(filename, dtype, nx, ny, timestep):
    """Read 2D data for a specific timestep from .grd file"""
    count = nx * ny
    offset = timestep * count * 4  # >f4 = 4 bytes
    data = np.fromfile(filename, dtype=dtype, count=count, offset=offset)
    arr2d = data.reshape(ny, nx)
    return arr2d


def write_hdf5(filename, dataset_name, arr2d):
    """Write 3D data to HDF5 file (without coordinates)"""
    arr3d = arr2d[np.newaxis, :, :]  # (1, ny, nx)
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


def write_xdmf(xdmf_filename, prefix, varname, nt, nx, ny, coords_file):
    """
    ParaView 最速構成:
    - Topology: 3DCoRectMesh
    - Geometry: VXVYVZ (x, y, z 座標を HDF5 から読み込み)
    """
    px = nx + 1
    py = ny + 1
    pz = 2  # 1層の場合は2点

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
          <DataItem Format="HDF" NumberType="Float" Precision="4" Dimensions="1 {ny} {nx}">
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
    """Main function to convert 2D .grd file to 3D(1-layer) HDF5 + XDMF format"""
    parser = argparse.ArgumentParser(
        description="2D grd → 3D(1-layer) HDF5 + XDMF (ParaView SAFE)"
    )
    parser.add_argument("input")
    parser.add_argument("output_prefix")
    parser.add_argument("--nx", type=int, required=True)
    parser.add_argument("--ny", type=int, required=True)
    parser.add_argument("--dtype", default=">f4")
    parser.add_argument("--varname", default="data")
    parser.add_argument(
        "--dx", type=float, default=1.0,
        help="Grid spacing in x direction (default: 1.0)"
    )
    parser.add_argument(
        "--dy", type=float, default=1.0,
        help="Grid spacing in y direction (default: 1.0)"
    )
    parser.add_argument(
        "--z-coords", type=float, nargs='+', default=None,
        help="Z coordinates (space-separated). Default: [0.0, 1.0] for 1-layer"
    )
    args = parser.parse_args()

    filesize = os.path.getsize(args.input)
    step_bytes = args.nx * args.ny * 4

    if filesize % step_bytes != 0:
        raise ValueError("ファイルサイズがステップ数と一致しません")

    nt = filesize // step_bytes
    print(f"[INFO] nt = {nt}")

    # z座標のデフォルト設定
    if args.z_coords is None:
        z_coords = [0.0, 1.0]
    else:
        z_coords = args.z_coords

    # 座標ファイル出力（X, Y, Z すべて）
    coords_filename = f"{args.output_prefix}_coords.h5"
    write_coords_hdf5(coords_filename, args.nx, args.ny, args.dx, args.dy, z_coords)
    print(f"[INFO] Wrote coordinates → {coords_filename}")

    # HDF5出力（データのみ）
    for t in range(nt):
        arr2d = read_2d_timestep(args.input, args.dtype, args.nx, args.ny, t)
        outname = f"{args.output_prefix}_{t:04d}.h5"
        write_hdf5(outname, args.varname, arr2d)
        print(f"[INFO] Wrote {outname}")

    # XDMF出力
    xdmf_name = f"{args.output_prefix}.xdmf"
    write_xdmf(xdmf_name, args.output_prefix, args.varname, nt,
               args.nx, args.ny, coords_filename)
    print(f"[INFO] XDMF saved → {xdmf_name}")


if __name__ == "__main__":
    main()
