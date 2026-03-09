import numpy as np
import matplotlib.pyplot as plt

def plot_feature(
    data: np.ndarray,
    ax: plt.Axes,
    position: int,
    bar_kwargs: dict = None,
    scatter_kwargs: dict = None
):
    """
    プレイヤーのボロノイ領域の面積の平均値を棒グラフで描画する．
    この関数では棒グラフ一つ分のみの描画を担当する（描画のカスタマイズ性の都合）
    :param data: プレイヤーのボロノイ領域の面積情報を格納したndarray
    :param ax: 描画先のAxes
    :param position: プレイヤーのボロノイ領域の面積の平均値を描画する位置
    :param bar_kwargs: matplotlib.pyplot.barの引数
    :param scatter_kwargs: matplotlib.pyplot.scatterの引数
    """
    if bar_kwargs is None:
        bar_kwargs = {}
    if scatter_kwargs is None:
        scatter_kwargs = {}

    # 通常の棒グラフの描画処理
    average = data.mean()
    ax.bar(position, average, **bar_kwargs)

    # 本データの散布図の描画処理
    offset_range = 0.2
    offsets = np.linspace(-offset_range, offset_range, len(data))
    ax.scatter(position + offsets, data, **scatter_kwargs)
    ax.grid(True, axis='y')

