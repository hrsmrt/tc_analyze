#!/usr/bin/env python3
"""
最適化効果のベンチマーク

各最適化手法の効果を実測します。
"""
import time

import numpy as np


def benchmark_binning():
    """ビニング処理のベンチマーク"""
    print("=" * 60)
    print("ベンチマーク1: ビニング処理（azim_wind_calc.pyの最適化）")
    print("=" * 60)

    # テストデータ
    nz = 74
    n_points = 1000000
    max_bin = 5000

    bin_idx = np.random.randint(0, max_bin, n_points)
    v_radial = np.random.randn(nz, n_points).astype(np.float32)

    print(f"データサイズ: {nz}×{n_points} = {nz * n_points:,}要素")
    print(f"ビン数: {max_bin}")
    print()

    # ❌ ループ版（遅い）
    print("【従来版】Pythonループ...")
    azim_sum_radial = np.zeros((nz, max_bin))
    start = time.time()
    for i, b in enumerate(bin_idx):
        azim_sum_radial[:, b] += v_radial[:, i]
    loop_time = time.time() - start
    print(f"  実行時間: {loop_time:.2f}秒")
    loop_result = azim_sum_radial.copy()

    # ✅ ベクトル化版1（np.add.at with transpose）
    print("\n【最適化版1】np.add.at() with transpose...")
    azim_sum_radial = np.zeros((nz, max_bin))
    start = time.time()
    np.add.at(azim_sum_radial.T, bin_idx, v_radial.T)
    vectorized1_time = time.time() - start
    print(f"  実行時間: {vectorized1_time:.2f}秒")
    print(f"  高速化率: {loop_time / vectorized1_time:.1f}倍")
    vectorized1_result = azim_sum_radial.copy()

    # ✅ ベクトル化版2（z方向ループ）
    print("\n【最適化版2】np.add.at() with z-loop...")
    azim_sum_radial = np.zeros((nz, max_bin))
    start = time.time()
    for z in range(nz):
        np.add.at(azim_sum_radial[z], bin_idx, v_radial[z])
    vectorized2_time = time.time() - start
    print(f"  実行時間: {vectorized2_time:.2f}秒")
    print(f"  高速化率: {loop_time / vectorized2_time:.1f}倍")
    vectorized2_result = azim_sum_radial.copy()

    # 結果の一致確認
    print("\n【検証】結果の一致確認...")
    print(
        f"  版1 vs 従来: {np.allclose(vectorized1_result, loop_result, rtol=1e-5)}"
    )
    print(
        f"  版2 vs 従来: {np.allclose(vectorized2_result, loop_result, rtol=1e-5)}"
    )

    print("\n【推奨】最適化版1（転置版）が最速です\n")


def benchmark_3d_operations():
    """3次元配列操作のベンチマーク"""
    print("=" * 60)
    print("ベンチマーク2: 3次元配列操作（divergence_calc.pyの最適化）")
    print("=" * 60)

    # テストデータ
    nz, ny, nx = 74, 128, 128
    dx, dy = 2000.0, 2000.0

    data_u = np.random.randn(nz, ny, nx).astype(np.float32)
    data_v = np.random.randn(nz, ny, nx).astype(np.float32)

    print(f"データサイズ: {nz}×{ny}×{nx} = {nz * ny * nx:,}要素")
    print()

    # ❌ ループ版（遅い）
    print("【従来版】Z方向のループ...")
    div = np.zeros((nz, ny, nx), dtype=np.float32)
    start = time.time()
    for z in range(nz):
        du_dx = (np.roll(data_u[z], -1, axis=1) - np.roll(data_u[z], 1, axis=1)) / (
            2 * dx
        )
        dv_dy = (np.roll(data_v[z], -1, axis=0) - np.roll(data_v[z], 1, axis=0)) / (
            2 * dy
        )
        div[z] = du_dx + dv_dy
    loop_time = time.time() - start
    print(f"  実行時間: {loop_time:.2f}秒")
    loop_result = div.copy()

    # ✅ ベクトル化版
    print("\n【最適化版】ベクトル化...")
    start = time.time()
    du_dx = (np.roll(data_u, -1, axis=2) - np.roll(data_u, 1, axis=2)) / (2 * dx)
    dv_dy = (np.roll(data_v, -1, axis=1) - np.roll(data_v, 1, axis=1)) / (2 * dy)
    div = du_dx + dv_dy
    vectorized_time = time.time() - start
    print(f"  実行時間: {vectorized_time:.2f}秒")
    print(f"  高速化率: {loop_time / vectorized_time:.1f}倍")
    vectorized_result = div.copy()

    # 結果の一致確認
    print("\n【検証】結果の一致確認...")
    print(f"  一致: {np.allclose(vectorized_result, loop_result, rtol=1e-5)}")

    print()


