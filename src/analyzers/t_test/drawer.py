import numpy as np
import matplotlib.pyplot as plt

from .stats import t_test
from ..features.drawer import plot_feature

def plot_t_test(
    data: [np.ndarray, np.ndarray],
    ax: plt.Axes,
    labels: [str, str],
    bar_kwargs: [dict, dict],
    scatter_kwargs: [dict, dict]
):
    """
    T検定の結果を描画する．
    :param data: T検定を行う二つのデータセット
    :param ax: 描画するAxes
    :param labels: データセットのラベル
    :param bar_kwargs: matplotlib.pyplot.barの引数
    :param scatter_kwargs: matplotlib.pyplot.scatterの引数
    """
    for idx, d in enumerate(data):
        plot_feature(d, ax, idx, bar_kwargs[idx], scatter_kwargs[idx])

    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels)
    ax.set_xlabel("Match type")
    ax.set_ylabel("Voronoi Area (cm^2)")
    ax.grid(True, axis='y')

    t_stat, p_value, cohens_d = t_test(data)
    
    if p_value < 0.001:
        text = "***"
    elif p_value < 0.01:
        text = "**"
    elif p_value < 0.05:
        text = "*"
    else:
        text = "n.s."

    text += f" (p={p_value:.4f}, d={cohens_d:.4f})"

    y_max = max(data[0].max(), data[1].max())
    y_line = y_max * 1.05
    y_text = y_line * 1.02

    ax.plot([0, 0, 1, 1], [y_line, y_line * 1.02, y_line * 1.02, y_line], lw=1.5, c='k')
    ax.text(0.5, y_text, text, ha='center', va='bottom', color='k')

    