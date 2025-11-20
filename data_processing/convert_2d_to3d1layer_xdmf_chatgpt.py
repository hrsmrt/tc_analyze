#!/usr/bin/env python3
"""
Convert multi-time 2D .grd → 3D(1-layer) HDF5 + XDMF (ParaView-friendly, Z non-uniform OK)

想定:
  - 入力 .grd は、2D フィールド (ny, nx) が時間方向に並んだ単一ファイル
  - 各ステップは等サイズ (ny, nx)
  - データ型はデフォルトで big-endian float32 (">f4")

出力:
  - <prefix>_coords.h5       : x, y, z 座標（全タイムステップで共通）
      /x_coords : shape (nx+1,)
      /y_coords : shape (ny+1,)
      /z_coords : shape (nz_pts,)  ※引数 --z-coords に依存
  - <prefix>_0000.h5, <prefix>_0001.h5, ... : 各 timestep の 3D データ
      /<varname> : shape (1, ny, nx)
  - <prefix>.xdmf            : ParaView 用 XDMF (3DRectMesh + VXVYVZ)

使用例:
  python $WORK/tc_analyze/data_processing/convert_2d_to3d1layer_xdmf_chatgpt.py \
      ss_slp.grd ss_slp \
      --varname ss_slp \
      --nx 2048 --ny 2048 \
      --dx 2000.0 --dy 1732.0508075688772 \
      --z-coords -1.0 1.0
"""

import argparse
import os

import h5py
import numpy as np


# ----------------------------------------------------------------------
# 低レベル I/O
# ----------------------------------------------------------------------
def read_2d_timestep(filename: str, dtype: str, nx: int, ny: int, timestep: int) -> np.ndarray:
    """
    .grd から指定 timestep の 2D データ (ny, nx) を読み込む。

    Parameters
    ----------
    filename : str
        入力 .grd ファイルパス
    dtype : str
        numpy dtype 文字列（例: ">f4"）
    nx, ny : int
        グリッド数
    timestep : int
        読み込むステップ index (0 始まり)

    Returns
    -------
    arr2d : ndarray, shape (ny, nx)
    """
    count = nx * ny
    # 1 要素あたりのバイト数（float32 = 4 bytes）
    itemsize = np.dtype(dtype).itemsize
    offset_bytes = timestep * count * itemsize

    data = np.fromfile(filename, dtype=dtype, count=count, offset=offset_bytes)
    if data.size != count:
        raise IOError(f"Failed to read timestep {timestep}: expected {count} values, got {data.size}")

    arr2d = data.reshape(ny, nx)
    return arr2d


def write_field_hdf5(filename: str, dataset_name: str, arr2d: np.ndarray) -> None:
    """
    2D データを (1, ny, nx) の 3D 配列として HDF5 に保存（座標は含めない）。

    Parameters
    ----------
    filename : str
        出力 HDF5 ファイル名
    dataset_name : str
        データセット名 (varname)
    arr2d : ndarray, shape (ny, nx)
    """
    arr3d = arr2d[np.newaxis, :, :]  # (1, ny, nx)

    with h5py.File(filename, "w") as f:
        # 圧縮・チャンクなし → 最速読み込み重視
        f.create_dataset(dataset_name, data=arr3d, compression=None)


def write_coords_hdf5(
    filename: str,
    nx: int,
    ny: int,
    dx: float,
    dy: float,
    z_coords: np.ndarray,
) -> None:
    """
    X, Y, Z 座標配列を HDF5 に保存する。

    Parameters
    ----------
    filename : str
        出力 HDF5 ファイル名
    nx, ny : int
        グリッド数
    dx, dy : float
        x, y 方向の格子間隔
    z_coords : ndarray, shape (nz_pts,)
        z 座標（非一様も可）
    """
    x_coords = np.arange(nx + 1, dtype=np.float32) * dx
    y_coords = np.arange(ny + 1, dtype=np.float32) * dy
    z_coords = np.asarray(z_coords, dtype=np.float32)

    with h5py.File(filename, "w") as f:
        f.create_dataset("x_coords", data=x_coords, compression=None, chunks=None)
        f.create_dataset("y_coords", data=y_coords, compression=None, chunks=None)
        f.create_dataset("z_coords", data=z_coords, compression=None, chunks=None)


