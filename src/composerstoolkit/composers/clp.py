import random
from typing import List, Iterator, Callable

from .. core import FiniteSequence, Transformer, Constraint

class CLP:
    def __init__(self,
            source_material: List[FiniteSequence],
            max_len_beats: int,
            n_voices: int,
            transformations: List[Transformer] = None,
            constraints: List[Constraint] = None,
            heuristics: List[Callable] = None
        ):
        self._source_material = source_material
        self._max_len_beats = max_len_beats
        self._n_voices = n_voices
        if transformations is None:
            transformations = []
        self._transformations = transformations
        if constraints is None:
            constraints = []
        self._constraints = constraints
        if heuristics is None:
            heuristics = []
        self._heuristics = heuristics
        self.solutions: List[List[FiniteSequence]] = []
        # Todo, check not violates input constraints

    def _is_within_len(self, solution: List[FiniteSequence]):
        for seq in solution:
            if seq.duration > self._max_len_beats:
                return False
        return True

    def _pick_fragment(self) -> FiniteSequence:
        return random.choice(self._source_material)

    def _get_transformations(self,
            voice: FiniteSequence,
            motive: FiniteSequence) -> List[FiniteSequence]:
        if len(self._transformations) == 0:
            return [voice + motive]
        candidates: List[FiniteSequence] = []
        motive_as_seq = motive.to_sequence()
        for transformer in self._transformations:
            candidate = voice +\
                FiniteSequence(list(transformer(motive_as_seq)))
            candidates.append(candidate)
        return candidates

    def _check_constraints(self, 
        candidates: List[FiniteSequence]) -> List[FiniteSequence]:
        # context = Context(
            # event = a,
            # sequence = seq,
            # beat_offset = i,
            # previous = previous
        # )
        # for constraint in constraints:
            # if 
        # candidates = filter(lambda: , candidates)
        return candidates

    def _chose_best_fit(self, 
        candidates: List[FiniteSequence]) -> List[FiniteSequence]:
        # TODO
        return candidates[0]

    def __iter__(self):
        return self

    def __next__(self):
        solution: List[FiniteSequence] = \
                [FiniteSequence([]) for i in range(self._n_voices)]

        while self._is_within_len(solution):
            memento = solution[:]
            for i_voice, voice in enumerate(solution): # each voice
                motive = self._pick_fragment()
                candidates = self._get_transformations(voice, motive)
                candidates = self._check_constraints(candidates)
                if len(candidates) == 0:
                    solution = memento
                    break
                best_candidate = self._chose_best_fit(candidates)
                solution[i_voice] = best_candidate
        for i_voice, voice in enumerate(solution):
            solution[i_voice] = voice.time_slice(0, self._max_len_beats)
        return solution


"""
previous_state = {}
while all voices are less than duration:
    for each voice in n_voices:
        if seq len is > duration
            continue
        pick motive from source
            if all transformations tried:
                restore previous state
                Backtrack
                break
            try all transformations
                if result in bad_paths,
                    remove transformation for this round
                    continue
                if result violates constraints
                    add to bad_paths
                    remove transformation for this round
                    continue
                if result > duration
                    add to bad_paths
                    remove transformation for this round
                    continue
            assess all transformations according to heuristics
            pick highest score, or random choice if tie
            update voices
            previous_state = current state
    
        
"""