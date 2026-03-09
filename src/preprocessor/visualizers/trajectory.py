from visualizers.base import BaseVisualizer

import pandas as pd

class TrajectoryVisualizer(BaseVisualizer):
    def __init__(self, court, figsize=(12, 16)):
        super().__init__(court, figsize)

    def draw_trajectories(self, trajectories: pd.DataFrame, title=None):
        """
        Draw trajectories on the court.
        :param trajectories: DataFrame containing trajectory data.
        :param title: Optional title for the plot.
        """
        self.setup_canvas(title)

        # Validate DataFrame structure
        expected_players = set(self.court.players)
        columns = set(trajectories.columns)

        for player in expected_players:
            x_col = f"x_{player}"
            y_col = f"y_{player}"
            if x_col not in columns or y_col not in columns:
                raise ValueError(f"Missing required columns for player '{player}': expected '{x_col}' and '{y_col}'")

        for player in self.court.players:
            self.ax.plot(
                trajectories[f"x_{player}"],
                trajectories[f"y_{player}"],
                label=player,
                color=self.court.colors[self.court.players.index(player)],
                marker="."
            )

        if title:
            self.ax.set_title(title)
        self.ax.legend(loc='upper right', bbox_to_anchor=(1, 1), fontsize='small')
        
        return self.fig, self.ax