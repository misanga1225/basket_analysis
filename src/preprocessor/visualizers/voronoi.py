from visualizers.base import BaseVisualizer
from processors.voronoi_area import VoronoiPreProcessor

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from matplotlib.animation import FuncAnimation

class VoronoiAreaVisualizer(BaseVisualizer):
    def __init__(self, court, figsize=(12, 16)):
        super().__init__(court, figsize)
        self.voronoi_processor = VoronoiPreProcessor(court)

    def draw_voronoi_animation(self, data: pd.DataFrame, interval=1000, title=None):
        """
        Draw an animation of Voronoi regions over time.
        :param data: DataFrame containing player positions.
        :param interval: Time interval between frames in milliseconds.
        :param title: Optional title for the plot.
        """
        if self.fig is None or self.ax is None:
            self.setup_canvas(title)

        def init():
            return []
        
        def update(frame):
            self.ax.clear()
            self.court._draw_court(self.ax)
            points = np.array([
                [data[f'x_{player}'][frame], data[f'y_{player}'][frame]]
                for player in self.court.players
            ])
            self._draw_voronoi_court(points, self.ax, title)
            return self.ax.patches + self.ax.lines
        
        anim = FuncAnimation(
            self.fig,
            update,
            frames=len(data),
            init_func=init,
            blit=True,
            interval=interval
        )

        return anim

    def _draw_voronoi_court(self, points: np.array, ax: plt.Axes=None, title=None):
        """
        Draw Voronoi regions on the court.
        :param points: Array of points for Voronoi calculation.
        :param title: Optional title for the plot.
        :param ax: Optional Matplotlib Axes to draw on. If None, uses the current Axes.
        """
        if ax is None:
            self.setup_canvas(title)
            ax = self.ax
            
        self.court._draw_court(ax)
        (player_ridge_vertices, clipped_vertices), _ = self.voronoi_processor.compute_voronoi_regions_and_areas(points)

        for player_idx, vertices in player_ridge_vertices.items():
            polygon = plt.Polygon(
                clipped_vertices[vertices],
                closed=True,
                alpha=0.3,
                label=self.court.players[player_idx],
                color=self.court.colors[player_idx]
                )
            ax.add_patch(polygon)

        for player_idx, vertex in enumerate(self.court.players):
            ax.plot(
                np.clip(points[player_idx, 0], 0, self.court.court_width),
                np.clip(points[player_idx, 1], 0, self.court.court_height),
                'o',
                color=self.court.colors[player_idx],
                markersize=7,
                label=vertex
            )

        if title:
            ax.set_title(title)
        
        return ax