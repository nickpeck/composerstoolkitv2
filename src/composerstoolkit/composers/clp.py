from typing import List, Iterator

from .. core import FiniteSequence, Transformer, Constraint

class InputViolatesConstraints(Exception):
    """Indicates that the seed given to a solver violates
    the constraints for the finished solution
    """

class CLPSolver:
    def __init__(self
            sequences: List[FiniteSequence],
            max_len_beats: int,
            transformers: List[Transformer] = None,
            constraints: List[Constraint] = None,
            heuristics: List[Callable] = None
        ):
        self._sequences = sequences
        self._max_len_beats = max_len_beats
        if transformers is None:
            transformers = []
        self._transformers = transformers
        if constraints is None:
            constraints = []
        self._constraints = constraints
        if heuristics is None:
            heuristics = []
        self._heuristics = heuristics

    def solve(self) -> Iterator[List[FiniteSequence]]:
        solutions: List[Sequence] = []
        cur_offset_beats = 0
        while cur_offset_beats <= self.max_len_beats:
            pass
        yield solution