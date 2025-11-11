# python $WORK/tc_analyze/center/find_lows.py
import numpy as np
import numpy as np
from scipy.ndimage import gaussian_filter
from skimage.feature import peak_local_max
import pickle

script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(script_dir, ".."))

# P: 2D SLP [Pa] or [hPa], lat x lon (or y x x)
# land_sea_mask: 1=ocean, 0=land (任意)
# dx_km, dy_km: 格子間隔 [km]（等間隔格子なら）
# min_sep_km: 低圧中心の最小分離距離
# thr_Pa: 極小の上限（例：101000Pa 以下など）

from utils.config import AnalysisConfig

config = AnalysisConfig()

    mode="r",
    shape=(config.nt, config.ny, config.nx)
)

def main():
    lows_all = []
    for t in range(config.nt):
        P = data_memmap[t]
        lows = find_lows_peakmax(P,thr_Pa=100500,dx_km=config.dx*1e-3,dy_km=config.dy*1e-3,min_sep_km=200)
        print(f"Time {t}: Found {len(lows)} low pressure centers")
        lows_all.append(lows)
    with open("./data/ss_slp_lows.pkl", "wb") as f:
        pickle.dump(lows_all, f)

def find_lows_peakmax(P, land_sea_mask=None, sigma=1.0, min_sep_km=200, 
                      dx_km=25, dy_km=25, thr_Pa=None):
    # 1) 平滑化（sigmaはグリッド単位）
    Ps = gaussian_filter(P, sigma=sigma, mode='nearest')

    # 2) しきい値マスク（任意）
    valid = np.isfinite(Ps)
    if land_sea_mask is not None:
        valid &= (land_sea_mask == 1)
    if thr_Pa is not None:
        valid &= (Ps <= thr_Pa)
    # 3) min_distance をグリッドに換算（等方近似）
    #   斜交格子や緯度経度の非等間隔は後述の注意を参照
    approx_dx = (dx_km + dy_km) * 0.5
    min_dist = max(1, int(np.round(min_sep_km / approx_dx)))
    # 4) 負圧にして極大探索
    coords = peak_local_max(-Ps, min_distance=min_dist, labels=valid.astype(np.uint8))
    # coords: [[i,j], ...]
    lows = []
    for (i, j) in coords:
        lows.append({
            "iy": int(i), "ix": int(j),
            "p": float(Ps[i, j])  # 平滑後の値
        })
    # 圧力の小さい順に並べる
    #lows.sort(key=lambda d: d["p"])
    return lows

if __name__ == "__main__":
    main()
