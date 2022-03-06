"""Use a weighed random process to grow a three note motive.
The outcome is guided by a series of user-specified constraints.

In this case, we take the notes C, D, E and try to grow a 16 beat
phrase in C major using by repeatedly applying transpositions and inversions
to a motive
"""

from composerstoolkit.core import Event, FixedSequence, Container, Sequence
from composerstoolkit.composers.solvers import grow_cantus_backtracking
from composerstoolkit.composers.constraints import (
    constraint_in_set, constraint_no_leaps_more_than)
from composerstoolkit.builders.generators import *
from composerstoolkit.builders.transformers import *
from composerstoolkit.resources.rhythms import *
from composerstoolkit.resources import scales

even_pulse = Sequence.from_generator(
    pulses([QUARTER_NOTE]))\
    .transform(loop())

seq = grow_cantus_backtracking(
        Event(pitches=[60], duration=QUARTER_NOTE),
    n_events=16,
    constraints=[
        constraint_in_set(scales.C_major),
        constraint_no_leaps_more_than(4)],
)

seq = Sequence(seq.events).transform(map_to_pulses(even_pulse))

Container(bpm=240, playback_rate=1)\
    .add_sequence(seq)\
    .playback()
