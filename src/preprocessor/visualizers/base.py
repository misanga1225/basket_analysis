import matplotlib.pyplot as plt

class BaseVisualizer:
    def __init__(self, court, figsize=(6, 8)):
        """
        Initialize the visualizer with a court and figure size.
        :param court: The court object to visualize.
        :param figsize: Size of the figure for visualization.
        """
        self.court = court
        self.figsize = figsize
        self.fig = None
        self.ax = None

    def setup_canvas(self, title=None):
        """
        Set up the canvas for drawing the court.
        :param title: Optional title for the plot.
        """
        self.fig, self.ax = plt.subplots(figsize=self.figsize)
        self.court._draw_court(self.ax)
        if title:
            self.ax.set_title(title)

    def show(self):
        plt.show(self.fig)

    def save(self, filepath):
        self.fig.savefig(filepath, bbox_inches='tight')