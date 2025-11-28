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
        t_first (int): 解析開始時刻のインデックス
        t_last (int): 解析終了時刻のインデックス
        t_step (int): 時間ループのステップ間隔
        dt_output (int): 出力時間間隔（秒）
        dt_hour (int): 出力時間間隔（時間）
        triangle_size (float): 三角形サイズ
        nz (int): 鉛直レベル数
        f (float): コリオリパラメータ
        input_folder (str): 入力データフォルダパス
        work_dir (str): 作業ディレクトリ
        vgrid_filepath (str): 鉛直グリッドファイルパス
        data_dir (str): データ出力の基底ディレクトリ
        fig_dir (str): 図出力の基底ディレクトリ
    """

    # デフォルト定数（全ファイルで共通のハードコード値）
    DEFAULT_NZ = 74
    EXTENT = 500e3  # 500km
    R_MAX = 1000e3  # 1000km
    R_PLOT_MAX = 500e3  # 500km

    def __init__(
        self,
        config_file: Optional[str] = None,
        base_dir: Optional[str] = None,
        auto_parse_args: bool = True,
        center_type: Optional[str] = None,
        center_path: Optional[str] = None,
    ):
        """
        設定ファイルを読み込む

        優先順位:
        1. 引数で明示的に指定
        2. コマンドライン引数 (--config, --center-type, --center-path)
        3. 環境変数 TC_ANALYZE_CONFIG
        4. setting.json の設定値
        5. デフォルト値

        Args:
            config_file (str, optional): 設定ファイルのパス
            base_dir (str, optional): 設定ファイルを探す基準ディレクトリ
            auto_parse_args (bool): コマンドライン引数を自動パースするか（デフォルト: True）
            center_type (str, optional): 中心座標のタイプ ("2d" or "3d")
            center_path (str, optional): 中心座標ファイルのパス（data_dir からの相対パス）

        Examples:
            >>> # デフォルト（ss_slp中心、2d）
            >>> config = AnalysisConfig()

            >>> # ms_presの各z面の中心を使用
            >>> config = AnalysisConfig(center_type="3d", center_path="center/ms_pres")

            >>> # コマンドライン: python script.py --center-type 3d --center-path center/ms_pres
            >>> config = AnalysisConfig()  # 自動的に引数を解析
        """
        # コマンドライン引数を一括解析
        parsed_config = None
        parsed_center_type = None
        parsed_center_path = None

        if auto_parse_args:
            parsed_config, parsed_center_type, parsed_center_path = (
                self._parse_args_from_argv()
            )

        # 設定ファイルの決定（優先順位: 引数 > コマンドライン > 環境変数 > デフォルト）
        if config_file is None:
            config_file = parsed_config

        if config_file is None:
            config_file = os.environ.get("TC_ANALYZE_CONFIG")

        if config_file is None:
            config_file = self._find_default_config(base_dir)

        # ファイルの存在確認と読み込み
        if base_dir is None:
            if os.path.exists(config_file):
                config_path = config_file
            else:
                raise FileNotFoundError(
                    f"設定ファイル '{config_file}' が見つかりません。\n"
                    f"カレントディレクトリ ({os.getcwd()}) に配置してください。"
                )
        else:
            config_path = os.path.join(base_dir, config_file)
            if not os.path.exists(config_path):
                raise FileNotFoundError(
                    f"設定ファイル '{config_path}' が見つかりません。"
                )

        with open(config_path, "r", encoding="utf-8") as f:
            self._data = json.load(f)

        self._config_path = config_path

        # 中心座標の設定（優先順位: 引数 > コマンドライン > setting.json > デフォルト）
        if center_type is None:
            center_type = parsed_center_type
        if center_type is None:
            center_type = self._data.get("center_type", "2d")

        if center_path is None:
            center_path = parsed_center_path
        if center_path is None:
            center_path = self._data.get("center_path", "center/ss_slp")

        self._center_type = center_type
        self._center_path = center_path

    def _parse_args_from_argv(self) -> tuple:
        """
        sys.argvから引数を抽出

        Returns:
            tuple: (config_file, center_type, center_path)
        """
        import sys

        config_file = None
        center_type = None
        center_path = None

        i = 0
        while i < len(sys.argv):
            arg = sys.argv[i]
            if arg in ["--config", "-c"] and i + 1 < len(sys.argv):
                config_file = sys.argv[i + 1]
                i += 2
            elif arg == "--center-type" and i + 1 < len(sys.argv):
                center_type = sys.argv[i + 1]
                i += 2
            elif arg == "--center-path" and i + 1 < len(sys.argv):
                center_path = sys.argv[i + 1]
                i += 2
            else:
                i += 1

        return config_file, center_type, center_path

    def _find_default_config(self, base_dir: Optional[str] = None) -> str:
        """
        デフォルトの設定ファイル候補を探す

        Args:
            base_dir (str, optional): 探索する基準ディレクトリ

        Returns:
            str: 見つかった設定ファイル名

        Raises:
            FileNotFoundError: 候補ファイルが1つも見つからない場合
        """
        candidate_files = ["setting.json", "config.json", "tc_analyze.json"]

        for candidate in candidate_files:
            if base_dir is None:
                check_path = candidate
            else:
                check_path = os.path.join(base_dir, candidate)

            if os.path.exists(check_path):
                return candidate

        # 候補が1つも見つからない
        raise FileNotFoundError(
            f"設定ファイルが見つかりません。\n"
            f"以下のいずれかを配置してください: {', '.join(candidate_files)}\n"
            f"または以下の方法で指定してください:\n"
            f"  - コマンドライン引数: --config <file>\n"
            f"  - 環境変数: TC_ANALYZE_CONFIG=<file>\n"
            f"カレントディレクトリ: {os.getcwd()}"
        )

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
    def t_step(self) -> int:
        """時間ループのステップ間隔"""
        return self._data.get("t_step", 1)

    @property
    def dt_output(self) -> int:
        """出力時間間隔（秒）"""
        return self._data["dt_output"]

    @property
    def dt_hour(self) -> int:
        """出力時間間隔（時間）"""
        return self._data.get("dt_hour", int(self.dt_output / 3600))

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

    @property
    def data_dir(self) -> str:
        """データ出力の基底ディレクトリ"""
        return self._data.get("data_dir", "./data")

    @property
    def fig_dir(self) -> str:
        """図出力の基底ディレクトリ"""
        return self._data.get("fig_dir", "./fig")

    @property
    def center_configs(self) -> dict:
        """
        中心座標ファイル名の設定

        Returns:
            dict: 中心座標のタイプごとのファイル名
                  例: {"ss_slp": "center_rrefine100km.npz",
                       "ms_pres": "center_rsearch200km_rrefine100km.npz"}
        """
        default_configs = {
            "ss_slp": "center.npz",
            "ms_pres": "center.npz"
        }
        return self._data.get("center_configs", default_configs)

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
    def center_type_str(self) -> str:
        """中心座標のタイプ ("2d" or "3d")"""
        return self._center_type

    @property
    def center_path_str(self) -> str:
        """中心座標ファイルのパス（data_dir からの相対パス）"""
        return self._center_path

    @property
    def center_x(self):
        """
        TC中心のx座標（キャッシュ付き）

        Returns:
            ndarray: center_type="2d" なら (nt,)、"3d" なら (nt, nz)
        """
        if not hasattr(self, "_center_x_cache"):
            self._center_x_cache = self._load_center_coordinates("x")
        return self._center_x_cache

    @property
    def center_y(self):
        """
        TC中心のy座標（キャッシュ付き）

        Returns:
            ndarray: center_type="2d" なら (nt,)、"3d" なら (nt, nz)
        """
        if not hasattr(self, "_center_y_cache"):
            self._center_y_cache = self._load_center_coordinates("y")
        return self._center_y_cache

    def _load_center_coordinates(self, coord: str):
        """
        中心座標を読み込む（内部メソッド）

        Args:
            coord (str): "x" or "y"

        Returns:
            ndarray: 中心座標配列
        """
        import numpy as np

        center_dir = os.path.join(self.data_dir, self._center_path)
        coord_idx = 0 if coord == "x" else 1

        # 最新形式: center.npz を最優先で読み込む
        npz_path = os.path.join(center_dir, "center.npz")
        if os.path.exists(npz_path):
            data = np.load(npz_path)
            center = data['center']
            if self._center_type == "2d":
                # shape: (nt, 2) -> (nt,)
                return center[:, coord_idx]
            elif self._center_type == "3d":
                # shape: (nt, nz, 2) -> (nt, nz)
                return center[:, :, coord_idx]

        # 新形式: center.npy を次に読み込む
        npy_path = os.path.join(center_dir, "center.npy")
        if os.path.exists(npy_path):
            center = np.load(npy_path)
            if self._center_type == "2d":
                # shape: (nt, 2) -> (nt,)
                return center[:, coord_idx]
            elif self._center_type == "3d":
                # shape: (nt, nz, 2) -> (nt, nz)
                return center[:, :, coord_idx]

        # 後方互換性: 旧形式のファイルを読み込む
        if self._center_type == "2d":
            # 2d: 単一ファイル x.txt, y.txt
            filepath = os.path.join(center_dir, f"{coord}.txt")

            # さらに古い形式も試す
            if not os.path.exists(filepath):
                legacy_path = os.path.join(self.data_dir, f"ss_slp_center_{coord}.txt")
                if os.path.exists(legacy_path):
                    filepath = legacy_path
                else:
                    raise FileNotFoundError(
                        f"中心座標ファイルが見つかりません:\n"
                        f"  新形式: {npy_path}\n"
                        f"  旧形式: {filepath}\n"
                        f"  古い形式: {legacy_path}\n"
                        f"center_type={self._center_type}, center_path={self._center_path}"
                    )

            return np.loadtxt(filepath, ndmin=1)

        elif self._center_type == "3d":
            # 3d: 複数ファイル x_z000.txt, x_z001.txt, ..., y_z000.txt, ...
            coords_list = []
            for z in range(self.nz):
                filepath = os.path.join(center_dir, f"{coord}_z{str(z).zfill(3)}.txt")

                if not os.path.exists(filepath):
                    raise FileNotFoundError(
                        f"中心座標ファイルが見つかりません:\n"
                        f"  新形式: {npy_path}\n"
                        f"  旧形式: {filepath}\n"
                        f"center_type={self._center_type}, center_path={self._center_path}"
                    )

                coords_list.append(np.loadtxt(filepath, ndmin=1))

            # shape: (nz, nt) -> 転置して (nt, nz) にする
            return np.array(coords_list).T

        else:
            raise ValueError(
                f"不正な center_type: {self._center_type}。'2d' または '3d' を指定してください。"
            )

    # === パス生成用のヘルパーメソッド ===

    def get_data_path(self, *paths: str) -> str:
        """
        データディレクトリ配下のパスを生成

        Args:
            *paths: パスの構成要素（例: "3d", "relative_wind_radial"）

        Returns:
            str: 完全なパス（例: "./data/3d/relative_wind_radial"）

        Example:
            >>> config.get_data_path("3d", "relative_wind_radial")
            "./data/3d/relative_wind_radial"
        """
        return os.path.join(self.data_dir, *paths)

    def get_fig_path(self, *paths: str) -> str:
        """
        図ディレクトリ配下のパスを生成

        Args:
            *paths: パスの構成要素（例: "3d", "vortex_region", "relative_wind_radial"）

        Returns:
            str: 完全なパス（例: "./fig/3d/vortex_region/relative_wind_radial"）

        Example:
            >>> config.get_fig_path("3d", "vortex_region", "relative_wind_radial")
            "./fig/3d/vortex_region/relative_wind_radial"
        """
        return os.path.join(self.fig_dir, *paths)

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
