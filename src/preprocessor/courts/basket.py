from courts.court import BaseCourt

import numpy as np
import matplotlib.pyplot as plt

class BasketCourt(BaseCourt):

    def __init__(self):
        
        court_width = 950
        court_height = 1505

        lines = [
            ([0, 300], [95, 95]),
            ([0, 300], [1410, 1410]),
            ([580, 580], [510, 995]),
            ([0, 580], [510, 510]),
            ([0, 580], [995, 995]),
            ([0, 950], [0, 0]),
            ([0, 950], [1505, 1505]),
            ([0, 0], [0, 1505]),
            ([950, 950], [0, 1505]),
        ]

        circles = [
            ((147.28, 752.5), 675, np.arcsin(657.5 / 675)),
            ((580, 752.5), 180, np.pi/2),
        ]

        super().__init__(court_width, court_height, lines, circles)

        self.players = ['O1red', 'O2blue', 'O3pink', 'D1black', 'D2orange', 'D3yellow']
        self.colors = ['red', 'blue', 'pink', 'black', 'orange', 'yellow']
