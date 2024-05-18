"""Library functions for derriving different permutations of a base sequence.
"""
import itertools
import math
from typing import Iterator, List, TypeVar, Generic
from more_itertools import windowed
import numpy as np

# pylint: disable=invalid-name
T = TypeVar('T')

class Permutations(Generic[T]):
    """Generate and manipulate permutations of an iterable
    """
    def __init__(self, starting_list: List[T],
        n_generations=1,
        return_last_gen_only=False):
        """
        Constructor for Permutations
        starting_list: List[T] - The list from which to seed the permutations
        kwargs:
            n_generations: int default 1
            return_last_gen_only: bool default False
        """
        self.starting_list = starting_list
        self.n_generations = n_generations
        self.return_last_gen_only = return_last_gen_only

    def __iter__(self) -> Iterator[List[T]]:
        generations = []
        for i in range(self.n_generations):
            a, b = itertools.tee(self.starting_list, 2)
            perms = itertools.permutations(a)
            if self.return_last_gen_only and i == self.n_generations-1:
                return itertools.chain(set(perms))
            try:
                generations.append(set(perms))
            except TypeError:
                generations.append(perms)
            if i < len(range(self.n_generations)):
                self.starting_list = self.__class__._new_generation(b)
        return itertools.chain(*generations)

    @staticmethod
    def _new_generation(parent_list) -> Iterator[List[T]]:
        for i in parent_list:
            if i <= 1:
                yield i
            elif i % 2 == 0:
                yield round(i/2)
                yield round(i/2)
            else:
                yield round(((i-1)/2) + 1)
                yield round((i-1)/2)

    def flatten(self) -> Iterator[T]:
        """Return the list of permutations as a single
        one-dimensional list
        """
        for _list in self:
            for item in _list:
                yield item

class SerialMatrix(Generic[T]):
    """
    Generate a Stockhausen-like array of permutations.
    for each item in the input list, return a new order, which is shifting of the
    source set relative to their cyclic indices in the ordered source set
    ie, for a sequence [2,1,3], yield permutations [2,1,3], [1,3,2], [3,2,1],
    this being based on [2,1,3] giving directional vectors [-1,2] in the ordered set {1,2,3}
    """
    def __init__(self, base_row=List[T]):
        self.base_row = base_row
        self.base_row_ordered = list(sorted(self.base_row))
        self.vectors = self._generate_vectors()

    def _generate_vectors(self):
        vectors = [self.base_row_ordered.index(right) - self.base_row_ordered.index(left) for left, right in windowed(self.base_row, 2)]
        return vectors

    def __iter__(self) -> Iterator[List[T]]:
        for item in self.base_row:
            result_list = [item]
            i = self.base_row_ordered.index(item)
            for v in self.vectors:
                i_current = self.base_row_ordered.index(result_list[-1])
                i_next = i_current + v
                if i_next > len(self.base_row_ordered)-1:
                    next = self.base_row_ordered[i_next - len(self.base_row_ordered)]
                else:
                    next = self.base_row_ordered[i_next]
                result_list.append(next)
            yield result_list

    def as_matrix(self) -> np.array:
        return np.array([permutation for permutation in self])
