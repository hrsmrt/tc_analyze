import numpy as np
import os
import sys
import gc

varname = sys.argv[1]

file_list = [
    f"../model/convert1/{varname}.grd",
    f"../model/convert2/{varname}.grd",
    f"../model/convert3/{varname}.grd",
    f"../model/convert4/{varname}.grd",
]

nt_list = [61, 61, 61, 61]
nz = 74
ny, nx = 2048, 2048
dtype = ">f4"
chunk_size = 10  # ← 必要に応じて調整

nt_total = nt_list[0] + sum(nt - 1 for nt in nt_list[1:])
output_path = f"./grd_data/{varname}.grd"

merged = np.memmap(output_path, dtype=dtype, mode="w+", shape=(nt_total, nz, ny, nx))

write_start = 0
for i, fname in enumerate(file_list):
    nt = nt_list[i]
    skip = 1 if i > 0 else 0
    valid_nt = nt - skip

    print(f"📂 読み込み開始: {fname}（{valid_nt}ステップ）")

    with open(fname, "rb") as f:
        if skip:
            f.seek(nz * ny * nx * 4, 1)

        for chunk_start in range(0, valid_nt, chunk_size):
            c = min(chunk_size, valid_nt - chunk_start)
            raw = np.fromfile(f, dtype=dtype, count=c * nz * ny * nx)
            frames = raw.reshape(c, nz, ny, nx)
            merged[write_start:write_start + c] = frames

            print(f"  ✅ チャンク書き出し: step {write_start} ～ {write_start + c - 1}")

            write_start += c
            del raw, frames
            gc.collect()

            if (write_start % (10 * chunk_size)) == 0:
                merged.flush()

merged.flush()
print(f"\n✅ 結合完了: {output_path}（{nt_total} 時間ステップ）")
