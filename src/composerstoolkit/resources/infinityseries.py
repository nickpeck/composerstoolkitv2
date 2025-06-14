from typing import Iterable
from itertools import count


def infinityseries(a, b) -> Iterable[int]:
    """
    Implementation of Per Norgard's infinity series for two starting integers a and b.
    """
    series = [a, b]
    yield a
    yield b
    for i in count(1, 1):
        item = series[2*i-2] - (series[i] - series[i-1])
        series.append(item)
        yield item
        item = series[2 * i - 1] + (series[i] - series[i - 1])
        series.append(item)
        yield item
