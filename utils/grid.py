"""
グリッド計算モジュール

グリッド座標の生成、メッシュグリッド作成、座標変換などの
グリッド関連の計算を提供します。
"""

from typing import Optional, Tuple

import numpy as np

from .config import AnalysisConfig


class GridHandler:
    """
    グリッド座標の計算と管理を行うクラス

    Attributes:
        config (AnalysisConfig): 設定インスタンス
        x (np.ndarray): x座標配列
        y (np.ndarray): y座標配列
        X (np.ndarray): xのメッシュグリッド
        Y (np.ndarray): yのメッシュグリッド
    """

    def __init__(self, config: AnalysisConfig):
        """
        グリッドハンドラを初期化

        Args:
            config (AnalysisConfig): 設定インスタンス
        """
        self.config = config
        self.x, self.y = self._create_coordinates()
        self.X, self.Y = self._create_meshgrid()

    def _create_coordinates(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        グリッド座標を生成

        Returns:
            tuple: (x座標配列, y座標配列)
        """
        x = (np.arange(self.config.nx) + 0.5) * self.config.dx
        y = (np.arange(self.config.ny) + 0.5) * self.config.dy
        return x, y

    def _create_meshgrid(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        メッシュグリッドを生成

        Returns:
            tuple: (Xメッシュグリッド, Yメッシュグリッド)
        """
        return np.meshgrid(self.x, self.y)

    def apply_periodic_boundary(
        self, dX: np.ndarray, dY: Optional[np.ndarray] = None
    ) -> Tuple[np.ndarray, ...]:
        """
        周期境界条件を適用

        Args:
            dX (np.ndarray): x方向の差分配列
            dY (np.ndarray, optional): y方向の差分配列

        Returns:
            tuple: 周期境界条件を適用した(dX,) または (dX, dY)
        """
        dX = dX.copy()
        dX[dX > 0.5 * self.config.x_width] -= self.config.x_width
        dX[dX < -0.5 * self.config.x_width] += self.config.x_width

        if dY is not None:
            dY = dY.copy()
            dY[dY > 0.5 * self.config.y_width] -= self.config.y_width
            dY[dY < -0.5 * self.config.y_width] += self.config.y_width
            return dX, dY

        return (dX,)

    def calculate_theta(self, center_x: float, center_y: float) -> np.ndarray:
        """
        中心座標からの角度を計算

        Args:
            center_x (float): 中心のx座標（メートル）
            center_y (float): 中心のy座標（メートル）

        Returns:
            np.ndarray: 角度配列（ラジアン）
        """
        dX = self.X - center_x
        dY = self.Y - center_y
        dX, dY = self.apply_periodic_boundary(dX, dY)
        theta = np.arctan2(dY, dX)
        return theta

    def calculate_radial_distance(self, center_x: float, center_y: float) -> np.ndarray:
        """
        中心座標からの半径距離を計算

        Args:
            center_x (float): 中心のx座標（メートル）
            center_y (float): 中心のy座標（メートル）

        Returns:
            np.ndarray: 半径距離配列（メートル）
        """
        dX = self.X - center_x
        dY = self.Y - center_y
        dX, dY = self.apply_periodic_boundary(dX, dY)
        r = np.sqrt(dX**2 + dY**2)
        return r

    def uv_to_radial_tangential(
        self,
        u: np.ndarray,
        v: np.ndarray,
        center_x: float,
        center_y: float,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        直交座標系の風速成分を放射状・接線方向成分に変換

        Args:
            u (np.ndarray): x方向の風速成分
            v (np.ndarray): y方向の風速成分
            center_x (float): 中心のx座標（メートル）
            center_y (float): 中心のy座標（メートル）

        Returns:
            tuple: (放射状成分, 接線方向成分)
        """
        theta = self.calculate_theta(center_x, center_y)

        # 角度が2次元の場合、風速データの次元に合わせてブロードキャスト
        if u.ndim == 3 and theta.ndim == 2:
            # (nz, ny, nx) の場合
            v_radial = u * np.cos(theta) + v * np.sin(theta)
            v_tangential = -u * np.sin(theta) + v * np.cos(theta)
        else:
            # 2次元の場合
            v_radial = u * np.cos(theta) + v * np.sin(theta)
            v_tangential = -u * np.sin(theta) + v * np.cos(theta)

        return v_radial, v_tangential

    def radial_tangential_to_uv(
        self,
        v_radial: np.ndarray,
        v_tangential: np.ndarray,
        center_x: float,
        center_y: float,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        放射状・接線方向成分を直交座標系の風速成分に変換

        Args:
            v_radial (np.ndarray): 放射状成分
            v_tangential (np.ndarray): 接線方向成分
            center_x (float): 中心のx座標（メートル）
            center_y (float): 中心のy座標（メートル）

        Returns:
            tuple: (x方向の風速成分, y方向の風速成分)
        """
        theta = self.calculate_theta(center_x, center_y)

        u = v_radial * np.cos(theta) - v_tangential * np.sin(theta)
        v = v_radial * np.sin(theta) + v_tangential * np.cos(theta)

        return u, v

    def get_vortex_region_indices(
        self,
        center_x: float,
        center_y: float,
        extent: Optional[float] = None,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        渦領域のグリッドインデックスを取得

        Args:
            center_x (float): 中心のx座標（メートル）
            center_y (float): 中心のy座標（メートル）
            extent (float, optional): 範囲（メートル）

        Returns:
            tuple: (x方向のインデックス配列, y方向のインデックス配列)
        """
        if extent is None:
            extent = self.config.EXTENT

        # 中心座標をインデックスに変換
        center_x_idx = int(center_x / self.config.dx)
        center_y_idx = int(center_y / self.config.dy)

        # 範囲をインデックスに変換
        extent_x = int(extent / self.config.dx)
        extent_y = int(extent / self.config.dy)

        # 周期境界条件を考慮したインデックス配列
        x_idx = np.array(
            [
                (center_x_idx - extent_x + i) % self.config.nx
                for i in range(2 * extent_x)
            ]
        )
        y_idx = np.array(
            [
                (center_y_idx - extent_y + i) % self.config.ny
                for i in range(2 * extent_y)
            ]
        )

        return x_idx, y_idx

    def extract_vortex_region(
        self,
        data: np.ndarray,
        center_x: float,
        center_y: float,
        extent: Optional[float] = None,
    ) -> np.ndarray:
        """
        データから渦領域を抽出

        Args:
            data (np.ndarray): 全領域のデータ
            center_x (float): 中心のx座標（メートル）
            center_y (float): 中心のy座標（メートル）
            extent (float, optional): 範囲（メートル）

        Returns:
            np.ndarray: 抽出された渦領域のデータ
        """
        x_idx, y_idx = self.get_vortex_region_indices(center_x, center_y, extent)

        # データの次元に応じて抽出
        if data.ndim == 2:
            # 2次元データ (ny, nx)
            return data[np.ix_(y_idx, x_idx)]
        elif data.ndim == 3:
            # 3次元データ (nz, ny, nx)
            return data[:, np.ix_(y_idx, x_idx)].reshape(
                data.shape[0], len(y_idx), len(x_idx)
            )
        else:
            raise ValueError(f"サポートされていないデータ次元: {data.ndim}")

    def get_vortex_region_meshgrid(
        self,
        extent: Optional[float] = None,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        渦領域用のメッシュグリッドを生成

        Args:
            extent (float, optional): 範囲（メートル）

        Returns:
            tuple: (Xメッシュグリッド, Yメッシュグリッド)
        """
        if extent is None:
            extent = self.config.EXTENT

        # 範囲をインデックスに変換
        extent_x = int(extent / self.config.dx)
        extent_y = int(extent / self.config.dy)

        # 渦領域用の座標配列を作成
        x_vortex = np.arange(0, 2 * extent_x * self.config.dx, self.config.dx)
        y_vortex = np.arange(0, 2 * extent_y * self.config.dy, self.config.dy)

        return np.meshgrid(x_vortex, y_vortex)

    def get_meshgrid_km(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        km単位のメッシュグリッドを生成

        Returns:
            tuple: (Xメッシュグリッド(km), Yメッシュグリッド(km))
        """
        return self.X * 1e-3, self.Y * 1e-3

    def create_radial_grid(self, r_max: float) -> np.ndarray:
        """
        方位角平均用の動径グリッドを生成

        Args:
            r_max (float): 最大半径（メートル）

        Returns:
            np.ndarray: 動径座標配列（メートル）
        """
        nr = int(r_max / self.config.dx)
        return (np.arange(nr) + 0.5) * self.config.dx

    def create_vertical_grid(self) -> np.ndarray:
        """
        鉛直グリッドを生成

        Returns:
            np.ndarray: 鉛直座標配列（メートル）
        """
        return np.loadtxt(self.config.vgrid_filepath)

    def create_radial_vertical_meshgrid(
        self, r_max: float, nz: Optional[int] = None
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        方位角平均プロット用の動径-鉛直メッシュグリッドを生成

        Args:
            r_max (float): 最大半径（メートル）
            nz (int, optional): z方向のグリッド数。Noneの場合は全て使用

        Returns:
            tuple: (動径メッシュグリッド, 鉛直メッシュグリッド)
        """
        rgrid = self.create_radial_grid(r_max)
        vgrid = self.create_vertical_grid()
        if nz is not None:
            vgrid = vgrid[:nz]
        return np.meshgrid(rgrid, vgrid)

    def __repr__(self) -> str:
        return (
            f"GridHandler(nx={self.config.nx}, ny={self.config.ny}, "
            f"dx={self.config.dx:.2f}, dy={self.config.dy:.2f})"
        )


def create_grid(config: Optional[AnalysisConfig] = None) -> GridHandler:
    """
    グリッドハンドラを作成（簡易版）

    Args:
        config (AnalysisConfig, optional): 設定インスタンス

    Returns:
        GridHandler: グリッドハンドラインスタンス
    """
    if config is None:
        from .config import get_config

        config = get_config()

    return GridHandler(config)
