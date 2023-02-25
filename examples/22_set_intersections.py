"""Use the solver to generate a chord progressions
via transformations of a set, enforcing a minimum number
of common pitch classes per chord motion.
"""

import random
from composerstoolkit import *

source_set = {60,62,64,66,69}
n_chords = 4
min_shared_pitches = 3

##################################

@Transformer
def _transpose(seq: Sequence, interval) -> Iterator[Event]:
    """Transpose all pitches in the
    given sequence by a constant interval.
    """
    #interval = random.choice(range(1,12))
    for evt in seq.events:
        yield Event(
                pitches=[p + interval for p in evt.pitches],
                duration=evt.duration)

@Transformer
def _invert_chord(seq: Sequence):
    for evt in seq.events:
        pitches = evt.pitches
        new_pitches = [evt.pitches[0]]
        vectors = []
        for i,p in enumerate(pitches):
            if i == 0:
                vectors.append(0)
                continue
            vectors.append(pitches[i] - pitches[i-1])
        for v in vectors[:-1]:
            new_pitches.append(new_pitches[-1:][0] - v)
        yield Event(new_pitches, evt.duration)

transformations = [_invert_chord()] + [_transpose(i) for i in range(1,12)] + [_transpose(i) for i in range(-1,-12)]
#transformations = [_invert_chord(), _transpose(1)]

solver = CLP(
    source_material = [
        FiniteSequence([
            Event(list(source_set), WHOLE_NOTE)
        ])
    ],
    n_voices = 1,
    max_len_beats = 4 * n_chords,
    transformations = transformations
)

@Constraint
def constraint_enforce_shared_pitches(sequence: FiniteSequence, min_shared: int=1) -> bool:
    if len(sequence.events) < 2:
        return True
    it1,it2 = itertools.tee(sequence.events)
    next(it2, None)
    for left, right in zip(it1,it2):
        left_pitches = [p % 12 for p in left.pitches]
        right_pitches = [p % 12 for p in right.pitches]
        intersection = set(right_pitches).intersection(set(left_pitches))
        if len(intersection) < min_shared:
            return False
    return True

@Constraint
def constraint_all_different_pitches(sequence: FiniteSequence) -> bool:
    for event in sequence.events:
        if len(event.pitches) != len(set(event.pitches)):
            return False
    return True

@Constraint
def constraint_no_repeated_adjacent_chords(sequence: FiniteSequence) -> bool:
    if len(sequence.events) < 2:
        return True
    it1,it2 = itertools.tee(sequence.events)
    next(it2, None)
    for left, right in zip(it1,it2):
        left_pitches = set([p % 12 for p in left.pitches])
        right_pitches = set([p % 12 for p in right.pitches])
        if left_pitches == right_pitches:
            return False
    return True

solver.add_constraint(constraint_enforce_shared_pitches(min_shared=min_shared_pitches))
solver.add_constraint(constraint_no_repeated_adjacent_chords())
solver.add_constraint(constraint_all_different_pitches())

for solution in solver:
    print(solution)
    solution.show_notation().playback()
    for channel_no, offset, seq in solution.sequences:
        print(list(seq.events))
