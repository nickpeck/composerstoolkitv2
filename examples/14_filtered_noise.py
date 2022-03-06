"""Probably of more use to textural compostion: the following example generates a
stream of random events and then illustrates various filters that might be applied to it.
"""

import random

from composerstoolkit import *
from composerstoolkit.resources import scales, pitches

pf = pitches.PitchFactory()

seq = Sequence.from_generator(
    random_noise(
        min_notes_per_chord=1,
        max_notes_per_chord=4)
).transform(
    fit_to_range(
        min_pitch = pf("C3"),
        max_pitch = pf("C5"))
).transform(
    fit_to_range(
        min_pitch = pf("C4"),
        max_pitch = pf("C5"))
).transform(
    rhythmic_augmentation(2)
).transform(
    modal_quantize(scales.C_mel_minor)
).transform(
    rhythmic_quantize(0.25)
).transform(
    filter_events(
        lambda e: min(e.pitches) < 59 or max(e.pitches) > 62
))

Container(bpm=150, playback_rate=1)\
    .add_sequence(seq)\
    .playback()
