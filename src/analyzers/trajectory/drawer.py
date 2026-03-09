import numpy as np
import matplotlib.pyplot as plt

def plot_trajectory(
    data: np.ndarray,
    ax: plt.Axes,
    **kwargs
):
    """
    プレイヤーのボロノイ領域の面積の軌跡を描画する．
    :param data: プレイヤーのボロノイ領域の面積情報を格納したndarray
    :param ax: 描画先のAxes
    :param kwargs: matplotlib.pyplot.plotの引数
    """
    xlim = kwargs.pop('xlim', None)
    ylim = kwargs.pop('ylim', None)

    ax.plot(data, **kwargs)
    ax.set_xlabel('Frame')
    ax.set_ylabel('Voronoi Area (cm^2)')

    if xlim is not None:
        ax.set_xlim(xlim)
    if ylim is not None:
        ax.set_ylim(ylim)
