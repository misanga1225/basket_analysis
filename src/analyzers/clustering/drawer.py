import numpy as np
import matplotlib.pyplot as plt

from .stats import k_medoids
from ..trajectory.drawer import plot_trajectory

def plot_kmedoids(
    data: list[np.ndarray],
    axes: list[plt.Axes],
    labels: list[str],
    n_clusters: int,
    **kwargs
):
    """
    DTWを用いたk-medoidsクラスタリングの結果を描画する．
    :param data: データセット
    :param ax: 描画するAxes
    :param labels: データセットのラベル
    :param n_clusters: クラスタ数
    :param kwargs: Additional arguments passed to the plot method.
    """
    if len(axes) != n_clusters:
        raise ValueError("Number of axes must be equal to the number of clusters")

    # cluster_labelsはどのデータがどのクラスタに属するか
    # medoid_indicesは各クラスタの代表点のインデックス
    cluster_labels, medoid_indices, sil_score = k_medoids(data, n_clusters)

    # 描画用色決定
    colors = plt.cm.tab10(np.linspace(0, 1, n_clusters))

    # medoid_indicesの軌跡だけ濃く描画する
    for idx, c_label in enumerate(cluster_labels):
        if idx in medoid_indices:
            alpha = 1.0
        else:
            alpha = 0.5

        plot_trajectory(
            data=data[idx],
            ax=axes[c_label],
            alpha=alpha,
            label=labels[idx],
            color=colors[c_label],
            **kwargs
        )

    for idx, ax in enumerate(axes):
        ax.set_title(f"Cluster {idx}")
        ax.legend(title="Games", loc='upper right')
        ax.grid(True)

    fig = axes[0].get_figure()
    fig.suptitle(f"Silhouette Score: {sil_score:.3f}")
