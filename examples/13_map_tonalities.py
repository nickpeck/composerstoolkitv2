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

def time_gate(cycle_length, in_secs, out_secs):
    def _gate(context):
        nonlocal cycle_length
        nonlocal in_secs
        nonlocal out_secs
        mod = context.beat_offset % cycle_length
        if mod >= in_secs and mod < out_secs:
            return True
        return False
    return _gate

chords = Sequence(events=[
        Event([pf("C3")], duration=EIGHTH_NOTE),
        Event([pf("F3")], duration=EIGHTH_NOTE),
        Event([pf("G3")], duration=EIGHTH_NOTE),
        Event([pf("Bb3")], duration=EIGHTH_NOTE),
        Event([pf("C4")], duration=EIGHTH_NOTE)]
).transform(
    loop()
).transform(
    gated(
        # maps the pattern to D major between 20-40 secs
        modal_quantize(scales.D_major),
        time_gate(60,20,40)
    )
).transform(
    gated(
        # maps the pattern to D major between 40-60 secs
        modal_quantize(scales.Db_major),
        time_gate(60,40,60)
    )
)

bassline = Sequence(events=[
        Event([pf("C1")], duration=EIGHTH_NOTE)]
).transform(
    loop()
).transform(
    gated(
        # maps the pattern to D major between 20-40 secs
        modal_quantize(scales.D_major),
        time_gate(60,20,40)
    )
).transform(
    gated(
        # maps the pattern to D major between 40-60 secs
        modal_quantize(scales.Db_major),
        time_gate(60,40,60)
    )
).transform(
    tie_repeated()
)

Container(bpm=95, playback_rate=1)\
    .add_sequence(chords)\
    .add_sequence(bassline)\
    .playback()
