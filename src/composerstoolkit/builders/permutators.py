"""Library functions for derriving different permutations of a base sequence.
"""
import itertools
from typing import Any, Iterator, List, TypeVar, Generic

T = TypeVar('T')

class Permutations(Generic[T]):
    def __init__(
        self,
        starting_list: List[T],
        n_generations: int=1,
        return_last_gen_only: bool=False):
        """
        return an unordered set of permutations of starting_list
        if n_generations,then derrive new generations as follows:
            if i is even, divide in two (4 => 2,2),
            else divide unevenly (5 => 3,2)
        if the new generation is {1}, do not bother dividing further
        """
        self.starting_list = starting_list
        self.n_generations = n_generations
        self.return_last_gen_only = return_last_gen_only

    def __iter__(self) -> Iterator[List[T]]:
        generations = []
        for i in range(self.n_generations):
            perms = itertools.permutations(self.starting_list)
            if self.return_last_gen_only and i == self.n_generations-1:
                return perms
            generations.append(perms)
            # if set(perms) == {1}:
                # break
            if i < len(range(self.n_generations)):
                starting_list = self._new_generation(self.starting_list)
        return itertools.chain(*generations)

    def _new_generation(self, parent_list) -> Iterator[List[T]]:
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
            yield int(i)

    def flatten(self) -> Iterator[T]:
        for _list in list(self):
            for item in _list:
                yield item
