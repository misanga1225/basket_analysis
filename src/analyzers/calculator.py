import numpy as np

def max_recursive(
    data: dict | np.ndarray | np.float64
) -> float:
    """
    辞書型のデータから最大値を取り出す．
    ただし辞書型のデータの最下層はndarrayであることを前提とする．
    :param data: 最大値を求める全データ
    :return: 最大値
    """
    if isinstance(data, np.ndarray):
        return np.max(data)
    elif isinstance(data, dict):
        return max(max_recursive(v) for v in data.values())
    elif isinstance(data, float):
        return data
    else:
        raise ValueError('data must be ndarray or dict')

def max_len_recursive(
    data: dict | np.ndarray
) -> int:
    """
    辞書型のデータから最大長を取り出す．
    ただし辞書型のデータの最下層はndarrayであることを前提とする．
    :param data: 最大値を求める全データ
    :return: 最大長
    """
    if isinstance(data, np.ndarray):
        return data.shape[0]
    elif isinstance(data, dict):
        return max(max_len_recursive(v) for v in data.values())
    else:
        raise ValueError('data must be ndarray or dict')

def dict_average(
    data: dict | np.ndarray
) -> dict:
    """
    辞書型の最下層のndarrayの平均値を計算する．
    :param data: 平均値を計算する全データ
    :return: 平均値
    """
    if isinstance(data, np.ndarray):
        return data.mean()
    elif isinstance(data, dict):
        return {key: dict_average(value) for key, value in data.items()}
    else:
        raise ValueError('data must be ndarray or dict')

def dict_std_dev(
    data: dict | np.ndarray
) -> dict:
    """
    辞書型の最下層のndarrayの標準偏差を計算する．
    :param data: 標準偏差を計算する全データ
    :return: 標準偏差
    """
    if isinstance(data, np.ndarray):
        return data.std()
    elif isinstance(data, dict):
        return {key: dict_std_dev(value) for key, value in data.items()}
    else:
        raise ValueError('data must be ndarray or dict')

def z_normarize(
    data: dict | np.ndarray
) -> dict:
    """
    辞書型の最下層のndarrayのz正規化を計算する．
    :param data: z正規化を計算する全データ
    :return: z正規化
    """
    if isinstance(data, np.ndarray):
        return (data - data.mean()) / data.std()
    elif isinstance(data, dict):
        return {key: z_normarize(value) for key, value in data.items()}
    else:
        raise ValueError('data must be ndarray or dict')