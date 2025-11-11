"""
プロット共通関数モジュール

プロット関連の設定、カスタムカラーマップ、変数ごとのプロット設定などを提供します。
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
from typing import Dict, Any, Optional, Tuple
import sys


def create_custom_colormap(
    base_cmap: str = "rainbow",
    n_white_colors: int = 3,
    n_colors: int = 256
) -> ListedColormap:
    """
    カスタムカラーマップを作成（下部を白に変更）

    Args:
        base_cmap (str): ベースとなるカラーマップ名
        n_white_colors (int): 白に変更する色の数
        n_colors (int): カラーマップの総色数

    Returns:
        ListedColormap: カスタムカラーマップ
    """
    original_cmap = plt.cm.get_cmap(base_cmap)
    colors = original_cmap(np.linspace(0, 1, n_colors))
    colors[:n_white_colors] = [1, 1, 1, 1]  # 白に変更
    return ListedColormap(colors)


def parse_style_argument(arg_index: int = 2) -> Optional[str]:
    """
    コマンドライン引数からmatplotlibスタイルシートを解析

    Args:
        arg_index (int): スタイル引数のインデックス (デフォルト: 2)

    Returns:
        str or None: スタイルシート名、またはNone
    """
    if len(sys.argv) > arg_index:
        mpl_style_sheet = sys.argv[arg_index]
        print(f"Using style: {mpl_style_sheet}")
        return mpl_style_sheet
    else:
        print("No style sheet specified, using default.")
        return None


# カスタムカラーマップのプリセット
CUSTOM_RAINBOW = create_custom_colormap("rainbow", 3)
CUSTOM_RAINBOW_20 = create_custom_colormap("rainbow", 20)


class PlotConfig:
    """
    変数ごとのプロット設定を管理するクラス
    """

    # 変数ごとのプロット設定
    VARIABLE_CONFIGS = {
        # アルベド
        "sa_albedo": {
            "levels": np.arange(0, 1.1, 0.1),
            "cmap": "Greys_r",
            "title": "アルベド",
            "extend": "neither",
        },
        # 雲被覆率
        "sa_cld_frac": {
            "levels": np.arange(0, 1.1, 0.1),
            "cmap": "Blues_r",
            "title": "雲被覆率",
            "extend": "both",
        },
        # 雲氷量
        "sa_cldi": {
            "levels": np.arange(0, 10, 0.1),
            "cmap": CUSTOM_RAINBOW,
            "title": r"鉛直積算雲氷量 [$\mathrm{kg/m^2}$]",
            "extend": "both",
        },
        "ss_cldi": {
            "levels": np.arange(0, 10, 0.1),
            "cmap": CUSTOM_RAINBOW,
            "title": r"鉛直積算雲氷量 [$\mathrm{kg/m^2}$]",
            "extend": "both",
        },
        # 雲水量
        "sa_cldw": {
            "levels": np.arange(0, 10, 0.1),
            "cmap": CUSTOM_RAINBOW,
            "title": r"鉛直積算雲水量 [$\mathrm{kg/m^2}$]",
            "extend": "both",
        },
        "ss_cldw": {
            "levels": np.arange(0, 10, 0.1),
            "cmap": CUSTOM_RAINBOW,
            "title": r"鉛直積算雲水量 [$\mathrm{kg/m^2}$]",
            "extend": "both",
        },
        # 海面蒸発量（data * 3600が必要）
        "sa_evap": {
            "levels": np.arange(0, 1, 0.1),
            "cmap": CUSTOM_RAINBOW,
            "title": r"海面蒸発量 [$\mathrm{kg/m^2/h}$]",
            "extend": "both",
            "data_transform": lambda data: data * 3600,
        },
        # 潜熱流束
        "sa_lh_sfc": {
            "levels": np.arange(0, 500, 10),
            "cmap": CUSTOM_RAINBOW,
            "title": r"潜熱流束 [$\mathrm{W/m^2}$]",
            "extend": "both",
        },
        # 顕熱流束
        "sa_sh_sfc": {
            "levels": np.arange(0, 100, 5),
            "cmap": CUSTOM_RAINBOW,
            "title": r"顕熱流束 [$\mathrm{W/m^2}$]",
            "extend": "both",
        },
        # 西風
        "sa_u10m": {
            "levels": np.arange(-50, 55, 5),
            "cmap": "bwr",
            "title": r"西風 [$\mathrm{m/s}$]",
            "extend": "both",
        },
        "ss_u10m": {
            "levels": np.arange(-50, 55, 5),
            "cmap": "bwr",
            "title": r"西風 [$\mathrm{m/s}$]",
            "extend": "both",
        },
        # 南風
        "sa_v10m": {
            "levels": np.arange(-50, 55, 5),
            "cmap": "bwr",
            "title": r"南風 [$\mathrm{m/s}$]",
            "extend": "both",
        },
        "ss_v10m": {
            "levels": np.arange(-50, 55, 5),
            "cmap": "bwr",
            "title": r"南風 [$\mathrm{m/s}$]",
            "extend": "both",
        },
        # 2m温度
        "sa_t2m": {
            "levels": np.arange(297, 303.1, 0.5),
            "cmap": "rainbow",
            "title": r"2m温度 [$\mathrm{K}$]",
            "extend": "both",
        },
        "ss_t2m": {
            "levels": np.arange(297, 303.1, 0.5),
            "cmap": "rainbow",
            "title": r"2m温度 [$\mathrm{K}$]",
            "extend": "both",
        },
        # 2m比湿
        "sa_q2m": {
            "levels": np.arange(0.015, 0.026, 0.001),
            "cmap": "rainbow",
            "title": r"2m比湿 [$\mathrm{kg/kg}$]",
            "extend": "both",
        },
        "ss_q2m": {
            "levels": np.arange(0.015, 0.026, 0.001),
            "cmap": "rainbow",
            "title": r"2m比湿 [$\mathrm{kg/kg}$]",
            "extend": "both",
        },
        # 可降水量
        "sa_vap_atm": {
            "levels": np.arange(50, 81, 5),
            "cmap": "rainbow",
            "title": r"可降水量 [$\mathrm{kg/m^2}$]",
            "extend": "both",
        },
        "ss_vap_atm": {
            "levels": np.arange(50, 81, 5),
            "cmap": "rainbow",
            "title": r"可降水量 [$\mathrm{kg/m^2}$]",
            "extend": "both",
        },
        # 海面気圧
        "ss_slp": {
            "levels": np.arange(960, 1012, 2),
            "cmap": "rainbow",
            "title": r"海面気圧 [$\mathrm{hPa}$]",
            "extend": "both",
        },
        # 降水量
        "sa_prcp": {
            "levels": np.arange(0, 100, 5),
            "cmap": CUSTOM_RAINBOW,
            "title": r"降水量 [$\mathrm{mm/h}$]",
            "extend": "both",
        },
        "ss_prcp": {
            "levels": np.arange(0, 100, 5),
            "cmap": CUSTOM_RAINBOW,
            "title": r"降水量 [$\mathrm{mm/h}$]",
            "extend": "both",
        },
    }

    @classmethod
    def get_config(cls, varname: str) -> Dict[str, Any]:
        """
        変数名に対応するプロット設定を取得

        Args:
            varname (str): 変数名

        Returns:
            dict: プロット設定

        Raises:
            ValueError: 未定義の変数名の場合
        """
        if varname not in cls.VARIABLE_CONFIGS:
            raise ValueError(
                f"変数 '{varname}' のプロット設定が定義されていません。\n"
                f"利用可能な変数: {', '.join(cls.VARIABLE_CONFIGS.keys())}"
            )
        return cls.VARIABLE_CONFIGS[varname].copy()

    @classmethod
    def create_contourf(
        cls,
        ax,
        X: np.ndarray,
        Y: np.ndarray,
        data: np.ndarray,
        varname: str,
        time_hour: Optional[int] = None,
        **kwargs
    ) -> Tuple[Any, str]:
        """
        変数名に基づいてcontourfプロットを作成

        Args:
            ax: matplotlib axes オブジェクト
            X (np.ndarray): X座標メッシュグリッド
            Y (np.ndarray): Y座標メッシュグリッド
            data (np.ndarray): プロットするデータ
            varname (str): 変数名
            time_hour (int, optional): 時刻（時間）
            **kwargs: 追加のcontourf引数（設定を上書き）

        Returns:
            tuple: (contourf オブジェクト, タイトル文字列)
        """
        config = cls.get_config(varname)

        # データ変換が必要な場合
        if "data_transform" in config:
            data = config["data_transform"](data)

        # プロット設定をマージ
        plot_kwargs = {
            "levels": config["levels"],
            "cmap": config["cmap"],
            "extend": config.get("extend", "neither"),
        }
        plot_kwargs.update(kwargs)

        # プロット実行
        contourf_obj = ax.contourf(X, Y, data, **plot_kwargs)

        # タイトル作成
        title = config["title"]
        if time_hour is not None:
            title = f"{title} t = {time_hour}h"

        return contourf_obj, title

    @classmethod
    def add_variable(
        cls,
        varname: str,
        levels: np.ndarray,
        cmap: str,
        title: str,
        extend: str = "neither",
        data_transform = None,
    ) -> None:
        """
        新しい変数のプロット設定を追加

        Args:
            varname (str): 変数名
            levels (np.ndarray): コンターレベル
            cmap (str): カラーマップ名
            title (str): プロットタイトル
            extend (str): 拡張設定
            data_transform (callable, optional): データ変換関数
        """
        config = {
            "levels": levels,
            "cmap": cmap,
            "title": title,
            "extend": extend,
        }
        if data_transform is not None:
            config["data_transform"] = data_transform

        cls.VARIABLE_CONFIGS[varname] = config


def setup_plot_style(style: Optional[str] = None) -> None:
    """
    matplotlibのスタイルを設定

    Args:
        style (str, optional): スタイルシート名
    """
    if style is not None:
        plt.style.use(style)


def set_vortex_region_ticks_empty(ax, extent: float) -> None:
    """
    渦領域プロット用の軸目盛りを設定（空ラベル）

    Args:
        ax: matplotlib axes オブジェクト
        extent (float): 範囲（メートル）
    """
    ax.set_xticks([0, extent, 2 * extent], ["", "", ""])
    ax.set_yticks([0, extent, 2 * extent], ["", "", ""])


def set_vortex_region_ticks_km(ax, extent: float) -> None:
    """
    渦領域プロット用の軸目盛りを設定（km単位のラベル付き）

    Args:
        ax: matplotlib axes オブジェクト
        extent (float): 範囲（メートル）
    """
    extent_km = int(extent * 1e-3)
    ax.set_xticks(
        [0, extent, 2 * extent],
        [f"-{extent_km}", "0", f"{extent_km}"]
    )
    ax.set_yticks(
        [0, extent, 2 * extent],
        [f"-{extent_km}", "0", f"{extent_km}"]
    )


def set_vortex_region_ticks_km_empty(ax, extent: float) -> None:
    """
    渦領域プロット用の軸目盛りを設定（km単位座標、空ラベル）

    2dプロットでX_cut*1e-3のようにkm単位でプロットする場合に使用

    Args:
        ax: matplotlib axes オブジェクト
        extent (float): 範囲（メートル）
    """
    extent_km = extent * 1e-3
    ax.set_xticks([0, extent_km, 2 * extent_km], [])
    ax.set_yticks([0, extent_km, 2 * extent_km], [])


def set_azimuthal_plot_ticks(ax, r_max: float = 1000e3, z_max: float = 20e3) -> None:
    """
    方位角平均プロット用の標準軸目盛りを設定

    Args:
        ax: matplotlib axes オブジェクト
        r_max (float): 最大半径（メートル、デフォルト: 1000km）
        z_max (float): 最大高度（メートル、デフォルト: 20km）
    """
    ax.set_xticks([0, 250e3, 500e3, 750e3, r_max], ["", "", "", "", ""])
    ax.set_yticks([0, 5e3, 10e3, 15e3, z_max], ["", "", "", "", ""])
    ax.set_ylim([0, z_max])
