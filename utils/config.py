"""
設定管理モジュール

setting.jsonファイルの読み込みと、設定値へのアクセスを提供します。
全ての解析スクリプトで共通に使用される設定値を一元管理します。
"""

import json
import os
from typing import Optional


class AnalysisConfig:
    """
    解析設定を管理するクラス

    setting.jsonファイルから設定を読み込み、計算された値も提供します。

    Attributes:
        glevel (int): グリッドレベル
        nt (int): 時間ステップ数
        dt_output (int): 出力時間間隔（秒）
        triangle_size (float): 三角形サイズ
        nz (int): 鉛直レベル数
        f (float): コリオリパラメータ
        input_folder (str): 入力データフォルダパス
        work_dir (str): 作業ディレクトリ
        vgrid_filepath (str): 鉛直グリッドファイルパス
    """

    # デフォルト定数（全ファイルで共通のハードコード値）
    DEFAULT_NZ = 74
    EXTENT = 500e3  # 500km
    R_MAX = 1000e3  # 1000km
    R_PLOT_MAX = 500e3  # 500km

    def __init__(
        self, config_file: str = "setting.json", base_dir: Optional[str] = None
    ):
        """
        設定ファイルを読み込む

        Args:
            config_file (str): 設定ファイルのパス（デフォルト: "setting.json"）
            base_dir (str, optional): 設定ファイルを探す基準ディレクトリ
        """
        if base_dir is None:
            # カレントディレクトリのみ
            if os.path.exists(config_file):
                config_path = config_file
            else:
                raise FileNotFoundError(
                    f"設定ファイル '{config_file}' が見つかりません。\n"
                    f"カレントディレクトリ ({os.getcwd()}) に配置してください。"
                )
        else:
            config_path = os.path.join(base_dir, config_file)

        with open(config_path, "r", encoding="utf-8") as f:
            self._data = json.load(f)

        self._config_path = config_path

    # === 基本設定値（setting.jsonから直接読み込み） ===

    @property
    def glevel(self) -> int:
        """グリッドレベル"""
        return self._data["glevel"]

    @property
    def nt(self) -> int:
        """時間ステップ数"""
        return self._data["nt"]

    @property
    def t_first(self) -> int:
        """解析開始時刻のインデックス"""
        return self._data.get("t_first", 0)

    @property
    def t_last(self) -> int:
        """解析終了時刻のインデックス（この値は含む）"""
        return self._data.get("t_last", self.nt)

    @property
    def dt_output(self) -> int:
        """出力時間間隔（秒）"""
        return self._data["dt_output"]

    @property
    def dt_hour(self) -> int:
        """出力時間間隔（時間）"""
        return int(self.dt_output / 3600)

    @property
    def triangle_size(self) -> float:
        """三角形サイズ"""
        return self._data["triangle_size"]

    @property
    def nz(self) -> int:
        """鉛直レベル数"""
        return self._data.get("nz", self.DEFAULT_NZ)

    @property
    def f(self) -> float:
        """コリオリパラメータ"""
        return self._data["f"]

    @property
    def input_folder(self) -> str:
        """入力データフォルダパス"""
        return self._data["input_folder"]

    @property
    def work_dir(self) -> str:
        """作業ディレクトリ"""
        return self._data["work_dir"]

    @property
    def vgrid_filepath(self) -> str:
        """鉛直グリッドファイルパス"""
        return self._data["vgrid_filepath"]

    @property
    def time_tick_step(self) -> int:
        """時間軸の目盛り間隔（秒）"""
        return self._data["time_tick_step"]

    @property
    def n_jobs(self) -> int:
        """並列処理のジョブ数"""
        return self._data.get("n_jobs", 1)

    # === 計算された設定値 ===

    @property
    def nx(self) -> int:
        """x方向のグリッド数"""
        return 2**self.glevel

    @property
    def ny(self) -> int:
        """y方向のグリッド数"""
        return 2**self.glevel

    @property
    def x_width(self) -> float:
        """x方向の領域幅"""
        return self.triangle_size

    @property
    def y_width(self) -> float:
        """y方向の領域幅"""
        return self.triangle_size * 0.5 * 3.0**0.5

    @property
    def dx(self) -> float:
        """x方向のグリッド間隔"""
        return self.x_width / self.nx

    @property
    def dy(self) -> float:
        """y方向のグリッド間隔"""
        return self.y_width / self.ny

    @property
    def time_list(self) -> list:
        """時間リスト（時間単位）"""
        return [t * self.dt_hour for t in range(self.nt)]

    @property
    def time_ticks(self) -> list:
        """時間メモリ（時間単位）"""
        return [t * self.dt_hour for t in range(0, self.nt, self.time_tick_step)]

    @property
    def center_x(self):
        """TC中心のx座標リスト（キャッシュ付き）"""
        if not hasattr(self, "_center_x"):
            import numpy as np

            self._center_x = np.loadtxt("./data/ss_slp_center_x.txt", ndmin=1)
        return self._center_x

    @property
    def center_y(self):
        """TC中心のy座標リスト（キャッシュ付き）"""
        if not hasattr(self, "_center_y"):
            import numpy as np

            self._center_y = np.loadtxt("./data/ss_slp_center_y.txt", ndmin=1)
        return self._center_y

    # === 領域計算用のヘルパーメソッド ===

    def get_extent_indices(
        self, center_x: int, center_y: int, extent: Optional[float] = None
    ) -> tuple:
        """
        指定された中心座標と範囲から、グリッドインデックスを計算

        Args:
            center_x (int): 中心のxインデックス
            center_y (int): 中心のyインデックス
            extent (float, optional): 範囲（メートル）。デフォルトはself.EXTENT

        Returns:
            tuple: (x_indices, y_indices) - グリッドインデックスのリスト
        """
        if extent is None:
            extent = self.EXTENT

        extent_x = int(extent / self.dx)
        extent_y = int(extent / self.dy)

        x_idx = [(center_x - extent_x + i) % self.nx for i in range(2 * extent_x)]
        y_idx = [(center_y - extent_y + i) % self.ny for i in range(2 * extent_y)]

        return x_idx, y_idx

    def __repr__(self) -> str:
        return (
            f"AnalysisConfig(glevel={self.glevel}, nt={self.nt}, "
            f"nx={self.nx}, ny={self.ny}, nz={self.nz})"
        )


# グローバルなデフォルトインスタンス（必要に応じて使用）
_default_config = None


def get_config(
    config_file: str = "setting.json", force_reload: bool = False
) -> AnalysisConfig:
    """
    グローバルな設定インスタンスを取得

    Args:
        config_file (str): 設定ファイルのパス
        force_reload (bool): 強制的に再読み込みするかどうか

    Returns:
        AnalysisConfig: 設定インスタンス
    """
    global _default_config

    if _default_config is None or force_reload:
        _default_config = AnalysisConfig(config_file)

    return _default_config
