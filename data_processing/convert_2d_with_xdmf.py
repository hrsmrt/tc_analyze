#!/usr/bin/env python3
"""
python $WORK/tc_analyze/data_processing/convert_2d_with_xdmf.py \
    ss_slp.grd ss_slp \
    --nx 2048 --ny 2048 \
    --varname ss_slp
"""

import numpy as np
import h5py
import argparse
import time
import os


def read_2d_timestep(filename, dtype, nx, ny, timestep):
    count = nx * ny
    offset = timestep * count * 4  # >f4 = 4 bytes
    data = np.fromfile(filename, dtype=dtype, count=count, offset=offset)
    return data.reshape(ny, nx)


def write_hdf5(filename, dataset_name, array):
    with h5py.File(filename, "w") as f:
        f.create_dataset(dataset_name, data=array, compression=None)


def write_xdmf(xdmf_filename, prefix, nt, nx, ny, varname):
    """
    ParaView で安全に読める XDMF v3 を生成。
    - Cell 中心値（ny × nx）
    - RectMesh 点数は (ny+1) × (nx+1)
    """

    with open(xdmf_filename, "w") as f:
        f.write("""<?xml version="1.0" ?>
<Xdmf Version="3.0">
  <Domain>
    <Grid Name="TimeSeries" GridType="Collection" CollectionType="Temporal">
""")

        px = nx + 1   # RectMesh 点数
        py = ny + 1

        for t in range(nt):
            h5name = f"{prefix}_{t:04d}.h5"

            f.write(f"""
      <Grid Name="Step{t}" GridType="Uniform">
        <Time Value="{t}" />

        <Topology TopologyType="2DRectMesh" Dimensions="{py} {px}" />

        <Geometry GeometryType="Origin_DxDy">
          <Origin>
            <DataItem Dimensions="2">0 0</DataItem>
          </Origin>
          <DxDy>
            <DataItem Dimensions="2">1 1</DataItem>
          </DxDy>
        </Geometry>

        <Attribute Name="{varname}" AttributeType="Scalar" Center="Cell">
          <DataItem Format="HDF" Dimensions="{ny} {nx}">
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
    parser = argparse.ArgumentParser(description="Convert multi-time 2D .grd -> HDF5 + XDMF")
    parser.add_argument("input")
    parser.add_argument("output_prefix")
    parser.add_argument("--nx", type=int, required=True)
    parser.add_argument("--ny", type=int, required=True)
    parser.add_argument("--dtype", default=">f4")
    parser.add_argument("--varname", default="data")
    args = parser.parse_args()

    filesize = os.path.getsize(args.input)
    step_bytes = args.nx * args.ny * 4
    if filesize % step_bytes != 0:
        raise ValueError("ファイルサイズがステップ数と一致しません")

    nt = filesize // step_bytes
    print(f"[INFO] Detected timesteps: nt = {nt}")

    # HDF5 出力
    for t in range(nt):
        t0 = time.time()
        arr = read_2d_timestep(args.input, args.dtype, args.nx, args.ny, t)

        outname = f"{args.output_prefix}_{t:04d}.h5"
        write_hdf5(outname, args.varname, arr)

        print(f"[INFO] Wrote {outname} ({time.time() - t0:.3f} s)")

    # XDMF 出力
    xdmf_name = f"{args.output_prefix}.xdmf"
    write_xdmf(xdmf_name, args.output_prefix, nt, args.nx, args.ny, args.varname)
    print(f"[INFO] XDMF saved: {xdmf_name}")


if __name__ == "__main__":
    main()
