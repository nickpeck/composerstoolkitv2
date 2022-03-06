"""Use a weighed random process to grow a three note motive.
The outcome is guided by a series of user-specified constraints.

In this case, we take the notes C, D, E and try to grow a 16 beat
phrase in C major using by repeatedly applying transpositions and inversions
to a motive
"""

from composerstoolkit import *
from composerstoolkit.resources import scales

seq = backtracking_solver(
        Event(pitches=[60], duration=QUARTER_NOTE),
    constraints=[
        constraint_in_set(scales.C_major),
        constraint_no_leaps_more_than(4)],
    heuristics=[
        heuristic_trend_upwards(60, 10)],
    n_events=15,
)

# we didn't use a constraint to prevent repeated notes,
# but we can use the tie_repeated transformer here to 
# make some interesting rhythms out of this repetition
seq = Sequence(seq.events).transform(tie_repeated())

Container(bpm=240, playback_rate=1)\
    .add_sequence(seq)\
    .playback()
