import numpy as np
import scipy as sp
import matplotlib.pyplot as plt

from .stats import cross_correlation

def plot_cross_correlation(
    data: [np.ndarray, np.ndarray],
    ax: plt.Axes,
    normed: bool = True,
    **kwargs,
):
    """
    相互相関係数の描画
    :param data: 計算元のデータ
    :param ax: 描画先のaxes
    :param normed: 正規化するかどうか
    :param kwargs: その他
    """ 
    cross_correlation_values = cross_correlation(data, normed)

    max_lags = len(cross_correlation_values) // 2
    lags = np.arange(-max_lags, max_lags + 1)

    ax.stem(lags, cross_correlation_values, **kwargs)
    ax.set_xlabel('Lag')
    ax.set_ylabel('Cross-correlation')
    ax.set_xlim(-max_lags, max_lags)
    ax.set_ylim(-1, 1)
    ax.grid(axis='y')
