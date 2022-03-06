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
        mod = context.beat_offset % cycle_length
        if mod >= in_secs and mod < out_secs:
            return False
        return True
    return _gate

even_pulse = Sequence.from_generator(
    pulses([EIGHTH_NOTE]))\
    .transform(loop())

chords = Sequence.from_generator(
    random_slice(Sequence(events=[
        Event([pf("G2")], duration=EIGHTH_NOTE),
        Event([pf("C3")], duration=EIGHTH_NOTE),
        Event([pf("F3")], duration=EIGHTH_NOTE),
        Event([pf("Bb3")], duration=EIGHTH_NOTE),
        Event([pf("C4")], duration=EIGHTH_NOTE)])
)).transform(
    loop()
).transform(
    map_to_pulses(even_pulse)
).transform(
    fit_to_range(
        min_pitch = pf("C2"),
        max_pitch = pf("C4"))
).transform(
    arpeggiate()
).transform(
    gated(
        modal_quantize(scales.Eb_major),
        time_gate(60,15,30)
    )
).transform(
    gated(
        modal_quantize(scales.Gb_major),
        time_gate(60,30,45)
    )
).transform(
    gated(
        modal_quantize(scales.Gb_major),
        time_gate(60,45,60)
    )
)

Container(bpm=95, playback_rate=1)\
    .add_sequence(chords)\
    .playback()
