from courts.court import BaseCourt

import numpy as np
import matplotlib.pyplot as plt

class BasketCourt(BaseCourt):

    def __init__(self):
        
        court_width = 950
        court_height = 1505

        lines = [
            ([0, 300], [100, 100]),
            ([0, 300], [1400, 1400]),
            ([580, 580], [500, 1000]),
            ([0, 580], [500, 500]),
            ([0, 580], [1000, 1000]),
            ([0, 950], [0, 0]),
            ([0, 950], [1505, 1505]),
            ([0, 0], [0, 1505]),
            ([950, 950], [0, 1505]),
        ]

        circles = [
            ((153.75, 748), 666.25, np.pi/2.32),
            ((580, 748), 190, np.pi/2),
        ]

        super().__init__(court_width, court_height, lines, circles)

        self.players = ['O1red', 'O2blue', 'O3pink', 'D1black', 'D2orange', 'D3yellow']
        self.colors = ['red', 'blue', 'pink', 'black', 'orange', 'yellow']
