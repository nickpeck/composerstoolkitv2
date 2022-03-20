"""Use the solver to generate a chord progression 
via transformations of a set, enforcing a minimum number
of common pitch classes per chord motion.
"""

import random
from composerstoolkit import *

source_set = {60,62,64,66,69}
n_chords = 4
min_shared_pitches = 2

##################################

@Transformer
def _transpose(seq: Sequence) -> Iterator[Event]:
    """Transpose all pitches in the
    given sequence by a constant interval.
    """
    interval = random.choice(range(1,11))
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

transformations = [_transpose(), _invert_chord()]

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
    if len(sequence.events) > 2:
        return True
    it1,it2 = itertools.tee(sequence.events)
    next(it2, None)
    for left, right in zip(it1,it2):
        left_pitches = [p % 12 for p in left.pitches]
        right_pitches = [p % 12 for p in right.pitches]
        intersection = set(right_pitches).intersection(set(left_pitches))
        if len(intersection) <= min_shared:
            return False
    return True

solver.add_constraint(constraint_enforce_shared_pitches(min_shared=min_shared_pitches))

for solution in solver:
    solution.show_notation().playback()