def benchmark_memory_access():
    """メモリアクセスパターンのベンチマーク"""
    print("=" * 60)
    print("ベンチマーク3: メモリアクセスパターン")
    print("=" * 60)

    # テストデータ
    nz, n_points = 74, 1000000
    data = np.random.randn(nz, n_points).astype(np.float32)

    print(f"データサイズ: {nz}×{n_points} = {nz * n_points:,}要素")
    print()

    # ❌ 列方向アクセス（遅い）
    print("【非効率】列方向アクセス...")
    start = time.time()
    result = np.zeros(n_points)
    for i in range(n_points):
        result[i] = data[:, i].sum()
    column_time = time.time() - start
    print(f"  実行時間: {column_time:.2f}秒")

    # ✅ 行方向アクセス（速い）
    print("\n【効率的】行方向アクセス（転置）...")
    data_T = data.T
    start = time.time()
    result = np.zeros(n_points)
    for i in range(n_points):
        result[i] = data_T[i].sum()
    row_time = time.time() - start
    print(f"  実行時間: {row_time:.2f}秒")
    print(f"  高速化率: {column_time / row_time:.1f}倍")

    # ✅✅ 完全ベクトル化（最速）
    print("\n【最適】完全ベクトル化...")
    start = time.time()
    result = data.sum(axis=0)
    vectorized_time = time.time() - start
    print(f"  実行時間: {vectorized_time:.2f}秒")
    print(f"  高速化率（列アクセスと比較）: {column_time / vectorized_time:.1f}倍")

    print()


def benchmark_io():
    """I/O操作のベンチマーク"""
    print("=" * 60)
    print("ベンチマーク4: ファイルI/O")
    print("=" * 60)

    import tempfile

    # テストデータ
    nt, ny, nx = 10, 128, 128
    data = np.random.randn(nt, ny, nx).astype(">f4")

    # 一時ファイル作成
    with tempfile.NamedTemporaryFile(suffix=".grd", delete=False) as f:
        temp_file = f.name
        data.tofile(f)

    print(f"データサイズ: {nt}タイムステップ × {ny}×{nx}")
    print()

    try:
        # ❌ 毎回ファイルを開閉（遅い）
        print("【従来版】毎回ファイルを開閉...")
        start = time.time()
        for t in range(nt):
            count_2d = ny * nx
            offset = count_2d * t * 4
            with open(temp_file, "rb") as f:
                f.seek(offset)
                _ = np.fromfile(f, dtype=">f4", count=count_2d).reshape(ny, nx)
        file_time = time.time() - start
        print(f"  実行時間: {file_time:.2f}秒")

        # ✅ メモリマップ（速い）
        print("\n【最適化版】np.memmap()...")
        start = time.time()
        data_mmap = np.memmap(temp_file, dtype=">f4", mode="r", shape=(nt, ny, nx))
        for t in range(nt):
            _ = data_mmap[t]
        memmap_time = time.time() - start
        print(f"  実行時間: {memmap_time:.2f}秒")
        print(f"  高速化率: {file_time / memmap_time:.1f}倍")

    finally:
        import os

        os.unlink(temp_file)

    print()


def main():
    """全ベンチマークを実行"""
    print("\n" + "=" * 60)
    print("tc_analyze 高速化ベンチマーク")
    print("=" * 60 + "\n")

    benchmark_binning()
    benchmark_3d_operations()
    benchmark_memory_access()
    benchmark_io()

    print("=" * 60)
    print("全ベンチマーク完了")
    print("=" * 60)


if __name__ == "__main__":
    main()
