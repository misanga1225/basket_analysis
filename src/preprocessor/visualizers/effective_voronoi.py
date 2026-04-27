from visualizers.base import BaseVisualizer
from processors.effective_voronoi import EffectiveVoronoiProcessor

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from matplotlib.animation import FuncAnimation
from matplotlib.patches import Polygon as MplPolygon
from shapely.geometry import Polygon as ShapelyPolygon, MultiPolygon


ARROW_LEN_CM = 100.0


class EffectiveVoronoiVisualizer(BaseVisualizer):
    """
    通常ボロノイ領域（薄塗り）と進行方向視野で切り出した有効ボロノイ領域（濃塗り）を
    重ね描きしてアニメーション化する。
    """

    def __init__(self, court, figsize=(12, 16)):
        super().__init__(court, figsize)

    def draw_effective_voronoi_animation(
        self,
        data: pd.DataFrame,
        precomputed_voronoi,
        theta_deg: float,
        radius: float = 2000.0,
        interval: int = 50,
        title: str | None = None,
    ):
        """
        :param data: 選手位置 DataFrame
        :param precomputed_voronoi: VoronoiPreProcessor.compute_all_frames() の戻り値
        :param theta_deg: 視野半角 [deg]
        :param radius: 扇形半径 [cm]
        :param interval: フレーム間隔 [ms]
        :param title: タイトル
        """
        if self.fig is None or self.ax is None:
            self.setup_canvas(title)

        processor = EffectiveVoronoiProcessor(
            court=self.court,
            theta_deg_list=[theta_deg],
            radius=radius,
        )
        _, polygon_dict, directions = processor.compute_all(
            data,
            precomputed_voronoi=precomputed_voronoi,
            return_polygons=True,
        )
        eff_polys_per_frame = polygon_dict[theta_deg]

        player_names = self.court.players
        colors = self.court.colors
        N = len(player_names)

        def init():
            return []

        def update(frame: int):
            self.ax.clear()
            self.court._draw_court(self.ax)

            (player_ridge_vertices, clipped_vertices), _ = precomputed_voronoi[frame]

            # 通常ボロノイ（薄塗り）
            for idx, indices in player_ridge_vertices.items():
                if len(indices) < 3:
                    continue
                self.ax.add_patch(
                    plt.Polygon(
                        clipped_vertices[indices],
                        closed=True,
                        alpha=0.1,
                        color=colors[idx],
                    )
                )

            # 有効ボロノイ（濃塗り）
            for idx in range(N):
                eff_poly = eff_polys_per_frame[frame].get(idx)
                if eff_poly is None or eff_poly.is_empty:
                    continue
                self._add_shapely_polygon(self.ax, eff_poly, color=colors[idx], alpha=0.5)

            # 選手位置 + 進行方向矢印
            for idx, p_name in enumerate(player_names):
                px = float(data[f'x_{p_name}'][frame])
                py = float(data[f'y_{p_name}'][frame])
                self.ax.plot(
                    np.clip(px, 0, self.court.court_width),
                    np.clip(py, 0, self.court.court_height),
                    'o',
                    color=colors[idx],
                    markersize=7,
                    label=p_name,
                )
                d = directions[idx, frame]
                if np.all(np.isfinite(d)):
                    self.ax.annotate(
                        '',
                        xy=(px + d[0] * ARROW_LEN_CM, py + d[1] * ARROW_LEN_CM),
                        xytext=(px, py),
                        arrowprops=dict(arrowstyle='->', color=colors[idx], lw=1.5),
                    )

            if title:
                elapsed = frame * 0.05
                self.ax.set_title(f"{title}  theta={theta_deg}deg  {elapsed:.2f}s")

            return self.ax.patches + self.ax.lines

        anim = FuncAnimation(
            self.fig,
            update,
            frames=len(data),
            init_func=init,
            blit=True,
            interval=interval,
        )

        return anim

    @staticmethod
    def _add_shapely_polygon(ax: plt.Axes, geom, color, alpha: float):
        """shapely の Polygon / MultiPolygon を matplotlib に描画。"""
        if isinstance(geom, ShapelyPolygon):
            xs, ys = geom.exterior.xy
            ax.add_patch(
                MplPolygon(
                    np.column_stack([xs, ys]),
                    closed=True,
                    alpha=alpha,
                    color=color,
                )
            )
        elif isinstance(geom, MultiPolygon):
            for sub in geom.geoms:
                xs, ys = sub.exterior.xy
                ax.add_patch(
                    MplPolygon(
                        np.column_stack([xs, ys]),
                        closed=True,
                        alpha=alpha,
                        color=color,
                    )
                )
