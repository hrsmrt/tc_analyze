"""
方位角平均計算関数

データを保存せず、必要時にその場で計算することでストレージを節約できます。
"""

import numpy as np


def calculate_azimuthal_mean_wind(
    data_u, data_v, t, center_x_list, center_y_list, grid_handler, r_max=1000e3
):
    """
    方位角平均風（動径・接線成分）を計算（オンデマンド）

    Parameters
    ----------
    data_u : memmap
        u風のメモリマップ (nt, nz, ny, nx)
    data_v : memmap
        v風のメモリマップ (nt, nz, ny, nx)
    t : int
        時刻インデックス
    center_x_list : ndarray
        台風中心のx座標リスト [m]
    center_y_list : ndarray
        台風中心のy座標リスト [m]
    grid_handler : GridHandler
        グリッドハンドラー
    r_max : float, optional
        最大半径 [m], デフォルト: 1000km

    Returns
    -------
    azim_mean_radial : ndarray (nz, nr)
        方位角平均動径風 [m/s]
    azim_mean_tangential : ndarray (nz, nr)
        方位角平均接線風 [m/s]

    Notes
    -----
    - データを保存せず、必要時に計算
    - ストレージ大幅節約（数GB〜数百GB）
    - azim_wind_calc.py のロジックを関数化
    """
    # 設定値を取得
    config = grid_handler.config
    cx = center_x_list[t]
    cy = center_y_list[t]

    # グリッド座標
    X, Y = grid_handler.X, grid_handler.Y

    # 中心からの距離と角度を計算
    dX = X - cx
    dY = Y - cy
    dX[dX > 0.5 * config.x_width] -= config.x_width
    dX[dX < -0.5 * config.x_width] += config.x_width

    theta = np.arctan2(dY, dX)
    R = np.sqrt(dX**2 + dY**2)

    # r_max 以内のマスク
    mask = R <= r_max
    valid_r = R[mask]

    # ビニング設定
    bin_idx = np.floor(valid_r / config.dx).astype(int)
    max_bin = int(np.floor(r_max / config.dx))
    bin_idx = np.clip(bin_idx, 0, max_bin - 1)

    count_r = np.bincount(bin_idx, minlength=max_bin)

    # データ読み込み
    data_u_t = data_u[t]
    data_v_t = data_v[t]

    valid_data_u = data_u_t[:, mask]
    valid_data_v = data_v_t[:, mask]

    # 動径・接線成分に変換
    v_radial = valid_data_u * np.cos(theta[mask]) + valid_data_v * np.sin(theta[mask])
    v_tangential = -valid_data_u * np.sin(theta[mask]) + valid_data_v * np.cos(theta[mask])

    # 方位角平均（動径風）
    azim_sum_radial = np.zeros((config.nz, max_bin), dtype=np.float32)
    np.add.at(azim_sum_radial.T, bin_idx, v_radial.T)

    with np.errstate(divide="ignore", invalid="ignore"):
        azim_mean_radial = np.where(count_r > 0, azim_sum_radial / count_r, np.nan)

    # 方位角平均（接線風）
    azim_sum_tangential = np.zeros((config.nz, max_bin), dtype=np.float32)
    np.add.at(azim_sum_tangential.T, bin_idx, v_tangential.T)

    with np.errstate(divide="ignore", invalid="ignore"):
        azim_mean_tangential = np.where(count_r > 0, azim_sum_tangential / count_r, np.nan)

    return azim_mean_radial.astype(np.float32), azim_mean_tangential.astype(np.float32)


