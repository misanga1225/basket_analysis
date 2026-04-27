from courts.court import BaseCourt
from processors.voronoi_area import VoronoiPreProcessor

import numpy as np
import pandas as pd

from shapely.geometry import Polygon as ShapelyPolygon


EPS_VELOCITY = 1e-8


class EffectiveVoronoiProcessor():
    """
    進行方向ベース 有効ボロノイ領域の算出。
    Shimizu & Okada (2025) の中央差分による移動ベクトルを進行方向とし、
    視野扇形 W(t; theta, R) で通常ボロノイ領域 V(t) を切り出す。
        V_eff(t) = V(t) ∩ W(t; theta, R)
    """

    def __init__(self, court: BaseCourt, theta_deg_list, radius: float = 2000.0, n_arc_points: int = 60):
        self.court = court
        self.theta_deg_list = list(theta_deg_list)
        self.radius = float(radius)
        self.n_arc_points = int(n_arc_points)

    @staticmethod
    def central_diff_velocity(positions: np.ndarray) -> np.ndarray:
        """
        中央差分による移動ベクトル: m(t) = p(t+1) - p(t-1)
        端点は片側差分。
        :param positions: (T, 2)
        :return: (T, 2)
        """
        T = positions.shape[0]
        velocity = np.zeros_like(positions, dtype=float)
        if T >= 3:
            velocity[1:-1] = positions[2:] - positions[:-2]
        if T >= 2:
            velocity[0] = positions[1] - positions[0]
            velocity[-1] = positions[-1] - positions[-2]
        return velocity

    @staticmethod
    def _resolve_directions(velocity: np.ndarray) -> np.ndarray:
        """
        ゼロ速度フレームを直前の有効方向で穴埋めする。
        最初から無効が続く区間は (NaN, NaN) で残し、後段で欠損として扱う。
        :param velocity: (T, 2)
        :return: (T, 2) 単位ベクトル化済み (NaN 含む)
        """
        T = velocity.shape[0]
        directions = np.full_like(velocity, np.nan, dtype=float)
        last_valid = None
        for t in range(T):
            v = velocity[t]
            norm = np.hypot(v[0], v[1])
            if norm > EPS_VELOCITY:
                last_valid = v / norm
                directions[t] = last_valid
            elif last_valid is not None:
                directions[t] = last_valid
            # else: NaN のまま
        return directions

    def make_wedge(self, origin, direction, theta_deg: float):
        """
        視野扇形 polygon。direction は単位ベクトル想定。
        :param origin: (x, y)
        :param direction: (dx, dy) 単位ベクトル想定
        :param theta_deg: 視野半角 [deg]
        :return: shapely Polygon または None
        """
        ox, oy = float(origin[0]), float(origin[1])
        dx, dy = float(direction[0]), float(direction[1])
        if not np.isfinite(dx) or not np.isfinite(dy):
            return None
        if np.hypot(dx, dy) < EPS_VELOCITY:
            return None

        base_angle = np.arctan2(dy, dx)
        theta = np.deg2rad(theta_deg)
        angles = np.linspace(base_angle - theta, base_angle + theta, self.n_arc_points)
        arc = [(ox + self.radius * np.cos(a), oy + self.radius * np.sin(a)) for a in angles]
        coords = [(ox, oy)] + arc + [(ox, oy)]
        return ShapelyPolygon(coords)

    def _build_voronoi_polygon(self, indices, clipped_vertices: np.ndarray):
        """
        VoronoiPreProcessor の出力からプレイヤーの V_i polygon を構築。
        """
        if len(indices) < 3:
            return None
        return ShapelyPolygon(clipped_vertices[indices])

    def compute_effective_for_frame(
        self,
        voronoi_poly,
        player_pos,
        direction,
        theta_deg: float,
    ):
        """
        :return: (effective_polygon_or_None, effective_area_float)
                 direction が無効なら (None, np.nan)
        """
        if voronoi_poly is None:
            return None, np.nan
        wedge = self.make_wedge(player_pos, direction, theta_deg)
        if wedge is None:
            return None, np.nan
        eff = voronoi_poly.intersection(wedge)
        if eff.is_empty:
            return eff, 0.0
        return eff, float(eff.area)

    def compute_all(
        self,
        data: pd.DataFrame,
        precomputed_voronoi,
        return_polygons: bool = False,
    ):
        """
        全フレーム・全 θ について有効ボロノイ面積を算出する。
        :param data: 選手位置 DataFrame (x_<player>, y_<player>)
        :param precomputed_voronoi: VoronoiPreProcessor.compute_all_frames() の戻り値
        :param return_polygons: True にすると polygon dict も返す（可視化用）
        :return:
            area_dict: {theta_deg: {player_name: np.ndarray (T,)}}
            polygon_dict (optional): {theta_deg: list[length T] of {player_idx: ShapelyPolygon}}
        """
        player_names = self.court.players
        T = len(data)
        N = len(player_names)

        # 位置時系列を (N, T, 2) に
        positions = np.stack([
            np.stack([
                data[f'x_{p}'].to_numpy(dtype=float),
                data[f'y_{p}'].to_numpy(dtype=float),
            ], axis=-1)
            for p in player_names
        ], axis=0)

        # 各選手の direction 時系列 (N, T, 2)
        directions = np.stack([
            self._resolve_directions(self.central_diff_velocity(positions[i]))
            for i in range(N)
        ], axis=0)

        # 結果バッファ
        area_dict = {
            theta: {p: np.full(T, np.nan, dtype=float) for p in player_names}
            for theta in self.theta_deg_list
        }
        polygon_dict = (
            {theta: [dict() for _ in range(T)] for theta in self.theta_deg_list}
            if return_polygons else None
        )

        for t in range(T):
            (player_ridge_vertices, clipped_vertices), _ = precomputed_voronoi[t]

            # フレーム単位で V_i polygon をキャッシュ
            v_polys = {
                idx: self._build_voronoi_polygon(player_ridge_vertices[idx], clipped_vertices)
                for idx in range(N)
            }

            for theta in self.theta_deg_list:
                for idx in range(N):
                    eff_poly, eff_area = self.compute_effective_for_frame(
                        v_polys[idx],
                        positions[idx, t],
                        directions[idx, t],
                        theta,
                    )
                    area_dict[theta][player_names[idx]][t] = eff_area
                    if return_polygons:
                        polygon_dict[theta][t][idx] = eff_poly

        if return_polygons:
            return area_dict, polygon_dict, directions
        return area_dict
