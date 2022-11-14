import random
from typing import List, Iterator, Callable

from .. core import FiniteSequence, Transformer, Constraint, Sequencer

class CLP:
    class Voice(FiniteSequence):
        def __init__(self, events):
            self.constraints = []
            super().__init__(events)
        def add_constraint(self, constraint: Constraint):
            self.constraints.append(constraint)

    def __init__(self,
            source_material: List[FiniteSequence],
            max_len_beats: int,
            n_voices: int,
            transformations: List[Transformer] = None,
            heuristics: List[Callable] = None
        ):
        self._source_material = source_material
        self._max_len_beats = max_len_beats
        self._n_voices = n_voices
        self._constraints = []
        if transformations is None:
            transformations = []
        self._transformations = transformations
        if heuristics is None:
            heuristics = []
        self._heuristics = heuristics
        self.solutions: List[List[FiniteSequence]] = []
        # Todo, check not violates input constraints
        self.voices = []
        self.visited_paths:List[FiniteSequence] = []
        for i in range(self._n_voices):
            try:
                events = self._source_material[i].events
            except IndexError:
                events = []
            self.voices.append(CLP.Voice(events))

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
        random.shuffle(self._transformations)
        for trans in self._transformations:
            motive_as_seq = motive.to_sequence()
            candidate = voice +\
                FiniteSequence(list(trans(motive_as_seq)))
            candidates.append(candidate)
        return candidates

    def _exclude_visited_paths(self,
        candidates: List[FiniteSequence],
        i_voice: int) -> List[FiniteSequence]:
        results = []
        for candidate in candidates:
            rejected = False
            for solution in self.visited_paths:
                head = candidate
                if candidate.duration > solution[i_voice].duration:
                    head = candidate.time_slice(0, solution[i_voice].duration)
                if solution[i_voice] == head:
                    rejected = True
            if not rejected:
                results.append(candidate)
        return results

    def _check_global_constraints(self, 
        candidates: List[FiniteSequence]) -> List[FiniteSequence]:
        results = []
        for candidate in candidates:
            rejected = False
            for constraint in self._constraints:
                if not constraint(candidate):
                    rejected = True
                    break
            if not rejected:
                results.append(candidate)
        return results

    def _check_local_constraints(self, 
        candidates: List[FiniteSequence],
        i_voice: int,
        solution: List[FiniteSequence]) -> List[FiniteSequence]:
        results = []
        constraints = self.voices[i_voice].constraints
        for candidate in candidates:
            rejected = False
            for constraint in constraints:
                if not constraint(candidate):
                    rejected = True
                    break
            if not rejected:
                results.append(candidate)
        return results

    def add_constraint(self, constraint: Constraint):
        self._constraints.append(constraint)

    def _chose_best_fit(self, 
        candidates: List[FiniteSequence]) -> List[FiniteSequence]:
        # TODO
        return candidates[0]

    def __iter__(self):
        return self

    def __next__(self) -> Sequencer:
        solution: List[FiniteSequence] = \
                [FiniteSequence([]) for i in range(self._n_voices)]

        while self._is_within_len(solution):
            memento = solution[:]
            for i_voice, voice in enumerate(solution): # each voice
                motive = self._pick_fragment()
                candidates = self._get_transformations(voice, motive)
                candidates = self._exclude_visited_paths(candidates, i_voice)
                if len(candidates) == 0:
                    solution = memento
                    break
                candidates = self._check_local_constraints(candidates, i_voice, solution)
                if len(candidates) == 0:
                    solution = memento
                    break
                candidates = self._check_global_constraints(candidates)
                if len(candidates) == 0:
                    solution = memento
                    break
                best_candidate = self._chose_best_fit(candidates)
                solution[i_voice] = best_candidate
        for i_voice, voice in enumerate(solution):
            solution[i_voice] = voice.time_slice(0, self._max_len_beats)
        self.visited_paths.append(solution)
        sequencer = Sequencer()
        for seq in solution:
            sequencer.add_sequence(seq)
        return sequencer


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