def calculate_azimuthal_mean_relative_wind(
    data_u, data_v, t, center_x_list, center_y_list, center_u_list, center_v_list, grid_handler, r_max=1000e3
):
    """
    相対風の方位角平均（動径・接線成分）を計算（オンデマンド）

    Parameters
    ----------
    data_u : memmap
        u風のメモリマップ (nt, nz, ny, nx)
    data_v : memmap
        v風のメモリマップ (nt, nz, ny, nx)
    t : int
        時刻インデックス
    center_x_list : ndarray
        台風中心のx座標リスト [m]
    center_y_list : ndarray
        台風中心のy座標リスト [m]
    center_u_list : ndarray
        台風中心のx方向移動速度リスト [m/s]
    center_v_list : ndarray
        台風中心のy方向移動速度リスト [m/s]
    grid_handler : GridHandler
        グリッドハンドラー
    r_max : float, optional
        最大半径 [m], デフォルト: 1000km

    Returns
    -------
    azim_mean_radial : ndarray (nz, nr)
        相対風の方位角平均動径風 [m/s]
    azim_mean_tangential : ndarray (nz, nr)
        相対風の方位角平均接線風 [m/s]

    Notes
    -----
    - データを保存せず、必要時に計算
    - ストレージ大幅節約（数GB〜数百GB）
    - azim_wind_relative_calc.py のロジックを関数化
    """
    # 設定値を取得
    config = grid_handler.config
    cx = center_x_list[t]
    cy = center_y_list[t]
    cu = center_u_list[t]
    cv = center_v_list[t]

    # グリッド座標
    X, Y = grid_handler.X, grid_handler.Y

    # 中心からの距離と角度を計算
    dX = X - cx
    dY = Y - cy
    dX[dX > 0.5 * config.x_width] -= config.x_width
    dX[dX < -0.5 * config.x_width] += config.x_width

    theta = np.arctan2(dY, dX)
    R = np.sqrt(dX**2 + dY**2)

    # r_max 以内のマスク
    mask = R <= r_max
    valid_r = R[mask]

    # ビニング設定
    bin_idx = np.floor(valid_r / config.dx).astype(int)
    max_bin = int(np.floor(r_max / config.dx))
    bin_idx = np.clip(bin_idx, 0, max_bin - 1)

    count_r = np.bincount(bin_idx, minlength=max_bin)

    # データ読み込みと相対風計算
    data_u_t = data_u[t] - cu
    data_v_t = data_v[t] - cv

    valid_data_u = data_u_t[:, mask]
    valid_data_v = data_v_t[:, mask]

    # 動径・接線成分に変換
    v_radial = valid_data_u * np.cos(theta[mask]) + valid_data_v * np.sin(theta[mask])
    v_tangential = -valid_data_u * np.sin(theta[mask]) + valid_data_v * np.cos(theta[mask])

    # 方位角平均（動径風）
    azim_sum_radial = np.zeros((config.nz, max_bin), dtype=np.float32)
    np.add.at(azim_sum_radial.T, bin_idx, v_radial.T)

    with np.errstate(divide="ignore", invalid="ignore"):
        azim_mean_radial = np.where(count_r > 0, azim_sum_radial / count_r, np.nan)

    # 方位角平均（接線風）
    azim_sum_tangential = np.zeros((config.nz, max_bin), dtype=np.float32)
    np.add.at(azim_sum_tangential.T, bin_idx, v_tangential.T)

    with np.errstate(divide="ignore", invalid="ignore"):
        azim_mean_tangential = np.where(count_r > 0, azim_sum_tangential / count_r, np.nan)

    return azim_mean_radial.astype(np.float32), azim_mean_tangential.astype(np.float32)


def calculate_azimuthal_mean_wind10m(
    data_u, data_v, t, center_x_list, center_y_list, grid_handler, r_max=1000e3
):
    """
    10m風の方位角平均（動径・接線成分）を計算（オンデマンド）

    Parameters
    ----------
    data_u : memmap
        u風のメモリマップ (nt, ny, nx) - 2D
    data_v : memmap
        v風のメモリマップ (nt, ny, nx) - 2D
    t : int
        時刻インデックス
    center_x_list : ndarray
        台風中心のx座標リスト [m]
    center_y_list : ndarray
        台風中心のy座標リスト [m]
    grid_handler : GridHandler
        グリッドハンドラー
    r_max : float, optional
        最大半径 [m], デフォルト: 1000km

    Returns
    -------
    azim_mean_radial : ndarray (nr,)
        10m風の方位角平均動径風 [m/s]
    azim_mean_tangential : ndarray (nr,)
        10m風の方位角平均接線風 [m/s]

    Notes
    -----
    - データを保存せず、必要時に計算
    - ストレージ大幅節約（数GB〜数百GB）
    - azim_wind10m_calc.py のロジックを関数化
    - 2Dデータ（地表面10m）なので、鉛直方向なし
    """
    # 設定値を取得
    config = grid_handler.config
    cx = center_x_list[t]
    cy = center_y_list[t]

    # グリッド座標
    X, Y = grid_handler.X, grid_handler.Y

    # 中心からの距離と角度を計算
    dX = X - cx
    dY = Y - cy
    dX[dX > 0.5 * config.x_width] -= config.x_width
    dX[dX < -0.5 * config.x_width] += config.x_width

    theta = np.arctan2(dY, dX)
    R = np.sqrt(dX**2 + dY**2)

    # r_max 以内のマスク
    mask = R <= r_max
    valid_r = R[mask]

    # ビニング設定
    bin_idx = np.floor(valid_r / config.dx).astype(int)
    max_bin = int(np.floor(r_max / config.dx))
    bin_idx = np.clip(bin_idx, 0, max_bin - 1)

    count_r = np.bincount(bin_idx, minlength=max_bin)

    # データ読み込み（2D）
    data_u_t = data_u[t]
    data_v_t = data_v[t]

    valid_data_u = data_u_t[mask]
    valid_data_v = data_v_t[mask]

    # 動径・接線成分に変換
    v_radial = valid_data_u * np.cos(theta[mask]) + valid_data_v * np.sin(theta[mask])
    v_tangential = -valid_data_u * np.sin(theta[mask]) + valid_data_v * np.cos(theta[mask])

    # 方位角平均（動径風）
    azim_sum_radial = np.zeros(max_bin, dtype=np.float32)
    np.add.at(azim_sum_radial, bin_idx, v_radial)

    with np.errstate(divide="ignore", invalid="ignore"):
        azim_mean_radial = np.where(count_r > 0, azim_sum_radial / count_r, np.nan)

    # 方位角平均（接線風）
    azim_sum_tangential = np.zeros(max_bin, dtype=np.float32)
    np.add.at(azim_sum_tangential, bin_idx, v_tangential)

    with np.errstate(divide="ignore", invalid="ignore"):
        azim_mean_tangential = np.where(count_r > 0, azim_sum_tangential / count_r, np.nan)

    return azim_mean_radial.astype(np.float32), azim_mean_tangential.astype(np.float32)
