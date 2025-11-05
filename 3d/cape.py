# nohup python $WORK/tc_analyze/cape.py &

# CAPEの計算
# 参考: Holton演習、Satoh(2014)p403
# モデル最下層(z=33m)のパーセルを考える
# LCL(lifting condensation level)まで: 乾燥断熱減率
# LCL〜LFC(level of free convection)〜ZT(浮力が0になる高度)まで: 湿潤断熱減率

import os
import sys
# 実行ファイル（この.pyファイル）を基準に相対パスを指定
script_dir = os.path.dirname(os.path.abspath(__file__))
target_path = os.path.join(script_dir, '../../module')
sys.path.append(target_path)
import numpy as np
import matplotlib.pyplot as plt
import json

# 定数
cp = 1004  # J/K/kg, 定圧比熱
L = 2.50e6 # J/kg,   凝結熱
Rd = 287   # J/K/kg, 乾燥大気の気体定数
Rv = 461   # J/K/kg, 水蒸気の気体定数
g = 9.81   # m/s^2, 重力定数

# ファイルを開いてJSONを読み込む
with open('setting.json', 'r', encoding='utf-8') as f:
    setting = json.load(f)
glevel = setting['glevel']
nt = setting['nt']
dt = setting['dt_output']
dt_hour = int(dt / 3600)
triangle_size = setting['triangle_size']
nx = 2 ** glevel
ny = 2 ** glevel
nz = 74
x_width = triangle_size
y_width = triangle_size * 0.5 * 3.0 ** 0.5
dx = x_width / nx
dy = y_width / ny
input_folder = setting['input_folder']

time_list = [t * dt_hour for t in range(nt)]

vgrid = np.loadtxt(script_dir + "/../database/vgrid/vgrid_c74.txt")

out_dir = f"./fig/cape/"
os.makedirs(out_dir,exist_ok=True)
os.makedirs(f"{out_dir}parcel_T",exist_ok=True)
os.makedirs(f"{out_dir}parcel_rho",exist_ok=True)

# 環境場
T_env = np.zeros(nz)
p_env = np.zeros(nz)
rho_env = np.zeros(nz)
rh_env = np.zeros(nz)

