"""Use a weighed random process to grow a three note motive.
The outcome is guided by a series of user-specified constraints.

In this case, we take the notes C, D, E and try to grow a 16 beat
phrase in C major using by repeatedly applying transpositions and inversions
to a motive.

The solver does not employ back-tracking, so it may well reach a dead-end
and need to be restarted a few times before a solution is reached.
"""

from composerstoolkit import *
from composerstoolkit.resources import scales

seq = develop(
    FiniteSequence(events=[
        Event(pitches=[60], duration=QUARTER_NOTE),
        Event(pitches=[62], duration=QUARTER_NOTE),
        Event(pitches=[64], duration=QUARTER_NOTE)]),
    mutators=[
        transpose_diatonic(1, scales.C_major),
        invert(),
        retrograde(3)],
    constraints=[
        constraint_in_set(scales.C_major),
        constraint_no_leaps_more_than(4)],
    min_beats=16
)

Context.get_context().new_sequencer(bpm=240, playback_rate=1)\
    .add_sequence(seq)\
    .playback()
