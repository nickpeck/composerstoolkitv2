"""Use a weighed random process to grow a three note motive.
The outcome is guided by a series of user-specified constraints.

In this case, we take the notes C, D, E and try to grow a 16 beat
phrase in C major using by repeatedly applying transpositions and inversions
to a motive
"""

from composerstoolkit.core import Event, FixedSequence, Container
from composerstoolkit.composers.solvers import grow_seed
from composerstoolkit.composers.constraints import (
    constraint_in_set, constraint_no_leaps_more_than)
from composerstoolkit.builders.transformers import *
from composerstoolkit.resources.rhythms import *
from composerstoolkit.resources import scales

seq = grow_seed(
    FixedSequence(events=[
        Event(pitches=[60], duration=QUARTER_NOTE),
        Event(pitches=[62], duration=QUARTER_NOTE),
        Event(pitches=[64], duration=QUARTER_NOTE)]),
    mutators=[
        transpose(2),
        transpose(-2),
        transpose(3),
        transpose(-3),
        invert(),
        retrograde(3)],
    constraints=[
        constraint_in_set(scales.C_major),
        constraint_no_leaps_more_than(4)],
    min_beats=16
)

Container(bpm=240, playback_rate=1)\
    .add_sequence(seq)\
    .playback()
