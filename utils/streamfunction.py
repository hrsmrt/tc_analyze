"""
流線関数の計算関数

データを保存せず、必要時にその場で計算する関数を提供します。
ストレージを大幅に節約できます。
"""

import numpy as np


def frac_roll_x_fft(row, shift):
    """
    1D row を周期境界で実数 shift (グリッド単位)だけ平行移動（サブピクセル対応）

    Parameters
    ----------
    row : ndarray
        1次元配列
    shift : float
        シフト量（グリッド単位）

    Returns
    -------
    ndarray
        シフトされた配列
    """
    fft_result = np.fft.fft(row)
    k = np.fft.fftfreq(row.size)
    phase = np.exp(-2j * np.pi * k * shift)
    return np.fft.ifft(fft_result * phase).real


def poisson_periodic_fft(rhs, lx, ly):
    """
    ∇²φ = rhs を 2D 周期境界で FFT 解

    Parameters
    ----------
    rhs : ndarray (ny, nx)
        右辺（渦度など）
    lx : float
        x方向のドメインサイズ
    ly : float
        y方向のドメインサイズ

    Returns
    -------
    phi : ndarray (ny, nx)
        解（流線関数など）
    """
    ny, nx = rhs.shape
    kx = 2 * np.pi * np.fft.fftfreq(nx, d=lx / nx)[None, :]  # (1,nx)
    ky = 2 * np.pi * np.fft.fftfreq(ny, d=ly / ny)[:, None]  # (ny,1)
    k2 = kx**2 + ky**2
    k2[0, 0] = np.inf  # 定数モードは任意 → 0 に固定
    rhs_fft = np.fft.fft2(rhs)
    phi_hat = rhs_fft / (-k2)
    phi_hat[0, 0] = 0.0
    return np.fft.ifft2(phi_hat).real


def calculate_streamfunction(zeta, dx, dy):
    """
    渦度から流線関数を計算

    ∇²ψ = -ζ を解く（周期境界条件）

    Parameters
    ----------
    zeta : ndarray (ny, nx) or (nz, ny, nx)
        渦度場
    dx : float
        x方向の格子間隔
    dy : float
        y方向の格子間隔

    Returns
    -------
    psi : ndarray
        流線関数（zetaと同じ形状）

    Notes
    -----
    - 3Dデータの場合は各z方向に独立に計算
    - データを保存せず、必要時に計算
    - ストレージ節約のため
    """
    if zeta.ndim == 2:
        # 2Dデータ
        ny, nx = zeta.shape
        lx, ly = nx * dx, ny * dy
        psi = poisson_periodic_fft(-zeta, lx, ly)
        return psi.astype(np.float32)

    elif zeta.ndim == 3:
        # 3Dデータ: 各z方向に独立に計算
        nz, ny, nx = zeta.shape
        lx, ly = nx * dx, ny * dy
        psi = np.zeros_like(zeta, dtype=np.float32)

        for z in range(nz):
            psi[z] = poisson_periodic_fft(-zeta[z], lx, ly)

        return psi

    else:
        raise ValueError(f"zeta must be 2D or 3D, got shape {zeta.shape}")


def calculate_streamfunction_from_memmap(data_vorticity_z, t, dx, dy):
    """
    メモリマップから流線関数を計算

    Parameters
    ----------
    data_vorticity_z : memmap or ndarray
        渦度データ (nt, nz, ny, nx)
    t : int
        時刻インデックス
    dx : float
        x方向の格子間隔
    dy : float
        y方向の格子間隔

    Returns
    -------
    psi : ndarray (nz, ny, nx)
        流線関数
    """
    zeta = data_vorticity_z[t]
    return calculate_streamfunction(zeta, dx, dy)
