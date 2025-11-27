"""
風速に関する計算関数

相対風、動径風、接線風などの計算関数を提供します。
データを保存せず、必要時にその場で計算することでストレージを節約できます。
"""

import numpy as np


def calculate_center_velocity(center_x_list, center_y_list, dt_output):
    """
    台風中心の移動速度を計算

    Parameters
    ----------
    center_x_list : ndarray
        中心のx座標リスト [m]
    center_y_list : ndarray
        中心のy座標リスト [m]
    dt_output : float
        時間ステップ間隔 [s]

    Returns
    -------
    center_u : ndarray
        中心のx方向移動速度 [m/s]
    center_v : ndarray
        中心のy方向移動速度 [m/s]

    Notes
    -----
    - 中央差分を使用（両端は前方/後方差分）
    - center_u[t] = (center_x[t+1] - center_x[t-1]) / (2 * dt)
    """
    nt = len(center_x_list)

    # x方向の移動速度
    center_u = np.zeros(nt, dtype=np.float32)
    center_u[1:-1] = (center_x_list[2:] - center_x_list[:-2]) / (2 * dt_output)
    center_u[0] = (center_x_list[1] - center_x_list[0]) / dt_output
    center_u[-1] = (center_x_list[-1] - center_x_list[-2]) / dt_output

    # y方向の移動速度
    center_v = np.zeros(nt, dtype=np.float32)
    center_v[1:-1] = (center_y_list[2:] - center_y_list[:-2]) / (2 * dt_output)
    center_v[0] = (center_y_list[1] - center_y_list[0]) / dt_output
    center_v[-1] = (center_y_list[-1] - center_y_list[-2]) / dt_output

    return center_u, center_v


def calculate_relative_wind(u, v, center_u, center_v):
    """
    相対風を計算（移動座標系）

    u_rel = u - center_u
    v_rel = v - center_v

    Parameters
    ----------
    u : ndarray
        絶対座標系のu風 [m/s]
    v : ndarray
        絶対座標系のv風 [m/s]
    center_u : float or ndarray
        台風中心のx方向移動速度 [m/s]
    center_v : float or ndarray
        台風中心のy方向移動速度 [m/s]

    Returns
    -------
    u_rel : ndarray
        相対風のu成分 [m/s]
    v_rel : ndarray
        相対風のv成分 [m/s]

    Notes
    -----
    - データを保存せず、必要時に計算
    - ストレージ節約のため
    """
    u_rel = (u - center_u).astype(np.float32)
    v_rel = (v - center_v).astype(np.float32)

    return u_rel, v_rel


def calculate_relative_wind_from_memmap(data_u, data_v, t, center_u_list, center_v_list):
    """
    メモリマップから相対風を計算

    Parameters
    ----------
    data_u : memmap
        u風のメモリマップ (nt, nz, ny, nx)
    data_v : memmap
        v風のメモリマップ (nt, nz, ny, nx)
    t : int
        時刻インデックス
    center_u_list : ndarray
        台風中心のx方向移動速度リスト [m/s]
    center_v_list : ndarray
        台風中心のy方向移動速度リスト [m/s]

    Returns
    -------
    u_rel : ndarray (nz, ny, nx)
        相対風のu成分 [m/s]
    v_rel : ndarray (nz, ny, nx)
        相対風のv成分 [m/s]
    """
    u = data_u[t]
    v = data_v[t]

    return calculate_relative_wind(u, v, center_u_list[t], center_v_list[t])


def calculate_radial_tangential_wind(u, v, cx, cy, grid_handler):
    """
    直交座標系の風を動径・接線成分に変換

    Parameters
    ----------
    u : ndarray
        u風 [m/s]
    v : ndarray
        v風 [m/s]
    cx : float
        台風中心のx座標 [m]
    cy : float
        台風中心のy座標 [m]
    grid_handler : GridHandler
        グリッドハンドラー

    Returns
    -------
    v_radial : ndarray
        動径風（中心向き正） [m/s]
    v_tangential : ndarray
        接線風（反時計回り正） [m/s]

    Notes
    -----
    - GridHandler.uv_to_radial_tangential() を使用
    - データを保存せず、必要時に計算
    """
    v_radial, v_tangential = grid_handler.uv_to_radial_tangential(u, v, cx, cy)
    return v_radial.astype(np.float32), v_tangential.astype(np.float32)


def calculate_relative_wind_radial_tangential(
    data_u, data_v, t, center_x_list, center_y_list, center_u_list, center_v_list, grid_handler
):
    """
    相対風の動径・接線成分を一度に計算（オンデマンド）

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

    Returns
    -------
    v_radial : ndarray (nz, ny, nx)
        相対風の動径成分 [m/s]
    v_tangential : ndarray (nz, ny, nx)
        相対風の接線成分 [m/s]

    Notes
    -----
    - 相対風計算と極座標変換を一度に実行
    - 中間データ（relative_u, relative_v）を保存不要
    - ストレージ大幅節約
    """
    # 1. 相対風を計算
    u_rel, v_rel = calculate_relative_wind_from_memmap(
        data_u, data_v, t, center_u_list, center_v_list
    )

    # 2. 極座標成分に変換
    v_radial, v_tangential = calculate_radial_tangential_wind(
        u_rel, v_rel, center_x_list[t], center_y_list[t], grid_handler
    )

    return v_radial, v_tangential


def calculate_absolute_wind_radial_tangential(
    data_u, data_v, t, center_x_list, center_y_list, grid_handler
):
    """
    絶対風の動径・接線成分を計算（オンデマンド）

    台風の移動を考慮しない絶対座標系での風の極座標成分

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

    Returns
    -------
    v_radial : ndarray (nz, ny, nx)
        絶対風の動径成分 [m/s]
    v_tangential : ndarray (nz, ny, nx)
        絶対風の接線成分 [m/s]

    Notes
    -----
    - メモリマップから直接読み込んで極座標変換
    - 中間データ（wind_radial, wind_tangential）を保存不要
    - ストレージ節約
    """
    # メモリマップからデータを取得
    u = data_u[t]
    v = data_v[t]

    # 極座標成分に変換
    v_radial, v_tangential = calculate_radial_tangential_wind(
        u, v, center_x_list[t], center_y_list[t], grid_handler
    )

    return v_radial, v_tangential
