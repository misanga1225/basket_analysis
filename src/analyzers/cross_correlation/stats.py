import numpy as np
import scipy as sp

def cross_correlation(
    data: [np.ndarray, np.ndarray],
    norm: bool = True,
):
    """
    相互相関係数の計算
    :param data: 計算元のデータ
    :param norm: 正規化するかどうか
    :return: 相互相関係数
    """
    if len(data[0]) != len(data[1]):
        raise ValueError("Data must have the same length")

    result = sp.signal.correlate(data[0], data[1], mode='full')
    if norm:
        norm_factor = np.linalg.norm(data[0]) * np.linalg.norm(data[1])
        if norm_factor == 0:
            return np.zeros_like(result)
        result = result / norm_factor
    return result