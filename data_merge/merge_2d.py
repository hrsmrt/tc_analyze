"""
2次元グリッドデータの結合スクリプト

使用例: python $WORK/tc_analyze/data_merge/merge_2d.py
"""

import sys

import numpy as np

varname = sys.argv[1]

file_list = [
    f"../model/convert1/{varname}.grd",
    f"../model/convert2/{varname}.grd",
    f"../model/convert3/{varname}.grd",
    f"../model/convert4/{varname}.grd",
]

nt_list = [61, 61, 61, 61]  # 各ファイルの時間数（重複含む）
NX = 2048
NY = 2048
DTYPE = ">f4"

# 重複を除いた時間数（先頭以外は1つスキップ）
nt_total = nt_list[0] + sum(nt - 1 for nt in nt_list[1:])

# memmap 出力ファイル作成
OUTPUT_PATH = f"./grd_data/{varname}.grd"
merged = np.memmap(OUTPUT_PATH, dtype=DTYPE, mode="w+", shape=(nt_total, NY, NX))

# ファイルを順次読み込み → 書き込み
write_start = 0
for i, fname in enumerate(file_list):
    print(f"Reading {fname} ...")
    nt = nt_list[i]
    raw_data = np.fromfile(fname, dtype=DTYPE).reshape(nt, NY, NX)

    # 2番目以降のファイルは先頭1つスキップ
    if i >= 1:
        raw_data = raw_data[1:]
        nt -= 1

    merged[write_start: write_start + nt] = raw_data
    write_start += nt

merged.flush()
print(f"✅ 結合完了: {OUTPUT_PATH} （{nt_total} 時間ステップ）")