# ----------------------------------------------------------------------
# XDMF 出力
# ----------------------------------------------------------------------
def write_xdmf(
    xdmf_filename: str,
    prefix: str,
    varname: str,
    nt: int,
    nx: int,
    ny: int,
    coords_file: str,
    z_coords: np.ndarray,
) -> None:
    """
    XDMF v3 を出力（3DRectMesh + VXVYVZ）。

    Parameters
    ----------
    xdmf_filename : str
        出力 XDMF ファイル名
    prefix : str
        データファイルの prefix （<prefix>_0000.h5 など）
    varname : str
        HDF5 内のデータセット名
    nt : int
        タイムステップ数
    nx, ny : int
        グリッド数
    coords_file : str
        座標を格納した HDF5 ファイル名
    z_coords : ndarray
        z 座標（点の数から nz_pts を決定）
    """
    px = nx + 1
    py = ny + 1
    pz = int(len(z_coords))

    with open(xdmf_filename, "w", encoding="utf-8") as f:
        f.write("""<?xml version="1.0" ?>
<Xdmf Version="3.0">
  <Domain>
    <Grid Name="TimeSeries" GridType="Collection" CollectionType="Temporal">
""")

        for t in range(nt):
            data_h5 = f"{prefix}_{t:04d}.h5"

            f.write(f"""
      <Grid Name="Step{t}" GridType="Uniform">
        <Time Value="{t}" />

        <!-- Rectilinear grid: points = (pz, py, px) -->
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
          <!-- Cell-centered: (nz_cells, ny, nx) = (pz-1, ny, nx) -->
          <DataItem Format="HDF" NumberType="Float" Precision="4" Dimensions="{pz-1} {ny} {nx}">
            {data_h5}:/{varname}
          </DataItem>
        </Attribute>

      </Grid>
""")

        f.write("""
    </Grid>
  </Domain>
</Xdmf>
""")


# ----------------------------------------------------------------------
# main
# ----------------------------------------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser(
        description="2D grd → 3D(1-layer) HDF5 + XDMF (RectMesh + VXVYVZ)"
    )
    parser.add_argument("input", help="input .grd file (multi-time 2D)")
    parser.add_argument("output_prefix", help="output prefix (e.g., ss_slp)")
    parser.add_argument("--nx", type=int, required=True, help="number of grid points in x")
    parser.add_argument("--ny", type=int, required=True, help="number of grid points in y")
    parser.add_argument(
        "--dtype",
        default=">f4",
        help='numpy dtype for input (default: ">f4" for big-endian float32)',
    )
    parser.add_argument(
        "--varname",
        default="data",
        help="dataset name in each HDF5 file (default: data)",
    )
    parser.add_argument(
        "--dx",
        type=float,
        default=1.0,
        help="grid spacing in x direction (default: 1.0)",
    )
    parser.add_argument(
        "--dy",
        type=float,
        default=1.0,
        help="grid spacing in y direction (default: 1.0)",
    )
    parser.add_argument(
        "--z-coords",
        type=float,
        nargs="+",
        default=None,
        help="z coordinates (points). "
             "Example for 1-layer: --z-coords -1.0 1.0 (default: 0.0 1.0)",
    )

    args = parser.parse_args()

    # ---- 入力ファイルサイズから timestep 数を判定
    filesize = os.path.getsize(args.input)
    itemsize = np.dtype(args.dtype).itemsize
    step_bytes = args.nx * args.ny * itemsize

    if filesize % step_bytes != 0:
        raise ValueError(
            f"ファイルサイズがステップ数と一致しません: "
            f"filesize={filesize}, step_bytes={step_bytes}"
        )

    nt = filesize // step_bytes
    print(f"[INFO] detected timesteps: nt = {nt}")

    # ---- z 座標設定
    if args.z_coords is None:
        z_coords = np.array([0.0, 1.0], dtype=np.float32)
    else:
        z_coords = np.array(args.z_coords, dtype=np.float32)
    if z_coords.ndim != 1 or z_coords.size < 2:
        raise ValueError("z-coords は少なくとも 2 点以上の 1 次元配列で指定してください。")

    # ---- 座標ファイル出力
    coords_filename = f"{args.output_prefix}_coords.h5"
    write_coords_hdf5(coords_filename, args.nx, args.ny, args.dx, args.dy, z_coords)
    print(f"[INFO] wrote coordinates → {coords_filename}")

    # ---- 各 timestep のフィールドを出力
    for t in range(nt):
        arr2d = read_2d_timestep(args.input, args.dtype, args.nx, args.ny, t)
        outname = f"{args.output_prefix}_{t:04d}.h5"
        write_field_hdf5(outname, args.varname, arr2d)
        print(f"[INFO] wrote {outname}")

    # ---- XDMF 出力
    xdmf_name = f"{args.output_prefix}.xdmf"
    write_xdmf(
        xdmf_name,
        args.output_prefix,
        args.varname,
        nt,
        args.nx,
        args.ny,
        coords_filename,
        z_coords,
    )
    print(f"[INFO] XDMF saved → {xdmf_name}")


if __name__ == "__main__":
    main()