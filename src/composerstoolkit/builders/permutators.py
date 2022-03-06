"""Library functions for derriving different permutations of a base sequence.
"""
import itertools
import math
from typing import Iterator, List, TypeVar, Generic

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
            perms = set(itertools.permutations(a))
            if self.return_last_gen_only and i == self.n_generations-1:
                return itertools.chain(perms)
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
