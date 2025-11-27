"""
方位角平均計算関数

データを保存せず、必要時にその場で計算することでストレージを節約できます。
"""

import numpy as np

from .basic import potential_temperature
from .thermodynamics import calculate_theta_e


def calculate_azimuthal_mean_3d(
    data, t, center_x_list, center_y_list, grid_handler, r_max=1000e3
):
    """
    3Dデータの方位角平均を計算（汎用版）

    Parameters
    ----------
    data : memmap or ndarray
        3Dデータのメモリマップまたは配列 (nt, nz, ny, nx)
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
    azim_mean : ndarray (nz, nr)
        方位角平均データ

    Notes
    -----
    - データを保存せず、必要時に計算
    - ストレージ大幅節約（数GB〜数百GB）
    - azim_3d_calc.py のロジックを関数化
    """
    # 設定値を取得
    config = grid_handler.config
    cx = center_x_list[t]
    cy = center_y_list[t]

    # グリッド座標
    X, Y = grid_handler.X, grid_handler.Y

    # 中心からの距離を計算
    R = np.sqrt((X - cx) ** 2 + (Y - cy) ** 2)

    # r_max 以内のマスク
    mask = R <= r_max
    valid_r = R[mask]

    # ビニング設定
    bin_idx = np.floor(valid_r / config.dx).astype(int)
    max_bin = int(np.floor(r_max / config.dx))
    bin_idx = np.clip(bin_idx, 0, max_bin - 1)

    count_r = np.bincount(bin_idx, minlength=max_bin)

    # データ読み込み
    data_t = data[t]
    valid_data = data_t[:, mask]

    # 方位角平均
    azim_sum = np.zeros((config.nz, max_bin), dtype=np.float32)
    np.add.at(azim_sum.T, bin_idx, valid_data.T)

    with np.errstate(divide="ignore", invalid="ignore"):
        azim_mean = np.where(count_r > 0, azim_sum / count_r, np.nan)

    return azim_mean.astype(np.float32)


def calculate_azimuthal_mean_2d(
    data, t, center_x_list, center_y_list, grid_handler, r_max=1000e3
):
    """
    2Dデータの方位角平均を計算（汎用版）

    Parameters
    ----------
    data : memmap or ndarray
        2Dデータのメモリマップまたは配列 (nt, ny, nx)
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
    azim_mean : ndarray (nr,)
        方位角平均データ

    Notes
    -----
    - データを保存せず、必要時に計算
    - ストレージ大幅節約（数GB〜数百GB）
    - azim_2d_calc.py のロジックを関数化
    """
    # 設定値を取得
    config = grid_handler.config
    cx = center_x_list[t]
    cy = center_y_list[t]

    # グリッド座標
    X, Y = grid_handler.X, grid_handler.Y

    # 中心からの距離を計算
    R = np.sqrt((X - cx) ** 2 + (Y - cy) ** 2)

    # r_max 以内のマスク
    mask = R <= r_max
    valid_r = R[mask]

    # ビニング設定
    bin_idx = np.floor(valid_r / config.dx).astype(int)
    max_bin = int(np.floor(r_max / config.dx))
    bin_idx = np.clip(bin_idx, 0, max_bin - 1)

    count_r = np.bincount(bin_idx, minlength=max_bin)

    # データ読み込み
    data_t = data[t]
    valid_data = data_t[mask]

    # 方位角平均
    data_r = np.bincount(bin_idx, weights=valid_data, minlength=max_bin)

    with np.errstate(divide="ignore", invalid="ignore"):
        azim_mean = np.where(count_r > 0, data_r / count_r, np.nan)

    return azim_mean.astype(np.float32)


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

    # 周期境界条件を考慮した距離計算（領域端に近い場合）
    cx2 = cx - config.x_width
    cy2 = cy - config.y_width
    dX2 = X - cx2
    dY2 = Y - cy2
    dX2[dX2 > 0.5 * config.x_width] -= config.x_width
    dX2[dX2 < -0.5 * config.x_width] += config.x_width
    R2 = np.sqrt(dX2**2 + dY2**2)
    R = np.minimum(R, R2)

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

