"""Illustrates using a gated transformer and tonality mapping to toggle
between three different tonalities

The example uses a sequence based on a C mixolydian tonality
(notes of F maj). This is mapped to a 60 second cycle, whereby
the pitches are "quantized" into a different modalities.

0-20 Fmaj
20-40 Dmaj
40-60 Dbmaj

Due to the way the mapping works, a different modal colour
might emerge rather than a straightforward transposition. This
yields some contrasting harmonic tensions.
"""
import random

from composerstoolkit import *
from composerstoolkit.resources import scales, pitches
from composerstoolkit.resources.rhythms import *

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

backing_figure = Sequence(events=[
        Event([], duration=HALF_NOTE),
        Event([pf("G5")], duration=TIED(WHOLE_NOTE, WHOLE_NOTE))]
).transform(
    loop()
).transform(
    concertize(
        scale=list(scales.F_major),
        voicing=[4,4,3,4,4],
        direction="down"
    )
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

pulses = Sequence.from_generator(
    collision_pattern(4,5))\
    .transform(loop())

melody = Sequence.from_generator(
    random_choice(choices=[
        Event([pf("C6")]),
        Event([pf("D6")]),
        Event([pf("F6")]),
        Event([pf("G6")]),
        Event([pf("Bb6")]),
        Event([pf("C7")])])
).transform(
    map_to_pulses(pulses)
).transform(
    linear_interpolate(
        steps = 4,
        constrain_to_scale = list(scales.F_major))
).transform(
    rhythmic_augmentation(0.6)
).transform(
    tie_repeated()
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

Container(bpm=95, playback_rate=1)\
    .add_sequence(melody)\
    .add_sequence(backing_figure)\
    .add_sequence(chords)\
    .add_sequence(bassline)\
    .playback()
