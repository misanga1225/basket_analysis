import matplotlib.pyplot as plt
import numpy as np

class BaseCourt:
    def __init__(self, court_width: int, court_height: int, lines=None, circles=None):
        """
        Base class for a sports court.
        :param court_width: Width of the court.
        :param court_height: Height of the court.
        :param lines: Optional list of lines to draw, each as ([x1, x2], [y1, y2]).
        :param circles: Optional list of circles to draw, each as ((center_x, center_y), radius, theta_end).
        """
        self.court_width = court_width
        self.court_height = court_height
        self.lines = lines if lines is not None else []
        self.circles = circles if circles is not None else []

    def _draw_court(self, ax: plt.Axes):
        """
        Draw the court using lines and arcs on the given Matplotlib Axes.
        :param ax: Matplotlib Axes object to draw on.
        """
        ax.clear()
        ax.set_xlim(0, self.court_width)
        ax.set_ylim(0, self.court_height)
        ax.set_aspect('equal', adjustable='box')

        for line in self.lines:
            ax.plot(*line, color='silver', linestyle='-', linewidth=1)

        for center, radius, theta_end in self.circles:
            theta = np.linspace(-theta_end, theta_end, 100)
            x = center[0] + radius * np.cos(theta)
            y = center[1] + radius * np.sin(theta)
            ax.plot(x, y, color='silver', linestyle='-', linewidth=1)

        ax.set_xlabel('X-axis (cm)')
        ax.set_ylabel('Y-axis (cm)')
        ax.set_title('Sports Court')

        return ax