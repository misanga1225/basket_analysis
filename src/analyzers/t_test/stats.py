import numpy as np
import scipy as sp

def t_test(
    data: [np.ndarray, np.ndarray]
) -> tuple[float, float, float]:
    """
    T検定を行う．
    :param data: T検定を行う二つのデータセット
    :return: T検定の結果 [t_stat, p_value, cohens_d]
    """
    t_stat, p_value = sp.stats.ttest_ind(data[0], data[1])

    n1, n2 = len(data[0]), len(data[1])
    var1, var2 = np.var(data[0], ddof=1), np.var(data[1], ddof=1)
    pooled_std = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
    cohens_d = (np.mean(data[0]) - np.mean(data[1])) / pooled_std
    
    return t_stat, p_value, cohens_d