def main():
    cape_evol = np.zeros(nt)
    for t in range(nt):
        count = nx * ny * nz
        offset = count * t * 4
        data = np.fromfile(f"{input_folder}ms_tem.grd",dtype=">f4",count=count,offset=offset)
        data = data.reshape(nz,ny,nx).T
        T_env = data.mean(axis=(0,1))
        data = np.fromfile(f"{input_folder}ms_pres.grd",dtype=">f4",count=count,offset=offset)
        data = data.reshape(nz,ny,nx).T
        p_env = data.mean(axis=(0,1))
        data = np.fromfile(f"{input_folder}ms_rho.grd",dtype=">f4",count=count,offset=offset)
        data = data.reshape(nz,ny,nx).T
        ms_rho = data.mean(axis=(0,1))
        data = np.fromfile(f"{input_folder}ms_rh.grd",dtype=">f4",count=count,offset=offset)
        data = data.reshape(nz,ny,nx).T
        rh_env = data.mean(axis=(0,1))
        T = calc_T(t,T_env[0],p_env, rh_env[0])
        rho_env = p_env / Rd / T_env
        rho = p_env / Rd / T
        lfc = False
        cape = 0
        for z in range(1,nz):
            b = (rho[z]+rho[z-1]-rho_env[z]-rho_env[z-1])/(rho_env[z]+rho_env[z-1]) * g
            print(z, vgrid[z],b , rho[z],rho_env[z])
            if lfc == False and rho[z] < rho_env[z]:
                lfc = True
            if lfc == True and rho[z] > rho_env[z]:
                break
            cape -= b * (vgrid[z]-vgrid[z-1])
        cape_evol[t] = cape
        print(f" CAPE: {cape:.4f} J/kg")

        # Temperature
        fig, ax = plt.subplots(figsize=(10, 6))
        plt.rcParams['xtick.direction'] = 'in'
        plt.rcParams['ytick.direction'] = 'in'
        plt.grid(True)
        ax.plot(T_env,vgrid*1e-3,label="Environment")
        ax.plot(T,vgrid*1e-3,label="Percel")
        ax.set_ylabel('z [km]')
        ax.set_xlabel('Temperature [K]')
        ax.set_title(f't={time_list[t]} hour')
        plt.grid()
        plt.legend()
        plt.savefig(os.path.join(out_dir, f"parcel_T/t{time_list[t]:04d}h.png"),dpi=300,bbox_inches="tight")
        plt.close()

        # Density
        fig, ax = plt.subplots(figsize=(10, 6))
        plt.rcParams['xtick.direction'] = 'in'
        plt.rcParams['ytick.direction'] = 'in'
        plt.grid(True)
        ax.plot(rho_env-ms_rho,vgrid*1e-3,label="Environment(rho_env-ms_rho)")
        ax.plot(rho-ms_rho,vgrid*1e-3,label="Percel-ms_rho")
        ax.set_ylabel('z [km]')
        ax.set_xlabel('Density [kg/m^3]')
        ax.set_title(f't={time_list[t]} hour')
        plt.grid()
        plt.legend()
        plt.savefig(os.path.join(out_dir, f"parcel_rho/t{time_list[t]:04d}h.png"),dpi=300,bbox_inches="tight")
        plt.close()

    plt.rcParams['xtick.direction'] = 'in'
    plt.rcParams['ytick.direction'] = 'in'
    plt.grid(True)
    plt.plot(time_list,cape_evol)
    plt.ylim([0,5000])
    plt.title("CAPE")
    plt.xlabel("Time [hour]")
    plt.ylabel("CAPE [J/kg]")
    plt.grid(False)
    plt.savefig(f"{out_dir}cape.png",dpi=300,bbox_inches="tight",pad_inches=0.05)
    plt.close()

# Tetensの式。初めだけ使う
def tetens(T):
    es0 = 6.11e2 # Pa
    T0 = 273.15 # K
    es = es0*np.exp(17.27*(T-T0)/(T-35.86))
    return es

def calc_T(t,T_zb,p_env,rh_zb):
    # パーセル
    T  = np.zeros(nz) # K, 気温
    pd = np.zeros(nz) # Pa 乾燥空気の圧力
    e  = np.zeros(nz) # Pa 水蒸気の圧力
    es = np.zeros(nz) # Pa 飽和水蒸気圧
    T[0] = T_zb
    es[0] = tetens(T[0])
    e[0] = rh_zb * es[0]
    pd[0] = p_env[0] - e[0]
    e_par_p = e[0]/p_env[0]

    houwa = False
    for i in range(1,nz):
        alpha = Rv*T[i-1]/p_env[i-1]
        if houwa == False: # 飽和するまで
            T[i] = T[i-1] + alpha/cp*(p_env[i]-p_env[i-1])
            e[i] = e_par_p*p_env[i]
            es[i] = es[i-1]+L/(Rv*T[i]**2)*es[i-1]*(T[i]-T[i-1])
            if e[i] > es[i]:
                houwa = True
                print(f"{time_list[t]}h, 高度{vgrid[i]/1000}kmで飽和(e={e[i]/100:.2f}hPa,es={es[i]/100:.2f}hPa)",end="")
        else: # 飽和したのち
            # 計算に必要な量を求める
            pd = p_env[i-1]-es[i-1]
            rho = pd/(Rd*T[i-1])
            alpha = 1/rho
            A = L*es[i-1]/(cp*rho*Rv*T[i-1]**2)*(L/(Rv*T[i-1])-1)
            
            # 次の高度の温度、圧力を求める
            T[i] = T[i-1] + 1/(1+A)*alpha/cp*(p_env[i]-p_env[i-1])
            es[i] = es[i-1]+L/(Rv*T[i]**2)*es[i-1]*(T[i]-T[i-1])
            e[i] = es[i]
    return T

if __name__ == "__main__":
    main()
