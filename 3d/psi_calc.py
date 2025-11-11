# python $WORK/tc_analyze/3d/psi_calc.py
# 流線関数の計算

import os
import numpy as np
from joblib import Parallel, delayed

from utils.config import AnalysisConfig

config = AnalysisConfig()

folder = f"./data/3d/psi/"
os.makedirs(folder, exist_ok=True)

def process_t(t):
    data = np.load(f"./data/3d/vorticity_z/vor_t{str(t).zfill(3)}.npy")
    psi = np.zeros((config.nz, config.ny, config.nx), dtype=np.float32)
    for z in range(config.nz):
        psi[z] = streamfunction_twisted(data[z], config.dx, config.dy)
    np.save(f"{folder}psi_t{str(t).zfill(3)}.npy", psi)
    print(f"t: {t} psi calc done")

def frac_roll_x_fft(row, shift):
    """1D row を周期境界で実数 shift (グリッド単位)だけ平行移動（サブピクセル対応）"""
    nx = row.size
    R = np.fft.fft(row)
    k = np.fft.fftfreq(nx)                 # 0,1/nx,...,-1/nx
    phase = np.exp(-2j*np.pi*k*shift)      # 位相乗算
    return np.fft.ifft(R * phase).real

def unshear(arr, alpha):
    """2D (ny,nx) の各行 j を x に +j*alpha だけ戻す（ねじれをほどく）"""
    ny, nx = arr.shape
    out = np.empty_like(arr, dtype=float)
    for j in range(ny):
        out[j] = frac_roll_x_fft(arr[j], j*alpha)
    return out

def reshear(arr, alpha):
    """unshear の逆（各行 j を x に -j*alpha だけ進める）"""
    ny, nx = arr.shape
    out = np.empty_like(arr, dtype=float)
    for j in range(ny):
        out[j] = frac_roll_x_fft(arr[j], -j*alpha)
    return out

def poisson_periodic_fft(rhs, Lx, Ly):
    """∇²φ = rhs を 2D 周期で FFT 解。Lx=nx*dx, Ly=ny*dy"""
    ny, nx = rhs.shape
    kx = 2*np.pi*np.fft.fftfreq(nx, d=Lx/nx)[None,:]  # (1,nx)
    ky = 2*np.pi*np.fft.fftfreq(ny, d=Ly/ny)[:,None]  # (ny,1)
    k2 = kx**2 + ky**2
    k2[0,0] = np.inf  # 定数モードは任意 → 0 に固定
    RHS = np.fft.fft2(rhs)
    phi_hat = RHS / (-k2)
    phi_hat[0,0] = 0.0
    return np.fft.ifft2(phi_hat).real

def streamfunction_twisted(zeta, dx, dy):
    """
    ねじれ周期（上下をまたぐと x が s_total グリッドずれ）の直交格子で ψ を計算
    zeta: 2D 渦度（ny,nx）
    dx,dy: 格子間隔
    s_total: 上下境界をまたぐときの x 方向総ずれ（グリッド数, 例 nx//2）
    """
    ny, nx = zeta.shape
    Lx, Ly = nx*dx, ny*dy

    # 2) 直交周期で Poisson
    psi = poisson_periodic_fft(-zeta, Lx, Ly)
    return psi

Parallel(n_jobs=config.n_jobs)(delayed(process_t)(t) for t in range(config.t_start, config.t_end))
