"""
3次元グリッドデータの結合スクリプト

複数のバイナリファイルを結合して1つのメモリマップ配列を作成する。
"""

import gc
import sys

import numpy as np

varname = sys.argv[1]

file_list = [
    f"../model/convert1/{varname}.grd",
    f"../model/convert2/{varname}.grd",
    f"../model/convert3/{varname}.grd",
    f"../model/convert4/{varname}.grd",
]

nt_list = [61, 61, 61, 61]
NZ = 74
ny, nx = 2048, 2048
DTYPE = ">f4"
CHUNK_SIZE = 10  # ← 必要に応じて調整

nt_total = nt_list[0] + sum(nt - 1 for nt in nt_list[1:])
OUTPUT_PATH = f"./grd_data/{varname}.grd"

merged = np.memmap(OUTPUT_PATH, dtype=DTYPE, mode="w+", shape=(nt_total, NZ, ny, nx))

write_start = 0
for i, fname in enumerate(file_list):
    nt = nt_list[i]
    skip = 1 if i > 0 else 0
    valid_nt = nt - skip

    print(f"📂 読み込み開始: {fname}（{valid_nt}ステップ）")

    with open(fname, "rb") as f:
        if skip:
            f.seek(NZ * ny * nx * 4, 1)

        for chunk_start in range(0, valid_nt, CHUNK_SIZE):
            c = min(CHUNK_SIZE, valid_nt - chunk_start)
            raw = np.fromfile(f, dtype=DTYPE, count=c * NZ * ny * nx)
            frames = raw.reshape(c, NZ, ny, nx)
            merged[write_start: write_start + c] = frames

            print(f"  ✅ チャンク書き出し: step {write_start} ～ {write_start + c - 1}")

            write_start += c
            del raw, frames
            gc.collect()

            if (write_start % (10 * CHUNK_SIZE)) == 0:
                merged.flush()

merged.flush()
print(f"\n✅ 結合完了: {OUTPUT_PATH}（{nt_total} 時間ステップ）")
