"""Illustrates using a gated transformer and tonality mapping to toggle
between two different tonalities
"""
import random

from composerstoolkit.core import Event, FiniteSequence, Container, Sequence, Constraint
from composerstoolkit.composers.solvers import develop
from composerstoolkit.composers.constraints import *
from composerstoolkit.builders.generators import *
from composerstoolkit.builders.transformers import *
from composerstoolkit.resources.rhythms import *
from composerstoolkit.composers.heuristics import *
from composerstoolkit.resources import scales, pitches, chords
from composerstoolkit.builders.permutators import Permutations

pf = pitches.PitchFactory()

def my_gate1(context):
    if context.beat_offset % 30 > 15:
        return False
    return True

even_pulse = Sequence.from_generator(
    pulses([EIGHTH_NOTE]))\
    .transform(loop())

chords = Sequence.from_generator(
    cantus([pf("G2"), pf("A2"), pf("B2"), pf("C2"), pf("D2"), pf("Gb2")])
).transform(
    loop()
).transform(
    map_to_pulses(even_pulse)
).transform(
    fit_to_range(
        min_pitch = pf("C3"),
        max_pitch = pf("C5"))
).transform(
    arpeggiate()
).transform(
    gated(
        map_tonality(scales.Db_major),
        my_gate1
    )
)

Container(bpm=150, playback_rate=1)\
    .add_sequence(chords)\
    .playback()
