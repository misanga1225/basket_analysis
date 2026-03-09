import numpy as np

def round_up(value: float) -> float:
    """
    グラフ表示の上限に適した値に丸める．
    """
    if value == 0:
        return 0

    if value < 0:
        return -round_up(-value)

    digits = int(np.floor(np.log10(value))) + 1
    base = 10.0 ** (digits - 1)
    rounded_value = np.ceil(value / base) * base

    return rounded_value

if __name__ == "__main__":
    print(round_up(52133))
    print(round_up(120))
    print(round_up(0))
    print(round_up(-120))
    print(round_up(-52133))
