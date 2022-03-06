"""Library functions for derriving different permutations of a base sequence.
"""
import itertools
from typing import Iterator, List, TypeVar, Generic

# pylint: disable=invalid-name
T = TypeVar('T')

class Permutations(Generic[T]):
    """Generate and manipulate permutations of an iterable
    """
    def __init__(self, starting_list: List[T], **kwargs):
        """
        Constructor for Permutations
        starting_list: List[T] - The list from which to seed the permutations
        kwargs:
            n_generations: int default 1
            return_last_gen_only: bool default False
        """
        self.starting_list = starting_list
        try:
            self.n_generations = kwargs["n_generations"]
        except KeyError:
            self.n_generations = 1

        try:
            self.return_last_gen_only = kwargs["return_last_gen_only"]
        except KeyError:
            self.return_last_gen_only = False

    def __iter__(self) -> Iterator[List[T]]:
        generations = []
        for i in range(self.n_generations):
            perms = itertools.permutations(self.starting_list)
            if self.return_last_gen_only and i == self.n_generations-1:
                return itertools.chain([perms])
            generations.append(perms)
            if i < len(range(self.n_generations)):
                self.starting_list = self.__class__._new_generation(self.starting_list)
        return itertools.chain(*generations)

    @staticmethod
    def _new_generation(parent_list) -> Iterator[List[T]]:
        next_gen = []
        for i in parent_list:
            if i <= 1:
                next_gen.append(i)
            elif i % 2 == 0:
                next_gen.append(i/2)
                next_gen.append(i/2)
            else:
                next_gen.append(((i-1)/2) + 1)
                next_gen.append((i-1)/2)
            yield i

    def flatten(self) -> Iterator[T]:
        """Return the list of permutations as a single
        one-dimensional list
        """
        for _list in self:
            for item in _list:
                yield item