def calculate_azimuthal_mean_theta(
    data_tem, data_pres, t, center_x_list, center_y_list, grid_handler, r_max=1000e3
):
    """
    温位の方位角平均を計算（オンデマンド）

    θ = T(Ps/P)^(Rd/Cp)

    Parameters
    ----------
    data_tem : memmap
        気温のメモリマップ (nt, nz, ny, nx)
    data_pres : memmap
        気圧のメモリマップ (nt, nz, ny, nx)
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
    azim_theta : ndarray (nz, nr)
        温位の方位角平均 [K]

    Notes
    -----
    - 方位角平均された気温・気圧から温位を計算
    - 中間データ（azim tem, azim pres）を保存不要
    - ストレージ大幅節約
    - 物理定数はutils.basicから取得
    """
    # 方位角平均を計算
    azim_tem = calculate_azimuthal_mean_3d(data_tem, t, center_x_list, center_y_list, grid_handler, r_max)
    azim_pres = calculate_azimuthal_mean_3d(data_pres, t, center_x_list, center_y_list, grid_handler, r_max)

    # 温位を計算（basic.potential_temperature を使用）
    theta = potential_temperature(azim_tem, azim_pres)

    return theta.astype(np.float32)


def calculate_azimuthal_mean_theta_e(
    data_tem, data_pres, data_qv, t, center_x_list, center_y_list, grid_handler, r_max=1000e3
):
    """
    相当温位の方位角平均を計算（オンデマンド）

    θ_e = T(Ps/P)^(Rd/Cp) * exp(Lv*rv/(Cp*T))

    Parameters
    ----------
    data_tem : memmap
        気温のメモリマップ (nt, nz, ny, nx)
    data_pres : memmap
        気圧のメモリマップ (nt, nz, ny, nx)
    data_qv : memmap
        比湿のメモリマップ (nt, nz, ny, nx)
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
    azim_theta_e : ndarray (nz, nr)
        相当温位の方位角平均 [K]

    Notes
    -----
    - 方位角平均された気温・気圧・比湿から相当温位を計算
    - 中間データ（azim tem, azim pres, azim qv）を保存不要
    - ストレージ大幅節約
    - 物理定数はutils.basicから取得
    """
    # 方位角平均を計算
    azim_tem = calculate_azimuthal_mean_3d(data_tem, t, center_x_list, center_y_list, grid_handler, r_max)
    azim_pres = calculate_azimuthal_mean_3d(data_pres, t, center_x_list, center_y_list, grid_handler, r_max)
    azim_qv = calculate_azimuthal_mean_3d(data_qv, t, center_x_list, center_y_list, grid_handler, r_max)

    # 相当温位を計算（thermodynamics.calculate_theta_e を使用）
    theta_e = calculate_theta_e(azim_tem, azim_pres, azim_qv)

    return theta_e.astype(np.float32)


def calculate_azimuthal_mean_momentum(
    azim_tangential, config, r_max=1000e3
):
    """
    角運動量の方位角平均を計算（オンデマンド）

    M = rv + f r^2/2

    Parameters
    ----------
    azim_tangential : ndarray (nz, nr)
        方位角平均接線風 [m/s]
    config : AnalysisConfig
        設定オブジェクト
    r_max : float, optional
        最大半径 [m], デフォルト: 1000km

    Returns
    -------
    azim_momentum : ndarray (nz, nr)
        角運動量の方位角平均 [m^2/s]

    Notes
    -----
    - 方位角平均接線風から角運動量を計算
    - 中間データを保存不要
    """
    # データの形状から半径方向のビン数を取得
    nr = azim_tangential.shape[1]
    rgrid = (np.arange(nr) + 0.5) * config.dx

    # 角運動量 M = rv + f r^2/2
    momentum = rgrid * azim_tangential + 0.5 * config.f * rgrid**2

    return momentum.astype(np.float32)
